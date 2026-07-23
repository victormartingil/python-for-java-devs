"""A tiny "external service client" — the thing you MOCK in tests (≈ a RestTemplate bean).

In a real service this would call Slack/SendGrid/an internal API. Tests must
never hit the network, so the HTTP layer is isolated in ONE function
(`post_webhook`) that tests patch — the seam, in Mockito terms the class
you'd @Mock and inject.

Run:  uv run pytest 12-advanced-testing/tests -v
"""

import httpx2


class NotificationError(Exception):
    """The remote service rejected or could not receive the notification."""


def post_webhook(url: str, text: str, timeout: float = 5.0) -> int:
    """POST a message to a webhook; return the remote status code.

    This is the ONLY network call in the module — patch this in tests:
        mocker-style:  monkeypatch.setattr("notify.post_webhook", fake)
        unittest.mock: patch("notify.post_webhook", return_value=200)
    """
    response = httpx2.post(url, json={"text": text}, timeout=timeout)
    return response.status_code


def send_completion_notice(webhook_url: str, task_title: str) -> str:
    """Business logic around the external call — THIS is what you unit-test.

    Raises NotificationError on non-2xx so callers can decide what to do
    (≈ your service wrapping RestClientException in a domain exception).
    """
    status = post_webhook(webhook_url, f"Task completed: {task_title}")
    if status >= 400:
        raise NotificationError(f"webhook returned {status}")
    return "sent"
