import re
from typing import List, Dict, Optional


from ..utils import extract_date
from ..base import BaseScraper
from services.database import DatabasePipeline, DummyPipeline
from services.extractor import PDFTextService


pdf = PDFTextService()

class GenoaScraper(BaseScraper):

    def __init__(self, pipeline: DatabasePipeline) -> None:
        super().__init__()

        self.gestora: str = "Genoa Capital"
        self.base_url: str = "https://www.genoacapital.com.br"
        self.letters: List[Dict] = []  # initialize as empty list

        self.pipeline = pipeline

    def scrape(self, limit: Optional[int] = None) -> List[Dict]:
        url = f"{self.base_url}/relatorios.html"
        soup = self.parse(url, verify=True)
        blogs = soup.find_all("section", class_="blog-article-wide")

        for blog in blogs:
            row = blog.find("div", class_="row")
            cols = row.find_all("div")

            title = cols[0].find("h4").get_text().strip()

            if title != 'Carta Mensal':
                continue

            p = cols[1].find("p").get_text().strip()
            date = extract_date(p)

            href = cols[3].find("a")['href']

            if href.endswith('.pdf'):
                pdf_url = f"{self.base_url}/{href}"
                text = pdf.extract_text(pdf_url)

                pattern = r"Cenário([\s\S]*?)GENOA CAPITAL RADAR"
                match = re.search(pattern, text)
                
                if match:
                    extracted_text = match.group(1).strip()

                letter = {
                    "gestora": self.gestora,
                    "title": title,
                    "date": date,
                    "url": pdf_url,
                    "content": extracted_text
                }

                self.letters.append(letter)

                if limit and len(self.letters) >= limit:
                    return self.letters # for testing purposes

        return self.letters
    

if __name__ == "__main__":
    pipeline = DummyPipeline()
    scraper = GenoaScraper(pipeline)
    letters = scraper.scrape(limit=3)

    print(letters)