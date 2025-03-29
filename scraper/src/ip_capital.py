import urllib3
from typing import List, Dict, Optional

from ..base import BaseScraper
from ..utils import extract_date
from services.database import DatabasePipeline, DummyPipeline
from services.extractor import PDFTextService


pdf = PDFTextService()

class IPCapitalScrape(BaseScraper):

    def __init__(self, pipeline: DatabasePipeline):
        super().__init__()
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        self.gestora = "IP Capital"
        self.base_url = "https://ip-capitalpartners.com/wp-content/themes/ip-capital/loop-reports.php"
        self.letters = []  # initialize as empty list

        self.pipeline = pipeline

    def get_urls(self, limit: Optional[int] = None) -> list[tuple[str, str]]:
        results = []
        page = 1
        has_content = True

        while has_content:
            url = f"{self.base_url}?paged={page}"

            soup = self.parse(url, verify=False)
            cards = soup.find_all("div", class_="card")

            for card in cards:
                title = card.find('h3').find('a').get_text().strip()
                date = card.find('p').get_text().strip()
                pdf_link = card.find('a', class_='btn-feature-download')
                
                if pdf_link and pdf_link['href'].endswith('.pdf'):
                    results.append((f'{title} ({date})', pdf_link['href']))

                    if limit and len(results) >= limit:
                        return results # for testing purposes

            load_more = soup.find('a', class_='load-more')
            
            if not load_more:
                has_content = False

            page += 1

        return results

    def scrape(self, limit: Optional[int] = None) -> List[Dict]:
        results = self.get_urls(limit=limit)
        
        for title, pdf_url in results:
            
            if self.should_skip(title):
                continue

            try:
                date = extract_date(title)
                text = pdf.extract_text(pdf_url, verify=False)
                
                letter = {
                    "gestora": self.gestora,
                    "title": title,
                    "date": date,
                    "url": pdf_url,
                    "content": text
                }

                self.letters.append(letter)

            except Exception as e:
                print(f"Failed to process {pdf_url}: {str(e)}")
        
        return self.letters

if __name__ == "__main__":
    scraper = IPCapitalScrape(pipeline=DummyPipeline())
    letters = scraper.scrape()

    print(len(letters))
    print(letters[0]['content'])
    print(letters[-1]['content'])