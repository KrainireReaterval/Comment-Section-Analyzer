from app import db
from datetime import datetime
import json

class Video(db.Model):
    __tablename__ = 'videos'
    
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    title = db.Column(db.String(500))
    description = db.Column(db.Text)
    duration = db.Column(db.String(50))
    published_at = db.Column(db.DateTime)
    comment_count = db.Column(db.Integer)
    view_count = db.Column(db.Integer)
    like_count = db.Column(db.Integer)
    
    # 分析结果
    main_vibe = db.Column(db.String(20))
    vibe_score = db.Column(db.Float)
    topics_json = db.Column(db.Text)
    analysis_complete = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    comments = db.relationship('Comment', backref='video', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'video_id': self.video_id,
            'title': self.title,
            'description': self.description,
            'duration': self.duration,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'comment_count': self.comment_count,
            'view_count': self.view_count,
            'like_count': self.like_count,
            'main_vibe': self.main_vibe,
            'vibe_score': self.vibe_score,
            'topics': (json.loads(self.topics_json) if self.topics_json else []),
            'analysis_complete': self.analysis_complete,
            'created_at': self.created_at.isoformat()
        }

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False, index=True)
    comment_id = db.Column(db.String(100), unique=True, index=True)
    parent_id = db.Column(db.String(100), index=True)
    
    author = db.Column(db.String(200))
    text = db.Column(db.Text)
    like_count = db.Column(db.Integer, default=0)
    reply_count = db.Column(db.Integer, default=0)
    published_at = db.Column(db.DateTime, index=True)
    
    # 分析结果
    sentiment = db.Column(db.String(20))
    sentiment_score = db.Column(db.Float)
    category = db.Column(db.String(50))
    labels_json = db.Column(db.Text)
    topics_json = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        # safely parse stored JSON fields
        labels = []
        topics = []
        try:
            if self.labels_json:
                labels = json.loads(self.labels_json)
        except Exception:
            labels = []

        try:
            if self.topics_json:
                topics = json.loads(self.topics_json)
        except Exception:
            topics = []

        return {
            'id': self.id,
            'comment_id': self.comment_id,
            'parent_id': self.parent_id,
            'author': self.author,
            'text': self.text,
            'like_count': self.like_count,
            'reply_count': self.reply_count,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'sentiment': self.sentiment,
            'sentiment_score': self.sentiment_score,
            'category': self.category,
            'labels': labels,
            'topics': topics,
            'created_at': self.created_at.isoformat()
        }

class Topic(db.Model):
    __tablename__ = 'topics'
    
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('videos.id'), nullable=False)
    name = db.Column(db.String(100))
    count = db.Column(db.Integer, default=0)
    percentage = db.Column(db.Float)
    
    positive_count = db.Column(db.Integer, default=0)
    negative_count = db.Column(db.Integer, default=0)
    neutral_count = db.Column(db.Integer, default=0)
    
    controversy_rate = db.Column(db.Float)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        total = self.positive_count + self.negative_count + self.neutral_count
        return {
            'name': self.name,
            'count': self.count,
            'percentage': round(self.percentage, 2),
            'positive_percentage': round(self.positive_count / total * 100, 2) if total > 0 else 0,
            'negative_percentage': round(self.negative_count / total * 100, 2) if total > 0 else 0,
            'neutral_percentage': round(self.neutral_count / total * 100, 2) if total > 0 else 0,
            'controversy_rate': round(self.controversy_rate, 2) if self.controversy_rate else 0
        }