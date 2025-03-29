import re
from typing import Optional

from ..base import BaseScraper
from services.database import DatabasePipeline
from services.extractor import PDFTextService


pdf = PDFTextService()

class MarAssetScraper(BaseScraper):
    
    def __init__(self, pipeline: DatabasePipeline):
        super().__init__()
        self.gestora = "Mar Asset"
        self.base_url = "https://www.marasset.com.br/conteudo-mar/"
        self.pipeline = pipeline

    def transform_date(self, title: str):
        meses = {
            'Jan.': '01',
            'Fev.': '02',
            'Mar.': '03',
            'Abr.': '04',
            'Mai.': '05',
            'Jun.': '06',
            'Jul.': '07',
            'Ago.': '08',
            'Set.': '09',
            'Out.': '10',
            'Nov.': '11',
            'Dez.': '12'
        }

        regex = r'^(' + '|'.join(meses.keys()) + r')\s+(\d{2,4})'
        match = re.match(regex, title.strip())

        if match:
            mes_abrev, ano_str = match.groups()
            mes = meses[mes_abrev]

            if len(ano_str) == 2:
                ano = int("20" + ano_str)
            else:
                ano = int(ano_str)

            return f"{ano:04d}-{mes}-01"  # retorna no formato YYYY-MM-DD

        return None

    def scrape(self, limit: Optional[int] = None):
        soup = self.parse(self.base_url)

        letters = []

        for div in soup.find_all("div", class_="document--term--item"):
            h4 = div.find("h4")

            if 'Cartas' != h4.get_text():
                continue

            media_div = div.find_all("div", class_="media")

            for media in media_div:
                a = media.find("a", href=True)
                pdf_url = a["href"]
                title = a.get("title", "").strip()

                if self.should_skip(title):
                    continue

                try:
                    text = pdf.extract_text(pdf_url)
                 
                except Exception as e:
                    print(f"Failed to process {pdf_url}: {str(e)}")
                
                letter = {
                    "gestora": self.gestora,
                    "title": title,
                    "date": self.transform_date(title),
                    "url": pdf_url,
                    "content": text
                }

                letters.append(letter)

                if limit and len(letters) >= limit:
                    return letters # for testing purposes

        return letters


if __name__ == "__main__":
    scraper = MarAssetScraper()
    letters = scraper.scrape()

    print(letters)
