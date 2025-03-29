import time
import requests
from bs4 import BeautifulSoup
from typing import Optional

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Accept": "application/pdf,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
}


class BaseScraper:

    MAX_RETRIES = 3

    def __init__(self, headers=None) -> None:
        self.headers = headers or HEADERS

        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def should_skip(self, title: Optional[str]) -> bool:
        if not hasattr(self, 'pipeline') or not hasattr(self, 'gestora'):
            raise AttributeError("Scraper must have 'pipeline' and 'gestora' attributes.")

        if not title:
            return True
        
        exists, _, content = self.pipeline.exists(self.gestora, title)
        
        return exists and content # skip if content exists

    def parse(self, url: str, verify: bool = True) -> Optional[BeautifulSoup]:
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                response = self.session.get(url, verify=verify, timeout=10)
                response.raise_for_status()
                
                return BeautifulSoup(response.content, "html.parser")

            except requests.RequestException as e:
                if attempt < self.MAX_RETRIES:
                    sleep_time = 2 ** (attempt - 1)
                    print(f"[INFO] Retrying in {sleep_time} seconds...")
                    
                    time.sleep(sleep_time)
                
                else:
                    print(f"[ERROR] All {self.MAX_RETRIES} attempts failed for {url}")

                    return None

    def scrape(self):
        raise NotImplementedError(
            "O método scrape() deve ser implementado pela subclasse.")
