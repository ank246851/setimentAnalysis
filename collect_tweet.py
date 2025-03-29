import tweepy
from textblob import TextBlob
import json
import pandas as pd

# Step 1: Authenticate with the X API
def authenticate():
    # Replace these with your actual credentials
    BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAM7u0AEAAAAApssn%2Bv18MubQgW%2B44hEO8jU1vlc%3DkOi9SlxQDtWVIdrytaijlkP1QpIgBBw9FiYeOpfbHgkuMOS8TV"
    client = tweepy.Client(bearer_token=BEARER_TOKEN)
    return client

# Step 2: Collect tweets based on a query
def collect_tweets(client, query, max_results=2):
    print(f"Collecting tweets for query: '{query}'...")
    tweets = client.search_recent_tweets(
        query=query,
        max_results=max_results,
        tweet_fields=["created_at", "author_id", "text"]  # Additional fields for metadata
    )
    return tweets.data

# Step 3: Perform sentiment analysis using TextBlob
def analyze_sentiment(tweets):
    results = []
    for tweet in tweets:
        # Create a TextBlob object for sentiment analysis
        blob = TextBlob(tweet.text)
        polarity = blob.sentiment.polarity  # Range: -1 (negative) to +1 (positive)
        subjectivity = blob.sentiment.subjectivity  # Range: 0 (objective) to 1 (subjective)

        # Classify sentiment
        if polarity > 0:
            sentiment = "Positive"
        elif polarity < 0:
            sentiment = "Negative"
        else:
            sentiment = "Neutral"

        # Append results
        results.append({
            "Tweet": tweet.text,
            "Polarity": polarity,
            "Subjectivity": subjectivity,
            "Sentiment": sentiment,
            "Created At": tweet.created_at
        })
    return results

# Step 4: Save results to a CSV file
def save_to_csv(results, filename="sentiment_analysis_results.csv"):
    df = pd.DataFrame(results)
    df.to_csv(filename, index=False)
    print(f"Results saved to {filename}")

# Main function to execute the pipeline
def main():
    # Step 1: Authenticate
    client = authenticate()

    # Step 2: Define query and collect tweets
    query = "AI OR MachineLearning lang:en"  # Example query
    tweets = collect_tweets(client, query, max_results=50)

    if not tweets:
        print("No tweets found. Exiting.")
        return

    # Step 3: Analyze sentiment
    results = analyze_sentiment(tweets)

    # Step 4: Save results
    save_to_csv(results)

    # Optional: Print results to console
    for result in results:
        print(f"Tweet: {result['Tweet']}")
        print(f"Polarity: {result['Polarity']}, Subjectivity: {result['Subjectivity']}, Sentiment: {result['Sentiment']}")
        print("-" * 50)

# Run the script
if __name__ == "__main__":
    main()