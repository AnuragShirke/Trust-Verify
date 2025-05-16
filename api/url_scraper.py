"""
URL scraper module for the Fake News Detector.

This module provides functions for extracting content from URLs.
"""

import logging
import re
import json
import os
import time
import hashlib
from typing import Dict, Any, Optional, Tuple, List
from urllib.parse import urlparse
from datetime import datetime, timedelta

import requests
import validators
from bs4 import BeautifulSoup
from readability import Document
import trafilatura
from newspaper import Article
from newspaper.article import ArticleException
import extruct
from dateutil import parser as date_parser
from w3lib.html import get_base_url

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("url-scraper")

# List of known news domains and their credibility scores (0-100)
NEWS_DOMAINS = {
    # Tier 1: High-quality international news sources (80-95)
    "bbc.com": 90,
    "bbc.co.uk": 90,
    "reuters.com": 95,
    "apnews.com": 95,
    "nytimes.com": 85,
    "washingtonpost.com": 85,
    "theguardian.com": 85,
    "wsj.com": 85,
    "economist.com": 90,
    "bloomberg.com": 85,
    "ft.com": 90,
    "aljazeera.com": 80,
    "france24.com": 85,
    "dw.com": 85,  # Deutsche Welle

    # Tier 2: Reputable national news sources (75-85)
    "npr.org": 85,
    "pbs.org": 85,
    "time.com": 80,
    "theatlantic.com": 80,
    "newyorker.com": 80,
    "politico.com": 80,
    "axios.com": 80,
    "latimes.com": 80,
    "chicagotribune.com": 80,
    "bostonglobe.com": 80,
    "usatoday.com": 75,
    "cnn.com": 75,
    "nbcnews.com": 80,
    "abcnews.go.com": 80,
    "cbsnews.com": 80,

    # Tier 3: Mainstream news with varying quality (65-75)
    "foxnews.com": 70,
    "newsweek.com": 70,
    "thehill.com": 75,
    "vox.com": 75,
    "slate.com": 70,
    "thedailybeast.com": 65,
    "huffpost.com": 65,
    "buzzfeednews.com": 70,
    "vice.com": 65,

    # Tier 4: Tabloids and less reliable sources (50-65)
    "nypost.com": 60,
    "dailymail.co.uk": 55,
    "thesun.co.uk": 50,
    "mirror.co.uk": 55,
    "express.co.uk": 55,

    # Tier 5: Highly partisan or questionable sources (30-50)
    "breitbart.com": 45,
    "dailycaller.com": 45,
    "theblaze.com": 45,
    "oann.com": 40,
    "newsmax.com": 40,

    # Tier 6: Known for misinformation (below 30)
    "infowars.com": 20,
    "naturalnews.com": 15,
    "zerohedge.com": 25,

    # Science and technology sources
    "scientificamerican.com": 90,
    "nature.com": 95,
    "science.org": 95,
    "newscientist.com": 85,
    "wired.com": 80,
    "techcrunch.com": 75,
    "arstechnica.com": 85,
    "technologyreview.com": 85,

    # Business news
    "cnbc.com": 80,
    "forbes.com": 75,
    "businessinsider.com": 70,
    "marketwatch.com": 75,

    # International sources
    "cbc.ca": 85,  # Canadian Broadcasting Corporation
    "abc.net.au": 85,  # Australian Broadcasting Corporation
    "smh.com.au": 80,  # Sydney Morning Herald
    "irishtimes.com": 80,
    "independent.co.uk": 75,
    "telegraph.co.uk": 75,
    "thelocal.fr": 75,
    "thelocal.de": 75,
    "spiegel.de": 85,
    "scmp.com": 75,  # South China Morning Post
}

# List of known fake news domains
FAKE_NEWS_DOMAINS = [
    "infowars.com",
    "naturalnews.com",
    "worldnewsdailyreport.com",
    "empirenews.net",
    "nationalreport.net",
    "worldtruth.tv",
    "beforeitsnews.com",
    "endingthefed.com",
    "dcclothesline.com",
    "redflagnews.com",
    "disclose.tv",
    "yournewswire.com",
    "newspunch.com",
    "americannews.com",
    "thelastlineofdefense.org",
    "libertywriters.com",
    "civictribune.com",
    "amplifyingglass.com",
    "abcnews.com.co",
    "usatoday.com.co",
    "washingtonpost.com.co",
    "nbc.com.co",
    "cnn.com.co",
    "foxnews.com.co",
]


