from http.client import HTTPConnection, HTTPSConnection, HTTPException
import json

import pytest


@pytest.fixture
def get_response(beacon_config):
    origin = beacon_config.origin
    connection_type = HTTPSConnection if origin.scheme == "https" else HTTPConnection

    def get(path):
        client = connection_type(origin.hostname, origin.port, timeout=beacon_config.timeout)
        try:
            client.request("GET", path)
            with client.getresponse() as response:
                return response.status, response.headers.get_content_type(), response.read()
        except (OSError, HTTPException) as error:
            pytest.fail(f"GET {path} did not complete: {error}")
        finally:
            client.close()

    return get


@pytest.mark.parametrize(
    ("path", "status"),
    [("/", 200), ("/health.json", 200), ("/missing-page", 404)],
    ids=["home-200", "health-200", "missing-404"],
)
def test_route_status(get_response, path, status):
    actual, _, _ = get_response(path)
    assert actual == status, f"GET {path}: expected {status}, got {actual}"


def test_home_release(get_response, beacon_config):
    status, _, body = get_response("/")
    assert status == 200
    assert beacon_config.release in body.decode("utf-8")


def test_health_payload(get_response, beacon_config):
    status, content_type, body = get_response("/health.json")
    assert status == 200
    assert content_type == "application/json"
    payload = json.loads(body)
    assert isinstance(payload, dict)
    assert payload.get("status") == "operational"
    assert payload.get("release") == beacon_config.release
