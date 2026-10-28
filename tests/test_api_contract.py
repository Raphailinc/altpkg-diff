import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from unittest.mock import Mock

import pytest
import requests
import responses

import package_comparison_tool.api as api
from package_comparison_tool.exceptions import AltApiError


def test_total_http_attempts_are_bounded(monkeypatch):
    calls = []

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            calls.append(self.path)
            self.send_response(503)
            self.end_headers()
            self.wfile.write(b"temporarily unavailable")

        def log_message(self, *_args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    monkeypatch.setattr(api, "ALT_RDB_API_BASE", f"http://127.0.0.1:{server.server_port}")
    monkeypatch.setattr(api.time, "sleep", lambda _delay: None)
    try:
        with pytest.raises(AltApiError):
            api.fetch_branch_binary_packages("p10", retries=3, retry_backoff=0)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
    assert len(calls) == 3


@pytest.mark.parametrize("payload", [[], None, {}, {"error": "upstream failed"}, {"packages": {}}])
@responses.activate
def test_unexpected_payload_cannot_become_empty_success(payload):
    url = f"{api.ALT_RDB_API_BASE}/branch_binary_packages/p10"
    responses.add(responses.GET, url, body=json.dumps(payload), status=200)
    with pytest.raises(AltApiError):
        api.fetch_branch_binary_packages("p10", retries=1)


@pytest.mark.parametrize("status, payload", [(200, {"packages": []}), (404, {}), (503, {})])
def test_response_is_closed_for_success_and_failure(status, payload):
    response = Mock(spec=requests.Response)
    response.status_code = status
    response.ok = status < 400
    response.text = "error"
    response.json.return_value = payload
    session = Mock(spec=requests.Session)
    session.headers = {}
    session.get.return_value = response
    if status == 200:
        assert api.fetch_branch_binary_packages("p10", session=session, retries=1) == []
    else:
        with pytest.raises(AltApiError):
            api.fetch_branch_binary_packages("p10", session=session, retries=1)
    response.close.assert_called_once()
    session.close.assert_not_called()


@responses.activate
def test_caller_session_user_agent_is_preserved():
    url = f"{api.ALT_RDB_API_BASE}/branch_binary_packages/p10"
    responses.add(responses.GET, url, json={"packages": []}, status=200)
    with requests.Session() as session:
        session.headers["User-Agent"] = "caller-agent"
        api.fetch_branch_binary_packages("p10", session=session)
    assert responses.calls[0].request.headers["User-Agent"] == "caller-agent"
