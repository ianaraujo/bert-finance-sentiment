import os
import re
import json
import csv
import sqlite3
import random
import argparse
from typing import List, Dict

conn = sqlite3.connect('letters.db')
cursor = conn.cursor()

split_pattern = re.compile(r'(?<=[.!?])(?:["”’\)\]]+)?\s+')
token_pattern = re.compile(r'\S+')

def read_data() -> List:
    cursor.execute(
        '''
        SELECT gestora, title, content 
        FROM letters
        WHERE content IS NOT NULL 
            AND content <> ''
            AND (gestora <> 'Encore' AND title NOT LIKE '%Comentário%')
        '''
    )
    data = cursor.fetchall()
    
    return data

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

def split_transcription(text: str, chunk_size: int = 500, overlap: int = 5) -> List[str]:
    tokens = token_pattern.findall(text)

    start = 0
    chunks = []
    total_tokens = len(tokens)

    while start < total_tokens:
        end = start + chunk_size

        chunk_tokens = tokens[start:end]
        chunk_text = ' '.join(chunk_tokens)
        
        chunks.append(chunk_text)

        if end >= total_tokens:
            break

        start += (chunk_size - overlap)

    return chunks

def generate_chunks(data: List, min_size: int = 20, max_size: int = 500, threshold: float = 0.05) -> List[Dict]:
    chunks: List[Dict] = []
    
    for row in data:
        text = row[2]
        gestora, title = row[0], row[1]
            
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
    
def create_random_sample(chunks_data: List[Dict], output_file: str, sample_size: int = 1000) -> None:
    sample_size = min(sample_size, len(chunks_data))

    sample = random.sample(chunks_data, sample_size)

    # write sample to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # write header
        writer.writerow(['text', 'label'])
        # write rows (label is left empty)
        for chunk in sample:
            writer.writerow([chunk['text'], '[LABEL]'])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process letters data and optionally export CSV sample.')
    parser.add_argument('--export', action='store_true', help='Export a random CSV sample of chunk data.')
    parser.add_argument('--path', type=str, help='Path to the CSV output file.')

    args = parser.parse_args()
    data = read_data()
    chunks_data = generate_chunks(data)

    for i in range(11):
        print(f'Example {i}: ', random.choice(chunks_data))

    print()
    print(f"Generated {len(chunks_data)} chunks from {len(data)} letters.")

    os.makedirs('data', exist_ok=True)

    with open('data/domain_training.jsonl', 'w', encoding='utf-8') as f:
        for chunk in chunks_data:
            f.write(json.dumps(chunk, ensure_ascii=False) + '\n')

    print('Data saved to data/domain_training.jsonl')

    if args.export:
        create_random_sample(chunks_data, sample_size=1000, output_file=args.path)
        print(f'Random sample of chunks saved to {args.path}')