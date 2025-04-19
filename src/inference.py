import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import torch
from datasets import Dataset

from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    BertForSequenceClassification,
    pipeline,
)

split_pattern = re.compile(r'(?<=[.!?])(?:["”’\)\]]+)?\s+')
token_pattern = re.compile(r'\S+')

def sanitize_text(text: str) -> str:

    substitutions = {
        "Œ": "ê",
        "ªo": "ão",
        "Æ": "á",
        "Ø": "é",
        "ª": "ã",
    }

    for k, v in substitutions.items():
        text = text.replace(k, v)

    # remover separações hifenizadas entre linhas
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)

    # remover quebras de linha no meio de frases
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)

    text = text.replace("\n", " ")
    text = " ".join(text.split())

    text = text.strip()
    
    return text

def sentence_chunks(text: str, min_tokens: int = 20, max_tokens: int = 500, non_letter_threshold: float = 0.05,) -> List[str]:
    chunks = []
    
    for sentence in split_pattern.split(text):
        sentence = sanitize_text(sentence)
        
        if not sentence:
            continue
        
        non_letter = sum(
            1 for c in sentence if not c.isalpha() and not c.isspace()
        )
        
        if (non_letter / len(sentence)) > non_letter_threshold:
            continue
        
        token_count = len(token_pattern.findall(sentence))
        
        if min_tokens <= token_count <= max_tokens:
            chunks.append(sentence)
    
    return chunks

# INFERENCE

DB_PATH            = "letters.db"
CUSTOM_MODEL_DIR   = "models/sentiment-bert-portuguese-asset-management-cls"
BENCHMARK_MODEL_ID = "lucas-leme/FinBERT-PT-BR"
DEVICE             = 0 if torch.cuda.is_available() else -1
BATCH_SIZE         = 64

class SentimentAnalysis:
    def __init__(
        self,
        db_path: str = DB_PATH,
        custom_model_dir: str = CUSTOM_MODEL_DIR,
        benchmark_model_name: str = BENCHMARK_MODEL_ID,
    ):
        self.db_path = Path(db_path)

        self.tokenizer_custom = AutoTokenizer.from_pretrained(custom_model_dir, do_lower_case=False)
        self.model_custom     = AutoModelForSequenceClassification.from_pretrained(custom_model_dir)
        
        self.model_custom.config.id2label = {0: "NEGATIVE", 1: "POSITIVE", 2: "NEUTRAL"}
        self.model_custom.config.label2id = {v: k for k, v in self.model_custom.config.id2label.items()}
        
        self.pipeline_custom  = pipeline(
            "text-classification",
            model=self.model_custom,
            tokenizer=self.tokenizer_custom,
            top_k=None,
            device=DEVICE,
        )

        self.tokenizer_bench = AutoTokenizer.from_pretrained(benchmark_model_name, do_lower_case=False)
        self.model_bench = BertForSequenceClassification.from_pretrained(benchmark_model_name)
        
        self.model_bench.config.id2label = {0: "POSITIVE", 1: "NEGATIVE", 2: "NEUTRAL"}
        self.model_bench.config.label2id = {"POSITIVE": 0, "NEGATIVE": 1, "NEUTRAL": 2}
        
        self.pipeline_bench = pipeline(
            "text-classification",
            model=self.model_bench,
            tokenizer=self.tokenizer_bench,
            top_k=None,
            device=DEVICE,
        )

        self._ensure_columns()

    @contextmanager
    def _db_connection(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            yield conn, cursor
        finally:
            cursor.close()
            conn.close()

    def _execute(
        self,
        query: str,
        params: Tuple[Any, ...] | None = None,
        fetch: bool = False,
    ):
        with self._db_connection() as (conn, cur):
            cur.execute(query, params or ())
            conn.commit()
            return cur.fetchall() if fetch else None

    def _ensure_columns(self):
        cols = [row[1] for row in self._execute("PRAGMA table_info(letters)", fetch=True)]
        for col in ("sentiment", "sentiment_benchmark"):
            if col not in cols:
                self._execute(f"ALTER TABLE letters ADD COLUMN {col} INTEGER")

    @staticmethod
    def _aggregate(prob_chunks: List[List[Dict[str, float]]]) -> int:
        if not prob_chunks:
            return 50
        
        scores, weights = [], []
        
        for chunk in prob_chunks:
            d = {x["label"]: x["score"] for x in chunk}
            p_pos, p_neg = d["POSITIVE"], d["NEGATIVE"]
            
            s_i = p_pos - p_neg
            w_i = p_pos + p_neg
            
            if w_i:
                p_pos, p_neg = p_pos / w_i, p_neg / w_i
                s_i = p_pos - p_neg
            
            scores.append(s_i)
            
            weights.append(w_i)

        S = np.dot(scores, weights) / sum(weights) if weights else 0.0
        S = np.sign(S) * abs(S) ** 0.75            # alpha = 0.75
        
        return int(50 * (S + 1))                   # [-1,1] -> [0,100]

    def _predict_pair(self, chunks: List[str]) -> Tuple[int, int]:
        if not chunks:
            return 50, 50

        pipe_kwargs = dict(batch_size=BATCH_SIZE, truncation=True, max_length=512)

        p_custom = self.pipeline_custom(chunks, **pipe_kwargs)
        p_bench  = self.pipeline_bench (chunks, **pipe_kwargs)

        return self._aggregate(p_custom), self._aggregate(p_bench)

    def run(self, where: str = "gestora <> 'Encore' and content is not null and content <> ''"):
        rows = self._execute(f"SELECT id, content FROM letters WHERE {where}", fetch=True)
        total = len(rows)
        
        for idx, (letter_id, content) in enumerate(rows, 1):
            chunks = sentence_chunks(content or "")
            s_custom, s_bench = self._predict_pair(chunks)
            
            self._execute(
                "UPDATE letters SET sentiment=?, sentiment_benchmark=? WHERE id=?",
                (s_custom, s_bench, letter_id),
            )
            
            print(f"\rProcessed {idx}/{total} id={letter_id}", end="", flush=True)
        
        print("\nSentiment analysis completed.")

if __name__ == "__main__":
    inference = SentimentAnalysis()
    inference.run()
