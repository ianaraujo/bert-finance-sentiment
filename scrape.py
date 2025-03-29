from services.loader import load_scrapers
from services.database import DatabasePipeline


def run():
    count = 0
    db = DatabasePipeline()

    for ScraperClass in load_scrapers():        
        scraper = ScraperClass(pipeline=db)
        
        try:
            letters = scraper.scrape(limit=None)
            len_letters = len(letters)
            count += len_letters

            print(f"{scraper.gestora} ({len_letters})")
            
            for letter in letters:
                db.store(letter)
        
        except Exception as e:
            print(f"Error in scraper {scraper.gestora}: {e}")

    print(f"Total: {count} new letters")
    
    total = db.count_all_letters()
    print(f"Total letters in database: {total}")


if __name__ == "__main__":
    run()