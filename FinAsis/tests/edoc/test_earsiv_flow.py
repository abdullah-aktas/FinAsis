from __future__ import annotations

from edoc.gib.client import GibClient


def test_earsiv_send_and_poll_idempotent(tmp_path):
    client = GibClient(state_dir=str(tmp_path))
    xml = b"<Invoice/>"
    res1 = client.send_archive_invoice(xml, idempotency_key="abc")
    assert res1.status == "PENDING"
    # idempotent
    res2 = client.send_archive_invoice(xml, idempotency_key="abc")
    assert res2.status == "PENDING"

    # poll progresses to ACCEPTED
    st1 = client.poll(res1.tracking_id)
    assert st1 in ("PENDING", "ACCEPTED")
    st2 = client.poll(res1.tracking_id)
    assert st2 == "ACCEPTED"
