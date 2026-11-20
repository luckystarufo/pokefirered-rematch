# Local dev server for web/. A stand-in for the AWS backend, with the same rules:
#  - never cached, so a normal reload always picks up the latest page, scripts and ROM;
#  - the invite gate: POST /api/invite {code} checks .local/invites.json (tools/invite.py). A code is valid for
#    24 hours from the first time it's entered, on any device; the browser gets a signed session cookie that
#    expires with it. GET /api/session says whether the cookie is still good;
#  - /rom/* and /emulator/* are only served with a valid session (in AWS, CloudFront checks the same cookie);
#  - POST /api/messages (closing page) and POST /api/invite-requests (gate page) append to .local/*.jsonl,
#    with a hidden bot-trap field and a per-visitor rate limit on the public request form.
import datetime, functools, hashlib, hmac, http.cookies, http.server, json, os, re, secrets, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(HERE, "..", "web")
LOCAL = os.path.join(HERE, "..", ".local")
INVITES = os.path.join(LOCAL, "invites.json")
SECRET_FILE = os.path.join(LOCAL, "session-secret")
MAX_BODY = 16 * 1024
INVITE_TTL = 24 * 3600
COOKIE = "rematch_session"
REQUEST_LIMIT = (5, 3600)  # at most 5 invitation requests per visitor per hour

os.makedirs(LOCAL, exist_ok=True)
if not os.path.exists(SECRET_FILE):
    with open(SECRET_FILE, "w") as f:
        f.write(secrets.token_hex(32))
SECRET = open(SECRET_FILE).read().strip().encode()

def now():
    return int(time.time())

def normalize_code(code):
    return re.sub(r"[^A-Z0-9]", "", str(code).upper())

def load_invites():
    try:
        with open(INVITES) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_invites(invites):
    with open(INVITES, "w") as f:
        json.dump(invites, f, indent=2)

def sign(code, exp):
    payload = f"{code}.{exp}"
    return payload + "." + hmac.new(SECRET, payload.encode(), hashlib.sha256).hexdigest()

def verify(token):
    """-> (code, exp) if the token is genuine and unexpired, else None"""
    try:
        code, exp, sig = token.split(".")
        good = hmac.new(SECRET, f"{code}.{exp}".encode(), hashlib.sha256).hexdigest()
        inv = load_invites().get(code)  # deleting an invite revokes it at once
        if hmac.compare_digest(sig, good) and int(exp) > now() and inv and inv.get("firstUsedAt") \
                and inv["firstUsedAt"] + INVITE_TTL > now():
            return code, int(exp)
    except Exception:
        pass
    return None

def append(name, entry):
    entry = {"at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), **entry}
    with open(os.path.join(LOCAL, name), "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

recent_requests = {}  # visitor -> [timestamps]

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def session(self):
        jar = http.cookies.SimpleCookie(self.headers.get("Cookie") or "")
        return verify(jar[COOKIE].value) if COOKIE in jar else None

    def reply(self, status, body=None, cookie=None):
        data = json.dumps(body or {}).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        if cookie:
            self.send_header("Set-Cookie", cookie)
        self.end_headers()
        self.wfile.write(data)

    def body(self):
        length = int(self.headers.get("Content-Length") or 0)
        if not 0 < length <= MAX_BODY:
            raise ValueError("size")
        return json.loads(self.rfile.read(length))

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/api/session":
            s = self.session()
            if not s:
                return self.reply(401)
            return self.reply(200, {"name": load_invites()[s[0]].get("name", ""), "expiresAt": s[1]})
        if path.startswith(("/rom/", "/emulator/")) and not self.session():
            return self.reply(401)
        return super().do_GET()

    def do_POST(self):
        path = self.path.split("?")[0]
        try:
            body = self.body()
        except Exception:
            return self.reply(400)
        if path == "/api/invite":
            return self.invite(body)
        if path == "/api/invite-requests":
            return self.invite_request(body)
        if path == "/api/messages":
            if not self.session():
                return self.reply(401)
            return self.message(body)
        return self.reply(404)

    def invite(self, body):
        code = normalize_code(body.get("code", ""))
        invites = load_invites()
        inv = invites.get(code)
        if not inv:
            return self.reply(404, {"error": "unknown"})
        if not inv.get("firstUsedAt"):
            inv["firstUsedAt"] = now()
            save_invites(invites)
        exp = inv["firstUsedAt"] + INVITE_TTL
        if exp <= now():
            return self.reply(410, {"error": "expired"})
        cookie = f"{COOKIE}={sign(code, exp)}; Max-Age={exp - now()}; Path=/; HttpOnly; SameSite=Lax"
        return self.reply(200, {"name": inv.get("name", ""), "expiresAt": exp}, cookie)

    def invite_request(self, body):
        if body.get("website"):  # the hidden bot trap: people never fill it in
            return self.reply(201)
        visitor = self.client_address[0]
        window_start = now() - REQUEST_LIMIT[1]
        times = [t for t in recent_requests.get(visitor, []) if t > window_start]
        if len(times) >= REQUEST_LIMIT[0]:
            return self.reply(429)
        email = str(body.get("email", "")).strip()[:254]
        why = str(body.get("why", "")).strip()[:2000]
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email) or not why:
            return self.reply(400)
        recent_requests[visitor] = times + [now()]
        append("invite-requests.jsonl", {"email": email, "why": why})
        return self.reply(201)

    def message(self, body):
        message = str(body.get("message", "")).strip()[:2000]
        if not message:
            return self.reply(400)
        append("messages.jsonl", {
            "invite": load_invites()[self.session()[0]].get("name", ""),
            "message": message,
            "trainerName": str(body.get("trainerName") or "")[:16],
            "rivalName": str(body.get("rivalName") or "")[:16],
            "yearPlayed": body.get("yearPlayed"),
        })
        return self.reply(201)

port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
handler = functools.partial(Handler, directory=WEB)
http.server.ThreadingHTTPServer(("127.0.0.1", port), handler).serve_forever()
