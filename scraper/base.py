import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Accept": "application/pdf,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
}


class BaseScraper:

    def __init__(self, headers=None) -> None:
        self.headers = headers or HEADERS

        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def parse(self, url: str, verify: bool = True) -> BeautifulSoup:
        try:
            response = self.session.get(url, verify=verify, timeout=10)
            response.raise_for_status()

        except requests.RequestException as e:
            print(f"Request failed for {url}: {e}")
            return None

        soup = BeautifulSoup(response.content, "html.parser")

        return soup

    def scrape(self):
        raise NotImplementedError(
            "O método scrape() deve ser implementado pela subclasse.")
