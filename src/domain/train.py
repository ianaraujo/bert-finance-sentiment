import json
import math
import random
import argparse
from typing import List, Dict

from datasets import Dataset, DatasetDict
from peft import LoraConfig, get_peft_model

from transformers import (
    AutoTokenizer, 
    PreTrainedTokenizer,
    AutoModelForMaskedLM, 
    TrainingArguments, 
    Trainer, 
    DataCollatorForLanguageModeling
)


class DomainTrainer:

    def __init__(self, model_name: str, path: str, smoke_test: bool = False) -> None:
        self.path = path

        self.model = AutoModelForMaskedLM.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, do_lower_case=False)

        self.lora_config = LoraConfig(
            r=8,             # Rank
            lora_alpha=32,   # LoRA alpha
            target_modules=["query", "value"], # BERT-based models
            lora_dropout=0.05,
            bias="none",
            # task_type=TaskType.MASKED_LM
        )

        self.training_args = TrainingArguments(
            output_dir="models/bert-portuguese-asset-management",
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
            # max_steps overrides num_train_epochs, so the training ends quickly.
            self.training_args.max_steps = 10

            self.training_args.per_device_train_batch_size = 4
            self.training_args.per_device_eval_batch_size = 4

            # turn off checkpoint saving for speed
            self.training_args.save_steps = 999999

            # rreduce or turn off logging
            self.training_args.logging_steps = 5

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

        peft_model = get_peft_model(self.model, self.lora_config)

        peft_model.print_trainable_parameters() # print()

        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer, 
            mlm=True, 
            mlm_probability=0.15
        )
        
        # evaluate the base model
        base_trainer = Trainer(
            model=self.model,
            args=self.training_args,
            eval_dataset=tokenized_dataset['validation'],
            data_collator=data_collator
        )

        base_eval_results = base_trainer.evaluate()
        print(f"Base Model Perplexity: {math.exp(base_eval_results['eval_loss']):.2f}")

        # create a new trainer for fine-tuning the PEFT model
        trainer = Trainer(
            model=peft_model,
            args=self.training_args,
            train_dataset=tokenized_dataset['train'],
            eval_dataset=tokenized_dataset['validation'],
            data_collator=data_collator
        )

        trainer.train()

        eval_results = trainer.evaluate()
        print(eval_results)
        # print(f">>> Perplexity Post-Training: {math.exp(eval_results['eval_loss']):.2f}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Train a domain-specific language model')
    parser.add_argument('--smoke-test', action='store_true', help='Run in smoke test mode (fast training with sample data)')
    args = parser.parse_args()

    model_name = "neuralmind/bert-base-portuguese-cased"
    path = 'data/domain_training.jsonl'

    trainer = DomainTrainer(model_name, path, smoke_test=args.smoke_test)

    trainer.run()

