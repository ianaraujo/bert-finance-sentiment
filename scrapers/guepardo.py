import re
import requests
from bs4 import BeautifulSoup

from main import DatabasePipeline
from .base import BaseScraper, headers


class GuepardoScraper(BaseScraper):
    def __init__(self, pipeline: DatabasePipeline):
        self.pipeline = pipeline

        self.gestora = "Guepardo"
        self.base_url = "https://www.guepardoinvest.com.br/cartas-da-gestora/"

    def extract_date(self, text: str):
        year_match = re.search(r'(\d{4})', text)

        if year_match:
            year = year_match.group(1)
        else:
            return None

        months = {
            'janeiro': '01',
            'fevereiro': '02',
            'março': '03',
            'abril': '04',
            'maio': '05',
            'junho': '06',
            'julho': '07',
            'agosto': '08',
            'setembro': '09',
            'outubro': '10',
            'novembro': '11',
            'dezembro': '12'
        }

        found_month = None 
        
        for month_name, month_num in months.items():
            if re.search(month_name, text, re.IGNORECASE):
                found_month = month_num
                
                break

        if not found_month:
            tri_match = re.search(r'(\d)º\s*Trimestre', text)
            if tri_match:
                tri = tri_match.group(1)
                found_month = {"1": "01", "2": "04", "3": "07", "4": "10"}.get(tri, "01")
            else:
                found_month = "01"

        return f"{year}-{found_month}-01"

    def scrape(self):
        letters = []
        
        response = requests.get(self.base_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        
        baixar_links = soup.find_all("span", string=lambda s: s and "baixar pdf" in s.lower())
     
        for span in baixar_links:
            href = span.find_previous("a").get("href")
            title_tag = span.find_previous(lambda tag: tag.name in ["h3"] and "Relatório de Gestão" in tag.get_text())
            date_tag = span.find_previous(lambda tag: tag.name == "h4")

            if not title_tag:
                continue
            
            title = " ".join([title_tag.get_text(strip=True), date_tag.get_text(strip=True)])
            date = self.extract_date(date_tag.get_text(strip=True))
            
            if self.pipeline.exists(self.gestora, title):
                continue

            letter = {
                "gestora": self.gestora,
                "title": title,
                "date": date,
                "url": href,
                "content": ""
            }

            letters.append(letter)

        for li in soup.find_all("li"):
            span = li.find("span", class_="elementor-icon-list-text")
            
            if span and "Carta aos Investidores" in span.get_text():
                title = span.get_text(strip=True)
                url = li.find("a", href=True)["href"]
                date = self.extract_date(title)
                
                if self.pipeline.exists(self.gestora, title):
                    continue

                letter = {
                    "gestora": self.gestora,
                    "title": title,
                    "date": date,
                    "url": url,
                    "content": ""
                }
                letters.append(letter)

        return letters


if __name__ == "__main__":
    class DummyPipeline(DatabasePipeline):
        def exists(self, gestora, title):
            return False

    pipeline = DummyPipeline()
    scraper = GuepardoScraper(pipeline)
    letters = scraper.scrape()
    
    print(len(letters))
