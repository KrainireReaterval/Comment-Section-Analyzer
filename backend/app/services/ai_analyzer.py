import openai
from config import Config
import json

openai.api_key = Config.OPENAI_API_KEY

class AIAnalyzer:
    """使用AI进行深度话题和标签分析"""
    
    @staticmethod
    def extract_topics_and_labels(comments_batch):
        """
        批量提取话题和标签
        comments_batch: 评论文本列表（建议每批50-100条）
        """
        if not comments_batch:
            return {
                "general_labels": [],
                "specific_topics": [],
                "keywords": []
            }
        
        # 组合评论文本
        combined_text = "\n".join([f"- {c}" for c in comments_batch[:100]])
        
        prompt = f"""Analyze these YouTube comments and extract:
1. Main topics being discussed (e.g., "Donald Trump", "democrats", "China", "racism")
2. Labels for categorization (e.g., #politics, #food, #careers, #people)

Comments:
{combined_text}

Return a JSON object with:
{{
  "general_labels": ["#politics", "#food", ...],
  "specific_topics": ["Donald Trump", "China", ...],
  "keywords": ["president", "election", ...]
}}

Only return valid JSON, no additional text."""

        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a comment analysis expert. Extract topics and labels from YouTube comments."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"AI analysis error: {e}")
            return {
                "general_labels": [],
                "specific_topics": [],
                "keywords": []
            }
    
    @staticmethod
    def label_single_comment(comment_text, known_topics):
        """
        为单条评论打标签
        使用规则+AI混合方法
        """
        labels = []
        topics = []
        
        text_lower = comment_text.lower()
        
        # 检测已知话题
        for topic in known_topics:
            if topic.lower() in text_lower:
                topics.append(topic)
        
        # 通用标签规则
        if any(word in text_lower for word in ['politic', 'president', 'election', 'government']):
            labels.append('#politics')
        if any(word in text_lower for word in ['food', 'cook', 'recipe', 'eat']):
            labels.append('#food')
        if any(word in text_lower for word in ['career', 'job', 'work', 'salary']):
            labels.append('#careers')
        if any(word in text_lower for word in ['people', 'person', 'human']):
            labels.append('#people')
        
        return {
            'labels': list(set(labels)),
            'topics': list(set(topics))
        }