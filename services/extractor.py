import io
import requests
import pypdf
from typing import Optional

class PDFTextService:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def extract_text(self, pdf_url: str, verify: bool=True) -> Optional[str]:
        try:
            response = requests.get(pdf_url, stream=True, timeout=self.timeout, verify=verify)
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
            print(f"Failed to extract text from PDF at {pdf_url}: {str(e)}")
            return None

if __name__ == "__main__":
    service = PDFTextService()
    url = "https://www.guepardoinvest.com.br/Carta-76-Carta-aos-Investidores-Mar16.pdf"

    text = service.extract_text(url)
    print("Extracted text:", text)
