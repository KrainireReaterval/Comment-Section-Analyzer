from transformers import pipeline

# Load sentiment model
print("Loading model... (this takes ~30 seconds first time)")
sentiment_analyzer = pipeline("sentiment-analysis", 
                             model="cardiffnlp/twitter-roberta-base-sentiment-latest")

# Test with sample comments
test_comments = [
    "This video is absolutely amazing! Best content ever!",
    "Terrible quality, waste of my time.",
    "It's okay, nothing special."
]

print("\n--- Sentiment Analysis Results ---")
for comment in test_comments:
    result = sentiment_analyzer(comment)[0]
    print(f"\nComment: {comment}")
    print(f"Sentiment: {result['label']} (confidence: {result['score']:.2f})")