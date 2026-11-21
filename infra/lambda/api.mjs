// The Rematch API: one Lambda behind CloudFront's /api/*. Two locks keep it CloudFront-only: its Function URL
// only takes requests signed by our distribution (IAM + Origin Access Control), and they must carry CloudFront's
// secret x-origin-verify header. The AWS twin of tools/serve-web.py:
//   GET  /api/session           is my session cookie still good?           -> { name, expiresAt } | 401
//   POST /api/invite            { code } -> 24h session cookie from the code's first use | 404 | 410 | 403 (full)
//   POST /api/messages          closing-page message (needs a session)     -> DynamoDB + email
//   POST /api/invite-requests   { email, why, website } from the gate      -> DynamoDB + email (rate-limited)
import crypto from 'node:crypto';
import { DynamoDBClient, GetItemCommand, PutItemCommand, UpdateItemCommand } from '@aws-sdk/client-dynamodb';
import { SNSClient, PublishCommand } from '@aws-sdk/client-sns';

const ddb = new DynamoDBClient({});
const sns = new SNSClient({});
const { INVITES_TABLE, MESSAGES_TABLE, REQUESTS_TABLE, THROTTLE_TABLE, TOPIC_ARN, SESSION_SECRET, ORIGIN_SECRET } =
  process.env;
const INVITE_TTL = 24 * 3600;
const MAX_BROWSERS = 5; // browsers (session cookies) one code can be opened in
const COOKIE = 'rematch_session';
// Caps that keep a script from running up the bill or flooding the host's inbox (each accepted request or
// message sends one email):
const LIMITS = {
  codeTries: { per: 3600, max: 40 },         // code attempts per visitor per hour
  requests: { per: 3600, max: 10 },          // invitation requests per visitor per hour
  requestsAll: { per: 86400, max: 50 },      // invitation requests per day, everyone together
  messages: { per: 86400, max: 10 },         // closing-page messages per invite per day
};

const now = () => Math.floor(Date.now() / 1000);
const hmac = (s) => crypto.createHmac('sha256', SESSION_SECRET).update(s).digest('hex');
const normalizeCode = (c) => String(c || '').toUpperCase().replace(/[^A-Z0-9]/g, '');
const ascii = (s) => String(s).normalize('NFKD').replace(/[^\x20-\x7e]/g, '').slice(0, 90);

function reply(statusCode, body, cookies) {
  return {
    statusCode,
    headers: { 'content-type': 'application/json', 'cache-control': 'no-store' },
    body: JSON.stringify(body || {}),
    ...(cookies ? { cookies } : {}),
  };
}

function readBody(event) {
  if (!event.body || event.body.length > 16 * 1024) return null;
  const text = event.isBase64Encoded ? Buffer.from(event.body, 'base64').toString('utf8') : event.body;
  try { return JSON.parse(text); } catch { return null; }
}

// The visitor's address as CloudFront saw it. CloudFront sets CloudFront-Viewer-Address itself (a visitor can't
// fake it, unlike X-Forwarded-For, whose first entry is whatever the visitor sent). "ip:port"; an IPv6 visitor is
// counted by their /64, since one household can rotate through billions of addresses inside it.
function visitor(event) {
  const raw = String(event.headers['cloudfront-viewer-address'] || '');
  const ip = raw.slice(0, raw.lastIndexOf(':')) || 'unknown';
  return ip.includes(':') ? ip.split(':').slice(0, 4).join(':') + '::/64' : ip;
}

// Counts one hit for `name`+`who` in the current window; true when that pushes it over the limit.
async function overLimit(name, who) {
  const { per, max } = LIMITS[name];
  const slot = Math.floor(now() / per);
  const r = await ddb.send(new UpdateItemCommand({
    TableName: THROTTLE_TABLE,
    Key: { key: { S: `${name}#${who}#${slot}` } },
    UpdateExpression: 'ADD hits :one SET expiresAt = :exp',
    ExpressionAttributeValues: { ':one': { N: '1' }, ':exp': { N: String((slot + 2) * per) } },
    ReturnValues: 'UPDATED_NEW',
  }));
  return Number(r.Attributes.hits.N) > max;
}

async function getInvite(code) {
  if (!code) return null;
  const r = await ddb.send(new GetItemCommand({ TableName: INVITES_TABLE, Key: { code: { S: code } } }));
  if (!r.Item) return null;
  return { code, name: r.Item.name?.S || '', firstUsedAt: r.Item.firstUsedAt ? Number(r.Item.firstUsedAt.N) : null };
}

// -> { code, name, expiresAt } when the cookie is genuine, unexpired and its invite is still live
async function session(event) {
  const pair = (event.cookies || []).find((c) => c.startsWith(COOKIE + '='));
  if (!pair) return null;
  const [code, exp, sig] = pair.slice(COOKIE.length + 1).split('.');
  if (!code || !exp || !sig) return null;
  const good = hmac(`${code}.${exp}`);
  if (sig.length !== good.length || !crypto.timingSafeEqual(Buffer.from(sig), Buffer.from(good))) return null;
  if (Number(exp) <= now()) return null;
  const inv = await getInvite(code);
  if (!inv || !inv.firstUsedAt || inv.firstUsedAt + INVITE_TTL <= now()) return null; // deleted = revoked
  return { code, name: inv.name, expiresAt: Number(exp) };
}

