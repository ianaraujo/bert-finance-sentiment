from typing import List, Dict, Optional

from ..utils import extract_date
from ..base import BaseScraper
from services.database import DatabasePipeline, DummyPipeline
from services.extractor import PDFTextService


pdf = PDFTextService()


class AlaskaScraper(BaseScraper):

    def __init__(self, pipeline: DatabasePipeline) -> None:
        super().__init__()

        self.gestora: str = "Alaska Asset Management"
        self.base_url: str = "https://www.alaska-asset.com.br/cartas/"
    
        self.letters: List[Dict] = []  # initialize as empty list
        self.pipeline = pipeline

    def scrape(self, limit: Optional[int] = None) -> List[Dict]:
        soup = self.parse(self.base_url)
        
        entries = soup.find_all("div", class_="entry")
        items = [(entry.find("div", class_="title"), entry.find("div", class_="body")) for entry in entries]

        for title_tag, body_tag in items:
            title_text = title_tag.find("h3").get_text(strip=True)

            for a in body_tag.find_all("a"):
                href = a.get("href")
                
                if "Mensais" in href:
                    continue
                    
                body_text = a.get_text(strip=True)
                title = " - ".join([title_text, body_text])         

                content = pdf.extract_text(href)

                letter = {
                    "gestora": self.gestora,
                    "title": title,
                    "date": extract_date(title),
                    "url": href,
                    "content": content
                }

                self.letters.append(letter)

                if limit and len(self.letters) >= limit:
                    return self.letters # for testing purposes

        return self.letters
    

if __name__ == "__main__":
    pipeline = DummyPipeline()
    scraper = AlaskaScraper(pipeline)
    letters = scraper.scrape(limit=None)

    print(len(letters))