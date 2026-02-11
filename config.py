KEYWORDS = [
    "ESG",
    "Sektor Energi",
    "Rupiah",
    "IHSG",
    "Inflasi",
    "Minyak",
    "Emas",
    "Saham",
    "Harga Minyak",
    "Harga Komoditas"
]

OUTPUT_FORMAT = "csv"  
OUTPUT_FOLDER = "output"
OUTPUT_FILENAME_PREFIX = "filtered_news"

CHECK_INTERVAL = 600  
MAX_RETRIES = 3
REQUEST_TIMEOUT = 15
DELAY_MIN = 1  
DELAY_MAX = 3

PRE_FILTER_MIN_DESCRIPTION_LENGTH = 100  

DATE_FILTER_START_YEAR = 2023  
DATE_FILTER_END_YEAR = 2026  

RSS_FEEDS = {

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

    # Kontan
    "Kontan Investasi": "https://investasi.kontan.co.id/rss",
    "Kontan Keuangan": "https://keuangan.kontan.co.id/rss",

    # Antara News
    "Antara Ekonomi": "https://www.antaranews.com/rss/ekonomi",
    "Antara Tekno": "https://www.antaranews.com/rss/tekno",
    "Antara Terkini": "https://www.antaranews.com/rss/terkini",

    # Tribunnews
    "Tribunnews": "https://www.tribunnews.com/rss",

    # Okezone
    "Okezone Economy": "https://sindikasi.okezone.com/index.php/rss/0/RSS2.0",
    "Okezone Techno": "https://sindikasi.okezone.com/index.php/rss/16/RSS2.0",
    "Okezone Finance": "https://sindikasi.okezone.com/index.php/rss/11/RSS2.0",

    # Katadata
    "Katadata": "https://katadata.co.id/rss",

    # Republika
    "Republika": "https://www.republika.co.id/rss",

}

# Sites with broken direct RSS — will be searched via Google News with keywords
GOOGLE_NEWS_SITES = [
    "detik.com",
    "kompas.com",
    "bisnis.com",
    "liputan6.com",
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
]

SCRAPED_URLS_FILE = "scraped_urls.txt"
MAX_URLS_IN_MEMORY = 10000 