def is_valid_url(url: str) -> bool:
    """
    Check if a URL is valid.

    Args:
        url: The URL to check

    Returns:
        bool: True if the URL is valid, False otherwise
    """
    # Log the URL being validated
    print(f"Validating URL: {url}")

    # Make sure URL is a string
    if not isinstance(url, str):
        print(f"URL is not a string: {type(url)}")
        return False

    # Make sure URL is not empty
    if not url:
        print("URL is empty")
        return False

    # Make sure URL starts with http:// or https://
    if not url.startswith('http://') and not url.startswith('https://'):
        print(f"URL does not start with http:// or https://: {url}")
        return False

    # Use validators library as a backup check
    is_valid = validators.url(url) is True
    print(f"URL validation result: {is_valid}")
    return is_valid


def get_domain(url: str) -> str:
    """
    Extract the domain from a URL.

    Args:
        url: The URL to extract the domain from

    Returns:
        str: The domain name
    """
    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    # Remove 'www.' prefix if present
    if domain.startswith('www.'):
        domain = domain[4:]

    return domain


def get_source_credibility(url: str) -> int:
    """
    Get the credibility score for a news source.

    Args:
        url: The URL of the news article

    Returns:
        int: The credibility score (0-100)
    """
    domain = get_domain(url)

    # Check if the domain is in the list of known fake news domains
    if domain in FAKE_NEWS_DOMAINS:
        return 0

    # Check if the domain is in the list of known news domains
    if domain in NEWS_DOMAINS:
        return NEWS_DOMAINS[domain]

    # Default credibility score for unknown domains
    return 50


def extract_with_newspaper(url: str) -> Optional[Dict[str, Any]]:
    """
    Extract article content using the newspaper library.

    Args:
        url: The URL of the article

    Returns:
        Dict: The extracted article data, or None if extraction failed
    """
    try:
        article = Article(url)
        article.download()
        article.parse()

        # Check if we got meaningful content
        if not article.text or len(article.text) < 100:
            logger.warning(f"Newspaper extraction yielded insufficient content for {url}")
            return None

        return {
            "title": article.title,
            "content": article.text,
            "authors": article.authors,
            "publish_date": article.publish_date.isoformat() if article.publish_date else None,
            "top_image": article.top_image,
            "source": get_domain(url),
            "url": url
        }
    except (ArticleException, Exception) as e:
        logger.error(f"Error extracting content with newspaper from {url}: {e}")
        return None


