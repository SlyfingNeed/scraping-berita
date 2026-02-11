KEYWORDS = [
    "ESG-L",
    "Transisi Energi",
    "Energi Terbarukan",
    "Energi Hijau",
    "Sustainability",
    "Keberlanjutan",
    
]

OUTPUT_FORMAT = "csv"  
OUTPUT_FOLDER = "output"
OUTPUT_FILENAME_PREFIX = "filtered_news"

CHECK_INTERVAL = 600  
MAX_RETRIES = 3
REQUEST_TIMEOUT = 15 # seconds
DELAY_MIN = 1  
DELAY_MAX = 3 

RSS_FEEDS = {
    # Detik
    "Detik Finance": "https://rss.detik.com/index.php/detikfinance",
    "Detik News": "https://rss.detik.com/index.php/detikcom",
    "Detik Inet": "https://rss.detik.com/index.php/detikinet",
    
    # Kompas
    "Kompas Money": "https://money.kompas.com/rss",
    "Kompas Tekno": "https://tekno.kompas.com/rss",
    "Kompas News": "https://www.kompas.com/rss",
    
    # Tempo
    "Tempo Bisnis": "https://rss.tempo.co/bisnis",
    "Tempo Teknologi": "https://rss.tempo.co/teknologi",
    "Tempo News": "https://rss.tempo.co/news",
    
    # CNN Indonesia
    "CNN Indonesia Ekonomi": "https://www.cnnindonesia.com/ekonomi/rss",
    "CNN Indonesia Teknologi": "https://www.cnnindonesia.com/teknologi/rss",
    
    # CNBC Indonesia
    "CNBC Indonesia Market": "https://www.cnbcindonesia.com/market/rss",
    "CNBC Indonesia Tech": "https://www.cnbcindonesia.com/tech/rss",
    "CNBC Indonesia News": "https://www.cnbcindonesia.com/news/rss",
    
    # Bisnis Indonesia
    "Bisnis Indonesia": "https://finansial.bisnis.com/rss",
    
    # Kontan
    "Kontan News": "https://www.kontan.co.id/rss/news",
    "Kontan Keuangan": "https://keuangan.kontan.co.id/rss",
    
    # Liputan6
    "Liputan6 Bisnis": "https://www.liputan6.com/bisnis/feed",
    "Liputan6 Tekno": "https://www.liputan6.com/tekno/feed",
    
    # Tribunnews
    "Tribunnews Bisnis": "https://www.tribunnews.com/bisnis/rss",
    "Tribunnews Techno": "https://www.tribunnews.com/techno/rss",
    
    # Antara News
    "Antara Ekonomi": "https://www.antaranews.com/rss/ekonomi",
    "Antara Tekno": "https://www.antaranews.com/rss/tekno",
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
]

SCRAPED_URLS_FILE = "scraped_urls.txt"
MAX_URLS_IN_MEMORY = 10000 
