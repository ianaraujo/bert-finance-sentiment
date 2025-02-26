import torch
from transformers import pipeline, AutoTokenizer
import re

class LlamaTextEnhancer:
    def __init__(self, model_id="meta-llama/Llama-3.2-1B-Instruct", segment_size=1000, overlap_size=200):
        self.segment_size = segment_size
        self.overlap_size = overlap_size

        self.pipe = pipeline("text-generation", model=model_id, torch_dtype=torch.bfloat16, device_map="auto")
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.eos_token_id = self.tokenizer.eos_token_id

    def _split_text(self, text):
        """Splits text into overlapping segments."""
        words = text.split()
        segments = []
        start = 0

        while start < len(words):
            end = start + self.segment_size
            segment = words[start:end]
            segments.append(" ".join(segment))
            start += (self.segment_size - self.overlap_size)
        
        return segments

    def _enhance_segment(self, segment):
        input_tokens = len(self.tokenizer.encode(segment))
        output_tokens = int(input_tokens * 1.2)

        prompt = (
            "Reescreva o texto a seguir corrigindo a pontuação e concordância em português. "
            f"Texto original: {segment}\n\n"
            "Retorne APENAS o texto corrigido, sem explicações adicionais.\n\n"
            "Texto corrigido:"
        )
        
        result = self.pipe(
            prompt, 
            max_new_tokens=output_tokens, 
            temperature=0.3,
            top_p=0.9, 
            repetition_penalty=1.1,
            do_sample=True
        )
        
        # Extract only the corrected text
        generated_text = result[0]["generated_text"]
        
        # Extract text after "Texto corrigido:" but stop at the first indicator of explanations
        enhanced_text = generated_text.split("Texto corrigido:")[-1].strip()
        
        # Remove any explanations that might follow
        explanation_starters = [
            "Aqui estão", 
            "Alterações:", 
            "Explicação:", 
            "Mudanças:", 
            "Aqui está",
            "*",
            "Notas:",
            "Obs:",
            "Observações:"
        ]
        
        for starter in explanation_starters:
            if starter in enhanced_text:
                enhanced_text = enhanced_text.split(starter)[0].strip()
        
        # Use regex to detect paragraphs that look like explanations
        pattern = r"\n\n.*?(alteraç|mudanç|correç|modificaç|ajust)"
        match = re.search(pattern, enhanced_text, re.IGNORECASE)
        if match:
            enhanced_text = enhanced_text[:match.start()].strip()
            
        return enhanced_text

    def _merge_segments(self, enhanced_segments):
        if not enhanced_segments:
            return ""
            
        merged_text = enhanced_segments[0]
        
        for i in range(1, len(enhanced_segments)):
            # Handle case where segments might be empty
            if not enhanced_segments[i]:
                continue
                
            # Get words from current segment
            current_words = enhanced_segments[i].split()
            
            # Ensure we have enough words to consider overlap
            if len(current_words) > self.overlap_size:
                merged_text += " " + " ".join(current_words[self.overlap_size:])
            else:
                # If segment is smaller than overlap, just append it
                merged_text += " " + enhanced_segments[i]
        
        return merged_text

    def enhance_text(self, text):
        segments = self._split_text(text)
        enhanced_segments = [self._enhance_segment(segment) for segment in segments]

        return self._merge_segments(enhanced_segments)


if __name__ == "__main__":
    pipeline = LlamaTextEnhancer()
    
    sample_text = """
    Olá pessoal meu nome é João Luiz Braga sou Analista aqui na encora 
    vim falar um pouquinho sobre o mês de junho um pouco atrasado mas 
    hoje é dia 10 agora são quase nove quase 10 horas da manhã Bom vamos 
    lá foi um mês difícil né porque no sentido de que a bolsa subiu muito 
    foi difícil acompanhar a gente tá até um ano bom mas um mês a gente 
    ficou um pouco para trás
    """.replace("\n", " ")

    enhanced_text = pipeline.enhance_text(sample_text)
    print(enhanced_text)