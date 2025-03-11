from datetime import datetime
from typing import List, Dict, Optional, Tuple

from ..base import BaseScraper
from services.database import DatabasePipeline, DummyPipeline


class DahliaScraper(BaseScraper):

    def __init__(self, pipeline: DatabasePipeline) -> None:
        super().__init__()

        self.gestora: str = "Dahlia Capital"
        self.base_url: str = "https://www.dahliacapital.com.br/_api/blog-frontend-adapter-public/v2/post-feed-page"
        
        self.params = {
            "languageCode": "pt",
            "page": 1,
            "pageSize": 12,
            "includeInitialPageData": "false",
            "type": "POST_LIST_WIDGET",
            "postListWidgetOptions.featuredOnly": "false",
            "postListWidgetOptions.categoryId": "c44150b1-916b-488c-99a5-1934f5a47d59",
            "translationsName": "post-list-widget"
        }

        self.headers = {
            "accept": "application/json, text/plain, */*",
            "authorization": ("PmASLbq6mLxXg-bsj5jbOGVb8zzlEhpBrKvSH94Mmzg."
                            "eyJpbnN0YW5jZUlkIjoiOTZiZTg0MjMtNDBiOC00NWU2LWJjMmIt"
                            "OWM5YzgzYzBiYjZmIiwiYXBwRGVmSWQiOiIyMmJlZjM0NS0zYzViLTRj"
                            "MTgtYjc4Mi03NGQ0MDg1MTEyZmYiLCJtZXRhU2l0ZUlkIjoiOTZiZTg0"
                            "MjMtNDBiOC00NWU2LWJjMmItOWM5YzgzYzBiYjZmIiwic2lnbkRhdGUi"
                            "OiIyMDI1LTAzLTExVDEwOjA5OjA2LjgzNloiLCJkZW1vTW9kZSI6ZmFs"
                            "c2UsImFpZCI6ImE1ZDIwZDQzLWE2YjktNGVjZS1iZDMwLTFkMGFhMWU2"
                            "NTk0YSIsInNpdGVPd25lcklkIjoiMWM2MzcyODctOTYxOC00MTBjLTkz"
                            "NWItMGZjMjE5ODRmN2UwIiwiYnMiOiJXN1A2Q2Y4dU1ZR1JROFlsZHU0bU"
                            "tXTUN0V3FqNzAyV1gzR0s5LWYwMTRJLklqWmpOVFl6TkRVd0xUZGhZMlV0"
                            "TkdJNFlTMWhZbUV4TFRNNE5qRmpORFl5T1RJMU55SSJ9"),
        }
        
        self.letters: List[Dict] = []  # initialize as empty list
        self.pipeline = pipeline

    def find_posts(self) -> List[Tuple]:
        posts = []

        while True:
            response = self.session.get(self.base_url, params=self.params, headers=self.headers)

            if response.status_code == 200:
                data = response.json()
                res = data.get("postFeedPage", {}).get("posts", {}).get("posts", [])
                
                for post in res:
                    posts.append((post.get("title"), post.get("firstPublishedDate"), post.get("link")))

                self.params["page"] += 1
            else:
                break

        return posts

    def scrape(self, limit: Optional[int] = None) -> List[Dict]:
        posts = self.find_posts()

        for title, date, url in posts: 
            soup = self.parse(url)

            content = soup.find("div", attrs={"data-id": "content-viewer"})
            extracted_text = content.get_text(separator=" ", strip=True)

            dt = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
            date_only = dt.strftime("%Y-%m-%d")

            letter = {
                "gestora": self.gestora,
                "title": title,
                "date": date_only,
                "url": url,
                "content": extracted_text
            }

            self.letters.append(letter)

            if limit and len(self.letters) >= limit:
                return self.letters # for testing purposes

        return self.letters
    

if __name__ == "__main__":
    pipeline = DummyPipeline()
    scraper = DahliaScraper(pipeline)
    letters = scraper.scrape(limit=3)

    print(letters)