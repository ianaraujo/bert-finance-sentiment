import re
from random import sample
from typing import List, Dict, Optional

from ..base import BaseScraper
from ..utils import extract_date
from services.database import DatabasePipeline, DummyPipeline
from services.extractor import PDFTextService
import time


pdf = PDFTextService()


class DynamoScraper(BaseScraper):

    def __init__(self, pipeline: DatabasePipeline) -> None:
        super().__init__()

        self.gestora: str = "Dynamo"
        self.base_url: str = "https://www.dynamo.com.br/cartas-dynamo"
    
        self.letters: List[Dict] = []  # initialize as empty list
        self.pipeline = pipeline

    def scrape(self, limit: Optional[int] = None) -> List[Dict]:
        page = 1
        has_content = True

        while has_content:
            url = self.base_url

            if page > 1:
                url = f"{self.base_url}?page={page}"
            
            for attempt in range(3):
                try:
                    soup = self.parse(url)
                    break
                
                except Exception as e:
                    if attempt == 2:
                        raise e
                    
                    time.sleep(10)

            items = soup.find_all("div", class_="block")

            if not items:
                break

            for item in items:
                span = item.find("span", class_="carta-n").find("a")
                pdf_url = "https://www.dynamo.com.br/" + span["href"]

                title = item.find("h3").get_text(strip=True)

                if self.should_skip(title):
                    continue
                
                text = pdf.extract_text(pdf_url, verbose=False)
                text = text.replace("-\n", " ").strip() if text else None

                if not text:
                    continue

                pattern = r"Rio de Janeiro,\s+(.*?\d{4})"
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
                    "url": pdf_url,
                    "content": text
                }

                self.letters.append(letter)

                if limit and len(self.letters) >= limit:
                    return self.letters
                
            page += 1

        return self.letters
    

if __name__ == "__main__":
    pipeline = DummyPipeline()
    scraper = DynamoScraper(pipeline)
    letters = scraper.scrape(limit=None)
    
    print(len(letters))