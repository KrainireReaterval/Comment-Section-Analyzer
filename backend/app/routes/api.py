from flask import Blueprint, request, jsonify
from app import db
from app.models import Video, Comment, Topic
from app.services import YouTubeScraper, SentimentAnalyzer, AIAnalyzer, TrendAnalyzer
from app.utils.helpers import extract_video_id
import json
from collections import Counter
from config import Config

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'message': 'YouTube Comment Analyzer API is running'
    })

@bp.route('/analyze', methods=['POST'])
def analyze_video():
    """
    完整分析流程：
    1. 爬取视频信息和评论
    2. 情感分析
    3. AI话题提取
    4. 标签分类
    5. 时间趋势
    6. 争议度计算
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    video_url = data.get('video_url')
    max_comments = min(data.get('max_comments', 1000), Config.MAX_COMMENTS_PER_REQUEST)
    
    if not video_url:
        return jsonify({'error': 'video_url is required'}), 400
    
    video_id = extract_video_id(video_url)
    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL'}), 400
    
    try:
        scraper = YouTubeScraper()
        sentiment_analyzer = SentimentAnalyzer()
        ai_analyzer = AIAnalyzer()
        
        # 1. 获取视频信息
        video_info = scraper.get_video_info(video_id)
        if not video_info:
            return jsonify({'error': 'Video not found'}), 404
        
        # 2. 保存/更新视频
        video = Video.query.filter_by(video_id=video_id).first()
        if not video:
            video = Video(**video_info)
            db.session.add(video)
        else:
            for key, value in video_info.items():
                setattr(video, key, value)
        db.session.commit()
        
        # 3. 爬取评论（大规模）
        comments_data = scraper.get_comments_batch(video_id, max_comments, include_replies=True)
        
        if not comments_data:
            return jsonify({
                'status': 'success',
                'message': 'No comments found',
                'video_id': video_id
            })
        
        # 4. AI提取话题（使用前100条评论样本）
        sample_texts = [c['text'] for c in comments_data[:100]]
        ai_result = ai_analyzer.extract_topics_and_labels(sample_texts)
        known_topics = ai_result.get('specific_topics', [])
        
        # 5. 分析并保存每条评论
        new_comments = 0
        for comment_data in comments_data:
            existing = Comment.query.filter_by(comment_id=comment_data['comment_id']).first()
            if existing:
                continue
            
            # 情感分析
            sentiment_result = sentiment_analyzer.analyze_sentiment(comment_data['text'])
            
            # 标签和话题
            label_result = ai_analyzer.label_single_comment(comment_data['text'], known_topics)
            
            # 保存评论
            comment = Comment(
                video_id=video.id,
                comment_id=comment_data['comment_id'],
                parent_id=comment_data.get('parent_id'),
                author=comment_data['author'],
                text=comment_data['text'],
                like_count=comment_data['like_count'],
                reply_count=comment_data.get('reply_count', 0),
                published_at=comment_data['published_at'],
                sentiment=sentiment_result['sentiment'],
                sentiment_score=sentiment_result['score'],
                labels_json=json.dumps(label_result['labels']),
                topics_json=json.dumps(label_result['topics'])
            )
            db.session.add(comment)
            new_comments += 1
        
        db.session.commit()
        
        # 6. 统计话题和生成Topic记录
        all_comments = Comment.query.filter_by(video_id=video.id).all()
        _generate_topic_statistics(video, all_comments)
        
        # 7. 计算整体氛围
        _calculate_main_vibe(video, all_comments)
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Analyzed {new_comments} new comments',
            'video_id': video_id,
            'total_comments': len(all_comments)
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/video/<video_id>/report', methods=['GET'])
def get_video_report(video_id):
    """
    获取完整分析报告
    包含：基本信息、整体氛围、话题分析、时间趋势、可视化数据
    """
    video = Video.query.filter_by(video_id=video_id).first()
    if not video:
        return jsonify({'error': 'Video not found'}), 404
    
    comments = Comment.query.filter_by(video_id=video.id).all()
    topics = Topic.query.filter_by(video_id=video.id).all()
    
    # 时间趋势
    trend_analyzer = TrendAnalyzer()
    trends = trend_analyzer.analyze_time_trends(comments)
    
    # 情感分布
    sentiment_dist = _calculate_sentiment_distribution(comments)
    
    # 标签分布（通用分类）
    label_dist = _calculate_label_distribution(comments)
    
    return jsonify({
        'video': {
            'video_id': video.video_id,
            'title': video.title,
            'duration': video.duration,
            'published_at': video.published_at.isoformat() if video.published_at else None,
            'view_count': video.view_count,
            'like_count': video.like_count,
            'comment_count': video.comment_count,
            'main_vibe': video.main_vibe,
            'vibe_score': video.vibe_score
        },
        'summary': {
            'total_comments_analyzed': len(comments),
            'main_vibe': video.main_vibe,
            'sentiment_distribution': sentiment_dist,
            'label_distribution': label_dist
        },
        'topics': [t.to_dict() for t in topics],
        'time_trends': trends,
        'comments_sample': [c.to_dict() for c in comments[:50]]
    })

@bp.route('/videos', methods=['GET'])
def get_all_videos():
    """获取所有已分析视频"""
    videos = Video.query.order_by(Video.created_at.desc()).all()
    return jsonify({
        'total': len(videos),
        'videos': [v.to_dict() for v in videos]
    })

@bp.route('/video/<video_id>/controversy', methods=['GET'])
def get_controversy_stats(video_id):
    """
    新增：获取争议度统计
    返回超过100回复的评论信息
    """
    video = Video.query.filter_by(video_id=video_id).first()
    if not video:
        return jsonify({'error': 'Video not found'}), 404
    
    comments = Comment.query.filter_by(video_id=video.id).all()
    
    # 找出高回复评论（超过100回复）
    high_reply_comments = [
        c for c in comments 
        if c.reply_count >= Config.CONTROVERSY_REPLY_THRESHOLD
    ]
    
    total_comments = len(comments)
    controversy_rate = (len(high_reply_comments) / total_comments * 100) if total_comments > 0 else 0
    
    return jsonify({
        'video_id': video_id,
        'total_comments': total_comments,
        'high_reply_comments_count': len(high_reply_comments),
        'controversy_rate': round(controversy_rate, 2),
        'threshold': Config.CONTROVERSY_REPLY_THRESHOLD,
        'high_reply_comments': [
            {
                'text': c.text[:200],
                'author': c.author,
                'reply_count': c.reply_count,
                'like_count': c.like_count,
                'sentiment': c.sentiment
            }
            for c in sorted(high_reply_comments, key=lambda x: x.reply_count, reverse=True)[:20]
        ]
    })

# ========== 辅助函数 ==========

def _generate_topic_statistics(video, comments):
    """生成话题统计"""
    # 删除旧的topic记录
    Topic.query.filter_by(video_id=video.id).delete()
    
    # 统计所有话题
    topic_counter = Counter()
    topic_sentiments = {}
    
    for comment in comments:
        if comment.topics_json:
            try:
                topics = json.loads(comment.topics_json)
            except Exception:
                topics = []

            for topic in topics:
                topic_counter[topic] += 1
                
                if topic not in topic_sentiments:
                    topic_sentiments[topic] = {'positive': 0, 'negative': 0, 'neutral': 0}
                
                topic_sentiments[topic][comment.sentiment] += 1
    
    total_comments = len(comments)
    min_threshold = Config.MIN_TOPIC_THRESHOLD
    
    # 保存符合阈值的话题（35%以上）
    for topic_name, count in topic_counter.items():
        percentage = count / total_comments * 100
        
        if percentage >= min_threshold * 100:  # 超过35%
            sentiments = topic_sentiments[topic_name]
            
            # 修正：计算争议度（传入所有评论）
            trend_analyzer = TrendAnalyzer()
            controversy = trend_analyzer.calculate_controversy_rate(
                all_comments=comments,
                controversy_threshold=Config.CONTROVERSY_REPLY_THRESHOLD
            )
            
            topic = Topic(
                video_id=video.id,
                name=topic_name,
                count=count,
                percentage=percentage,
                positive_count=sentiments['positive'],
                negative_count=sentiments['negative'],
                neutral_count=sentiments['neutral'],
                controversy_rate=controversy
            )
            db.session.add(topic)

def _calculate_main_vibe(video, comments):
    """计算整体氛围"""
    if not comments:
        return
    
    sentiment_counts = Counter(c.sentiment for c in comments)
    total = len(comments)
    
    positive_ratio = sentiment_counts.get('positive', 0) / total
    negative_ratio = sentiment_counts.get('negative', 0) / total
    
    if positive_ratio > 0.5:
        video.main_vibe = 'positive'
    elif negative_ratio > 0.5:
        video.main_vibe = 'negative'
    else:
        video.main_vibe = 'neutral'
    
    # 计算氛围分数
    avg_score = sum(c.sentiment_score for c in comments) / total
    video.vibe_score = round(avg_score, 3)
    video.analysis_complete = True

def _calculate_sentiment_distribution(comments):
    """计算情感分布"""
    if not comments:
        return {'positive': 0, 'negative': 0, 'neutral': 0}
    
    total = len(comments)
    sentiment_counts = Counter(c.sentiment for c in comments)
    
    return {
        'positive': round(sentiment_counts.get('positive', 0) / total * 100, 2),
        'negative': round(sentiment_counts.get('negative', 0) / total * 100, 2),
        'neutral': round(sentiment_counts.get('neutral', 0) / total * 100, 2)
    }

def _calculate_label_distribution(comments):
    """计算标签分布（通用分类）"""
    label_counter = Counter()
    
    for comment in comments:
        if comment.labels_json:
            try:
                labels = json.loads(comment.labels_json)
            except Exception:
                labels = []

            for label in labels:
                label_counter[label] += 1
    
    total_labels = sum(label_counter.values())
    
    return {
        label: {
            'count': count,
            'percentage': round(count / total_labels * 100, 2) if total_labels > 0 else 0
        }
        for label, count in label_counter.most_common()
    }