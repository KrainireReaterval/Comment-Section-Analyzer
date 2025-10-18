from textblob import TextBlob

class SentimentAnalyzer:
    
    @staticmethod
    def analyze_sentiment(text):
        """分析情感 - 使用TextBlob"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            # 情感分类
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'sentiment': sentiment,
                'score': round(polarity, 3)
            }
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {
                'sentiment': 'neutral',
                'score': 0.0
            }