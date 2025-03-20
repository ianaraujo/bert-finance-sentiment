import io
import requests
import pypdf
from typing import Optional


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
    "Accept": "application/pdf,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
}

class PDFTextService:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def extract_text(self, pdf_url: str, verify: bool = True, verbose: bool = True) -> Optional[str]:
        try:
            response = requests.get(
                pdf_url,
                allow_redirects=True,
                stream=True,
                timeout=self.timeout,
                headers=HEADERS,
                verify=verify
            )

            response.raise_for_status()

            pdf_bytes = io.BytesIO(response.content)
            reader = pypdf.PdfReader(pdf_bytes)

            extracted_text = ""

            for page in reader.pages:
                page_text = page.extract_text()

                if page_text:
                    extracted_text += page_text

            return extracted_text

        except Exception as e:
            if verbose:
                print(f"Failed to extract text from PDF at {pdf_url}: {str(e)}")
            
            return None


if __name__ == "__main__":
    service = PDFTextService()

    url = "https://www.marasset.com.br/document/jan-25-pregando-no-deserto/"
    text = service.extract_text(url)

    print("Extracted text:", text)
