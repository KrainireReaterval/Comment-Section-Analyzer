import requests

BASE_URL = "http://localhost:5001"
TIMEOUT = 30

def test_get_api_health_check():
    url = f"{BASE_URL}/api/health"
    headers = {
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request to {url} failed: {e}"

    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

    try:
        data = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    # Assuming the health endpoint returns a JSON with a status or health key indicating service status
    # We'll check for either 'status' or 'health' keys with expected values like 'healthy' or 'ok'
    status = None
    for key in ('status', 'health', 'message'):
        if key in data:
            status = data[key]
            break

    assert status is not None, "Health check response JSON does not contain 'status', 'health', or 'message' key"

    assert isinstance(status, str), f"Status value should be string, got {type(status)}"
    assert status.lower() in ("healthy", "ok", "running", "up"), f"Unexpected health status: {status}"

test_get_api_health_check()