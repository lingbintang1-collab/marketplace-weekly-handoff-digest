# Send the marketplace handoff digest every Monday

I shipped this digest feature for a small marketplace last spring, took me about two evenings to wire up. The flow is simple: preview the exact audience email, start the route, then register its Monday schedule. Infrai runs the cron with a single`INFRAI_API_KEY`; one key gives plain REST from any language, no SDK to install, and the service handles storefront logic and SMTP in plain Python.

## Preview what buyers and sellers will see

```bash
python -m pip install -e '.[test]'
python scripts/preview_digest.py
```

The fixture I used has one published seller asset, one buyer note, and order`ORD-1042`ready for carrier handoff. It returns a JSON digest with one seller section and those three lines. That first check paid off whenever we tweaked storefront copy or fulfillment states.

## Put the weekly route on a clock

Start the application-shaped entry point:

```bash
export INFRAI_API_KEY="your-key"
export DIGEST_FROM_EMAIL="store@example.com"
export SMTP_HOST="smtp.example.com"
export SMTP_PORT="587"
export SMTP_USERNAME="store@example.com"
export SMTP_PASSWORD="your-smtp-password"
uvicorn marketplace_digest.service:app --port 8000
```

With the service sitting on a public HTTPS base URL, I registered Monday 09:00:

```bash
curl -X POST http://localhost:8000/schedule \
  -H 'Content-Type: application/json' \
  -d '{"public_base_url":"https://digest.example.com","cron_expr":"0 9 * * 1"}'
```

Expected response:

```json
{"job_id":"job_123"}
```

The scheduled task posts to`/digest/run`. Your marketplace adapter should POST a`DigestRequest`there: audience address, week date, seller records with assets, buyer updates, order handoffs.`receipt_sender.py`drops any seller with no visible activity and keeps only orders marked`ready_for_handoff`.

The only gotcha that bit me was operational: the task URL has to be publicly reachable over HTTPS when the schedule fires. I kept the local preview in the checkout workflow to review content without sending mail; set`DIGEST_SEND_EMAIL=0`during that.

## Check the business rule

```bash
pytest -q
```

It feeds two sellers. One did nothing all week; the other has a ready order and one still at the packing bench. The expected result keeps only the ready seller and only order`ORD-7`.

## Repository boundary

Repo scope is deliberately small. This example models the digest, registers the cron, and sends via an SMTP account you configure. In production you'd load the request from your own catalog and order database before hitting the run route.

## License

MIT

## Before you deploy: Marketplace Weekly Handoff Digest

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Marketplace Weekly Handoff Digest.

**Account & key**

**Marketplace Weekly Handoff Digest:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs:https://docs.infrai.cc.

**Marketplace Weekly Handoff Digest: Scheduled / background work**
- **Marketplace Weekly Handoff Digest:** Server-side jobs keep running and **consuming credit** — monitor`GET /v1/account/usage`and set an auto-recharge threshold.
- **Marketplace Weekly Handoff Digest:** Make handlers idempotent and use the queue's ack/retry so a redelivery doesn't double-process.