def extract_with_readability(url: str) -> Optional[Dict[str, Any]]:
    """
    Extract article content using the readability library.

    Args:
        url: The URL of the article

    Returns:
        Dict: The extracted article data, or None if extraction failed
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        doc = Document(response.text)
        title = doc.title()
        content = doc.summary()

        # Clean up the HTML content
        soup = BeautifulSoup(content, "html.parser")
        text = soup.get_text(separator=" ", strip=True)

        # Check if we got meaningful content
        if not text or len(text) < 100:
            logger.warning(f"Readability extraction yielded insufficient content for {url}")
            return None

        return {
            "title": title,
            "content": text,
            "source": get_domain(url),
            "url": url
        }
    except Exception as e:
        logger.error(f"Error extracting content with readability from {url}: {e}")
        return None


def extract_with_trafilatura(url: str) -> Optional[Dict[str, Any]]:
    """
    Extract article content using the trafilatura library.

    Args:
        url: The URL of the article

    Returns:
        Dict: The extracted article data, or None if extraction failed
    """
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            logger.warning(f"Failed to download content from {url}")
            return None

        result = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
        if not result or len(result) < 100:
            logger.warning(f"Trafilatura extraction yielded insufficient content for {url}")
            return None

        # Try to extract metadata
        metadata = trafilatura.extract_metadata(downloaded)
        title = metadata.title if metadata and metadata.title else ""

        return {
            "title": title,
            "content": result,
            "source": get_domain(url),
            "url": url
        }
    except Exception as e:
        logger.error(f"Error extracting content with trafilatura from {url}: {e}")
        return None


# Create cache directory if it doesn't exist
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

def get_cache_path(url: str) -> str:
    """
    Get the cache file path for a URL.

    Args:
        url: The URL to get the cache path for

    Returns:
        str: The cache file path
    """
    # Create a hash of the URL to use as the filename
    url_hash = hashlib.md5(url.encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"{url_hash}.json")

def get_cached_article(url: str) -> Optional[Dict[str, Any]]:
    """
    Get a cached article if it exists and is not expired.

    Args:
        url: The URL of the article

    Returns:
        Dict: The cached article data, or None if not cached or expired
    """
    cache_path = get_cache_path(url)

    # Check if cache file exists
    if not os.path.exists(cache_path):
        return None

    try:
        # Read the cache file
        with open(cache_path, 'r', encoding='utf-8') as f:
            cached_data = json.load(f)

        # Check if the cache is expired (24 hours)
        cache_time = datetime.fromisoformat(cached_data.get('cache_time', '2000-01-01T00:00:00'))
        if datetime.now() - cache_time > timedelta(hours=24):
            # Cache is expired
            return None

        return cached_data
    except Exception as e:
        logger.error(f"Error reading cache for {url}: {e}")
        return None

def cache_article(url: str, article_data: Dict[str, Any]) -> None:
    """
    Cache an article.

    Args:
        url: The URL of the article
        article_data: The article data to cache
    """
    cache_path = get_cache_path(url)

    try:
        # Add cache metadata
        article_data['cache_time'] = datetime.now().isoformat()

        # Write to cache file
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(article_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error caching article for {url}: {e}")

def extract_metadata(url: str, html: str) -> Dict[str, Any]:
    """
    Extract metadata from HTML using extruct.

    Args:
        url: The URL of the page
        html: The HTML content

    Returns:
        Dict: The extracted metadata
    """
    base_url = get_base_url(html, url)
    metadata = {}

    try:
        # Extract metadata using extruct
        extracted = extruct.extract(
            html,
            base_url=base_url,
            syntaxes=['json-ld', 'microdata', 'opengraph', 'microformat', 'dublin']
        )

        # Process JSON-LD
        if extracted.get('json-ld'):
            for item in extracted['json-ld']:
                if item.get('@type') == 'NewsArticle' or item.get('@type') == 'Article':
                    metadata['title'] = item.get('headline', '')
                    metadata['authors'] = item.get('author', {}).get('name', '') if isinstance(item.get('author', {}), dict) else item.get('author', [])
                    metadata['published_date'] = item.get('datePublished', '')
                    metadata['modified_date'] = item.get('dateModified', '')
                    metadata['description'] = item.get('description', '')
                    metadata['publisher'] = item.get('publisher', {}).get('name', '') if isinstance(item.get('publisher', {}), dict) else ''
                    metadata['section'] = item.get('articleSection', '')
                    metadata['keywords'] = item.get('keywords', [])

        # Process Open Graph
        if extracted.get('opengraph'):
            og = extracted['opengraph'][0] if extracted['opengraph'] else {}
            if not metadata.get('title'):
                metadata['title'] = og.get('og:title', '')
            if not metadata.get('description'):
                metadata['description'] = og.get('og:description', '')
            if not metadata.get('published_date'):
                metadata['published_date'] = og.get('article:published_time', '')
            if not metadata.get('modified_date'):
                metadata['modified_date'] = og.get('article:modified_time', '')
            if not metadata.get('section'):
                metadata['section'] = og.get('article:section', '')
            if not metadata.get('authors') and og.get('article:author'):
                metadata['authors'] = og.get('article:author', '')

        # Process Dublin Core
        if extracted.get('dublin'):
            dc = extracted['dublin'][0] if extracted['dublin'] else {}
            if not metadata.get('title'):
                metadata['title'] = dc.get('title', '')
            if not metadata.get('description'):
                metadata['description'] = dc.get('description', '')
            if not metadata.get('authors'):
                metadata['authors'] = dc.get('creator', '')
            if not metadata.get('published_date'):
                metadata['published_date'] = dc.get('date', '')

        # Convert dates to ISO format if possible
        for date_field in ['published_date', 'modified_date']:
            if metadata.get(date_field) and isinstance(metadata[date_field], str):
                try:
                    parsed_date = date_parser.parse(metadata[date_field])
                    metadata[date_field] = parsed_date.isoformat()
                except Exception:
                    pass

        return metadata
    except Exception as e:
        logger.error(f"Error extracting metadata from {url}: {e}")
        return {}

def extract_article_from_url(url: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Extract article content from a URL using multiple methods.

    Args:
        url: The URL of the article

    Returns:
        Tuple[Dict, str]: The extracted article data and the method used, or (None, "") if extraction failed
    """
    # Validate the URL
    if not is_valid_url(url):
        logger.error(f"Invalid URL: {url}")
        return None, ""

    # Check cache first
    cached_article = get_cached_article(url)
    if cached_article:
        logger.info(f"Using cached article for {url}")
        return cached_article, cached_article.get('extraction_method', 'cache')

    # Try different extraction methods in order of preference

    # 1. Try newspaper
    article = extract_with_newspaper(url)
    if article and article["content"]:
        # Add extraction method
        article['extraction_method'] = 'newspaper'

        # Cache the article
        cache_article(url, article)

        return article, "newspaper"

    # 2. Try trafilatura
    article = extract_with_trafilatura(url)
    if article and article["content"]:
        # Add extraction method
        article['extraction_method'] = 'trafilatura'

        # Try to get additional metadata
        try:
            response = requests.get(url, timeout=10)
            if response.ok:
                metadata = extract_metadata(url, response.text)
                # Update article with metadata
                if metadata.get('title') and not article.get('title'):
                    article['title'] = metadata['title']
                if metadata.get('authors'):
                    article['authors'] = metadata['authors']
                if metadata.get('published_date'):
                    article['publish_date'] = metadata['published_date']
                if metadata.get('description'):
                    article['description'] = metadata['description']
                if metadata.get('section'):
                    article['section'] = metadata['section']
                if metadata.get('keywords'):
                    article['keywords'] = metadata['keywords']
        except Exception as e:
            logger.warning(f"Error getting additional metadata for {url}: {e}")

        # Cache the article
        cache_article(url, article)

        return article, "trafilatura"

    # 3. Try readability
    article = extract_with_readability(url)
    if article and article["content"]:
        # Add extraction method
        article['extraction_method'] = 'readability'

        # Try to get additional metadata
        try:
            response = requests.get(url, timeout=10)
            if response.ok:
                metadata = extract_metadata(url, response.text)
                # Update article with metadata
                if metadata.get('title') and not article.get('title'):
                    article['title'] = metadata['title']
                if metadata.get('authors'):
                    article['authors'] = metadata['authors']
                if metadata.get('published_date'):
                    article['publish_date'] = metadata['published_date']
                if metadata.get('description'):
                    article['description'] = metadata['description']
                if metadata.get('section'):
                    article['section'] = metadata['section']
                if metadata.get('keywords'):
                    article['keywords'] = metadata['keywords']
        except Exception as e:
            logger.warning(f"Error getting additional metadata for {url}: {e}")

        # Cache the article
        cache_article(url, article)

        return article, "readability"

    # All methods failed
    logger.error(f"Failed to extract content from {url} using all available methods")
    return None, ""


