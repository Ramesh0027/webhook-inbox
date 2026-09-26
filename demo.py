from core import Inbox, sign

body = b'{"order":"ORDER-DEMO","event":"shipped"}'
box = Inbox(clock=lambda: 1000)
for _ in range(2):
    print(
        "New delivery:",
        box.accept(
            "evt-demo", body, 1000, sign(b"demo-only", 1000, body), b"demo-only"
        ),
    )
print("Pending:", box.pending())
box.mark_processed("evt-demo")
box.close()
