from typing import List, Dict, Optional

from ..utils import extract_date
from ..base import BaseScraper
from services.database import DatabasePipeline, DummyPipeline
from services.extractor import PDFTextService


pdf = PDFTextService()


class KapitaloScraper(BaseScraper):

    def __init__(self, pipeline: DatabasePipeline) -> None:
        super().__init__()

        self.gestora: str = "Kapitalo"
        self.base_url: str = "https://www.kapitalo.com.br/carta-do-gestor/kapa-e-zeta/"
    
        self.letters: List[Dict] = []  # initialize as empty list
        self.pipeline = pipeline

    def scrape(self, limit: Optional[int] = None) -> List[Dict]:
        soup = self.parse(self.base_url)
        section = soup.find("ul", class_="cartasGestor")
        items = section.find_all("li")

        for item in items:
            href = item.find("a")["href"]

            title_text = item.find("p").get_text(strip=True)
            month_text = item.find("p", class_="date").get_text(strip=True)
            date_text = extract_date(href.split("/")[-1].split(".")[0])

            text = pdf.extract_text(href)

            if not date_text:
                date_text = extract_date(text[:100])

                if not date_text:
                    continue

            title = f"{title_text} - {month_text} {date_text[0:4]}"

            if self.should_skip(title):
                continue

            letter = {
                "gestora": self.gestora,
                "title": title,
                "date": date_text,
                "url": href,
                "content": text
            }

            self.letters.append(letter)

            if limit and len(self.letters) >= limit:
                return self.letters # for testing purposes

        return self.letters
    

if __name__ == "__main__":
    pipeline = DummyPipeline()
    scraper = KapitaloScraper(pipeline)
    letters = scraper.scrape(limit=None)

    print(len(letters))