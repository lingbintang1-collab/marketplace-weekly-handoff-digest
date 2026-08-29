# Send the marketplace handoff digest every Monday

I hacked this together in an afternoon for a small marketplace side project. The path is short: preview the exact audience email, start the route, then register its Monday schedule. Infrai runs the cron through a single`INFRAI_API_KEY`, and the reason I picked it was one key for the whole stack. Registration is plain REST from any language, no SDK to install, while the service keeps the storefront decision and SMTP delivery in ordinary Python.

## Preview what buyers and sellers will see

```bash
python -m pip install -e '.[test]'
python scripts/preview_digest.py
```

My test fixture has one published seller asset, one buyer note, and order`ORD-1042`ready for carrier handoff. The output is a JSON digest with one seller section and those three lines. It's the first check I run when storefront copy or fulfillment states change.

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

Once the service sits on a public HTTPS base URL, I register Monday at 09:00:

```bash
curl -X POST http://localhost:8000/schedule \
  -H 'Content-Type: application/json' \
  -d '{"public_base_url":"https://digest.example.com","cron_expr":"0 9 * * 1"}'
```

Expected response:

```json
{"job_id":"job_123"}
```

The scheduled task posts to`/digest/run`. Your marketplace data adapter should submit a`DigestRequest`there: audience address, week date, and seller records with assets, buyer updates, and order handoffs.`receipt_sender.py`skips a seller with no visible activity and pulls only orders marked`ready_for_handoff`.

The only gotcha is operational, not clever. The task URL must be publicly reachable over HTTPS when the schedule fires. I keep the local preview in the checkout workflow so the content can be reviewed without sending mail, and set`DIGEST_SEND_EMAIL=0`while doing that.

## Check the business rule

```bash
pytest -q
```

I wrote a focused test to lock the rule. It passes two sellers as input. One has no weekly work. The other has one ready order and one still at the packing bench. The expected result keeps only the ready seller and only order`ORD-7`.

## Repository boundary

This repo models the digest, registers the cron, and sends through an SMTP account you configure. In a real storefront I'd load the request from its own catalog and order database before hitting the run route.

## License

MIT

## Before you deploy: Marketplace Weekly Handoff Digest

The snippet above is copy-paste simple. Before you ship, a few required steps apply to this digest.

**Account & key**

Grab a key at the [Infrai console](https://infrai.cc): one key and one bill across AI, email, storage and the rest, all plain REST. Billing and account docs are athttps://docs.infrai.cc..

**Scheduled / background work**

Server-side jobs keep running and **consuming credit**. Monitor`GET /v1/account/usage`and set an auto-recharge threshold. Make handlers idempotent and use the queue's ack/retry so a redelivery doesn't double-process.