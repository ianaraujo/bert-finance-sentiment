import sqlite3

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

def main():
    count = 0
    db = DatabasePipeline()

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
            print(f"Erro no scraper {scraper.gestora}: {e}")

    print(f"Total: {count} cartas")

if __name__ == "__main__":
    main()