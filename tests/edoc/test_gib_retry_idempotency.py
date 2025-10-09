from edoc.gib.client import GibClient


def test_send_is_idempotent(tmp_path):
    client = GibClient(state_dir=str(tmp_path))
    data = b"<xml/>"
    r1 = client.send_invoice(data, idempotency_key="K1")
    r2 = client.send_invoice(data, idempotency_key="K1")
    assert r1.tracking_id == r2.tracking_id
    assert r1.status == r2.status


def test_poll_transitions_to_accepted(tmp_path):
    client = GibClient(state_dir=str(tmp_path))
    res = client.send_invoice(b"<xml/>")
    status1 = client.poll(res.tracking_id)
    status2 = client.poll(res.tracking_id)
    assert status1 in {"PENDING", "ACCEPTED"}
    assert status2 == "ACCEPTED"
