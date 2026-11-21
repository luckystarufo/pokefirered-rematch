#!/usr/bin/env python3
"""Invite codes. Locally they live in .local/invites.json (tools/serve-web.py); with --aws, in the deployed
DynamoDB table (names from .local/outputs.json, written by tools/deploy.sh). A code is valid for 24 hours
from the first time it's entered, in up to 5 browsers (each browser that enters it takes one of the 5).

  tools/invite.py [--aws] add "Alex"     create a code for Alex
  tools/invite.py [--aws] list           every code: who, unused/active/expired, browsers used (of 5)
  tools/invite.py [--aws] reset CODE     give a code a fresh 24 hours and all 5 browsers back (from next use)
  tools/invite.py [--aws] revoke CODE    delete a code; it stops working at once, even mid-game
"""
import json, os, secrets, subprocess, sys, time

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
INVITES = os.path.join(ROOT, ".local", "invites.json")
OUTPUTS = os.path.join(ROOT, ".local", "outputs.json")
ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"  # no 0/O, 1/I/L: easy to read out loud
TTL = 24 * 3600
MAX_BROWSERS = 5  # same as the API (infra/lambda/api.mjs, tools/serve-web.py)


def pretty(code):
    return code[:4] + "-" + code[4:]


def norm(code):
    return "".join(c for c in code.upper() if c.isalnum())


def state(first_used):
    if not first_used:
        return "unused"
    left = first_used + TTL - time.time()
    return f"active, {int(left / 3600)}h left" if left > 0 else "expired"


class Local:
    def load(self):
        try:
            with open(INVITES) as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save(self, invites):
        os.makedirs(os.path.dirname(INVITES), exist_ok=True)
        with open(INVITES, "w") as f:
            json.dump(invites, f, indent=2)

    def add(self, code, name):
        invites = self.load()
        invites[code] = {"name": name, "createdAt": int(time.time()), "firstUsedAt": None}
        self.save(invites)

    def all(self):
        return [(c, i.get("name", ""), i.get("firstUsedAt"), i.get("browsers", 0)) for c, i in self.load().items()]

    def reset(self, code):
        invites = self.load()
        if code not in invites:
            sys.exit(f"No such code: {pretty(code)}")
        invites[code]["firstUsedAt"] = None
        invites[code]["browsers"] = 0
        self.save(invites)

    def revoke(self, code):
        invites = self.load()
        if code not in invites:
            sys.exit(f"No such code: {pretty(code)}")
        del invites[code]
        self.save(invites)


class Aws:
    def __init__(self):
        try:
            with open(OUTPUTS) as f:
                out = json.load(f)["Rematch"]
        except FileNotFoundError:
            sys.exit("No .local/outputs.json: deploy first (tools/deploy.sh).")
        self.table = out["InvitesTable"]
        self.kvs = out["RevokedStoreArn"]

    def aws(self, *args):
        r = subprocess.run(["aws", *args, "--region", "us-east-1", "--output", "json"], capture_output=True, text=True)
        if r.returncode:
            sys.exit(r.stderr.strip())
        return json.loads(r.stdout) if r.stdout.strip() else {}

    def add(self, code, name):
        item = {"code": {"S": code}, "name": {"S": name}, "createdAt": {"N": str(int(time.time()))}}
        self.aws("dynamodb", "put-item", "--table-name", self.table, "--item", json.dumps(item),
                 "--condition-expression", "attribute_not_exists(code)")

    def all(self):
        items, start = [], None
        while True:
            args = ["dynamodb", "scan", "--table-name", self.table]
            if start:
                args += ["--exclusive-start-key", json.dumps(start)]
            r = self.aws(*args)
            items += r.get("Items", [])
            start = r.get("LastEvaluatedKey")
            if not start:
                break
        return [(i["code"]["S"], i.get("name", {}).get("S", ""),
                 int(i["firstUsedAt"]["N"]) if "firstUsedAt" in i else None,
                 int(i["browsers"]["N"]) if "browsers" in i else 0) for i in items]

    def reset(self, code):
        self.aws("dynamodb", "update-item", "--table-name", self.table, "--key", json.dumps({"code": {"S": code}}),
                 "--update-expression", "REMOVE firstUsedAt, browsers", "--condition-expression", "attribute_exists(code)")

    def revoke(self, code):
        self.aws("dynamodb", "delete-item", "--table-name", self.table, "--key", json.dumps({"code": {"S": code}}))
        # the edge check (CloudFront) can't read DynamoDB: tell it through the KeyValueStore
        etag = self.aws("cloudfront-keyvaluestore", "describe-key-value-store", "--kvs-arn", self.kvs)["ETag"]
        self.aws("cloudfront-keyvaluestore", "put-key", "--kvs-arn", self.kvs, "--key", f"revoked:{code}",
                 "--value", "1", "--if-match", etag)


def main(args):
    store = Aws() if args[:1] == ["--aws"] else Local()
    if args[:1] == ["--aws"]:
        args = args[1:]
    if args[:1] == ["add"] and len(args) == 2:
        code = "".join(secrets.choice(ALPHABET) for _ in range(8))
        store.add(code, args[1])
        print(f"{args[1]}: {pretty(code)}")
    elif args == ["list"]:
        for code, name, first_used, browsers in sorted(store.all(), key=lambda x: x[1].lower()):
            print(f"{pretty(code)}  {name:<16} {state(first_used):<18} {browsers}/{MAX_BROWSERS} browsers")
    elif args[:1] in (["reset"], ["revoke"]) and len(args) == 2:
        code = norm(args[1])
        getattr(store, args[0])(code)
        print(f"{args[0]}: {pretty(code)}")
    else:
        sys.exit(__doc__)


main(sys.argv[1:])
