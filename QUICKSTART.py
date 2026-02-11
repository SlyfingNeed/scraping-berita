"""
QUICK START GUIDE
Indonesian News Keyword-Based Scraper
=====================================

STEP 1: INSTALL DEPENDENCIES
----------------------------
Open terminal in this folder and run:

    pip install -r requirements.txt

STEP 2: CONFIGURE KEYWORDS
--------------------------
Edit config.py and set your keywords:

    KEYWORDS = ["bitcoin", "crypto", "ai", "startup"]

STEP 3: RUN THE SCRAPER
-----------------------

Single run:
    python main.py

Continuous mode (runs every 10 minutes):
    python main.py --continuous

Export to XLSX instead of CSV:
    python main.py --format xlsx

WHAT IT DOES
------------
1. Fetches RSS feeds from 10+ Indonesian news sources
2. Scrapes articles that match your keywords
3. Extracts clean article text
4. Saves to CSV/XLSX in output/ folder

OUTPUT FILE
-----------
Location: output/filtered_news_YYYY_MM_DD.csv

Columns:
- title: Article title
- content: Full clean text
- matched_keyword: Keywords found
- source: News source
- category: Article category
- published_date: Publication date
- url: Article URL
- scraped_at: When scraped

CUSTOMIZATION
-------------
All settings in config.py:

- KEYWORDS: Words to search for
- OUTPUT_FORMAT: "csv" or "xlsx"
- CHECK_INTERVAL: Seconds between cycles (continuous mode)
- RSS_FEEDS: News sources to scrape

ADDING NEWS SOURCES
-------------------
Edit config.py, add to RSS_FEEDS:

    "Source Name": "https://site.com/rss",

EXPECTED PERFORMANCE
--------------------
- Scans: 1000-3000 articles/day
- Saves: 20-200 matched articles/day (depends on keywords)
- Speed: 2-5 seconds per article

RUNNING 24/7
------------

Windows (Task Scheduler):
1. Open Task Scheduler
2. Create task that runs: python main.py --continuous
3. Set trigger: At startup

Linux (screen):
    screen -S scraper
    python main.py --continuous
    # Press Ctrl+A then D to detach

TROUBLESHOOTING
---------------

No matches?
- Check keywords are spelled correctly
- Try broader keywords
- Verify RSS feeds are working

Errors?
- Check internet connection
- Some sites may block automated requests
- Try again with random delays (already built-in)

File won't open in Excel?
- File uses UTF-8 encoding
- Should work in Excel 2013+
- Try --format xlsx for better Excel compatibility

TESTING INDIVIDUAL COMPONENTS
------------------------------

Test RSS collector:
    python rss_collector.py

Test article scraper:
    python article_scraper.py

Test keyword filter:
    python keyword_filter.py

Test exporter:
    python exporter.py

NEED HELP?
----------
Check README.md for full documentation
"""

if __name__ == "__main__":
    print(__doc__)
