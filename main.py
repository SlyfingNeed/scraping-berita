import sys
import time
import argparse
from datetime import datetime
from typing import List, Dict

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

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
    get_timestamp,
    is_article_in_date_range
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
        
        # Step 2: Filter by date range
        print_header("FILTERING BY DATE & DEDUPLICATION")
        
        date_filtered = []
        outside_date_range = 0
        
        for article in rss_articles:
            # Check date range
            if is_article_in_date_range(
                article.get('published_date', ''),
                config.DATE_FILTER_START_YEAR,
                config.DATE_FILTER_END_YEAR
            ):
                date_filtered.append(article)
            else:
                outside_date_range += 1
        
        # Filter out already scraped URLs
        new_articles = []
        for article in date_filtered:
            if not self.url_tracker.is_scraped(article['url']):
                new_articles.append(article)
            else:
                self.stats['already_scraped'] += 1
        
        if config.DATE_FILTER_START_YEAR or config.DATE_FILTER_END_YEAR:
            date_range = f"{config.DATE_FILTER_START_YEAR or '...'}-{config.DATE_FILTER_END_YEAR or '...'}"
            print(f"  Date range: {date_range}")
            print(f"  Within date range: {len(date_filtered)}")
            print(f"  Outside date range: {outside_date_range}")
        print(f"  New articles to process: {len(new_articles)}")
        print(f"  Already scraped: {self.stats['already_scraped']}")
        
        if not new_articles:
            print("\n  No new articles to scrape")
            return
        
        # Step 3: Pre-filter by title/description to avoid scraping irrelevant articles
        print_header("PRE-FILTERING BY TITLE & DESCRIPTION")
        candidates = []
        skipped_no_potential = 0
        short_description_count = 0

        for article in new_articles:
            title_text = article.get('title', '')
            desc_text = article.get('description', '')
            
            # If RSS description is too short or missing, we can't reliably pre-filter
            # Include it as a candidate to check full content
            desc_length = len(desc_text.strip())
            if desc_length < config.PRE_FILTER_MIN_DESCRIPTION_LENGTH:
                candidates.append(article)
                short_description_count += 1
                continue
            
            # Check if title or RSS description contains any keyword
            pre_match = self.keyword_filter.check_article(
                title_text, desc_text, return_all=False
            )
            if pre_match:
                candidates.append(article)
            else:
                # DON'T mark as scraped — title pre-filter is cheap,
                # and we want these re-evaluated if keywords change.
                skipped_no_potential += 1

        print(f"  Candidates with keyword in title/desc: {len(candidates) - short_description_count}")
        print(f"  Candidates (short/no description):     {short_description_count}")
        print(f"  Skipped (no keyword potential):         {skipped_no_potential}")
        print(f"  Total candidates to scrape:             {len(candidates)}")

        if not candidates:
            print("\n  ⚠ No articles matched keywords in title/description")
            print("  Tip: Your keywords may be too specific for RSS descriptions.")
            print("       Consider broadening keywords or lowering the pre-filter threshold.")
            self.print_summary()
            return

        # Step 4: Scrape full content for candidates only
        print_header("SCRAPING MATCHED CANDIDATES")
        matched_articles = []

        for i, article in enumerate(candidates, 1):
            print(f"\n[{i}/{len(candidates)}] {article['title'][:65]}")
            print(f"  Source: {article['source']}")

            # Scrape full article content
            content = self.article_scraper.scrape_article(article['url'])
            self.stats['articles_scraped'] += 1

            if not content:
                print(f"  ✗ Could not extract content")
                self.url_tracker.add_url(article['url'])
                continue

            print(f"  ✓ Extracted {len(content)} characters")

            # Verify keyword match in full content (title + content)
            matched_keyword = self.keyword_filter.check_article(
                article['title'],
                content,
                return_all=True
            )

            if matched_keyword:
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
            else:
                print(f"  ✗ No keyword match in full content")

            # Mark URL as scraped
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
