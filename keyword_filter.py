import re
from typing import Optional, List
import config
from utils import normalize_text


class KeywordFilter:
        
    def __init__(self, keywords: List[str] = None):
        self.keywords = keywords or config.KEYWORDS
        # Normalize keywords for better matching
        self.normalized_keywords = [normalize_text(kw) for kw in self.keywords]
        print(f"✓ Loaded {len(self.keywords)} keywords")
    
    def find_matching_keyword(self, title: str, content: str) -> Optional[str]:

        # Normalize inputs
        title_normalized = normalize_text(title)
        content_normalized = normalize_text(content) if content else ""
        
        # Check each keyword
        for i, keyword in enumerate(self.normalized_keywords):

            if keyword in title_normalized or keyword in content_normalized:
                return self.keywords[i]  # Return original keyword
        
        return None
    
    def find_all_matching_keywords(self, title: str, content: str) -> List[str]:

        title_normalized = normalize_text(title)
        content_normalized = normalize_text(content) if content else ""
        
        matched = []
        
        for i, keyword in enumerate(self.normalized_keywords):
            if keyword in title_normalized or keyword in content_normalized:
                matched.append(self.keywords[i])
        
        return matched
    
    def check_article(self, title: str, content: str, return_all: bool = False) -> Optional[str]:

        if return_all:
            matches = self.find_all_matching_keywords(title, content)
            return ', '.join(matches) if matches else None
        else:
            return self.find_matching_keyword(title, content)
    
    def is_match(self, title: str, content: str = "") -> bool:

        return self.find_matching_keyword(title, content) is not None


if __name__ == "__main__":
    
    filter = KeywordFilter()
    
    print("Testing Keyword Filter")
 
    test_cases = [
        {
            "title": "Harga Bitcoin Naik Signifikan di 2024",
            "content": "Bitcoin mencapai rekor tertinggi...",
            "should_match": True
        },
        {
            "title": "Inflasi Indonesia Turun",
            "content": "Bank Indonesia mengumumkan inflasi turun...",
            "should_match": True
        },
        {
            "title": "Berita Olahraga Terbaru",
            "content": "Timnas Indonesia menang...",
            "should_match": False
        },
        {
            "title": "Perkembangan AI di Dunia",
            "content": "Artificial Intelligence berkembang pesat...",
            "should_match": True
        },
        {
            "title": "Startup Fintech Indonesia Raih Pendanaan",
            "content": "Sebuah startup lokal mendapat investasi...",
            "should_match": True
        },
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['title'][:50]}")
        matched = filter.check_article(test['title'], test['content'])
        
        if matched:
            print(f" MATCHED: {matched}")
        else:
            print(f" NO MATCH")
        
        if (matched is not None) == test['should_match']:
            print(" Test passed")
        else:
            print(" Test failed")
