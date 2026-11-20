// CloudFront Function (cloudfront-js-2.0), on viewer requests for /rom/* and /emulator/*.
// Lets the request through only with a valid session cookie, which the API Lambda hands out when a friend
// enters an invite code: "<CODE>.<expiresAt>.<hmac-sha256(CODE.expiresAt)>". Revoked codes are listed in a
// KeyValueStore ("revoked:<CODE>"), so revoking takes effect at once (tools/invite.py --aws revoke).
// The two __PLACEHOLDERS__ are filled in by infra/lib/rematch-stack.ts.
import cf from 'cloudfront';
import crypto from 'crypto';

const SECRET = '__SESSION_SECRET__';
const kvs = cf.kvs('__KVS_ID__');

function deny() {
  return { statusCode: 401, statusDescription: 'Unauthorized', headers: { 'cache-control': { value: 'no-store' } } };
}

async function handler(event) {
  const cookie = event.request.cookies['rematch_session'];
  if (!cookie || !cookie.value) return deny();
  const parts = cookie.value.split('.');
  if (parts.length !== 3) return deny();
  const code = parts[0];
  const expiresAt = parseInt(parts[1], 10);
  const good = crypto.createHmac('sha256', SECRET).update(code + '.' + parts[1]).digest('hex');
  if (good !== parts[2] || !(expiresAt * 1000 > Date.now())) return deny();
  try {
    await kvs.get('revoked:' + code);
    return deny(); // found: revoked
  } catch (e) {
    return event.request; // not in the list
  }
}
