import re
import sqlite3
import torch
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from contextlib import contextmanager
from datasets import Dataset
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
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            yield conn, cursor
        finally:
            cursor.close()
            conn.close()

    def _execute_query(self, query: str, params: tuple = None, fetch: bool = False) -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
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
        with self._db_connection() as (conn, cursor):
            cursor.execute("PRAGMA table_info(letters)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'sentiment' not in columns:
                cursor.execute("ALTER TABLE letters ADD COLUMN sentiment INTEGER")
                
                conn.commit()

    def read_letters(self, where_clause: str = "") -> List[Dict]:
        with self._db_connection() as (conn, cursor):
            query = "SELECT id, content FROM letters"
            if where_clause:
                query += f" WHERE {where_clause}"
                
            cursor.execute(query)
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            
            return [dict(zip(columns, row)) for row in rows]
    

    def calculate_score(self, prob: list[list[dict]], alpha: float = 0.5, slope: Optional[float] = None, normalized: bool = True) -> int:
        self.scores = np.array([])
        self.weights = np.array([])

        for chunk in prob:
            label_scores = {d['label']: d['score'] for d in chunk}

            p_pos = label_scores['POSITIVE']
            p_neg = label_scores['NEGATIVE']

            # polarity: s_i = p_pos - p_neg
            s_i = p_pos - p_neg
            
            # weight: w_i = p_pos + p_neg
            w_i = p_pos + p_neg

            if normalized and w_i > 0:
                p_norm_pos = p_pos / w_i
                p_norm_neg = p_neg / w_i
                s_i = p_norm_pos - p_norm_neg

            self.scores = np.append(self.scores, s_i)
            self.weights = np.append(self.weights, w_i)


        if len(self.weights) == 0 or self.weights.sum() == 0:
            return 50
    
        S = np.sum(self.weights * self.scores) / np.sum(self.weights)  # [-1, +1]
        
        if alpha != 1.0:
            S = np.sign(S) * (np.abs(S) ** alpha) # [-1, +1]

        if slope:
            logistic = lambda x, slope: 1 / (1 + np.exp(-slope * x))
            
            S = logistic(S, slope) # [0, 1]
            final_score = int(S * 100.0) # scale to [0, 100]

        else: 
            final_score = int(50.0 * (S + 1.0)) # scale to [0, 100]

        return final_score

    def predict_sentiment(self, letters: List[Dict[str, Any]]) -> None:
        dataset = Dataset.from_list(letters)

        def process_example(example):
            text = example["content"]
            
            if not text:
                return {"sentiment": 50}
            
            chunks = []
            
            text = text.replace('\n', ' ').replace('  ', ' ')
            sentences = re.split(r'(?<=[.!?])', text)
            
            for sentence in sentences:
                tokens = self.tokenizer(sentence, add_special_tokens=False)
                token_length = len(tokens["input_ids"])
                
                if 15 <= token_length <= 500:
                    chunks.append(sentence)
            
            if not chunks:
                return {"sentiment": 50}

            chunk_dataset = Dataset.from_dict({"text": chunks})
            text_list = chunk_dataset["text"]

            prob = self.pipeline(text_list, batch_size=64)
            score = self.calculate_score(prob, alpha=0.75, normalized=True)

            return {"sentiment": score}

        dataset = dataset.map(process_example, batched=False)

        for row in dataset:
            self._execute_query(
                "UPDATE letters SET sentiment = ? WHERE id = ?",
                (row["sentiment"], row["id"])
            )
            
            print(f"Processing letter with id {row['id']}", end='\r')


    def run(self) -> None:
        letters = self.read_letters("gestora <> 'Encore' and content is not null")
        self.predict_sentiment(letters)

        print("Sentiment analysis completed")

if __name__ == "__main__":
    sa = SentimentAnalysis()
    sa.run()