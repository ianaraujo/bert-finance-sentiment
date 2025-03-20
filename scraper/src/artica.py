from datetime import datetime
from typing import List, Dict, Optional

from ..base import BaseScraper
from services.database import DatabasePipeline, DummyPipeline


class ArticaScraper(BaseScraper):

    def __init__(self, pipeline: DatabasePipeline) -> None:
        super().__init__()

        self.gestora: str = "Ártica Capital"
        self.base_url: str = "https://artica.capital/cartas-asset/"
    
        self.letters: List[Dict] = []  # initialize as empty list
        self.pipeline = pipeline

    def get_letter_text(self, url: str) -> str:
        soup = self.parse(url)
        
        section = soup.find_all("div", class_="elementor-section-wrap")[1]
        text = section.get_text(separator=" ", strip=True) if section else None

        return text

    def scrape(self, limit: Optional[int] = None) -> List[Dict]:
        soup = self.parse(self.base_url)
        items = soup.find_all("div", class_="jet-listing-grid__item")

        for item in items:
            time_tag = item.find("time")
            date_text = time_tag.get_text(strip=True) if time_tag else None
            
            if date_text:
                date = datetime.strptime(date_text, "%d/%m/%Y")
                date_text = date.strftime("%Y-%m-%d")

            title_span = None

            for span in item.find_all("span", class_="jet-listing-dynamic-link__label"):
                if "Ler mais" not in span.get_text():
                    title_span = span
                    break

            title = title_span.get_text(strip=True) if title_span else None

            href = None
            
            for a in item.find_all("a", class_="jet-listing-dynamic-link__link", href=True):
                span = a.find("span", class_="jet-listing-dynamic-link__label")
                
                if span and "Ler mais" in span.get_text():
                    href = a["href"]
                    break

            letter = {
                "gestora": self.gestora,
                "title": title,
                "date": date_text,
                "url": href,
                "content": self.get_letter_text(href)
            }

            self.letters.append(letter)

            if limit and len(self.letters) >= limit:
                return self.letters # for testing purposes

        return self.letters
    

if __name__ == "__main__":
    pipeline = DummyPipeline()
    scraper = ArticaScraper(pipeline)
    letters = scraper.scrape(limit=None)

    print(len(letters))