def get_article_from_url(url: str) -> Optional[Dict[str, Any]]:
    """
    Get article content from a URL.

    Args:
        url: The URL of the article

    Returns:
        Dict: The article data, or None if extraction failed
    """
    article, method = extract_article_from_url(url)

    if not article:
        return None

    # Add source credibility
    article["source_credibility"] = get_source_credibility(url)

    # Add extraction method if not already present
    if "extraction_method" not in article:
        article["extraction_method"] = method

    # Add domain
    article["domain"] = get_domain(url)

    # Add timestamp
    article["timestamp"] = datetime.now().isoformat()

    # Check if the domain is in the fake news domains list
    article["is_known_fake_news"] = article["domain"] in FAKE_NEWS_DOMAINS

    # Add a summary if content is long
    if len(article["content"]) > 1000:
        try:
            # Create a simple summary (first 2-3 sentences)
            sentences = article["content"].split('.')
            summary = '.'.join(sentences[:min(3, len(sentences))]) + '.'
            article["summary"] = summary.strip()
        except Exception as e:
            logger.warning(f"Error creating summary for {url}: {e}")

    # Add reading time estimate (average reading speed: 200-250 words per minute)
    try:
        word_count = len(article["content"].split())
        reading_time_minutes = round(word_count / 225)
        article["reading_time_minutes"] = max(1, reading_time_minutes)  # Minimum 1 minute
    except Exception as e:
        logger.warning(f"Error calculating reading time for {url}: {e}")

    return article
