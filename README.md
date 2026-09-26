# Webhook Inbox

![Project cover](docs/cover.svg)

Signed webhook ingestion with timestamp validation and durable duplicate suppression in SQLite.

An independent engineering lab by Ramesh Yenduri. Examples use synthetic data.

## Run

Python 3.12+; standard library only, no package installation required.

```sh
python demo.py
python -m unittest -v
```

## Design and behavior

`sign(secret, timestamp, body)` produces a SHA-256 HMAC over the timestamp and raw body. `Inbox.accept()` verifies freshness and the signature before decoding JSON or inserting a delivery. A unique event ID makes retries harmless. Reusing an ID for different content raises an error. Accepted payloads survive reopening the database; `pending()` and `mark_processed()` model an inbox consumer. Tests cover tampering, stale timestamps and duplicates.

## Read the code

- `core.py` — implementation and public API.
- `demo.py` — deterministic, runnable usage example.
- `test_core.py` — behavior and failure-path tests.
- `.github/workflows/ci.yml` — runs the suite on Python 3.12 and 3.13.

## Scope and tradeoffs

Library-level receiver, not a public HTTP service. Signature format is this demo's protocol, not a provider-specific scheme. Secrets are passed explicitly; no real secret is committed. Timestamp checks require synchronized clocks. Processing and downstream side effects are not an atomic transaction; consumers still need idempotency. A production queue would add claims, retries and retention.
