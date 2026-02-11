import feedparser
import requests
from typing import List, Dict
import config
from utils import random_delay, get_random_user_agent, print_header


class RSSCollector:
        
    def __init__(self):
        self.session = requests.Session()
        self.collected_articles = []
    
    def fetch_rss_feed(self, feed_url: str, source_name: str) -> List[Dict]:

        articles = []
        
        try:
            # Add random delay and user agent
            headers = {'User-Agent': get_random_user_agent()}
            
            # Fetch RSS feed
            response = self.session.get(
                feed_url, 
                headers=headers, 
                timeout=config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            # Parse RSS
            feed = feedparser.parse(response.content)
            
            # Extract articles
            for entry in feed.entries:
                article = {
                    'title': entry.get('title', '').strip(),
                    'url': entry.get('link', '').strip(),
                    'published_date': entry.get('published', ''),
                    'category': entry.get('category', ''),
                    'source': source_name,
                    'description': entry.get('summary', '').strip()
                }
                
                # Only add if we have title and URL
                if article['title'] and article['url']:
                    articles.append(article)
            
            print(f" {source_name}: {len(articles)} articles")
            
        except requests.exceptions.Timeout:
            print(f" {source_name}: Timeout")
        except requests.exceptions.RequestException as e:
            print(f" {source_name}: Request error - {str(e)[:50]}")
        except Exception as e:
            print(f" {source_name}: Parse error - {str(e)[:50]}")
        
        return articles
    
    def collect_all_feeds(self) -> List[Dict]:

        print_header("COLLECTING RSS FEEDS")
        
        all_articles = []
        
        for source_name, feed_url in config.RSS_FEEDS.items():
            articles = self.fetch_rss_feed(feed_url, source_name)
            all_articles.extend(articles)
            
            # Random delay between feeds
            random_delay()
        
        print(f"\n✓ Total articles collected: {len(all_articles)}")
        self.collected_articles = all_articles
        return all_articles
    
    def get_unique_urls(self) -> List[str]:
        """Get list of unique article URLs"""
        return list(set(article['url'] for article in self.collected_articles))


if __name__ == "__main__":
    # Test RSS collector
    collector = RSSCollector()
    articles = collector.collect_all_feeds()
    
    if articles:
        print("\nSample articles:")
        for article in articles[:3]:
            print(f"  - {article['title'][:60]}...")
            print(f"    {article['url'][:80]}")
