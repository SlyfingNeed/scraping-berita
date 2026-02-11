# Indonesian News Scraper

A production-grade Python scraper that collects Indonesian news articles based on specific keywords from multiple sources and exports them to CSV/XLSX.

## Features

✅ **Keyword-focused**: Only collects articles matching your target keywords  
✅ **Multi-source**: Scrapes from 10+ Indonesian news sources via RSS  
✅ **Clean extraction**: Uses trafilatura + BeautifulSoup for article content  
✅ **Deduplication**: Prevents collecting the same article twice  
✅ **CSV/XLSX export**: Export to your preferred format  
✅ **Anti-blocking**: Random delays, rotating user-agents  
✅ **Cron-ready**: Can run continuously or as scheduled job  

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Keywords

Edit `config.py` to set your target keywords:

```python
KEYWORDS = [
    "bitcoin",
    "crypto",
    "suku bunga",
    "inflasi",
    "IHSG",
    "AI",
    "startup"
]
```

### 3. Run Scraper

**Single run:**
```bash
python main.py
```

**Continuous mode (runs every 10 minutes):**
```bash
python main.py --continuous
```

**Override output format:**
```bash
python main.py --format xlsx
```

## Project Structure

```
scraping-berita/
├── main.py              # Main orchestration
├── config.py            # Configuration (keywords, sources, settings)
├── rss_collector.py     # RSS feed collection
├── article_scraper.py   # Article content extraction
├── keyword_filter.py    # Keyword matching logic
├── exporter.py          # CSV/XLSX export
├── utils.py             # Deduplication & helpers
├── requirements.txt     # Python dependencies
├── scraped_urls.txt     # Tracks scraped URLs (auto-generated)
└── output/              # Output folder (auto-generated)
    └── filtered_news_YYYY_MM_DD.csv
```

## Configuration

All settings are in `config.py`:

### Keywords
```python
KEYWORDS = ["bitcoin", "crypto", "ai", "startup"]
```

### Output Settings
```python
OUTPUT_FORMAT = "csv"  # Options: "csv" or "xlsx"
OUTPUT_FOLDER = "output"
```

### Scraping Settings
```python
CHECK_INTERVAL = 600  # seconds (for continuous mode)
MAX_RETRIES = 3
REQUEST_TIMEOUT = 15
DELAY_MIN = 1  # random delay between requests
DELAY_MAX = 3
```

### News Sources

The scraper includes RSS feeds from:
- **Detik** (Finance, News, Inet)
- **Kompas** (Money, Tekno, News)
- **Tempo** (Bisnis, Teknologi, News)
- **CNN Indonesia** (Ekonomi, Teknologi)
- **CNBC Indonesia** (Market, Tech, News)
- **Bisnis Indonesia**
- **Kontan** (News, Keuangan)
- **Liputan6** (Bisnis, Tekno)
- **Tribunnews** (Bisnis, Techno)
- **Antara News** (Ekonomi, Tekno)

To add/remove sources, edit `RSS_FEEDS` in `config.py`.

## Output Format

Each row contains:

| Column | Description |
|--------|-------------|
| title | Article title |
| content | Clean full article text |
| matched_keyword | Keywords that triggered match |
| source | News source name |
| category | Article category (if available) |
| published_date | Publication date |
| url | Article URL |
| scraped_at | Timestamp when scraped |

Files are named: `filtered_news_YYYY_MM_DD.csv`

## How It Works

1. **Fetch RSS Feeds**: Collects article URLs from all configured sources
2. **Check Duplicates**: Skips URLs already scraped (tracked in `scraped_urls.txt`)
3. **Scrape Content**: Extracts clean article text using trafilatura/BeautifulSoup
4. **Keyword Filter**: Checks if title OR content contains target keywords
5. **Save Results**: Appends matched articles to CSV/XLSX

## Keyword Matching

- **Case-insensitive**: "Bitcoin" matches "bitcoin"
- **Partial match**: "Bitcoin Indonesia" matches "bitcoin"
- **Title OR content**: Matches if keyword appears in either
- **Multiple keywords**: Saves all matched keywords (comma-separated)

Example:
```python
keyword = "bitcoin"
✓ Matches: "Bitcoin", "bitcoin", "Bitcoin Naik"
✓ Matches in title: "Harga Bitcoin Melonjak"
✓ Matches in content: Article mentioning "...bitcoin..."
```

## Performance

**Expected metrics:**
- RSS feeds: ~1000-3000 articles/day scanned
- Filtered results: ~20-200 articles/day saved (depends on keywords)
- Processing speed: ~2-5 seconds per article
- Memory usage: Low (~50-100 MB)

## Running 24/7 on Server

### Option 1: Screen (Linux)
```bash
screen -S scraper
python main.py --continuous
# Press Ctrl+A, then D to detach
```

Resume: `screen -r scraper`

### Option 2: Systemd Service (Linux)

Create `/etc/systemd/system/news-scraper.service`:
```ini
[Unit]
Description=Indonesian News Scraper
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/scraping-berita
ExecStart=/usr/bin/python3 main.py --continuous
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable news-scraper
sudo systemctl start news-scraper
sudo systemctl status news-scraper
```

### Option 3: Cron (Runs every hour)
```bash
crontab -e
# Add:
0 * * * * cd /path/to/scraping-berita && python main.py
```

### Option 4: Windows Task Scheduler
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily, repeat every 1 hour
4. Action: Start program `python.exe`
5. Arguments: `main.py --continuous`
6. Start in: `C:\Users\seva\scraping-berita`

## Adding a New Source

Edit `config.py` and add to `RSS_FEEDS`:

```python
RSS_FEEDS = {
    # ... existing sources ...
    "New Source Name": "https://newssite.com/rss",
}
```

Most Indonesian news sites provide RSS feeds at:
- `/rss`
- `/feed`
- `/rss.xml`

## Troubleshooting

**No articles matched:**
- Check if keywords are correct (case-insensitive)
- Try broader keywords
- Verify RSS feeds are working

**Scraping errors:**
- Some sites may block automated access
- Random delays and user-agents should help
- RSS feeds are more reliable than homepage scraping

**File encoding issues:**
- Output uses UTF-8 with BOM (`utf-8-sig`)
- Should display correctly in Excel

**Memory issues:**
- URL tracker limits to 10,000 URLs
- Older URLs are automatically removed

## Tech Stack

- **Python 3.8+**
- **requests**: HTTP requests
- **feedparser**: RSS parsing
- **trafilatura**: Article extraction (primary)
- **beautifulsoup4**: HTML parsing (fallback)
- **pandas**: Data export
- **openpyxl**: Excel support

## License

MIT License - Free to use and modify

## Support

For issues or questions:
1. Check `config.py` settings
2. Run with verbose output to see errors
3. Test individual components (each file has `if __name__ == "__main__"` tests)

---

**Author**: Built by senior Python data engineer  
**Purpose**: Topic monitoring and research for Indonesian news  
**Last Updated**: February 2026
