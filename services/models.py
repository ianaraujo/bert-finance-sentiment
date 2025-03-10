import re
import torch
from transformers import pipeline, AutoTokenizer

class LlamaTextEnhancer:
    def __init__(self, model_id="meta-llama/Llama-3.2-1B-Instruct", chunk_size=1600, overlap_size=200):
        """
        :param model_id: The model ID from Hugging Face or local path.
        :param chunk_size: How many tokens to include in each chunk.
        :param overlap_size: How many tokens to overlap between chunks.
        """
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size

        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        # Some Llama models don't have a pad token; use EOS as pad
        if not self.tokenizer.pad_token:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.pipe = pipeline(
            "text-generation",
            model=model_id,
            torch_dtype=torch.bfloat16,
            device_map="auto"
        )

    def _split_into_chunks(self, text):
        """
        Splits the text into overlapping token chunks so we don't exceed the model's max token limit.
        """
        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        chunks = []
        start = 0

        while start < len(tokens):
            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]
            chunks.append(chunk_tokens)
            # Move start forward but keep some overlap
            start += (self.chunk_size - self.overlap_size)

        return chunks

    def _enhance_chunk(self, tokens):
        """
        Generates the corrected text for a single chunk of tokens.
        """
        # Decode tokens back to string
        segment_text = self.tokenizer.decode(tokens, skip_special_tokens=True)

        # Simple prompt in Portuguese
        prompt = (
            "Reescreva o texto a seguir em português, corrigindo pontuação, ortografia e concordância. "
            "Retorne APENAS o texto corrigido, sem explicações ou exemplos.\n\n"
            f"Texto: {segment_text}\n\n"
            "Texto corrigido:"
        )

        # Estimate output size as 120% of input tokens
        # (adjust up/down if you find truncation or too-long outputs)
        max_new_tokens = int(len(tokens) * 1.2)

        # Generate
        result = self.pipe(
            prompt,
            max_new_tokens=max_new_tokens,
            temperature=0.3,
            top_p=0.9,
            repetition_penalty=1.1,
            do_sample=True
        )[0]["generated_text"]

        # Extract only what's after "Texto corrigido:"
        if "Texto corrigido:" in result:
            result = result.split("Texto corrigido:", 1)[-1].strip()

        # Remove any trailing explanations (basic heuristic):
        # For instance, if the model tries to add something like "Explicação: ...", etc.
        explanation_markers = ["Explicação:", "Notas:", "Observações:", "Mudanças:", "Alterações:"]
        
        for marker in explanation_markers:
            if marker in result:
                result = result.split(marker, 1)[0].strip()

        return result

    def _merge_chunks(self, enhanced_chunks):
        """
        Merges overlapping chunks into one final text by skipping the overlap in subsequent chunks.
        """
        if not enhanced_chunks:
            return ""

        merged_text = enhanced_chunks[0]
        for i in range(1, len(enhanced_chunks)):
            # Overlap skip: convert chunk to tokens, then skip overlap tokens
            prev_tokens = self.tokenizer.encode(merged_text, add_special_tokens=False)
            current_tokens = self.tokenizer.encode(enhanced_chunks[i], add_special_tokens=False)

            # We skip the first `overlap_size` tokens of the current chunk to avoid duplication
            to_add = current_tokens[self.overlap_size:] if len(current_tokens) > self.overlap_size else []
            # Decode and append
            merged_text += " " + self.tokenizer.decode(to_add, skip_special_tokens=True).strip()

        return merged_text

    def enhance_text(self, text):
        """
        Public method to enhance the entire text by splitting into chunks, enhancing, and merging.
        """
        chunks = self._split_into_chunks(text)
        enhanced_chunks = [self._enhance_chunk(chunk) for chunk in chunks]
        return self._merge_chunks(enhanced_chunks)

if __name__ == "__main__":
    sample_text = """
    Olá pessoal meu nome é João Luiz Braga sou Analista aqui na encora
    vim falar um pouquinho sobre o mês de junho um pouco atrasado mas
    hoje é dia 10 agora são quase nove quase 10 horas da manhã Bom vamos
    lá foi um mês difícil né porque no sentido de que a bolsa subiu muito
    foi difícil acompanhar a gente tá até um ano bom mas um mês a gente
    ficou um pouco para trás
    """.replace("\n", " ")

    enhancer = LlamaTextEnhancer()
    corrected_text = enhancer.enhance_text(sample_text)
    
    print(corrected_text)
