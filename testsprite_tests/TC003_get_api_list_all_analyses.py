import requests

BASE_URL = "http://localhost:5001"
TIMEOUT = 30
HEADERS = {
    "Accept": "application/json"
}

def test_get_api_list_all_analyses():
    url = f"{BASE_URL}/api/analyses"
    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request to {url} failed: {e}"
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    try:
        data = response.json()
    except ValueError:
        assert False, "Response is not valid JSON."

    # The response should be a list (or an object containing a list) of analyses
    assert isinstance(data, (list, dict)), "Response JSON should be a list or dict."
    # If dict, try to locate analyses list inside, else check the list directly
    analyses = data.get("analyses") if isinstance(data, dict) else data

    assert isinstance(analyses, list), "Analyses should be a list."

    # For each analysis, check relevant metadata presence
    for analysis in analyses:
        assert isinstance(analysis, dict), "Each analysis entry should be a dict."
        # Check for keys typical of metadata, e.g. id, video_id, created_at (based on common patterns)
        assert "id" in analysis, "Analysis item missing 'id'."
        assert "video_id" in analysis or "videoUrl" in analysis or "video_id" in analysis, "Analysis item missing video id."
        assert "created_at" in analysis or "timestamp" in analysis or "date" in analysis, "Analysis item missing creation date."

test_get_api_list_all_analyses()