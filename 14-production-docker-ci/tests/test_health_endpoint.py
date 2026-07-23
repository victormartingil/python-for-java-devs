"""/health ≈ Actuator's liveness endpoint — plus proof the logs are structured.

The health endpoint itself comes from module 11's app (unmodified); what
this module adds AROUND it is structlog — so we also assert that hitting any
endpoint emits one parseable JSON log line with fields, not a string.
"""

import io
import json
import logging

import pytest
from fastapi.testclient import TestClient
from prodapp.logging_config import make_json_handler


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.fixture
def json_log_stream() -> io.StringIO:
    """Route the app's real JSON handler into a StringIO for one test.

    (Capturing stdout doesn't work here: the handler bound sys.stdout at import
    time, before pytest's capture existed — so we swap the handler, like a test
    appender on Logback's root logger.)
    """
    stream = io.StringIO()
    root = logging.getLogger()
    original_handlers = root.handlers
    root.handlers = [make_json_handler(stream)]
    yield stream
    root.handlers = original_handlers


def test_requests_emit_json_logs(client: TestClient, json_log_stream: io.StringIO) -> None:
    client.get("/health")
    lines = json_log_stream.getvalue().strip().splitlines()

    json_lines = [line for line in lines if line.startswith("{")]
    assert json_lines, f"expected JSON log lines, got: {lines}"

    http_events = [
        parsed for line in json_lines if (parsed := json.loads(line)).get("event") == "http_request"
    ]
    assert http_events, "no http_request event found in the JSON logs"
    entry = http_events[-1]
    assert entry["path"] == "/health"
    assert entry["status_code"] == 200
    assert entry["method"] == "GET"
    assert entry["level"] == "info"  # fields, not a string to regex
