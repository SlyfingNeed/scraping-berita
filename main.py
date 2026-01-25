from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import csv
import json
from datetime import datetime


class DetikScraper:
    def __init__(self, headless=False):
        print("Init Chrome")
        options = webdriver.ChromeOptions()
        
        if headless:
            options.add_argument('--headless=new')
        
        # config
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # auto install driver chrome
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.wait = WebDriverWait(self.driver, 10)
            print("Browser initialized successfully!")
        except Exception as e:
            print(f"Error initializing browser: {e}")
            raise
        
    def search_news(self, keyword, max_results=10):
        print(f"Searching for: {keyword}")
        
        search_url = f"https://www.detik.com/search/searchall?query={keyword.replace(' ', '+')}"
        self.driver.get(search_url)
        
        time.sleep(3)
        
        articles = []
        
        try:
            article_elements = self.driver.find_elements(By.CSS_SELECTOR, "article")
            
            print(f"Found {len(article_elements)} articles")
            
            for idx, article in enumerate(article_elements[:max_results]):
                try:
                    article_data = self._extract_article_info(article)
                    if article_data:
                        articles.append(article_data)
                        print(f"Scraped article {idx + 1}: {article_data['title'][:50]}...")
                except Exception as e:
                    print(f"Error nyari article {idx + 1}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error: {e}")
        
        return articles
    
    def scrape_category(self, category, max_results=10):
        """
        Scrape cuman dari kategori
        """
        if category == "news":
            url = "https://news.detik.com/"
        else:
            url = f"https://{category}.detik.com/"
        
        print(f"Scraping category: {category}")
        self.driver.get(url)
        time.sleep(3)
        
        articles = []
        
        try:
            article_elements = self.driver.find_elements(By.CSS_SELECTOR, "article, .list-content__item")
            
            for idx, article in enumerate(article_elements[:max_results]):
                try:
                    article_data = self._extract_article_info(article)
                    if article_data:
                        articles.append(article_data)
                        print(f"Scraped article {idx + 1}: {article_data['title'][:50]}...")
                except Exception as e:
                    print(f"Error extracting article {idx + 1}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error finding articles: {e}")
        
        return articles
    
    def _extract_article_info(self, article_element):
        """extract informasi dari 1 artikel"""
        article_data = {
            'title': '',
            'url': '',
            'image': '',
            'timestamp': '',
            'category': ''
        }
        
        try:
            title_element = article_element.find_element(By.CSS_SELECTOR, "h2 a, h3 a, .media__title a, a")
            article_data['title'] = title_element.text.strip()
            article_data['url'] = title_element.get_attribute('href')
        except NoSuchElementException:
            return None
        
        try:
            img_element = article_element.find_element(By.CSS_SELECTOR, "img")
            article_data['image'] = img_element.get_attribute('src')
        except NoSuchElementException:
            pass
        
        try:
            time_element = article_element.find_element(By.CSS_SELECTOR, ".media__date, time, .date")
            article_data['timestamp'] = time_element.text.strip()
        except NoSuchElementException:
            pass
        
        return article_data
    
    def filter_by_keyword(self, articles, keywords):
        """filter keywords"""
        if isinstance(keywords, str):
            keywords = [keywords]
        
        keywords_lower = [k.lower() for k in keywords]
        
        filtered = []
        for article in articles:
            title_lower = article['title'].lower()
            if any(keyword in title_lower for keyword in keywords_lower):
                filtered.append(article)
        
        return filtered
    
    def save_to_csv(self, articles, filename='detik_articles.csv'):
        if not articles:
            print("No articles to save")
            return
        
        keys = articles[0].keys()
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(articles)
        
        print(f"Saved {len(articles)} articles to {filename}")
    
    def save_to_json(self, articles, filename='detik_articles.json'):
        """Save articles to JSON file"""
        if not articles:
            print("No articles to save")
            return
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        
        print(f"Saved {len(articles)} articles to {filename}")
    
    def close(self):
        self.driver.quit()
        print("Browser closed.")


# run
if __name__ == "__main__":
    scraper = DetikScraper(headless=False)

    # Daftar kata kunci 
    esg_energi_keywords = [
        "ESG sektor energi Indonesia",
        "indeks ESG energi",
        "energi terbarukan ESG",
        "perusahaan minyak gas ESG",
        "investasi energi berkelanjutan",
        "transisi energi ESG",
        "Pertamina ESG",
        "PLN keberlanjutan",
        "Medco Energi ESG",
        "perusahaan energi terbarukan Indonesia",
        "saham energi hijau",
        "pengurangan emisi sektor energi",
        "energi karbon netral",
        "laporan keberlanjutan energi",
        "pengungkapan ESG energi",
        "risiko iklim perusahaan energi"
    ]

    geopolitik_energi_keywords = [
        "kebijakan OPEC",
        "sanksi minyak Rusia",
        "embargo energi",
        "krisis minyak Timur Tengah",
        "kebijakan energi AS Tiongkok",
        "keamanan energi geopolitik",
        "geopolitik LNG",
        "politik pipa gas",
        "perang dagang minyak",
        "sanksi energi Rusia",
        "gangguan pasokan gas",
        "larangan ekspor energi",
        "cadangan minyak strategis",
        "kerja sama energi ASEAN",
        "diplomasi energi Indonesia",
        "perdagangan energi terbarukan",
        "tarif energi bersih"
    ]

    kebijakan_pasar_keywords = [
        "volatilitas harga minyak",
        "fluktuasi saham energi",
        "ketidakpastian pasar minyak mentah",
        "guncangan harga gas alam",
        "krisis komoditas energi",
        "pajak karbon sektor energi",
        "skema perdagangan emisi",
        "mandat energi terbarukan",
        "reformasi subsidi bahan bakar fosil",
        "kebijakan transisi energi Indonesia",
        "kebijakan net zero energi",
        "indeks sektor energi",
        "kinerja saham minyak gas",
        "indeks saham energi terbarukan",
        "volatilitas ETF energi",
        "dampak kebijakan iklim energi",
        "regulasi ESG energi",
        "dampak harga karbon energi",
        "taksonomi hijau energi"
    ]

    semua_kata_kunci = (
        esg_energi_keywords +
        geopolitik_energi_keywords +
        kebijakan_pasar_keywords
    )

    print("\nMulai pencarian...")
    semua_artikel = []

    for keyword in semua_kata_kunci:
        print(f"Mencari: {keyword}")
        articles = scraper.search_news(keyword, max_results=10)
        for article in articles:
            article['kategori_pencarian'] = keyword
        semua_artikel.extend(articles)
        time.sleep(2)

    print(f"\nTotal artikel terkumpul: {len(semua_artikel)}")
    scraper.save_to_csv(semua_artikel, "hasil_pencarian_ESG_L_Indonesia.csv")
    scraper.save_to_json(semua_artikel, "hasil_pencarian_ESG_L_Indonesia.json")
    scraper.close()