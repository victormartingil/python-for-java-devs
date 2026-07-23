"""BackgroundTasks ≈ fire-and-forget @Async — and an honest look at its limits.

FastAPI's BackgroundTasks runs work AFTER the response is sent, in the SAME
process. Right tool for: welcome emails, audit records, cache warming,
webhook fan-out — short, best-effort side effects the client shouldn't wait
for (202 Accepted = "queued", not "done" ≈ a JMS ack).

Wrong tool when you need any of: retries with backoff, surviving a deploy or
crash, rate limiting, visibility into pending work, or workers on other
machines. That is a REAL queue — Dramatiq or Celery + Redis/RabbitMQ
(≈ JMS). The endpoint shape stays identical; only the "send" line changes
from background_tasks.add_task(fn, ...) to queue.send(...).
"""

import structlog
from fastapi import APIRouter, BackgroundTasks, status
from pydantic import BaseModel, Field

router = APIRouter(prefix="/jobs", tags=["jobs"])
log = structlog.get_logger("jobs")

# Demo "delivery log" so tests can observe the background task actually ran.
# In production this function would call SMTP/SendGrid — the SENT list is
# exactly the kind of seam module 12 would mock.
SENT_WELCOME_EMAILS: list[dict[str, str]] = []


def _send_welcome_email(email: str, username: str) -> None:
    SENT_WELCOME_EMAILS.append({"email": email, "username": username})
    log.info("welcome_email_sent", email=email, username=username)


class WelcomeEmailRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    username: str = Field(min_length=1, max_length=50)


@router.post("/welcome-email", status_code=status.HTTP_202_ACCEPTED)
def send_welcome_email(
    payload: WelcomeEmailRequest, background_tasks: BackgroundTasks
) -> dict[str, str]:
    # Registered, not executed: the function runs after the response is sent.
    background_tasks.add_task(_send_welcome_email, payload.email, payload.username)
    return {"status": "accepted"}
