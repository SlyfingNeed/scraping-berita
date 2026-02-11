import sys
import time
import argparse
from datetime import datetime
from typing import List, Dict

import config
from rss_collector import RSSCollector
from article_scraper import ArticleScraper
from keyword_filter import KeywordFilter
from exporter import Exporter
from utils import (
    URLTracker, 
    random_delay, 
    print_header, 
    print_article_info,
    get_timestamp
)


class NewsScraperOrchestrator:

    def __init__(self, output_format: str = None):
        print_header("Init")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        self.url_tracker = URLTracker()
        self.rss_collector = RSSCollector()
        self.article_scraper = ArticleScraper()
        self.keyword_filter = KeywordFilter()
        self.exporter = Exporter(output_format)
        
        # Stats
        self.stats = {
            'rss_fetched': 0,
            'articles_scanned': 0,
            'articles_scraped': 0,
            'articles_matched': 0,
            'articles_saved': 0,
            'already_scraped': 0
        }
    
    def run_scraping_cycle(self):

        print_header(f"SCRAPING CYCLE - {datetime.now().strftime('%H:%M:%S')}")
        
        # Step 1: Collect RSS feeds
        rss_articles = self.rss_collector.collect_all_feeds()
        self.stats['rss_fetched'] = len(rss_articles)
        
        if not rss_articles:
            print("\n No articles collected from RSS feeds")
            return
        
        # Step 2: Filter out already scraped URLs
        print_header("FILTERING NEW ARTICLES")
        new_articles = []
        
        for article in rss_articles:
            if not self.url_tracker.is_scraped(article['url']):
                new_articles.append(article)
            else:
                self.stats['already_scraped'] += 1
        
        print(f"  New articles to process: {len(new_articles)}")
        print(f"  Already scraped: {self.stats['already_scraped']}")
        
        if not new_articles:
            print("\nNo new articles to scrape")
            return
        
        # Step 3: Scrape and filter articles
        print_header("SCRAPING & FILTERING ARTICLES")
        matched_articles = []
        
        for i, article in enumerate(new_articles, 1):
            print(f"\n[{i}/{len(new_articles)}] Processing: {article['title'][:60]}...")
            
            # Quick check: Does title match keywords?
            title_match = self.keyword_filter.find_matching_keyword(article['title'], "")
            
            if title_match:
                print(f"  ✓ Title matched keyword: {title_match}")
            
            # Scrape full article content
            print(f"  Scraping content...")
            content = self.article_scraper.scrape_article(article['url'])
            
            self.stats['articles_scraped'] += 1
            
            if not content:
                print(f"  Could not extract content")
                # Mark as scraped even if failed to avoid retrying
                self.url_tracker.add_url(article['url'])
                continue
            
            print(f" Extracted {len(content)} characters")
            
            # Check if content matches keywords
            matched_keyword = self.keyword_filter.check_article(
                article['title'], 
                content,
                return_all=True  # Get all matching keywords
            )
            
            if matched_keyword:
                # Article matches! Save it
                self.stats['articles_matched'] += 1
                
                article_data = {
                    'title': article['title'],
                    'content': content,
                    'matched_keyword': matched_keyword,
                    'source': article['source'],
                    'category': article.get('category', ''),
                    'published_date': article.get('published_date', ''),
                    'url': article['url'],
                    'scraped_at': get_timestamp()
                }
                
                matched_articles.append(article_data)
                print_article_info(article_data)
                
                # Mark URL as scraped
                self.url_tracker.add_url(article['url'])
            else:
                print(f" No keyword match")
                # Mark as scraped
                self.url_tracker.add_url(article['url'])
            
            # Add delay between articles
            random_delay()
        
        # Step 4: Save matched articles
        if matched_articles:
            print_header("SAVING RESULTS")
            output_path = self.exporter.save_articles(matched_articles)
            self.stats['articles_saved'] = len(matched_articles)
        else:
            print_header("NO MATCHES FOUND")
            print(" Scraping complete but no articles matched keywords")
        
        # Step 5: Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print scraping cycle summary"""
        print_header("CYCLE SUMMARY")
        print(f"RSS Articles Fetched:     {self.stats['rss_fetched']}")
        print(f"Already Scraped (skipped): {self.stats['already_scraped']}")
        print(f"Articles Scraped:         {self.stats['articles_scraped']}")
        print(f"Keyword Matches:          {self.stats['articles_matched']}")
        print(f"Articles Saved:           {self.stats['articles_saved']}")
        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    def run_continuous(self):
        
        print(f"\n CONTINUOUS MODE")
        print(f"Will run every {config.CHECK_INTERVAL} seconds")
        print(f"Press Ctrl+C to stop\n")
        
        cycle_count = 0
        
        try:
            while True:
                cycle_count += 1
                print(f"\n{'='*60}")
                print(f"CYCLE #{cycle_count}")
                print(f"{'='*60}")
                
                # Reset stats for new cycle
                self.stats = {
                    'rss_fetched': 0,
                    'articles_scanned': 0,
                    'articles_scraped': 0,
                    'articles_matched': 0,
                    'articles_saved': 0,
                    'already_scraped': 0
                }
                
                # Run scraping cycle
                self.run_scraping_cycle()
                
                # Wait before next cycle
                print(f"\n Waiting {config.CHECK_INTERVAL} seconds until next cycle...")
                time.sleep(config.CHECK_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n\n✓ Stopped by user")
            print(f"Total cycles completed: {cycle_count}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Indonesian News Keyword-Based Scraper'
    )
    parser.add_argument(
        '--continuous',
        action='store_true',
        help='Run continuously (every 10 minutes)'
    )
    parser.add_argument(
        '--format',
        choices=['csv', 'xlsx'],
        default=None,
        help='Output format (overrides config.py)'
    )
    
    args = parser.parse_args()
    
    # Initialize orchestrator
    orchestrator = NewsScraperOrchestrator(output_format=args.format)
    
    try:
        if args.continuous:
            # Continuous mode
            orchestrator.run_continuous()
        else:
            # Single run
            orchestrator.run_scraping_cycle()
            print("\n Scraping complete!")
    
    except Exception as e:
        print(f"\n Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
