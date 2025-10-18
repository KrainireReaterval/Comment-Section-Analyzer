"""
Sentiment Analysis Tool using VADER
Analyzes text sentiment with visualization capabilities
"""

import sys
import os
from typing import List, Dict, Union
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

try:
    import nltk
    from nltk.sentiment.vader import SentimentIntensityAnalyzer
except ImportError:
    print("NLTK not installed. Installing now...")
    os.system(f"{sys.executable} -m pip install nltk")
    import nltk
    from nltk.sentiment.vader import SentimentIntensityAnalyzer

# Download required NLTK data
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    print("Downloading VADER lexicon...")
    nltk.download('vader_lexicon', quiet=True)


class SentimentAnalyzer:
    """
    A class for performing sentiment analysis using VADER
    """
    
    def __init__(self):
        """Initialize the sentiment analyzer"""
        self.analyzer = SentimentIntensityAnalyzer()
        
    def analyze_text(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of a single text
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with sentiment scores (neg, neu, pos, compound)
        """
        if not text or not isinstance(text, str):
            return {'neg': 0.0, 'neu': 1.0, 'pos': 0.0, 'compound': 0.0}
        
        scores = self.analyzer.polarity_scores(text)
        return scores
    
    def classify_sentiment(self, compound_score: float) -> str:
        """
        Classify sentiment based on compound score
        
        Args:
            compound_score: Compound sentiment score (-1 to 1)
            
        Returns:
            Sentiment label: 'Positive', 'Negative', or 'Neutral'
        """
        if compound_score >= 0.05:
            return 'Positive'
        elif compound_score <= -0.05:
            return 'Negative'
        else:
            return 'Neutral'
    
    def analyze_batch(self, texts: List[str]) -> pd.DataFrame:
        """
        Analyze sentiment for multiple texts
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            DataFrame with texts and their sentiment scores
        """
        results = []
        
        for text in texts:
            scores = self.analyze_text(text)
            sentiment = self.classify_sentiment(scores['compound'])
            
            results.append({
                'text': text,
                'negative': scores['neg'],
                'neutral': scores['neu'],
                'positive': scores['pos'],
                'compound': scores['compound'],
                'sentiment': sentiment
            })
        
        return pd.DataFrame(results)
    
    def analyze_from_csv(self, csv_path: str, text_column: str) -> pd.DataFrame:
        """
        Analyze sentiment from a CSV file
        
        Args:
            csv_path: Path to CSV file
            text_column: Name of column containing text to analyze
            
        Returns:
            DataFrame with sentiment analysis results
        """
        try:
            df = pd.read_csv(csv_path)
            
            if text_column not in df.columns:
                raise ValueError(f"Column '{text_column}' not found in CSV")
            
            texts = df[text_column].astype(str).tolist()
            results = self.analyze_batch(texts)
            
            # Merge with original dataframe
            final_df = pd.concat([df, results.drop('text', axis=1)], axis=1)
            return final_df
            
        except Exception as e:
            print(f"Error reading CSV: {e}")
            raise
    
    def visualize_results(self, df: pd.DataFrame, save_path: str = None):
        """
        Create visualizations of sentiment analysis results
        
        Args:
            df: DataFrame with sentiment results
            save_path: Optional path to save the figure
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Sentiment Analysis Results', fontsize=16, fontweight='bold')
        
        # 1. Sentiment Distribution (Pie Chart)
        sentiment_counts = df['sentiment'].value_counts()
        colors = {'Positive': '#2ecc71', 'Negative': '#e74c3c', 'Neutral': '#95a5a6'}
        pie_colors = [colors.get(sent, '#3498db') for sent in sentiment_counts.index]
        
        axes[0, 0].pie(sentiment_counts.values, labels=sentiment_counts.index, 
                       autopct='%1.1f%%', startangle=90, colors=pie_colors)
        axes[0, 0].set_title('Sentiment Distribution')
        
        # 2. Compound Score Distribution (Histogram)
        axes[0, 1].hist(df['compound'], bins=30, color='skyblue', edgecolor='black')
        axes[0, 1].axvline(x=0.05, color='green', linestyle='--', label='Positive threshold')
        axes[0, 1].axvline(x=-0.05, color='red', linestyle='--', label='Negative threshold')
        axes[0, 1].set_xlabel('Compound Score')
        axes[0, 1].set_ylabel('Frequency')
        axes[0, 1].set_title('Compound Score Distribution')
        axes[0, 1].legend()
        
        # 3. Sentiment Scores Box Plot
        score_data = df[['negative', 'neutral', 'positive']].melt(
            var_name='Score Type', value_name='Score'
        )
        sns.boxplot(data=score_data, x='Score Type', y='Score', ax=axes[1, 0])
        axes[1, 0].set_title('Sentiment Score Distribution')
        axes[1, 0].set_ylabel('Score')
        
        # 4. Average Scores by Sentiment
        avg_scores = df.groupby('sentiment')[['negative', 'neutral', 'positive']].mean()
        avg_scores.plot(kind='bar', ax=axes[1, 1], color=['#e74c3c', '#95a5a6', '#2ecc71'])
        axes[1, 1].set_title('Average Scores by Sentiment Category')
        axes[1, 1].set_ylabel('Average Score')
        axes[1, 1].set_xlabel('Sentiment')
        axes[1, 1].legend(title='Score Type')
        axes[1, 1].tick_params(axis='x', rotation=0)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Visualization saved to {save_path}")
        
        plt.show()
    
    def generate_report(self, df: pd.DataFrame) -> str:
        """
        Generate a text report of sentiment analysis
        
        Args:
            df: DataFrame with sentiment results
            
        Returns:
            Formatted report string
        """
        total = len(df)
        sentiment_counts = df['sentiment'].value_counts()
        
        report = "=" * 60 + "\n"
        report += "SENTIMENT ANALYSIS REPORT\n"
        report += "=" * 60 + "\n\n"
        
        report += f"Total texts analyzed: {total}\n\n"
        
        report += "Sentiment Distribution:\n"
        report += "-" * 40 + "\n"
        for sentiment, count in sentiment_counts.items():
            percentage = (count / total) * 100
            report += f"  {sentiment:10s}: {count:4d} ({percentage:5.1f}%)\n"
        
        report += "\n" + "Average Scores:\n"
        report += "-" * 40 + "\n"
        report += f"  Negative  : {df['negative'].mean():.4f}\n"
        report += f"  Neutral   : {df['neutral'].mean():.4f}\n"
        report += f"  Positive  : {df['positive'].mean():.4f}\n"
        report += f"  Compound  : {df['compound'].mean():.4f}\n"
        
        report += "\n" + "Most Positive Texts:\n"
        report += "-" * 40 + "\n"
        top_positive = df.nlargest(3, 'compound')
        for idx, row in top_positive.iterrows():
            report += f"  Score: {row['compound']:.4f}\n"
            report += f"  Text: {row['text'][:80]}...\n\n"
        
        report += "Most Negative Texts:\n"
        report += "-" * 40 + "\n"
        top_negative = df.nsmallest(3, 'compound')
        for idx, row in top_negative.iterrows():
            report += f"  Score: {row['compound']:.4f}\n"
            report += f"  Text: {row['text'][:80]}...\n\n"
        
        report += "=" * 60 + "\n"
        
        return report


def main():
    """Main function to demonstrate sentiment analysis"""
    
    # Initialize analyzer
    analyzer = SentimentAnalyzer()
    
    # Example texts to analyze
    example_texts = [
        "I absolutely love this product! It's amazing and works perfectly.",
        "This is the worst experience I've ever had. Completely disappointed.",
        "The product is okay. Nothing special but it gets the job done.",
        "Fantastic service! Highly recommend to everyone!",
        "Terrible quality. Would not buy again.",
        "It's fine, I guess. Neither good nor bad.",
        "Best purchase ever! So happy with this decision!",
        "Waste of money. Don't bother buying this.",
        "Pretty average product. Does what it says.",
        "I'm extremely satisfied with my purchase!"
    ]
    
    print("Analyzing example texts...\n")
    
    # Analyze single text
    print("Single Text Analysis:")
    print("-" * 60)
    sample_text = example_texts[0]
    scores = analyzer.analyze_text(sample_text)
    sentiment = analyzer.classify_sentiment(scores['compound'])
    
    print(f"Text: {sample_text}")
    print(f"Scores: {scores}")
    print(f"Sentiment: {sentiment}\n")
    
    # Analyze batch
    print("Batch Analysis:")
    print("-" * 60)
    results_df = analyzer.analyze_batch(example_texts)
    print(results_df.to_string(index=False))
    print()
    
    # Generate report
    print(analyzer.generate_report(results_df))
    
    # Save results to CSV
    output_file = 'sentiment_analysis_results.csv'
    results_df.to_csv(output_file, index=False)
    print(f"\nResults saved to: {output_file}")
    
    # Create visualizations
    try:
        print("\nGenerating visualizations...")
        analyzer.visualize_results(results_df, save_path='sentiment_analysis_plot.png')
    except Exception as e:
        print(f"Visualization error: {e}")
        print("Install matplotlib and seaborn: pip install matplotlib seaborn")


if __name__ == "__main__":
    main()