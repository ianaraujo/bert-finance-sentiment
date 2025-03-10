import re
from typing import Optional
from youtube_transcript_api import YouTubeTranscriptApi

from services.database import DatabasePipeline, DummyPipeline
from services.models import LlamaTextEnhancer
from ..base import BaseScraper


enhancer = LlamaTextEnhancer()

class EncoreScraper(BaseScraper):
    
    def __init__(self, pipeline: DatabasePipeline):
        super().__init__()
        self.gestora = "Encore"
        self.base_url = "https://encore.am/midias/"
        self.pipeline = pipeline

    def transform_date(self, date_str: str) -> str:
        months = {
            "janeiro": "01",
            "fevereiro": "02",
            "março": "03",
            "abril": "04",
            "maio": "05",
            "junho": "06",
            "julho": "07",
            "agosto": "08",
            "setembro": "09",
            "outubro": "10",
            "novembro": "11",
            "dezembro": "12",
        }

        parts = date_str.split(" de ")

        if len(parts) != 3:
            raise ValueError(
                "Date string does not match expected format 'DD de month de YYYY'")

        day = int(parts[0])
        month_str = parts[1].strip().lower()
        year = parts[2].strip()
        month = months.get(month_str)

        if not month:
            raise ValueError(f"Unknown month: {month_str}")

        return f"{year}-{month}-{day:02d}"

    def get_urls(self):
        soup = self.parse(self.base_url)
        nav = soup.find("a", class_="last", href=True)

        match = re.search(r'/page/(\d+)/', nav["href"])

        if match:
            last_page = match.group(1)
        else:
            raise Exception("Could not determine the total number of pages")

        return [self.base_url + f'page/{page_number}/' for page_number in range(1, int(last_page) + 1)]

    def get_youtube_text(self, id: str):
        transcript = YouTubeTranscriptApi.get_transcript(id, languages=["pt"])
        transcript_text = ' '.join([chunk['text'] for chunk in transcript])

        return transcript_text

    def _process_youtube_content(self, content) -> tuple[str, str]:
        iframes = content.find_all("iframe")
        youtube_iframe = None
        
        for iframe in iframes:
            src = iframe.get("src", "")
            
            if src.startswith("https://www.youtube.com"):
                youtube_iframe = iframe
                break
        
        if not youtube_iframe:
            return None, None
            
        src = youtube_iframe.get("src")
        match = re.search(r'youtube\.com/embed/([a-zA-Z0-9_-]+)', src)

        if not match:
            return None, None
        
        youtube_id = match.group(1)
        youtube_href = f"https://www.youtube.com/watch?v={youtube_id}"

        return youtube_id, youtube_href

    def _process_letter_content(self, content) -> tuple[str, str]:
        if not content:
            return None, None

        for img in content.find_all("img"):
            img.extract()

        href = None
        pdf_media = content.find("div", class_="wp-block-file")

        if pdf_media:
            href = pdf_media.find("a", href=True)["href"]
            pdf_media.extract()

        text = content.get_text(separator=" ", strip=True)

        return text, href

    def _scrape_items(self, content_type: str, limit: Optional[int] = None) -> list[dict]:
        items = []
        for url in self.get_urls():
            soup = self.parse(url)
            
            for div in soup.find_all("div", class_="card-midia"):
                title = div.find("h3").get_text().strip()

                keyword = 'comentário' if content_type == 'video' else 'carta'
                
                if keyword not in title.lower():
                    continue

                date_element = div.find("span", class_="data")
                a = div.find("a", class_="btn btn-vermais", href=True)

                detail_soup = self.parse(a["href"])
                detail_content = detail_soup.find("div", class_="content")

                if content_type == 'video':
                    youtube_id, href = self._process_youtube_content(detail_content)
                    
                    if youtube_id:
                        raw_text = self.get_youtube_text(id=youtube_id)
                        text = enhancer.enhance_text(raw_text)
                    else:
                        text, href = None, None
                else:
                    text, href = self._process_letter_content(detail_content)

                items.append({
                    "gestora": self.gestora,
                    "title": title,
                    "date": self.transform_date(date_element.text),
                    "url": href,
                    "content": text
                })

                if limit and len(items) >= int(limit / 2):
                    return items # for testing purposes

        return items

    def scrape(self, limit: Optional[int] = None) -> list[dict]:
        letters = self._scrape_items('letter', limit)
        videos = self._scrape_items('video', limit)

        return letters + videos


if __name__ == "__main__":
    scraper = EncoreScraper(pipeline=DummyPipeline())
    letters = scraper.scrape(limit=5)

    for letter in letters:
        print(letter['title'])
        print(letter['content'])
        print()
