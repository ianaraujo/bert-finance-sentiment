import sqlite3
import argparse
from scrapers.loader import load_scrapers

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
        
    def store(self, letter, allow_update=False):
        cursor = self.conn.cursor()
        
        # check if letter already exists
        cursor.execute('SELECT id FROM letters WHERE title = ?', (letter['title'],))
        existing = cursor.fetchone()
        
        if existing:
            if allow_update:
                cursor.execute('''
                    UPDATE letters 
                    SET content = ?, date = ?, url = ?
                    WHERE title = ?
                ''', (letter['content'], letter['date'], letter['url'], letter['title']))
            return
            
        cursor.execute('''
            INSERT INTO letters (gestora, title, date, url, content)
            VALUES (?, ?, ?, ?, ?)
        ''', (letter['gestora'], letter['title'], letter['date'], letter['url'], letter['content']))
        
        self.conn.commit()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--update', action='store_true', help='Update existing records')
    args = parser.parse_args()

    count = 0
    pipeline = DatabasePipeline()
    
    for ScraperClass in load_scrapers():        
        scraper = ScraperClass()
        try:
            letters = scraper.scrape()
            len_letters = len(letters)

            count += len_letters
            print(f"{scraper.gestora} ({len_letters})")

            for letter in letters:
                letter["gestora"] = scraper.gestora
                pipeline.store(letter, allow_update=args.update)
        
        except Exception as e:
            print(f"Erro no scraper {scraper.gestora}: {e}")

    print(f"Total: {count} cartas")

if __name__ == "__main__":
    main()