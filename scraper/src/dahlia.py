import os
import re
import time
from typing import List, Dict, Optional

from ..utils import extract_date
from ..base import BaseScraper
from services.database import DatabasePipeline, DummyPipeline


class DahliaScraper(BaseScraper):

    def __init__(self, pipeline: DatabasePipeline) -> None:
        super().__init__()

        self.gestora: str = "Dahlia Capital"
        self.base_url: str = "https://www.dahliacapital.com.br/"
        
        self.letters: List[Dict] = []  # initialize as empty list
        self.pipeline = pipeline

    def find_posts(self) -> List[str]:
        urls_file = os.path.join(os.path.dirname(__file__), "dahlia_urls.txt")
        
        with open(urls_file, "r") as f:
            urls = [url.strip() for url in f if url.strip()]
                    
        return urls

    def scrape(self, limit: Optional[int] = None) -> List[Dict]:
        posts = self.find_posts()

        for url in posts:
            soup = self.parse(url)

            title = soup.find("h1", attrs={"data-hook": "post-title"}).get_text(strip=True)

            if self.should_skip(title):
                continue

            content = soup.find("div", attrs={"data-id": "content-viewer"})
            text = content.get_text(separator=" ", strip=True)

            pattern = r"São Paulo,\s+(.*?\d{4})"
            match = re.search(pattern, text)
                
            if match:
                date_str = match.group(1)
                date = extract_date(date_str)
            else:
                date = extract_date(text[:100])

            if not date:
                continue

            letter = {
                "gestora": self.gestora,
                "title": title,
                "date": date,
                "url": url,
                "content": text
            }

            self.letters.append(letter)

            if limit and len(self.letters) >= limit:
                return self.letters # for testing purposes
            
            time.sleep(5)

        return self.letters
    

if __name__ == "__main__":
    pipeline = DummyPipeline()
    scraper = DahliaScraper(pipeline)
    letters = scraper.scrape(limit=None)

    print(len(letters))