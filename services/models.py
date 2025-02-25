import torch
from transformers import pipeline, AutoTokenizer

class LlamaTextEnhancer:
    def __init__(self, model_id="meta-llama/Llama-3.2-1B-Instruct", segment_size=1000, overlap_size=200):
        self.segment_size = segment_size
        self.overlap_size = overlap_size

        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.pipe = pipeline("text-generation", model=model_id, torch_dtype=torch.bfloat16, device_map="auto")
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
        prompt = (
            "Por favor, corrija a pontuação e a gramática do seguinte texto em português:\n\n"
            f"{segment}\n\nTexto corrigido:"
        )
        result = self.pipe(prompt, max_new_tokens=512, temperature=0.7, top_p=0.9, repetition_penalty=1.1)
        enhanced_text = result[0]["generated_text"]
        
        return enhanced_text

    def _merge_segments(self, enhanced_segments):
        merged_text = enhanced_segments[0]
        
        for i in range(1, len(enhanced_segments)):
            merged_text += " " + " ".join(enhanced_segments[i].split()[self.overlap_size:])
        
        return merged_text

    def enhance_text(self, text):
        segments = self._split_text(text)
        enhanced_segments = [self._enhance_segment(segment) for segment in segments]

        return self._merge_segments(enhanced_segments)


if __name__ == "__main__":
    pipeline = LlamaTextEnhancer(segment_size=50, overlap_size=10)
    
    sample_text = """
    ola meu nome e maria eu gosto de aprender linguas hoje vamos falar sobre inteligencia artificial
    e suas aplicacoes mas antes disso vamos entender um pouco sobre o que e inteligencia artificial
    """.replace("\n", " ")

    enhanced_text = pipeline.enhance_text(sample_text)
    print("Texto corrigido:\n", enhanced_text)
