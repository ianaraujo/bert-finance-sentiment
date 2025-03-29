import re
from typing import List, Dict, Optional

from ..base import BaseScraper
from ..utils import extract_date
from services.database import DatabasePipeline, DummyPipeline
from services.extractor import PDFTextService


pdf = PDFTextService()


class SquadraScraper(BaseScraper):

    def __init__(self, pipeline: DatabasePipeline) -> None:
        super().__init__()

        self.gestora: str = "Squadra Investimentos"
        self.base_url: str = "https://www.squadrainvest.com.br/cartas/"
    
        self.letters: List[Dict] = []  # initialize as empty list
        self.pipeline = pipeline

    def scrape(self, limit: Optional[int] = None) -> List[Dict]:
        soup = self.parse(self.base_url)
       
        items = (
            soup
            .find("div", class_="post-content")
            .find("div", class_="fusion-builder-row")
            .find_all("div", class_="fusion-layout-column")
        )

        for item in items:
            h2_tag = item.find("h2")

            title = h2_tag.get_text(strip=True) if h2_tag else None

            if self.should_skip(title):
                continue

            pdf_url = h2_tag.find("a", href=True)["href"] if h2_tag else None

            text = pdf.extract_text(pdf_url) if pdf_url else None

            pattern = r"Rio de Janeiro,\s+(.*?\d{4})"
            match = re.search(pattern, text)
                
            if match:
                date_str = match.group(1)
                date = extract_date(date_str)
            else:
                date = extract_date(title)

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
                return self.letters # for testing purposes

        return self.letters
    

if __name__ == "__main__":
    pipeline = DummyPipeline()
    scraper = SquadraScraper(pipeline)
    letters = scraper.scrape(limit=None)
    
    print(len(letters))