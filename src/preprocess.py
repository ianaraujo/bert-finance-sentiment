import re
import sqlite3
import random
from typing import List, Dict

conn = sqlite3.connect('letters.db')
cursor = conn.cursor()

split_pattern = re.compile(r'(?<=[.!?])(?:["”’\)\]]+)?\s+')
token_pattern = re.compile(r'\w+')

def read_data() -> List:
    cursor.execute(
        '''
        SELECT content 
        FROM letters
        WHERE gestora <> 'Encore'
        AND content IS NOT NULL 
        AND content <> ''
        '''
    )
    data = cursor.fetchall()
    
    return data

def sanitize_text(text: str) -> str:
    text = text.replace("\n", " ")
    text = " ".join(text.split())
    text = text.strip()
    
    return text

def generate_chunks(data: List, min_size: int = 10, max_size: int = 500, threshold: float = 0.1) -> List[Dict]:
    chunks: List[Dict] = []
    
    for row in data:
        text = row[0]
        sentences = split_pattern.split(text)

        for sentence in sentences:
            sentence = sanitize_text(sentence)
            sentence_len = len(sentence)
            
            if sentence_len == 0:
                continue

            not_letter = sum(1 for c in sentence if not c.isalpha() and not c.isspace())

            if (not_letter / sentence_len) > threshold:
                continue
            
            tokens = token_pattern.findall(sentence)
            token_count = len(tokens)

            if token_count < min_size:
                continue

            if token_count <= max_size:
                chunks.append({'text': sentence})
                continue
    
    return chunks
    

if __name__ == '__main__':
    data = read_data()
    final_data = generate_chunks(data)

    print(f"Generated {len(final_data)} chunks")
    
    for i in range(11):
        print(f'Example {i}: ', random.choice(final_data))