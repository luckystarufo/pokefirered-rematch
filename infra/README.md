# Rematch on AWS

One CDK stack, `Rematch`, in us-east-1. CDK runs in Docker (`tools/cdk.sh`); nothing to install but Docker.

| Piece | What it does |
|---|---|
| S3 bucket (private) | the page, EmulatorJS, the font, and the ROM (gzipped). Only CloudFront can read it (Origin Access Control). |
| CloudFront | HTTPS at `https://d….cloudfront.net/`. `/emulator/*` and `/rom/*` need a live session cookie, checked at the edge by a CloudFront Function (`edge/session-check.js`); revoked codes sit in a KeyValueStore. |
| Lambda `Api` (`lambda/api.mjs`) | `/api/*`: invite codes (24 h from first use), closing-page messages, invitation requests. Only answers requests that come through CloudFront. |
| DynamoDB | `Invites`, `Messages`, `InviteRequests`, `Throttle` (rate limit, auto-expiring). Messages and requests are kept even if the stack is deleted. |
| SNS | emails the host every message and request (confirm the subscription email once). |
| Budget | emails the host if the month's AWS bill passes (or is forecast to pass) $5. |

## Locks

- The bucket is private; only this CloudFront distribution can read it.
- `/emulator/*` and `/rom/*` need a signed, unexpired, unrevoked session cookie (checked at the edge).
- The API's Function URL only accepts requests signed by this distribution (IAM + Origin Access Control), and
  they must also carry the secret `x-origin-verify` header. POSTs carry an `x-amz-content-sha256` body hash
  (the page adds it) so CloudFront can sign them.
- Limits (Throttle table, by the visitor address CloudFront reports): 40 code tries/h, 10 invitation requests/h,
  50 requests/day in total, 10 messages per invite per day. At most 10 API copies run at once.
- The Lambda may only: read/update invites, add messages and requests, count throttle hits, email the host.

Settings live in `.local/deploy.json` (git-ignored): `notifyEmail`, `sessionSecret`, `originSecret`.

## Everyday

```sh
tools/rom-builder/make.sh                  # build the ROM (game/pokefirered.gba)
tools/deploy.sh diff                       # what would change
tools/deploy.sh                            # put the current page + ROM online
python3 tools/invite.py --aws add "Alex"   # a code for Alex (also: list, reset CODE, revoke CODE)
python3 tools/read-messages.py --aws       # messages and invitation requests
```

## Teardown

```sh
tools/cdk.sh destroy Rematch
```

This removes everything except the `Messages` and `InviteRequests` tables (kept on purpose). Delete those in
the DynamoDB console when you no longer want them. The one-time CDK bootstrap stack (`CDKToolkit`) stays too;
delete it from the CloudFormation console if you're done with CDK in this account.
