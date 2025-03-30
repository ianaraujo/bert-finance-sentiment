import json
import torch
import random
import argparse
from typing import List, Dict

from datasets import Dataset, DatasetDict
from peft import LoraConfig, get_peft_model

from transformers import (
    AutoTokenizer, 
    PreTrainedTokenizer,
    AutoModelForMaskedLM, 
    AutoModelForSequenceClassification,
    TrainingArguments, 
    Trainer, 
    DataCollatorForLanguageModeling,
    DataCollatorWithPadding
)

from train_domain import DomainTrainer


class SentimentTrainer(DomainTrainer):
    def __init__(self, domain_model: str, sentiment_data_path: str, num_labels: int = 3, smoke_test: bool = False):
        self.domain_model = domain_model
        self.sentiment_data_path = sentiment_data_path
        self.num_labels = num_labels
        self.smoke_test = smoke_test

        self.tokenizer = AutoTokenizer.from_pretrained(domain_model, do_lower_case=False)

        self.model = AutoModelForSequenceClassification.from_pretrained(
            domain_model,
            num_labels=self.num_labels
        )

        # Create training arguments
        self.training_args = TrainingArguments(
            output_dir="models/bert-portuguese-mkt-sentiment",
            overwrite_output_dir=True,
            evaluation_strategy="epoch",
            learning_rate=1e-4,
            per_device_train_batch_size=16,
            per_device_eval_batch_size=16,
            num_train_epochs=3,
            weight_decay=0.01,
            logging_steps=100,
            save_steps=1000,
            fp16=True
        )

        if smoke_test:
            self.training_args.max_steps = 10
            self.training_args.per_device_train_batch_size = 4
            self.training_args.per_device_eval_batch_size = 4
            self.training_args.save_steps = 999999
            self.training_args.logging_steps = 5

    def _read_training_data(self, path: str) -> List[Dict]:
        data: List[Dict] = []

        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                data.append(json.loads(line))

        return data

    def _train_test_split(self, data: List[Dict], test_size: float = 0.2) -> DatasetDict:
        if self.smoke_test:
            data = random.sample(data, min(100, len(data)))

        dataset = Dataset.from_list(data)
        train_test_split = dataset.train_test_split(test_size=test_size, seed=42, shuffle=True)
        val_test_split = train_test_split['test'].train_test_split(test_size=0.5, seed=42)

        return DatasetDict({
            'train': train_test_split['train'],
            'validation': val_test_split['train'],
            'test': val_test_split['test']
        })

    def _tokenize_function(self, examples):
        return self.tokenizer(
            examples["text"],
            truncation=True,
            padding="max_length",
            max_length=512
        )
    
    def _default_data_collator(features):
        return {
            "input_ids": torch.tensor([f["input_ids"] for f in features], dtype=torch.long),
            "attention_mask": torch.tensor([f["attention_mask"] for f in features], dtype=torch.long),
            "labels": torch.tensor([f["label"] for f in features], dtype=torch.long),
        }

    def run_sentiment_training(self):
        data = self._read_training_data(self.sentiment_data_path)
        dataset_dict = self._train_test_split(data)

        tokenized_ds = dataset_dict.map(
            self._tokenize_function,
            batched=True,
            remove_columns=["text"]
        )

        trainer = Trainer(
            model=self.model,
            args=self.training_args,
            train_dataset=tokenized_ds["train"],
            eval_dataset=tokenized_ds["validation"],
            data_collator=self._default_data_collator
        )

        # Train
        trainer.train()

        # Evaluate
        results = trainer.evaluate(tokenized_ds["test"])
        print("Test set results:", results)
        # If you want accuracy/F1, you can do:
        # predictions = trainer.predict(tokenized_ds["test"])
        # use sklearn metrics with predictions.label_ids and predictions.predictions

        # Save final sentiment model
        trainer.save_model("models/bert-sentiment-classification")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sentiment Fine-Tuning')
    parser.add_argument('--smoke-test', action='store_true', help='Run quick smoke test')
    args = parser.parse_args()

    # 1) First, you'd have run DomainTrainer to produce a domain-finetuned model checkpoint
    #    e.g., "models/bert-domain-finetuned"

    domain_checkpoint = "models/bert-domain-finetuned"  # from domain trainer
    sentiment_data_path = "data/sentiment_training.jsonl"

    # 2) Now, create our new trainer for sentiment
    sentiment_trainer = SentimentTrainer(
        domain_checkpoint=domain_checkpoint,
        sentiment_data_path=sentiment_data_path,
        num_labels=3, 
        smoke_test=args.smoke_test
    )

    # 3) Run sentiment fine-tuning
    sentiment_trainer.run_sentiment_training()
