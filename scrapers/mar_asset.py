import re
import requests
from bs4 import BeautifulSoup

from main import DatabasePipeline
from .base import BaseScraper, headers


class MarAssetScraper(BaseScraper):
    def __init__(self, pipeline: DatabasePipeline):
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

    def scrape(self):
        response = requests.get(self.base_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        letters = []

        for div in soup.find_all("div", class_="document--term--item"):
            h4 = div.find("h4")

            if 'Cartas' != h4.get_text():
                continue

            media_div = div.find_all("div", class_="media")

            for media in media_div:
                a = media.find("a", href=True)
                href = a["href"]
                title = a.get("title", "").strip()

                if self.pipeline.exists(self.gestora, title):
                    continue
                
                letter = {
                    "gestora": self.gestora,
                    "title": title,
                    "date": self.transform_date(title),
                    "url": href,
                    "content": ""
                }

                letters.append(letter)

        return letters


if __name__ == "__main__":
    scraper = MarAssetScraper()
    letters = scraper.scrape()

    print(letters)
