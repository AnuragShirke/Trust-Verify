#!/usr/bin/env python
"""
News Collector Script

This script collects news articles from various RSS feeds and optionally from NewsAPI.
It processes the articles and prepares them for analysis.
"""

import os
import time
import json
import logging
import datetime
import feedparser
import newspaper
from newspaper import Article
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/news_collector.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("news_collector")

# List of RSS feeds to monitor
RSS_FEEDS = [
    # General news
    "http://rss.cnn.com/rss/cnn_topstories.rss",
    "https://www.nytimes.com/svc/collections/v1/publish/https://www.nytimes.com/section/world/rss.xml",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.theguardian.com/world/rss",
    "https://www.washingtonpost.com/rss/world",

    # Technology
    "https://feeds.feedburner.com/TechCrunch",
    "https://www.wired.com/feed/rss",

    # Science
    "https://www.sciencedaily.com/rss/all.xml",
    "https://www.sciencenews.org/feed",

    # Potentially less reliable sources (for testing)
    "https://www.infowars.com/feed/custom_feed_rss",
    "https://www.breitbart.com/feed/",
]

# NewsAPI configuration (optional)
NEWSAPI_KEY = os.environ.get("NEWSAPI_KEY", "")
USE_NEWSAPI = NEWSAPI_KEY != ""

def extract_domain(url: str) -> str:
    """Extract the domain from a URL."""
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    if domain.startswith('www.'):
        domain = domain[4:]
    return domain

def fetch_from_rss_feeds() -> List[Dict[str, Any]]:
    """Fetch articles from RSS feeds."""
    articles = []

    for feed_url in RSS_FEEDS:
        try:
            logger.info(f"Fetching from RSS feed: {feed_url}")
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:10]:  # Limit to 10 articles per feed
                try:
                    # Extract basic information from the feed
                    article_data = {
                        "title": entry.get("title", ""),
                        "url": entry.get("link", ""),
                        "published_date": entry.get("published", ""),
                        "source": extract_domain(feed_url),
                        "source_url": feed_url,
                        "collection_time": datetime.datetime.now().isoformat(),
                        "content": entry.get("summary", ""),
                    }

                    # Skip if no URL
                    if not article_data["url"]:
                        continue

                    articles.append(article_data)
                    logger.debug(f"Added article: {article_data['title']}")
                except Exception as e:
                    logger.error(f"Error processing feed entry: {str(e)}")
        except Exception as e:
            logger.error(f"Error fetching feed {feed_url}: {str(e)}")

    return articles

def fetch_from_newsapi() -> List[Dict[str, Any]]:
    """Fetch articles from NewsAPI."""
    if not USE_NEWSAPI:
        return []

    articles = []
    try:
        import requests

        logger.info("Fetching from NewsAPI")
        url = f"https://newsapi.org/v2/top-headlines?language=en&apiKey={NEWSAPI_KEY}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            for article in data.get("articles", []):
                article_data = {
                    "title": article.get("title", ""),
                    "url": article.get("url", ""),
                    "published_date": article.get("publishedAt", ""),
                    "source": article.get("source", {}).get("name", ""),
                    "source_url": "",
                    "collection_time": datetime.datetime.now().isoformat(),
                    "content": article.get("description", ""),
                }

                # Skip if no URL
                if not article_data["url"]:
                    continue

                articles.append(article_data)
                logger.debug(f"Added article from NewsAPI: {article_data['title']}")
        else:
            logger.error(f"NewsAPI returned status code {response.status_code}")
    except Exception as e:
        logger.error(f"Error fetching from NewsAPI: {str(e)}")

    return articles

def enrich_article_data(article_data: Dict[str, Any]) -> Dict[str, Any]:
    """Enrich article data using newspaper3k."""
    try:
        url = article_data["url"]
        logger.info(f"Enriching article: {url}")

        article = Article(url)
        article.download()
        article.parse()

        # Try to extract additional information
        try:
            article.nlp()
        except Exception as e:
            logger.warning(f"NLP processing failed: {str(e)}")

        # Update article data with enriched information
        article_data["full_text"] = article.text
        article_data["authors"] = article.authors
        article_data["top_image"] = article.top_image

        if hasattr(article, 'summary') and article.summary:
            article_data["summary"] = article.summary

        if hasattr(article, 'keywords') and article.keywords:
            article_data["keywords"] = article.keywords

        # Use the full text as content if available
        if article.text:
            article_data["content"] = article.text

        return article_data
    except Exception as e:
        logger.error(f"Error enriching article {article_data['url']}: {str(e)}")
        return article_data

def save_articles_to_file(articles: List[Dict[str, Any]], filename: str = "collected_articles.json"):
    """Save articles to a JSON file."""
    try:
        # Create the output directory if it doesn't exist
        os.makedirs("data", exist_ok=True)

        filepath = f"data/{filename}"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)

        logger.info(f"Saved {len(articles)} articles to {filepath}")
    except Exception as e:
        logger.error(f"Error saving articles to file: {str(e)}")

def main():
    """Main function to collect news articles."""
    logger.info("Starting news collection")

    # Collect articles from RSS feeds
    rss_articles = fetch_from_rss_feeds()
    logger.info(f"Collected {len(rss_articles)} articles from RSS feeds")

    # Collect articles from NewsAPI if configured
    newsapi_articles = fetch_from_newsapi()
    logger.info(f"Collected {len(newsapi_articles)} articles from NewsAPI")

    # Combine all articles
    all_articles = rss_articles + newsapi_articles

    # Enrich a subset of articles (to avoid rate limiting)
    enriched_articles = []
    for article in all_articles[:20]:  # Limit to 20 articles for enrichment
        enriched_article = enrich_article_data(article)
        enriched_articles.append(enriched_article)
        time.sleep(1)  # Sleep to avoid overwhelming the servers

    # Save the enriched articles
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    save_articles_to_file(enriched_articles, f"articles_{timestamp}.json")

    logger.info("News collection completed")

if __name__ == "__main__":
    main()
