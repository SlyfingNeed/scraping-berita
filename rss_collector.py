import feedparser
import requests
import re
from urllib.parse import urlparse, parse_qs, unquote
from typing import List, Dict
from bs4 import BeautifulSoup
import config
from utils import random_delay, get_random_user_agent, print_header


def _build_gnews_url(keyword: str, start_year: int = None, end_year: int = None, site: str = None) -> str:
    """
    Build a Google News RSS search URL for a keyword with optional date range and site.
    
    Examples:
        ESG             → q=ESG+after:2023-01-01+before:2026-12-31
        Sektor Energi   → q=%22Sektor+Energi%22+after:2023-01-01+before:2026-12-31
        site:detik.com  → q=site:detik.com+ESG+after:2023-01-01+before:2026-12-31
    """
    parts = []

    # Site restriction (if any)
    if site:
        parts.append(f"site:{site}")

    # Keyword — wrap multi-word in quotes for exact match
    if ' ' in keyword:
        parts.append('%22' + keyword.replace(' ', '+') + '%22')
    else:
        parts.append(keyword)

    # Date range
    if start_year:
        parts.append(f"after:{start_year}-01-01")
    if end_year:
        parts.append(f"before:{end_year}-12-31")

    q = '+'.join(parts)
    return f"https://news.google.com/rss/search?q={q}&hl=id&gl=ID&ceid=ID:id"


