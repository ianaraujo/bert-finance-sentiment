import torch
from pathlib import Path
from peft import PeftModel, PeftConfig

from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
)


def merge_lora(adapter_dir: str, output_dir: str) -> None:
    adapter_dir = Path(adapter_dir)
    output_dir  = Path(output_dir)

    # 1) Read the adapter’s config to discover which base checkpoint to load
    peft_cfg       = PeftConfig.from_pretrained(adapter_dir)
    base_model_dir = peft_cfg.base_model_name_or_path

    # 2) Load base model & tokenizer
    tokenizer  = AutoTokenizer.from_pretrained(base_model_dir, do_lower_case=False)
    
    base_model = AutoModelForSequenceClassification.from_pretrained(
        base_model_dir,
        num_labels=3,
    )

    # 3) Attach adapter weights
    model = PeftModel.from_pretrained(base_model, adapter_dir)
    model.eval()

    # 4) Merge LoRA → base weights and drop PEFT wrappers
    merged_model = model.merge_and_unload()

    # 5) Save the fully merged model + tokenizer
    merged_model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)

    print(f"✔  Merged model written to: {output_dir.resolve()}\n"
          f"   Load with: AutoModelForSequenceClassification.from_pretrained('{output_dir}')")


if __name__ == "__main__":
    merge_lora(
        adapter_dir="models/bert-portuguese-finance-sentiment",
        output_dir="models/sentiment-bert-portuguese-asset-management-cls",
    )
