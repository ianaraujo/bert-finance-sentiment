import json
import math
import torch
import random
import argparse
import warnings
from typing import List, Dict

from datasets import Dataset, DatasetDict
# from peft import LoraConfig, get_peft_model

from transformers import (
    AutoTokenizer, 
    PreTrainedTokenizer,
    AutoModelForMaskedLM, 
    TrainingArguments, 
    Trainer, 
    DataCollatorForLanguageModeling,
    logging,
)

logging.set_verbosity_error()
warnings.filterwarnings("ignore", message="Can't initialize NVML")


class DomainTrainer:

    def __init__(self, base_model: str, path: str, smoke_test: bool = False) -> None:
        self.path = path

        self.base_model_name = base_model

        self.base_model = AutoModelForMaskedLM.from_pretrained(base_model)
        self.tokenizer = AutoTokenizer.from_pretrained(base_model, do_lower_case=False)

        self.model_name = 'bert-portuguese-asset-management'

        self.training_args = TrainingArguments(
            output_dir=f"models/{self.model_name}",
            overwrite_output_dir=True,
            eval_strategy="epoch",
            learning_rate=1e-4,
            per_device_train_batch_size=8,
            per_device_eval_batch_size=8,
            num_train_epochs=3,
            weight_decay=0.01,
            logging_steps=100,
            save_strategy="no",
            fp16=True
        )

        if smoke_test:
            # max_steps overrides num_train_epochs, so the training ends quickly.
            self.training_args.max_steps = 10

            self.training_args.per_device_train_batch_size = 4
            self.training_args.per_device_eval_batch_size = 4

            # rreduce or turn off logging
            self.training_args.logging_steps = 5

        print("Using device:", torch.device("cuda" if torch.cuda.is_available() else "cpu"))

        if torch.cuda.is_available():
            print("GPU:", torch.cuda.get_device_name(0))

    def _tokenize_function(self, examples) -> PreTrainedTokenizer:
        return self.tokenizer(
            examples["text"], 
            truncation=True,           # ensures sequences longer than max_length are cut off
            padding="max_length",      # pads all sequences to the max_length
            max_length=512             # sets the maximum length
        )

    def _read_training_data(self, path: str) -> List[Dict]:
        data: List[Dict] = []

        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                data.append(json.loads(line))

        return data
    
    def _train_test_split(self, data: List[Dict], test_size: float = 0.2) -> DatasetDict:
        
        if self.training_args.max_steps == 10:
            data = random.sample(data, 100)
        
        dataset = Dataset.from_list(data)

        train_test_split = dataset.train_test_split(test_size=test_size, seed=55, shuffle=True)
        validation_test_split = train_test_split['test'].train_test_split(test_size=0.5)

        train = train_test_split['train']
        validation = validation_test_split['train']
        test = validation_test_split['test']

        return DatasetDict({
            'train': train,
            'validation': validation,
            'test': test
        })
    
    def run(self) -> None:
        # read data and create train/validation/test split
        data = self._read_training_data(self.path)
        dataset_dict = self._train_test_split(data)

        # tokenize dataset
        tokenized_dataset = dataset_dict.map(
            self._tokenize_function, 
            batched=True,
            remove_columns=["text"]
        )

        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer, 
            mlm=True, 
            mlm_probability=0.15
        )

        # create a new trainer for fine-tuning the PEFT model
        trainer = Trainer(
            model=self.base_model,
            args=self.training_args,
            train_dataset=tokenized_dataset['train'],
            eval_dataset=tokenized_dataset['validation'],
            data_collator=data_collator
        )

        trainer.train()

        eval_results_ft = trainer.evaluate()
        
        if 'eval_loss' in eval_results_ft:
            print(f"Fine-tuned model Perplexity: {math.exp(eval_results_ft['eval_loss']):.2f}")

        # reload the original base model for evaluation
        base_model_original = AutoModelForMaskedLM.from_pretrained(self.base_model_name)
        
        base_trainer = Trainer(
            model=base_model_original,
            args=self.training_args,
            eval_dataset=tokenized_dataset['validation'],
            data_collator=data_collator
        )

        eval_results_base = base_trainer.evaluate()
        
        if 'eval_loss' in eval_results_base:
            print(f"Base model Perplexity: {math.exp(eval_results_base['eval_loss']):.2f}")

        # save the fine-tuned model
        trainer.save_model(f"models/{self.model_name}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train a domain-specific language model')
    parser.add_argument('--smoke-test', action='store_true', help='Run in smoke test mode (fast training with sample data)')
    args = parser.parse_args()

    base_model = "neuralmind/bert-base-portuguese-cased" if args.smoke_test else "neuralmind/bert-large-portuguese-cased"
    path = 'data/domain_training.jsonl'

    trainer = DomainTrainer(base_model, path, smoke_test=args.smoke_test)

    trainer.run()

