import os
import time
import random
from datetime import datetime
from typing import Set, Optional
import re
import config


class URLTracker:
        
    def __init__(self, filepath: str = config.SCRAPED_URLS_FILE):
        self.filepath = filepath
        self.urls: Set[str] = set()
        self.load_urls()
    
    def load_urls(self):
        
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    self.urls = set(line.strip() for line in f if line.strip())
                print(f"Loaded {len(self.urls)} previously scraped URLs")
                
                # Limit memory usage
                if len(self.urls) > config.MAX_URLS_IN_MEMORY:
                    # Keep only the most recent URLs
                    self.urls = set(list(self.urls)[-config.MAX_URLS_IN_MEMORY:])
                    print(f"  Trimmed to last {config.MAX_URLS_IN_MEMORY} URLs")
            except Exception as e:
                print(f" Warning loading URL tracker: {e}")
                self.urls = set()
    
    def is_scraped(self, url: str) -> bool:
        """Check if URL has been scraped before"""
        return url in self.urls
    
    def add_url(self, url: str):
        """Mark URL as scraped"""
        self.urls.add(url)
        try:
            with open(self.filepath, 'a', encoding='utf-8') as f:
                f.write(url + '\n')
        except Exception as e:
            print(f" Warning saving URL: {e}")
    
    def add_urls(self, urls: list):
        """Mark multiple URLs as scraped"""
        for url in urls:
            self.add_url(url)


def random_delay():
    """Add random delay between requests to avoid blocking"""
    delay = random.uniform(config.DELAY_MIN, config.DELAY_MAX)
    time.sleep(delay)


def get_random_user_agent() -> str:
    """Return a random user agent from config"""
    return random.choice(config.USER_AGENTS)


def get_timestamp() -> str:
    """Get current timestamp in ISO format"""
    return datetime.now().isoformat()


def get_date_string() -> str:
    """Get current date as YYYY_MM_DD for filenames"""
    return datetime.now().strftime("%Y_%m_%d")


def ensure_output_folder():
    """Create output folder if it doesn't exist"""
    if not os.path.exists(config.OUTPUT_FOLDER):
        os.makedirs(config.OUTPUT_FOLDER)
        print(f"✓ Created output folder: {config.OUTPUT_FOLDER}")


def normalize_text(text: str) -> str:
    """Normalize text for better matching"""
    if not text:
        return ""
    return text.strip().lower()


def clean_url(url: str) -> str:
    """Clean and normalize URL"""
    return url.split('?')[0].split('#')[0].strip()


def print_header(text: str):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_article_info(article_data: dict):
    """Print formatted article information"""
    print(f"\nMATCHED: {article_data['title'][:80]}...")
    print(f"  Keyword: {article_data['matched_keyword']}")
    print(f"  Source: {article_data['source']}")
    print(f"  URL: {article_data['url'][:80]}...")


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length"""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def parse_article_year(date_string: str) -> Optional[int]:
    """
    Parse year from various RSS date formats.
    Returns year as integer, or None if parsing fails.
    
    Supports formats:
    - ISO 8601: 2024-01-15T10:30:00Z
    - RFC 822/2822: Mon, 15 Jan 2024 10:30:00 +0000
    - Simple dates: 2024-01-15, 15/01/2024
    """
    if not date_string:
        return None
    
    # Try to extract 4-digit year using regex
    year_match = re.search(r'\b(20\d{2})\b', date_string)
    if year_match:
        year = int(year_match.group(1))
        # Sanity check: year should be reasonable (2000-2030)
        if 2000 <= year <= 2030:
            return year
    
    return None


def is_article_in_date_range(date_string: str, start_year: Optional[int] = None, end_year: Optional[int] = None) -> bool:
    """
    Check if article's publication date is within the specified year range.
    
    Args:
        date_string: Publication date from RSS feed
        start_year: Earliest year to include (None = no lower bound)
        end_year: Latest year to include (None = no upper bound)
    
    Returns:
        True if article is within range (or if date filtering disabled)
    """
    # If both are None, date filtering is disabled
    if start_year is None and end_year is None:
        return True
    
    year = parse_article_year(date_string)
    
    # If we can't parse the year, include the article by default
    # (don't exclude articles just because date parsing failed)
    if year is None:
        return True
    
    # Check year bounds
    if start_year and year < start_year:
        return False
    if end_year and year > end_year:
        return False
    
    return True
