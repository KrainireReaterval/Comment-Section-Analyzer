from googleapiclient.discovery import build
from datetime import datetime
import isodate
from config import Config
from googleapiclient.discovery import build
from datetime import datetime
import isodate
from config import Config
import time
import logging

logger = logging.getLogger(__name__)


class YouTubeScraper:
    def __init__(self):
        self.youtube = build('youtube', 'v3', developerKey=Config.YOUTUBE_API_KEY)

    def get_video_info(self, video_id):
        """获取视频基本信息"""
        try:
            request = self.youtube.videos().list(
                part='snippet,contentDetails,statistics',
                id=video_id
            )
            response = request.execute()

            items = response.get('items', [])
            if not items:
                return None

            video = items[0]
            snippet = video.get('snippet', {})
            stats = video.get('statistics', {})
            content_details = video.get('contentDetails', {})
            duration = content_details.get('duration')

            # safe published_at
            published_at = None
            if 'publishedAt' in snippet and snippet['publishedAt']:
                try:
                    published_at = datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00'))
                except Exception:
                    logger.exception('Failed to parse publishedAt')

            def _int_safe(value):
                try:
                    return int(value)
                except Exception:
                    return 0

            duration_str = None
            if duration:
                try:
                    duration_str = str(isodate.parse_duration(duration))
                except Exception:
                    logger.exception('Failed to parse duration')

            return {
                'video_id': video_id,
                'title': snippet.get('title', ''),
                'description': snippet.get('description', ''),
                'duration': duration_str,
                'published_at': published_at,
                'comment_count': _int_safe(stats.get('commentCount', 0)),
                'view_count': _int_safe(stats.get('viewCount', 0)),
                'like_count': _int_safe(stats.get('likeCount', 0))
            }
        except Exception:
            logger.exception("Error fetching video info")
            return None

    def get_comments_batch(self, video_id, max_results=10000, include_replies=True):
        """
        批量获取评论 - 支持大规模爬取
        max_results: 最多获取多少条评论（支持10k+）
        include_replies: 是否包含回复
        """
        comments = []
        page_token = None

        try:
            while len(comments) < max_results:
                # 每次请求100条（YouTube API最大值）
                request = self.youtube.commentThreads().list(
                    part='snippet,replies',
                    videoId=video_id,
                    maxResults=min(100, max_results - len(comments)),
                    pageToken=page_token,
                    textFormat='plainText',
                    order='relevance'
                )

                response = request.execute()

                for item in response.get('items', []):
                    snippet = item.get('snippet', {})
                    top = snippet.get('topLevelComment', {})
                    top_comment = top.get('snippet', {})

                    # 主评论
                    try:
                        published_at = None
                        if top_comment.get('publishedAt'):
                            published_at = datetime.fromisoformat(top_comment['publishedAt'].replace('Z', '+00:00'))
                    except Exception:
                        published_at = None

                    comments.append({
                        'comment_id': item.get('id'),
                        'parent_id': None,
                        'author': top_comment.get('authorDisplayName'),
                        'text': top_comment.get('textDisplay', ''),
                        'like_count': int(top_comment.get('likeCount', 0)) if top_comment.get('likeCount') is not None else 0,
                        'reply_count': int(snippet.get('totalReplyCount', 0)),
                        'published_at': published_at
                    })

                    # 回复评论
                    if include_replies and 'replies' in item:
                        for reply in item.get('replies', {}).get('comments', []):
                            reply_snippet = reply.get('snippet', {})
                            try:
                                reply_published = None
                                if reply_snippet.get('publishedAt'):
                                    reply_published = datetime.fromisoformat(reply_snippet['publishedAt'].replace('Z', '+00:00'))
                            except Exception:
                                reply_published = None

                            comments.append({
                                'comment_id': reply.get('id'),
                                'parent_id': item.get('id'),
                                'author': reply_snippet.get('authorDisplayName'),
                                'text': reply_snippet.get('textDisplay', ''),
                                'like_count': int(reply_snippet.get('likeCount', 0)) if reply_snippet.get('likeCount') is not None else 0,
                                'reply_count': 0,
                                'published_at': reply_published
                            })

                # 检查是否还有下一页
                if 'nextPageToken' in response and len(comments) < max_results:
                    page_token = response['nextPageToken']
                    time.sleep(0.5)  # 避免API限流
                else:
                    break

            logger.info("Successfully fetched %d comments", len(comments))
            return comments

        except Exception:
            logger.exception("Error fetching comments")
            return comments  # 返回已获取的评论