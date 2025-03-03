import sqlite3
import argparse

from services.loader import load_scrapers

class DatabasePipeline:
    def __init__(self, db_path='letters.db'):
        self.conn = sqlite3.connect(db_path)
        self._create_table()
        
    def _create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS letters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gestora TEXT,
                title TEXT,
                date TEXT,
                url TEXT,
                content TEXT
            )
        ''')

        self.conn.commit()
        
    def exists(self, gestora: str, title: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM letters WHERE gestora = ? AND title = ?', (gestora, title))
        
        return cursor.fetchone() is not None

    def store(self, letter) -> None:
        cursor = self.conn.cursor()
        
        if not self.exists(letter['gestora'], letter['title']):
            cursor.execute('''
                INSERT INTO letters (gestora, title, date, url, content)
                VALUES (?, ?, ?, ?, ?)
            ''', (letter['gestora'], letter['title'], letter['date'], letter['url'], letter['content']))
            
            self.conn.commit()

    def clean_data(self, gestora: str) -> None:
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM letters WHERE gestora = ?', (gestora,))
        
        self.conn.commit()

class DummyPipeline(DatabasePipeline):
    def exists(self, **kwargs):
        return False

def get_scraper_by_name(name: str):
    scrapers = load_scrapers()
    
    for ScraperClass in scrapers:
        scraper = ScraperClass(pipeline=DummyPipeline())
        
        if scraper.gestora.lower().replace(' ', '_') == name.lower():
            return ScraperClass
    
    return None

def main():
    parser = argparse.ArgumentParser(description='Scrape investment letters')
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