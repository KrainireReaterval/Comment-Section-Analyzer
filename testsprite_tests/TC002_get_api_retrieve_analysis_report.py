import requests
import re

BASE_URL = "http://localhost:5001"
TIMEOUT = 30

def test_get_api_retrieve_analysis_report():
    # Helper function to extract video ID from a YouTube URL
    def extract_video_id(youtube_url):
        # Supports formats:
        # https://www.youtube.com/watch?v=VIDEO_ID
        # https://youtu.be/VIDEO_ID
        patterns = [
            r"youtube\.com/watch\?v=([^&]+)",
            r"youtu\.be/([^?&]+)"
        ]
        for pattern in patterns:
            match = re.search(pattern, youtube_url)
            if match:
                return match.group(1)
        return None

    # Step 1: Create a new analysis by POST /api/videos/analyze to get a valid video ID and ensure a report exists
    analyze_url = f"{BASE_URL}/api/videos/analyze"
    youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Example video
    max_comments = 500

    analyze_payload = {
        "video_url": youtube_url,
        "max_comments": max_comments
    }
    headers = {"Content-Type": "application/json"}

    created_analysis_id = None
    try:
        analyze_response = requests.post(analyze_url, json=analyze_payload, headers=headers, timeout=TIMEOUT)
        assert analyze_response.status_code == 200, f"Expected status 200 from /api/videos/analyze, got {analyze_response.status_code}"
        analyze_data = analyze_response.json()
        # Video ID might be returned in response or we extract from URL
        if "video_id" in analyze_data:
            video_id = analyze_data["video_id"]
        else:
            video_id = extract_video_id(youtube_url)
        assert video_id, "Failed to get video ID from analyze response or URL"

        created_analysis_id = video_id

        # Step 2: GET /api/videos/report?video_id=VIDEO_ID
        report_url = f"{BASE_URL}/api/videos/report"
        params = {"video_id": video_id}

        report_response = requests.get(report_url, params=params, timeout=TIMEOUT)
        assert report_response.status_code == 200, f"Expected status 200 from /api/videos/report, got {report_response.status_code}"
        report_data = report_response.json()

        # Validate report content keys
        # Expected keys: video info, sentiment overview, topics, sample comments
        # We assume keys: 'video_info', 'sentiment_overview', 'topics', 'sample_comments'
        expected_keys = ["video_info", "sentiment_overview", "topics", "sample_comments"]
        for key in expected_keys:
            assert key in report_data, f"Missing '{key}' in report response"

        # Validate video_info has essential fields
        video_info = report_data["video_info"]
        for field in ["title", "channel_title", "published_at", "video_url"]:
            assert field in video_info, f"Missing '{field}' in video_info"

        # Validate sentiment_overview contains sentiment distribution counts or percentages with expected sentiments
        sentiment_overview = report_data["sentiment_overview"]
        for sentiment in ["positive", "negative", "neutral"]:
            assert sentiment in sentiment_overview, f"Missing sentiment '{sentiment}' in sentiment_overview"

        # Validate topics is a non-empty list or dict
        topics = report_data["topics"]
        assert topics is not None, "Topics section is None"
        assert (isinstance(topics, list) or isinstance(topics, dict)), "Topics should be a list or dict"
        assert len(topics) > 0, "Topics is empty"

        # Validate sample_comments is a list of dicts with comment data
        sample_comments = report_data["sample_comments"]
        assert isinstance(sample_comments, list), "sample_comments should be a list"
        assert len(sample_comments) > 0, "sample_comments is empty"
        # Each comment should have text and sentiment at least
        for comment in sample_comments:
            assert isinstance(comment, dict), "Each comment should be a dict"
            assert "text" in comment and isinstance(comment["text"], str), "Comment missing 'text' or not string"
            assert "sentiment" in comment, "Comment missing 'sentiment'"

    finally:
        # Cleanup: If there is an API to delete the analysis, call it here.
        # No delete API documented in PRD, so skipping cleanup.
        pass

test_get_api_retrieve_analysis_report()
