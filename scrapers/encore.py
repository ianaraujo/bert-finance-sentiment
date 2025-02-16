import re
import requests
from bs4 import BeautifulSoup

from .base import BaseScraper, headers


class EncoreScraper(BaseScraper):
    def __init__(self):
        self.gestora = "Encore"
        self.base_url = "https://encore.am/midias/"

    def get_urls(self):
        response = requests.get(self.base_url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        nav = soup.find("a", class_="last", href=True)
        match = re.search('/page/(\d+)/', nav["href"])

        if match:
            last_page = match.group(1)
        else:
            raise Exception("Could not determine the total number of pages")

        return [self.base_url + f'page/{page_number}/' for page_number in range(1, int(last_page) + 1)]

    def scrape_letters(self):
        letters = []
        
        for url in self.get_urls():
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, "html.parser")

            for div in soup.find_all("div", class_="card-midia"):
                title = div.find("h3").get_text()

                if 'carta' in title.lower():
                    date = div.find("span", class_="data")
                    a = div.find("a", class_="btn btn-vermais", href=True)

                    response = requests.get(a["href"], headers=headers)
                    carta_soup = BeautifulSoup(response.text, "html.parser")

                    content = carta_soup.find("div", class_="content")

                    if content:
                        for img in content.find_all("img"):
                            img.extract()
        
                        pdf_media = content.find("div", class_="wp-block-file")

                        if pdf_media: 
                            href = pdf_media.find("a", href=True)["href"]
                            pdf_media.extract()

                        text = content.get_text(separator=" ", strip=True)
                    
                    letters.append({"title": title, "href": href, "date": date.text, "text": text})

        return letters

    def scrape(self):
        letters = self.scrape_letters()
        videos = []

        return list(letters + videos)


if __name__ == "__main__":
    scraper = EncoreScraper()
    letters = scraper.scrape()

    print(letters[0])
