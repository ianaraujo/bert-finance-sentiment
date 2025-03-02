import urllib3
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional

from .base import BaseScraper, headers
from main import DatabasePipeline
from services.extractor import PDFTextService


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

pipeline = DatabasePipeline()

class IPCapitalScrape(BaseScraper):
    def __init__(self, pipeline: DatabasePipeline, service: Optional[PDFTextService] = None):
        self.gestora = "IP Capital"
        self.base_url = "https://ip-capitalpartners.com/wp-content/themes/ip-capital/loop-reports.php"
        self.letters = []  # Initialize as empty list
        
        self.session = requests.Session()
        self.session.headers = headers

        self.pipeline = pipeline
        self.service = service if service else PDFTextService()


    def get_urls(self) -> list[tuple[str, str]]:
        results = []
        page = 1
        has_content = True

        while has_content:
            url = f"{self.base_url}?paged={page}"
            response = self.session.get(url, headers=headers, verify=False)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            cards = soup.find_all("div", class_="card")

            for card in cards:
                title = card.find('h3').find('a').get_text().strip()
                date = card.find('p').get_text().strip()
                pdf_link = card.find('a', class_='btn-feature-download')
                
                if pdf_link and pdf_link['href'].endswith('.pdf'):
                    results.append((f'{title} ({date})', pdf_link['href']))

            load_more = soup.find('a', class_='load-more')
            
            if not load_more:
                has_content = False

            page += 1

        return results

    def scrape(self) -> List[Dict]:
        results = self.get_urls()
        
        for title, pdf_url in results:
            try:
                date = None
                text = self.service.extract_text(pdf_url, verify=False)
                
                letter = {
                    "gestora": self.gestora,
                    "title": title,
                    "date": '2023-01-01',
                    "url": pdf_url,
                    "content": text
                }

                self.letters.append(letter)

            except Exception as e:
                print(f"Failed to process {pdf_url}: {str(e)}")
        
        return self.letters

if __name__ == "__main__":
    scraper = IPCapitalScrape(pipeline)
    letters = scraper.scrape()

    print(len(letters))
    print(letters[0]['content'])
    print(letters[-1]['content'])