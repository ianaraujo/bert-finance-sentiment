import re
import sqlite3
import torch
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from contextlib import contextmanager
from transformers import AutoTokenizer, BertForSequenceClassification, pipeline

class SentimentAnalysis:
    def __init__(self, db_path: Optional[str] = "letters.db", model_name: str = "lucas-leme/FinBERT-PT-BR"):
        self.db_path = db_path
        self.scores = np.array([])
        self.weights = np.array([])
        
        # initialize the model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = BertForSequenceClassification.from_pretrained(model_name)
        
        self.pipeline = pipeline(
            task='text-classification',
            model=self.model,
            tokenizer=self.tokenizer,
            top_k=None,
            device=0 if torch.cuda.is_available() else -1
        )
        
        if self.db_path:
            self._alter_table()

    @contextmanager
    def _db_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            yield conn, cursor
        finally:
            cursor.close()
            conn.close()

    def _execute_query(self, query: str, params: tuple = None, fetch: bool = False) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
        """Execute a query and return connection and cursor"""
        with self._db_connection() as (conn, cursor):
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            conn.commit()
            
            if fetch:
                return cursor.fetchall()
            return None

    def _alter_table(self) -> None:
        """Add sentiment column if it doesn't exist"""
        with self._db_connection() as (conn, cursor):
            cursor.execute("PRAGMA table_info(letters)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'sentiment' not in columns:
                cursor.execute("ALTER TABLE letters ADD COLUMN sentiment INTEGER")
                conn.commit()

    def read_letters(self, where_clause: str = "") -> List[Dict]:
        """Read letters from database with optional WHERE clause"""
        with self._db_connection() as (conn, cursor):
            query = "SELECT id, content FROM letters"
            if where_clause:
                query += f" WHERE {where_clause}"
                
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            
            return [dict(zip(columns, row)) for row in rows]
    
    def update_sentiment(self, letter_id: int, sentiment_score: int) -> None:
        """Update sentiment score for a letter"""
        self._execute_query(
            "UPDATE letters SET sentiment = ? WHERE id = ?",
            (sentiment_score, letter_id)
        )

    def calculate_score(self, prob: list[list[dict]], w_threshold: float = 0.1, alpha: float = 1.0, normalized: bool = False) -> int:
        for chunk in prob:
            label_scores = {d['label']: d['score'] for d in chunk}

            p_pos = label_scores['POSITIVE']
            p_neg = label_scores['NEGATIVE']

            # polarity: s_i = p_pos - p_neg
            s_i = p_pos - p_neg
            
            # weight: w_i = p_pos + p_neg
            w_i = p_pos + p_neg

            if w_i < w_threshold:
                continue

            if normalized and w_i > 0:
                p_norm_pos = p_pos / w_i
                p_norm_neg = p_neg / w_i
                s_i = p_norm_pos - p_norm_neg

            self.scores = np.append(self.scores, s_i)
            self.weights = np.append(self.weights, w_i)

        if len(self.weights) == 0 or self.weights.sum() == 0:
            final_score = 50
    
        else:
            S = np.sum(self.weights * self.scores) / np.sum(self.weights)  # [-1, +1]
            
            if alpha != 1.0:
                S = np.sign(S) * (np.abs(S) ** alpha) # [-1, +1]
            
            # scale to [0, 100]
            final_score = int(50.0 * (S + 1.0))

        return final_score

    def predict_sentiment(self, letters: List[Dict[str, Any]]) -> None:
        """Predict sentiment for a list of letters"""
        for i, letter in enumerate(letters, 1):
            text = letter['content']

            if not text:
                continue

            text = text.replace('\n', ' ').replace('  ', ' ')

            chunks = []
            sentences = re.split(r'(?<=[.!?])', text)

            for text in sentences:
                tokens = self.tokenizer(text, add_special_tokens=False)
                token_length = len(tokens["input_ids"])
            
                if 15 <= token_length <= 500:
                    chunks.append(text)

            prob = self.pipeline(chunks, batch_size=12)
            score = self.calculate_score(prob)
            self.update_sentiment(letter['id'], score)

            print(f"Processing letters ({i}/{len(letters)})", end='\r')

    def run(self) -> None:
        """Run sentiment analysis"""
        letters = self.read_letters("gestora <> 'Encore'")
        self.predict_sentiment(letters)

        print("Sentiment analysis completed")

if __name__ == "__main__":
    sa = SentimentAnalysis()
    sa.run()