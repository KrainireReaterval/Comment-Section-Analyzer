from collections import defaultdict
from datetime import datetime
import pandas as pd

class TrendAnalyzer:
    """分析评论时间趋势"""
    
    @staticmethod
    def analyze_time_trends(comments):
        """
        分析评论时间趋势
        返回：年度统计和累计统计
        """
        if not comments:
            return {
                'yearly_counts': [],
                'cumulative_counts': []
            }
        
        # 按年份分组
        yearly_data = defaultdict(int)
        
        for comment in comments:
            if comment.published_at:
                year = comment.published_at.year
                yearly_data[year] += 1
        
        # 排序
        sorted_years = sorted(yearly_data.keys())
        
        # 年度统计（折线图数据）
        yearly_counts = [
            {'year': year, 'count': yearly_data[year]}
            for year in sorted_years
        ]
        
        # 累计统计（柱状图数据）
        cumulative = 0
        cumulative_counts = []
        for year in sorted_years:
            cumulative += yearly_data[year]
            cumulative_counts.append({
                'year': year,
                'cumulative': cumulative,
                'new': yearly_data[year]
            })
        
        return {
            'yearly_counts': yearly_counts,
            'cumulative_counts': cumulative_counts
        }
    
    @staticmethod
    def calculate_controversy_rate(all_comments, controversy_threshold=100):
        """
        修正：计算争议度
        按照README定义：
        controversy_rate = (num_reply_in_stack / num_all_comments) * 100%
        num_reply_in_stack = 超过100个回复的评论数量
        """
        if not all_comments:
            return 0.0
        
        total_comments = len(all_comments)

        # 统计回复数超过阈值的评论，使用 getattr 保证健壮性
        high_reply_comments = sum(
            1 for c in all_comments
            if getattr(c, 'reply_count', 0) >= controversy_threshold
        )

        controversy = (high_reply_comments / total_comments * 100) if total_comments > 0 else 0.0

        return controversy