import requests
import trafilatura
from bs4 import BeautifulSoup
from typing import Optional
import config
from utils import get_random_user_agent, random_delay


class ArticleScraper:
    """Scrapes and extracts clean article content from URLs"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
        })
    
    def scrape_article(self, url: str, retries: int = 0) -> Optional[str]:

        if retries >= config.MAX_RETRIES:
            return None
        
        try:
            # Rotate user agent per request
            self.session.headers['User-Agent'] = get_random_user_agent()
            
            # Fetch page (allow_redirects handles Google News URLs automatically)
            response = self.session.get(
                url, 
                timeout=config.REQUEST_TIMEOUT,
                allow_redirects=True
            )
            response.raise_for_status()

            # Use the final redirected URL for trafilatura
            final_url = response.url
            
            content = self._extract_with_trafilatura(response.text, final_url)
            
            if not content or len(content) < 100:
                content = self._extract_with_beautifulsoup(response.text)
            
            return content
            
        except requests.exceptions.Timeout:
            print(f"  ⚠ Timeout: {url[:60]}...")
            random_delay()
            return self.scrape_article(url, retries + 1)
            
        except requests.exceptions.RequestException as e:
            print(f"  ⚠ Request error: {str(e)[:50]}")
            if retries < config.MAX_RETRIES - 1:
                random_delay()
                return self.scrape_article(url, retries + 1)
            return None
            
        except Exception as e:
            print(f"Scraping error: {str(e)[:50]}")
            return None
    
    def _extract_with_trafilatura(self, html: str, url: str) -> Optional[str]:
        
        try:
            content = trafilatura.extract(
                html,
                include_comments=False,
                include_tables=False,
                no_fallback=False,
                favor_precision=True,
                url=url
            )
            
            if content:
                # Clean up content
                content = content.strip()
                # Remove excessive whitespace
                content = ' '.join(content.split())
                return content
            
        except Exception as e:
            print(f"Trafilatura error: {str(e)[:40]}")
        
        return None
    
    def _extract_with_beautifulsoup(self, html: str) -> Optional[str]:
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 
                                'aside', 'iframe', 'form', 'button']):
                element.decompose()
            
            # Try common article containers
            article_selectors = [
                'article',
                '[class*="article-content"]',
                '[class*="article-body"]',
                '[class*="post-content"]',
                '[class*="entry-content"]',
                '[id*="article"]',
                '[class*="detail"]',
                '[class*="content"]',
                'main',
            ]
            
            content_text = ""
            
            for selector in article_selectors:
                elements = soup.select(selector)
                if elements:
                    # Get text from all matching elements
                    for element in elements:
                        text = element.get_text(separator=' ', strip=True)
                        if len(text) > len(content_text):
                            content_text = text
            
            # If no selector worked, try getting all paragraphs
            if not content_text or len(content_text) < 100:
                paragraphs = soup.find_all('p')
                content_text = ' '.join(p.get_text(strip=True) for p in paragraphs)
            
            # Clean up
            content_text = ' '.join(content_text.split())
            
            if len(content_text) > 100:
                return content_text
            
        except Exception as e:
            print(f"  ⚠ BeautifulSoup error: {str(e)[:40]}")
        
        return None


if __name__ == "__main__":
    # Test article scraper
    scraper = ArticleScraper()
    
    # Test URLs from different sources
    test_urls = [
        "https://www.cnbcindonesia.com/tech/",
        "https://tekno.kompas.com/",
    ]
    
    print("Testing article scraper...\n")
    for url in test_urls:
        print(f"Testing: {url}")
        content = scraper.scrape_article(url)
        if content:
            print(f"Extracted {len(content)} characters")
            print(f"  Preview: {content[:150]}...\n")
        else:
            print("Failed to extract\n")
