import sqlite3

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
        
    def exists(self, gestora: str, title: str) -> tuple:
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, content FROM letters WHERE gestora = ? AND title = ?', (gestora, title))
        
        data = cursor.fetchone()
        id = data[0]
        content = data[1]
        
        if data is None:
            return (False, None, None)
        else:
            return (True, id, content)

    def store(self, letter) -> None:
        exists, id, content = self.exists(letter['gestora'], letter['title'])
        
        if not exists:
            # letter doesn't exist, insert new record
            cursor = self.conn.cursor()
            
            cursor.execute('''
                INSERT INTO letters (gestora, title, date, url, content)
                VALUES (?, ?, ?, ?, ?)
            ''', (letter['gestora'], letter['title'], letter['date'], letter['url'], letter['content']))
            
            self.conn.commit()

        if exists and content == '':
            # letter exists but has empty content, update it
            cursor = self.conn.cursor()
            
            cursor.execute('''
                UPDATE letters SET content = ? WHERE id = ?
            ''', (letter['content'], id))
            
            self.conn.commit()

        return

    def clean_data(self, gestora: str) -> None:
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM letters WHERE gestora = ?', (gestora,))
        
        self.conn.commit()

    def count_all_letters(self) -> int:
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM letters')
        return cursor.fetchone()[0]


class DummyPipeline(DatabasePipeline):
    
    def exists(self, gestora, title) -> tuple:
        return (False, None, None)