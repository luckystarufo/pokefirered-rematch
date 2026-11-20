#!/usr/bin/env python3
"""Read what friends left: closing-page messages and invitation requests, oldest first.

  tools/read-messages.py          from the local server (.local/*.jsonl)
  tools/read-messages.py --aws    from the deployed DynamoDB tables (names in .local/outputs.json)
"""
import json, os, subprocess, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def local(name):
    try:
        with open(os.path.join(ROOT, ".local", name), encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]
    except FileNotFoundError:
        return []


def scan(table):
    items, start = [], None
    while True:
        args = ["aws", "dynamodb", "scan", "--table-name", table, "--region", "us-east-1", "--output", "json"]
        if start:
            args += ["--exclusive-start-key", json.dumps(start)]
        r = subprocess.run(args, capture_output=True, text=True)
        if r.returncode:
            sys.exit(r.stderr.strip())
        page = json.loads(r.stdout)
        for it in page.get("Items", []):
            row = {k: list(v.values())[0] for k, v in it.items()}
            row["at"] = row.pop("id", "").split("#")[0]
            items.append(row)
        start = page.get("LastEvaluatedKey")
        if not start:
            return items


def main():
    if sys.argv[1:] == ["--aws"]:
        try:
            with open(os.path.join(ROOT, ".local", "outputs.json")) as f:
                out = json.load(f)["Rematch"]
        except FileNotFoundError:
            sys.exit("No .local/outputs.json: deploy first (tools/deploy.sh).")
        messages, requests = scan(out["MessagesTable"]), scan(out["RequestsTable"])
    elif not sys.argv[1:]:
        messages, requests = local("messages.jsonl"), local("invite-requests.jsonl")
    else:
        sys.exit(__doc__)

    print(f"=== Messages ({len(messages)}) ===")
    for m in sorted(messages, key=lambda m: m["at"]):
        who = m.get("invite") or "?"
        print(f"\n{m['at'][:16]}  {who}  (trainer {m.get('trainerName')}, rival {m.get('rivalName')}, "
              f"played {m.get('yearPlayed')})\n  {m['message']}")
    print(f"\n=== Invitation requests ({len(requests)}) ===")
    for r in sorted(requests, key=lambda r: r["at"]):
        print(f"\n{r['at'][:16]}  {r['email']}\n  {r['why']}")


main()
