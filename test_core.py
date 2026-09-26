import unittest

from core import Inbox, sign


class Tests(unittest.TestCase):
    def setUp(self):
        self.box = Inbox(clock=lambda: 1000)
        self.body = b'{"order":"A"}'
        self.secret = b"demo-only"

    def tearDown(self):
        self.box.close()

    def accept(self, body=None, ts=1000):
        body = self.body if body is None else body
        return self.box.accept("e1", body, ts, sign(self.secret, ts, body), self.secret)

    def test_duplicate_and_ack(self):
        self.assertTrue(self.accept())
        self.assertFalse(self.accept())
        self.assertEqual(len(self.box.pending()), 1)
        self.box.mark_processed("e1")
        self.assertEqual(self.box.pending(), [])

    def test_tampered_and_stale(self):
        with self.assertRaises(ValueError):
            self.box.accept(
                "e1", b"{}", 1000, sign(self.secret, 1000, self.body), self.secret
            )
        with self.assertRaises(ValueError):
            self.accept(ts=699)
        self.assertEqual(self.box.pending(), [])

    def test_reused_id_and_invalid_payload(self):
        self.accept()
        with self.assertRaises(ValueError):
            self.accept(b'{"order":"B"}')
        self.assertEqual(self.box.pending()[0][1], {"order": "A"})
        with self.assertRaises(ValueError):
            self.accept(b"[]")


if __name__ == "__main__":
    unittest.main()
