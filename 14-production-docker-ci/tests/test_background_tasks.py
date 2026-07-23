"""BackgroundTasks ≈ fire-and-forget @Async: 202 now, work after the response.

TestClient waits for background tasks to finish before returning the
response (it runs the full request lifecycle), so by the time post() returns,
the "email" must be in the delivery log — that IS the assertion.
"""

from fastapi.testclient import TestClient
from prodapp.jobs import SENT_WELCOME_EMAILS


def test_welcome_email_is_accepted_then_delivered(client: TestClient) -> None:
    response = client.post(
        "/jobs/welcome-email", json={"email": "alice@example.com", "username": "alice"}
    )

    assert response.status_code == 202  # accepted ≠ done (≈ JMS ack)
    assert response.json() == {"status": "accepted"}
    # The background task ran after the response was produced:
    assert SENT_WELCOME_EMAILS == [{"email": "alice@example.com", "username": "alice"}]


def test_welcome_email_validates_payload(client: TestClient) -> None:
    response = client.post("/jobs/welcome-email", json={"email": "", "username": "alice"})
    assert response.status_code == 422
    assert SENT_WELCOME_EMAILS == []  # nothing queued on a bad request
