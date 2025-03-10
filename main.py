import argparse

from services.loader import load_scrapers
from services.database import DatabasePipeline, DummyPipeline


def get_scraper_by_name(name: str):
    scrapers = load_scrapers()
    
    for ScraperClass in scrapers:
        scraper = ScraperClass(pipeline=DummyPipeline())
        
        if scraper.gestora.lower().replace(' ', '_') == name.lower():
            return ScraperClass
    
    return None

def main():
    parser = argparse.ArgumentParser(description='Run scrapers to get letters from investment funds managers')
    parser.add_argument('--scraper', type=str, help='Name of the specific scraper to run (e.g., ip_capital)')
    args = parser.parse_args()

    db = DatabasePipeline()
    count = 0

    if args.scraper:
        ScraperClass = get_scraper_by_name(args.scraper)
        
        if not ScraperClass:
            print(f"Scraper '{args.scraper}' not found")
            return
        
        scraper = ScraperClass(pipeline=db)
        
        print(f"Clearing existing data for {scraper.gestora}...")
        db.clean_data(scraper.gestora)
        
        try:
            letters = scraper.scrape()
            count = len(letters)
            print(f"{scraper.gestora} ({count})")
            
            for letter in letters:
                db.store(letter)
        
        except Exception as e:
            print(f"Error in scraper {scraper.gestora}: {e}")
    
    else:
        for ScraperClass in load_scrapers():        
            scraper = ScraperClass(pipeline=db)
            
            try:
                letters = scraper.scrape()
                len_letters = len(letters)
                count += len_letters

                print(f"{scraper.gestora} ({len_letters})")
                
                for letter in letters:
                    db.store(letter)
            
            except Exception as e:
                print(f"Error in scraper {scraper.gestora}: {e}")

    print(f"Total: {count} letters")

if __name__ == "__main__":
    main()