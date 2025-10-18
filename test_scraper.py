from youtube_comment_downloader import *

# Test with a popular video
url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Replace with any YouTube URL

downloader = YoutubeCommentDownloader()
comments = downloader.get_comments_from_url(url, sort_by=SORT_BY_POPULAR)

# Print first 5 comments to verify it works
count = 0
for comment in comments:
    print(f"\n--- Comment {count + 1} ---")
    print(f"Text: {comment['text']}")
    print(f"Author: {comment['author']}")
    print(f"Likes: {comment['votes']}")
    
    count += 1
    if count >= 5:
        break

print(f"\nSuccess! Scraped {count} comments")