from googleapiclient.discovery import build
from datetime import datetime
import isodate
from config import Config
import time

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
            
            if not response['items']:
                return None
            
            video = response['items'][0]
            snippet = video['snippet']
            stats = video['statistics']
            duration = video['contentDetails']['duration']
            
            return {
                'video_id': video_id,
                'title': snippet['title'],
                'description': snippet.get('description', ''),
                'duration': str(isodate.parse_duration(duration)),
                'published_at': datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00')),
                'comment_count': int(stats.get('commentCount', 0)),
                'view_count': int(stats.get('viewCount', 0)),
                'like_count': int(stats.get('likeCount', 0))
            }
        except Exception as e:
            print(f"Error fetching video info: {e}")
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
                
                for item in response['items']:
                    top_comment = item['snippet']['topLevelComment']['snippet']
                    
                    # 主评论
                    comments.append({
                        'comment_id': item['id'],
                        'parent_id': None,
                        'author': top_comment['authorDisplayName'],
                        'text': top_comment['textDisplay'],
                        'like_count': top_comment['likeCount'],
                        'reply_count': item['snippet']['totalReplyCount'],
                        'published_at': datetime.fromisoformat(top_comment['publishedAt'].replace('Z', '+00:00'))
                    })
                    
                    # 回复评论
                    if include_replies and 'replies' in item:
                        for reply in item['replies']['comments']:
                            reply_snippet = reply['snippet']
                            comments.append({
                                'comment_id': reply['id'],
                                'parent_id': item['id'],
                                'author': reply_snippet['authorDisplayName'],
                                'text': reply_snippet['textDisplay'],
                                'like_count': reply_snippet['likeCount'],
                                'reply_count': 0,
                                'published_at': datetime.fromisoformat(reply_snippet['publishedAt'].replace('Z', '+00:00'))
                            })
                
                # 检查是否还有下一页
                if 'nextPageToken' in response and len(comments) < max_results:
                    page_token = response['nextPageToken']
                    time.sleep(0.5)  # 避免API限流
                else:
                    break
            
            print(f"Successfully fetched {len(comments)} comments")
            return comments
            
        except Exception as e:
            print(f"Error fetching comments: {e}")
            return comments  # 返回已获取的评论