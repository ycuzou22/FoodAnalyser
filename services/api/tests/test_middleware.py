from httpx import AsyncClient
from structlog.testing import capture_logs


async def test_request_id_is_generated_when_absent(client: AsyncClient) -> None:
    response = await client.get("/health")

    request_id = response.headers["x-request-id"]
    assert len(request_id) == 32


async def test_safe_incoming_request_id_is_kept(client: AsyncClient) -> None:
    response = await client.get("/health", headers={"X-Request-ID": "mobile-7f3a9c21"})

    assert response.headers["x-request-id"] == "mobile-7f3a9c21"


async def test_unsafe_incoming_request_id_is_replaced(client: AsyncClient) -> None:
    injected = 'abc"}\n{"level":"error","event":"forged'

    response = await client.get("/health", headers={"X-Request-ID": injected.replace("\n", " ")})

    assert response.headers["x-request-id"] != injected
    assert len(response.headers["x-request-id"]) == 32


async def test_access_log_has_required_fields_and_no_query_string(client: AsyncClient) -> None:
    with capture_logs() as logs:
        await client.get("/health?q=yaourt+nature", headers={"X-Request-ID": "trace-log-123456"})

    access = [entry for entry in logs if entry["event"] == "request"]
    assert len(access) == 1
    entry = access[0]
    assert entry["method"] == "GET"
    assert entry["path"] == "/health"
    assert entry["status"] == 200
    assert isinstance(entry["duration_ms"], float)
    assert "yaourt" not in str(entry)
