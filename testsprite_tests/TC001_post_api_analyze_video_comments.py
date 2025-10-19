import requests

BASE_URL = "http://localhost:5001"
TIMEOUT = 30

def test_post_api_analyze_video_comments():
    url = f"{BASE_URL}/api/analyze"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "max_comments": 500
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        assert False, f"Request failed: {e}"

    # Validate response status code
    assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"

    # Validate response JSON structure and content
    try:
        data = response.json()
    except ValueError:
        assert False, "Response is not valid JSON"

    # Expected keys in a successful analysis response could include status, analysis_id, results, etc.
    # Since the PRD does not specify exact response schema, we validate common expected fields.
    assert isinstance(data, dict), "Response JSON is not an object"

    # Check for success indication
    # Typical response might have a 'status' field indicating success or a flag
    assert "status" in data, "Response JSON missing 'status' field"
    assert data["status"].lower() == "success", f"Analysis status is not success: {data.get('status')}"

    # Check for presence of results or analysis data
    assert "analysis_id" in data or "results" in data, "Response missing analysis results or analysis_id"

    # Optionally check that results contain expected elements if present
    if "results" in data:
        results = data["results"]
        assert isinstance(results, dict), "'results' should be a dictionary"
        # Check example fields likely present in analysis results
        for key in ["sentiment_summary", "topics", "comment_count"]:
            assert key in results, f"'results' missing expected key: {key}"

    # Check max_comments is respected or reported (if applicable)
    if "requested_max_comments" in data:
        assert data["requested_max_comments"] == payload["max_comments"], "Max comments value mismatch in response"

test_post_api_analyze_video_comments()