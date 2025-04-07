import csv
import torch
import argparse
import warnings
import numpy as np
from typing import List, Dict
from sklearn.metrics import accuracy_score, f1_score

from peft import LoraConfig, get_peft_model, TaskType

from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    TrainingArguments, 
    Trainer,
    logging,
)

from train_domain import DomainTrainer

logging.set_verbosity_error()
warnings.filterwarnings("ignore", message="Can't initialize NVML")


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

        self.model.config.label2id = {"NEGATIVE": 0, "POSITIVE": 1, "NEUTRAL": 2}
        self.model.config.id2label = {0: "NEGATIVE", 1: "POSITIVE", 2: "NEUTRAL"}

        self.lora_config = LoraConfig(
            r=8,             # Rank
            lora_alpha=32,   # LoRA alpha
            target_modules=["query", "value"], # BERT-based models
            lora_dropout=0.05,
            bias="none",
            task_type=TaskType.SEQ_CLS,
        )

        self.training_args = TrainingArguments(
            overwrite_output_dir=True,
            eval_strategy="epoch",
            learning_rate=1e-4,
            per_device_train_batch_size=16,
            per_device_eval_batch_size=16,
            num_train_epochs=3,
            weight_decay=0.01,
            logging_steps=50,
            save_strategy="no",
            remove_unused_columns=False,
            fp16=True
        )

        if smoke_test:
            self.training_args.max_steps = 10
            self.training_args.per_device_train_batch_size = 4
            self.training_args.per_device_eval_batch_size = 4
            self.training_args.logging_steps = 5

        print("Using device:", torch.device("cuda" if torch.cuda.is_available() else "cpu"))

        if torch.cuda.is_available():
            print("GPU:", torch.cuda.get_device_name(0))

    def _read_training_data(self, path: str) -> List[Dict]:
        data: List[Dict] = []
        
        with open(path, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)     
            for row in reader:
                data.append(dict(row))

        return data

    def _default_data_collator(self, features):
        return {
            "input_ids": torch.tensor([f["input_ids"] for f in features], dtype=torch.long),
            "attention_mask": torch.tensor([f["attention_mask"] for f in features], dtype=torch.long),
            "labels": torch.tensor([int(f["label"]) for f in features], dtype=torch.long),
        }

    def run(self):
        data = self._read_training_data(self.sentiment_data_path)
        dataset_dict = self._train_test_split(data)
        tokenized_ds = dataset_dict.map(self._tokenize_function, batched=True)

        peft_model = get_peft_model(self.model, self.lora_config)
        peft_model.print_trainable_parameters() # print()

        trainer = Trainer(
            model=peft_model,
            args=self.training_args,
            train_dataset=tokenized_ds["train"],
            eval_dataset=tokenized_ds["validation"],
            data_collator=self._default_data_collator,
        )

        trainer.train()
        trainer.save_model("models/bert-portuguese-finance-sentiment")

        # evaluate
        predictions = trainer.predict(tokenized_ds["test"])
        preds = np.argmax(predictions.predictions, axis=1)
        labels = predictions.label_ids
        acc_domain = accuracy_score(labels, preds)
        f1_domain = f1_score(labels, preds, average="macro")
        
        print(f"Domain Adapted Model - Accuracy: {acc_domain:.4f}, F1: {f1_domain:.4f}")

        # evaluate base model: neuralmind/bert-base-portuguese-cased
        
        base_model = AutoModelForSequenceClassification.from_pretrained(
            "neuralmind/bert-base-portuguese-cased",
            num_labels=self.num_labels
        )

        base_model.to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))
        
        base_trainer = Trainer(
            model=base_model,
            args=self.training_args,
            eval_dataset=tokenized_ds["test"],
            data_collator=self._default_data_collator,
        )

        base_predictions = base_trainer.predict(tokenized_ds["test"])
        base_preds = np.argmax(base_predictions.predictions, axis=1)
        acc_base = accuracy_score(labels, base_preds)
        f1_base = f1_score(labels, base_preds, average="macro")
        
        print(f"Base Model - Accuracy: {acc_base:.4f}, F1: {f1_base:.4f}")

        # evaluate benchmark model: lucas-leme/FinBERT-PT-BR
        
        benchmark_model = AutoModelForSequenceClassification.from_pretrained(
            "lucas-leme/FinBERT-PT-BR",
            num_labels=self.num_labels
        )
        
        benchmark_model.config.num_labels = self.num_labels
        benchmark_model.config.problem_type = "single_label_classification"
        benchmark_model.to(torch.device("cuda" if torch.cuda.is_available() else "cpu"))
        
        benchmark_trainer = Trainer(
            model=benchmark_model,
            args=self.training_args,
            eval_dataset=tokenized_ds["test"],
            data_collator=self._default_data_collator,
        )
        
        benchmark_predictions = benchmark_trainer.predict(tokenized_ds["test"])
        benchmark_preds = np.argmax(benchmark_predictions.predictions, axis=1)
        acc_benchmark = accuracy_score(labels, benchmark_preds)
        f1_benchmark = f1_score(labels, benchmark_preds, average="macro")
        
        print(f"Benchmark Model (FinBERT-PT-BR) - Accuracy: {acc_benchmark:.4f}, F1: {f1_benchmark:.4f}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sentiment Fine-Tuning')
    parser.add_argument('--smoke-test', action='store_true', help='Run quick smoke test')
    args = parser.parse_args()

    domain_checkpoint = "models/bert-portuguese-asset-management"  # from domain trainer

    sentiment_data_path = "data/cls_training_sample.csv" if args.smoke_test else "data/cls_training.csv"
    
    sentiment_trainer = SentimentTrainer(
        domain_model=domain_checkpoint,
        sentiment_data_path=sentiment_data_path,
        num_labels=3, 
        smoke_test=args.smoke_test
    )

    sentiment_trainer.run()
