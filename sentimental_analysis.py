# -*- coding: utf-8 -*-
"""
Created on Sat May 30 20:53:05 2026

@author: DELL
"""

import pandas as pd
import feedparser
import praw
from datetime import datetime
from transformers import pipeline

class MarketSentimentPipeline:
    def __init__(self, reddit_client_id: str, reddit_secret: str):
        # Initialize FinBERT: specifically trained on financial text
        print("Loading FinBERT model... (This may take a moment)")
        self.nlp = pipeline("sentiment-analysis", model="ProsusAI/finbert")
        
        # Initialize Reddit API
        self.reddit = praw.Reddit(
            client_id=reddit_client_id,
            client_secret=reddit_secret,
            user_agent="CompIntel Dashboard / 1.0"
        )
        
    def score_text(self, text: str) -> dict:
        """Processes text through FinBERT and returns a normalized score."""
        try:
            # FinBERT returns labels: 'positive', 'negative', 'neutral'
            result = self.nlp(text[:512])[0]  # Truncate to 512 tokens
            
            # Convert labels to a numerical spectrum: -1.0 to 1.0
            score_map = {"positive": 1.0, "neutral": 0.0, "negative": -1.0}
            raw_score = score_map[result['label']] * result['score']
            
            return {
                "label": result['label'],
                "confidence": round(result['score'], 3),
                "net_score": round(raw_score, 3)
            }
        except Exception as e:
            return {"label": "error", "confidence": 0.0, "net_score": 0.0}

    def fetch_reddit(self, query: str, limit: int = 20) -> list:
        """Scrapes recent posts from r/Finanzen and general search."""
        results = []
        subreddit = self.reddit.subreddit("Finanzen+investing")
        for submission in subreddit.search(query, sort="new", limit=limit):
            sentiment = self.score_text(submission.title)
            results.append({
                "source": "Reddit",
                "target": query,
                "text": submission.title,
                "sentiment_score": sentiment["net_score"]
            })
        return results

    def fetch_news(self, query: str) -> list:
        """Uses Google News RSS as a free, unauthenticated media scraper."""
        results = []
        # URL encode the query for Google News
        url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}+finance&hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(url)
        
        for entry in feed.entries[:10]: # Top 10 recent articles
            sentiment = self.score_text(entry.title)
            results.append({
                "source": "Media",
                "target": query,
                "text": entry.title,
                "sentiment_score": sentiment["net_score"]
            })
        return results

    def fetch_x(self, query: str) -> list:
        """
        Placeholder for X/Twitter pipeline. 
        Requires Enterprise API or an unofficial scraper like ntscraper.
        """
        # Mocking the output for architectural completeness
        mock_tweets = [f"{query} app is crashing again during open!", f"Love the new savings plan from {query}."]
        results = []
        for tweet in mock_tweets:
            sentiment = self.score_text(tweet)
            results.append({
                "source": "X (Twitter)",
                "target": query,
                "text": tweet,
                "sentiment_score": sentiment["net_score"]
            })
        return results

    def aggregate_sentiment(self, broker_name: str) -> pd.DataFrame:
        """Orchestrates the pulls and returns a consolidated DataFrame."""
        print(f"Gathering signals for {broker_name}...")
        
        all_signals = []
        all_signals.extend(self.fetch_reddit(broker_name))
        all_signals.extend(self.fetch_news(broker_name))
        all_signals.extend(self.fetch_x(broker_name))
        
        df = pd.DataFrame(all_signals)
        return df

if __name__ == "__main__":
    # You will need to insert your own Reddit API keys here
    pipeline = MarketSentimentPipeline("YOUR_ID", "YOUR_SECRET")
    
    # Run a test for a target broker
    df_signals = pipeline.aggregate_sentiment("Trade Republic")
    
    print(f"\n--- Sentiment Signals for Trade Republic ---")
    print(df_signals[['source', 'sentiment_score', 'text']].head().to_markdown(index=False))
    
    # Calculate the aggregate brand sentiment score
    avg_score = df_signals['sentiment_score'].mean()
    print(f"\nAggregate Net Sentiment: {avg_score:.2f} (-1.0 to 1.0)")