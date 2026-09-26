import hashlib
import hmac
import json
import sqlite3
import time


def sign(secret: bytes, timestamp: int, body: bytes) -> str:
    return hmac.new(
        secret, str(timestamp).encode() + b"." + body, hashlib.sha256
    ).hexdigest()


class Inbox:
    def __init__(self, path=":memory:", clock=time.time, tolerance=300):
        if tolerance < 0:
            raise ValueError("tolerance must be nonnegative")
        self.clock, self.tolerance = clock, tolerance
        self.db = sqlite3.connect(path)
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS inbox(id TEXT PRIMARY KEY, digest TEXT NOT NULL, payload TEXT NOT NULL, processed INTEGER NOT NULL DEFAULT 0)"
        )

    def accept(self, event_id, body, timestamp, signature, secret):
        if not event_id or not secret:
            raise ValueError("event ID and secret required")
        if abs(self.clock() - timestamp) > self.tolerance:
            raise ValueError("stale timestamp")
        if not hmac.compare_digest(sign(secret, timestamp, body), signature):
            raise ValueError("invalid signature")
        payload = json.loads(body)
        if not isinstance(payload, dict):
            raise ValueError("payload must be an object")
        digest = hashlib.sha256(body).hexdigest()
        with self.db:
            changed = self.db.execute(
                "INSERT OR IGNORE INTO inbox(id,digest,payload) VALUES (?,?,?)",
                (event_id, digest, body.decode()),
            ).rowcount
            prior = self.db.execute(
                "SELECT digest FROM inbox WHERE id=?", (event_id,)
            ).fetchone()[0]
            if prior != digest:
                raise ValueError("event ID reused with different payload")
        return bool(changed)

    def pending(self):
        return [
            (row[0], json.loads(row[1]))
            for row in self.db.execute(
                "SELECT id,payload FROM inbox WHERE processed=0 ORDER BY rowid"
            )
        ]

    def mark_processed(self, event_id):
        with self.db:
            if not self.db.execute(
                "UPDATE inbox SET processed=1 WHERE id=?", (event_id,)
            ).rowcount:
                raise KeyError(event_id)

    def close(self):
        self.db.close()