class RSSCollector:
    """Collects article URLs and metadata from RSS feeds"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': get_random_user_agent(),
            'Accept': 'application/rss+xml, application/xml, text/xml, */*',
            'Accept-Language': 'id-ID,id;q=0.9,en;q=0.7',
        })
        self.collected_articles = []

    @staticmethod
    def _resolve_google_news_url(gnews_url: str) -> str:
        """
        Google News RSS wraps real article URLs in a redirect.
        Extract the actual article URL from the Google News link.
        """
        # Google News URLs look like:
        # https://news.google.com/rss/articles/CBMi...?oc=5
        # The actual URL is sometimes in the link itself after redirect,
        # but we can also just return the gnews_url and let requests follow redirects.
        # For RSS entries, the 'link' field sometimes contains the direct URL already.
        if 'news.google.com' not in gnews_url:
            return gnews_url
        return gnews_url  # We'll resolve during scraping via redirects

    @staticmethod
    def _extract_source_from_gnews(entry, feed_source_name: str) -> str:
        """
        Extract the real source name from a Google News RSS entry.
        Google News entries have a <source> tag with the real publisher.
        """
        # feedparser stores the source in entry.source.title
        source = getattr(entry, 'source', None)
        if source and hasattr(source, 'title'):
            return source.title
        # Fallback: extract from feed source name
        return feed_source_name.replace(' (via Google News)', '')

    def _is_google_news_feed(self, feed_url: str) -> bool:
        return 'news.google.com' in feed_url

    def fetch_rss_feed(self, feed_url: str, source_name: str) -> List[Dict]:
        """Fetch and parse a single RSS feed."""
        articles = []
        is_gnews = self._is_google_news_feed(feed_url)

        try:
            response = self.session.get(
                feed_url,
                timeout=config.REQUEST_TIMEOUT,
                allow_redirects=True
            )
            response.raise_for_status()

            feed = feedparser.parse(response.content)

            if not feed.entries:
                print(f"  ⚠ {source_name}: 0 articles (empty feed)")
                return articles

            for entry in feed.entries:
                url = entry.get('link', '').strip()
                title = entry.get('title', '').strip()

                if not title or not url:
                    continue

                # Clean HTML from title (some feeds wrap titles in tags)
                if '<' in title:
                    title = BeautifulSoup(title, 'html.parser').get_text(strip=True)

                # Determine real source for Google News entries
                real_source = (
                    self._extract_source_from_gnews(entry, source_name)
                    if is_gnews
                    else source_name
                )

                # Get description/summary and clean HTML
                description = entry.get('summary', '').strip()
                if description and '<' in description:
                    description = BeautifulSoup(description, 'html.parser').get_text(strip=True)

                article = {
                    'title': title,
                    'url': url,
                    'published_date': entry.get('published', ''),
                    'category': entry.get('category', ''),
                    'source': real_source,
                    'description': description,
                    'is_gnews': is_gnews,
                }
                articles.append(article)

            print(f"  ✓ {source_name}: {len(articles)} articles")

        except requests.exceptions.Timeout:
            print(f"  ⚠ {source_name}: Timeout")
        except requests.exceptions.ConnectionError:
            print(f"  ⚠ {source_name}: Connection error")
        except requests.exceptions.RequestException as e:
            print(f"  ⚠ {source_name}: HTTP {str(e)[:50]}")
        except Exception as e:
            print(f"  ⚠ {source_name}: Parse error - {str(e)[:50]}")

        return articles

    def collect_all_feeds(self) -> List[Dict]:
        """Collect articles from all configured RSS feeds + Google News keyword feeds."""
        all_articles = []

        # ── 1. Direct RSS feeds ──
        print_header("COLLECTING DIRECT RSS FEEDS")
        rss_ok = 0
        rss_fail = 0

        for source_name, feed_url in config.RSS_FEEDS.items():
            articles = self.fetch_rss_feed(feed_url, source_name)
            if articles:
                rss_ok += 1
            else:
                rss_fail += 1
            all_articles.extend(articles)
            random_delay()

        print(f"\n  Direct RSS — OK: {rss_ok} | Failed: {rss_fail}")

        # ── 2. Google News keyword-based feeds ──
        print_header("COLLECTING GOOGLE NEWS (KEYWORD SEARCH)")
        start_y = getattr(config, 'DATE_FILTER_START_YEAR', None)
        end_y   = getattr(config, 'DATE_FILTER_END_YEAR', None)
        gnews_ok = 0
        gnews_fail = 0

        # 2a. Per-keyword search (all sites)
        for keyword in config.KEYWORDS:
            feed_url = _build_gnews_url(keyword, start_year=start_y, end_year=end_y)
            source_name = f"GNews: {keyword}"
            articles = self.fetch_rss_feed(feed_url, source_name)
            if articles:
                gnews_ok += 1
            else:
                gnews_fail += 1
            all_articles.extend(articles)
            random_delay()

        # 2b. Per-site search (for sites with broken direct RSS)
        gnews_sites = getattr(config, 'GOOGLE_NEWS_SITES', [])
        for site in gnews_sites:
            # Use top-5 keywords joined with OR for each site
            kw_parts = []
            for kw in config.KEYWORDS[:6]:
                if ' ' in kw:
                    kw_parts.append(f'"%22{kw}%22"'.replace('%22', '%22'))
                else:
                    kw_parts.append(kw)
            # Build site-specific URL with combined keywords
            combined = '+OR+'.join(
                '%22' + kw.replace(' ', '+') + '%22' if ' ' in kw else kw
                for kw in config.KEYWORDS[:6]
            )
            q_parts = [f"site:{site}", combined]
            if start_y:
                q_parts.append(f"after:{start_y}-01-01")
            if end_y:
                q_parts.append(f"before:{end_y}-12-31")
            feed_url = f"https://news.google.com/rss/search?q={'+'.join(q_parts)}&hl=id&gl=ID&ceid=ID:id"
            source_name = f"GNews: {site}"
            articles = self.fetch_rss_feed(feed_url, source_name)
            if articles:
                gnews_ok += 1
            else:
                gnews_fail += 1
            all_articles.extend(articles)
            random_delay()

        print(f"\n  Google News — OK: {gnews_ok} | Failed: {gnews_fail}")

        # ── 3. Deduplicate by URL ──
        seen_urls = set()
        unique_articles = []
        for a in all_articles:
            if a['url'] not in seen_urls:
                seen_urls.add(a['url'])
                unique_articles.append(a)

        print(f"\n  Total articles: {len(all_articles)} | Unique: {len(unique_articles)}")
        self.collected_articles = unique_articles
        return unique_articles

    def get_unique_urls(self) -> List[str]:
        return list(set(a['url'] for a in self.collected_articles))


if __name__ == "__main__":
    collector = RSSCollector()
    articles = collector.collect_all_feeds()
    if articles:
        print("\nSample articles:")
        for article in articles[:5]:
            print(f"  - [{article['source']}] {article['title'][:60]}")
            print(f"    {article['url'][:80]}")
