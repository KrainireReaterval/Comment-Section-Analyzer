import logging
from textblob import TextBlob

logger = logging.getLogger(__name__)


class SentimentAnalyzer:

    @staticmethod
    def analyze_sentiment(text):
        """分析情感 - 使用TextBlob"""
        try:
            # guard against non-string inputs
            if text is None:
                return {'sentiment': 'neutral', 'score': 0.0}

            blob = TextBlob(str(text))
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
        except Exception:
            logger.exception("Error analyzing sentiment")
            return {
                'sentiment': 'neutral',
                'score': 0.0
            }