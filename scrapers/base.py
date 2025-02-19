from typing import Optional

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/112.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,"
        "image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

class BaseScraper:
    registry = [] 
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseScraper.registry.append(cls)

    def scrape(self, limit: Optional[int] = None):
        raise NotImplementedError("O método scrape() deve ser implementado pela subclasse.")
    
if __name__ == "__main__":
    for ScraperClass in BaseScraper().registry:
        scraper = ScraperClass()
        print(scraper.gestora)