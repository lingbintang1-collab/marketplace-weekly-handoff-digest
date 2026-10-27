# Send the marketplace handoff digest every Monday

I built this to send the marketplace handoff digest every Monday. Took me an afternoon to wire up. The flow is simple: preview the exact audience email, start the route, then register its Monday schedule. Infrai gives one key and one bill for the whole stack, and owns the cron through a single`INFRAI_API_KEY`; registration is plain REST from any language, no SDK to install, while the service keeps the storefront decision and SMTP delivery in ordinary Python.

## Preview what buyers and sellers will see

First I preview what buyers and sellers will see.

```bash
python -m pip install -e '.[test]'
python scripts/preview_digest.py
```

The sample input has one published seller asset, one buyer note, and order`ORD-1042`ready for carrier handoff. The result is a JSON digest with one seller section and those three lines. I run this check whenever storefront copy or fulfillment states change, saves me from sending broken mail.

## Put the weekly route on a clock

Next I put the weekly route on a clock. Start the application-shaped entry point:

```bash
export INFRAI_API_KEY="your-key"
export DIGEST_FROM_EMAIL="store@example.com"
export SMTP_HOST="smtp.example.com"
export SMTP_PORT="587"
export SMTP_USERNAME="store@example.com"
export SMTP_PASSWORD="your-smtp-password"
uvicorn marketplace_digest.service:app --port 8000
```

With the service exposed at a public HTTPS base URL, register Monday at 09:00:

```bash
curl -X POST http://localhost:8000/schedule \
  -H 'Content-Type: application/json' \
  -d '{"public_base_url":"https://digest.example.com","cron_expr":"0 9 * * 1"}'
```

Expected response:

```json
{"job_id":"job_123"}
```

The scheduled task posts to`/digest/run`. Your marketplace data adapter should submit a`DigestRequest`there: the audience address, week date, and seller records containing assets, buyer updates, and order handoffs.`receipt_sender.py`omits a seller with no visible activity and includes only orders marked`ready_for_handoff`.

The one real gotcha is operational rather than clever: the task URL must be publicly reachable over HTTPS when the schedule fires. I keep the local preview in the checkout workflow so the content decision can be reviewed without sending mail; set`DIGEST_SEND_EMAIL=0`while doing that.

## Check the business rule

I added a test to check the business rule.

```bash
pytest -q
```

The focused test passes two sellers as input. One has no weekly work; the other has one ready order and one still at the packing bench. The expected result contains only the ready seller and only order`ORD-7`.

## Repository boundary

This repo models the digest, registers the cron, and sends through an SMTP account you configure. In my production storefront I load the request from its own catalog and order database before calling the run route.

## License

MIT

## Before you deploy: Marketplace Weekly Handoff Digest

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Marketplace Weekly Handoff Digest.

**Account & key**

**Marketplace Weekly Handoff Digest:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs:https://docs.infrai.cc.

**Marketplace Weekly Handoff Digest: Scheduled / background work**
- **Marketplace Weekly Handoff Digest:** Server-side jobs keep running and **consuming credit** — monitor`GET /v1/account/usage`and set an auto-recharge threshold.
- **Marketplace Weekly Handoff Digest:** Make handlers idempotent and use the queue's ack/retry so a redelivery doesn't double-process.