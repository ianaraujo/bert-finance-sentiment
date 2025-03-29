from typing import List, Dict, Optional

from ..utils import extract_date
from ..base import BaseScraper
from services.database import DatabasePipeline, DummyPipeline
from services.extractor import PDFTextService


pdf = PDFTextService()


class AlphaKeyScraper(BaseScraper):

    def __init__(self, pipeline: DatabasePipeline) -> None:
        super().__init__()

        self.gestora: str = "Alpha Key"
        self.base_url: str = "https://alphakey.com.br/fundos/alpha-key-lb-i-fic-fim/"
    
        self.letters: List[Dict] = []  # initialize as empty list
        self.pipeline = pipeline

    def scrape(self, limit: Optional[int] = None) -> List[Dict]:
        soup = self.parse(self.base_url)
        section = soup.find("section", class_="fund-docs")
        row = section.find("div", class_="row")

        children = row.find_all("div", class_="col-md-4")
        items = [a for child in children[1:] for a in child.find_all("a", class_="fund-doc")]

        for item in items:
            href = item["href"]
            title = item.find("h5").get_text(strip=True)

            if self.should_skip(title):
                continue

            date_text = item.find("span").get_text(strip=True)
            date = extract_date(date_text)

            text = pdf.extract_text(href)
            
            if not text:
                continue

            letter = {
                "gestora": self.gestora,
                "title": title,
                "date": date,
                "url": href,
                "content": text
            }

            self.letters.append(letter)

            if limit and len(self.letters) >= limit:
                return self.letters # for testing purposes

        return self.letters
    

if __name__ == "__main__":
    pipeline = DummyPipeline()
    scraper = AlphaKeyScraper(pipeline)
    letters = scraper.scrape(limit=None)

    print(len(letters))