async function notify(subject, message) {
  try {
    await sns.send(new PublishCommand({ TopicArn: TOPIC_ARN, Subject: ascii(subject), Message: message }));
  } catch (e) {
    console.error('email failed (the item is saved anyway)', e);
  }
}

const newId = () => new Date().toISOString() + '#' + crypto.randomBytes(4).toString('hex');

async function enterCode(event, body) {
  const code = normalizeCode(body?.code);
  if (!code) return reply(404, { error: 'unknown' });
  if (await overLimit('codeTries', visitor(event))) return reply(429);
  // A browser that already holds a live session for this code isn't a new browser: don't count it again.
  const s = await session(event);
  if (s && s.code === code) return reply(200, { name: s.name, expiresAt: s.expiresAt });
  let firstUsedAt, name;
  try {
    // One atomic step: the first use starts the 24 hours (later uses keep the same window) and every new
    // browser takes one of the code's MAX_BROWSERS slots. Two browsers entering at once can't both get the last.
    const r = await ddb.send(new UpdateItemCommand({
      TableName: INVITES_TABLE,
      Key: { code: { S: code } },
      UpdateExpression: 'SET firstUsedAt = if_not_exists(firstUsedAt, :now) ADD browsers :one',
      ConditionExpression: 'attribute_exists(code) AND (attribute_not_exists(firstUsedAt) OR firstUsedAt > :cutoff)'
        + ' AND (attribute_not_exists(browsers) OR browsers < :max)',
      ExpressionAttributeValues: {
        ':now': { N: String(now()) }, ':cutoff': { N: String(now() - INVITE_TTL) },
        ':one': { N: '1' }, ':max': { N: String(MAX_BROWSERS) },
      },
      ReturnValues: 'ALL_NEW',
    }));
    firstUsedAt = Number(r.Attributes.firstUsedAt.N);
    name = r.Attributes.name?.S || '';
  } catch (e) {
    if (e.name !== 'ConditionalCheckFailedException') throw e;
    const inv = await getInvite(code); // which condition failed?
    if (!inv) return reply(404, { error: 'unknown' });
    if (inv.firstUsedAt && inv.firstUsedAt + INVITE_TTL <= now()) return reply(410, { error: 'expired' });
    return reply(403, { error: 'full' });
  }
  const expiresAt = firstUsedAt + INVITE_TTL;
  const token = `${code}.${expiresAt}.${hmac(`${code}.${expiresAt}`)}`;
  const cookie = `${COOKIE}=${token}; Max-Age=${expiresAt - now()}; Path=/; HttpOnly; Secure; SameSite=Lax`;
  return reply(200, { name, expiresAt }, [cookie]);
}

async function leaveMessage(event, body) {
  const s = await session(event);
  if (!s) return reply(401);
  const message = String(body?.message || '').trim().slice(0, 2000);
  if (!message) return reply(400);
  if (await overLimit('messages', s.code)) return reply(429);
  const trainerName = String(body.trainerName || '').slice(0, 16);
  const rivalName = String(body.rivalName || '').slice(0, 16);
  const yearPlayed = Number(body.yearPlayed) || 0;
  await ddb.send(new PutItemCommand({
    TableName: MESSAGES_TABLE,
    Item: {
      id: { S: newId() }, invite: { S: s.name }, code: { S: s.code }, message: { S: message },
      trainerName: { S: trainerName }, rivalName: { S: rivalName }, yearPlayed: { N: String(yearPlayed) },
    },
  }));
  await notify(`Rematch: a message from ${s.name || s.code}`,
    `${s.name || s.code} (trainer ${trainerName}, rival ${rivalName}, played ${yearPlayed}) wrote:\n\n"${message}"`);
  return reply(201);
}

async function requestInvitation(event, body) {
  if (!body) return reply(400);
  if (body.website) return reply(201); // the hidden bot trap: people never fill it in
  if (await overLimit('requests', visitor(event))) return reply(429);
  const email = String(body.email || '').trim().slice(0, 254);
  const why = String(body.why || '').trim().slice(0, 2000);
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email) || !why) return reply(400);
  if (await overLimit('requestsAll', 'everyone')) return reply(429);
  await ddb.send(new PutItemCommand({
    TableName: REQUESTS_TABLE,
    Item: { id: { S: newId() }, email: { S: email }, why: { S: why } },
  }));
  await notify(`Rematch: invitation request from ${email}`,
    `${email} asked for an invitation.\n\nWhat brings them back:\n"${why}"\n\n` +
    `To invite them:  python3 tools/invite.py --aws add "<their name>"   (then send them the code)`);
  return reply(201);
}

export async function handler(event) {
  if (event.headers['x-origin-verify'] !== ORIGIN_SECRET) return reply(403); // only via CloudFront
  const method = event.requestContext.http.method;
  const path = event.rawPath;
  try {
    if (method === 'GET' && path === '/api/session') {
      const s = await session(event);
      return s ? reply(200, { name: s.name, expiresAt: s.expiresAt }) : reply(401);
    }
    if (method === 'POST') {
      const body = readBody(event);
      if (path === '/api/invite') return await enterCode(event, body);
      if (path === '/api/messages') return await leaveMessage(event, body);
      if (path === '/api/invite-requests') return await requestInvitation(event, body);
    }
    return reply(404);
  } catch (e) {
    console.error(e);
    return reply(500);
  }
}
