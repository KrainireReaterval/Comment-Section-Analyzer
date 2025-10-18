import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # YouTube API
    YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
    
    # OpenAI API (用于AI分析)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///youtube_comments.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis (用于任务队列)
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Analysis settings
    MIN_TOPIC_THRESHOLD = 0.35  # 话题出现35%以上才显示
    MAX_COMMENTS_PER_REQUEST = 10000
    CONTROVERSY_REPLY_THRESHOLD = 100  # 超过100回复算争议
    
    # CORS
    CORS_HEADERS = 'Content-Type'