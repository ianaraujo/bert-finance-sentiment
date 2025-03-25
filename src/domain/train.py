import json
from typing import List, Dict

from datasets import Dataset, DatasetDict
from peft import LoraConfig, get_peft_model, TaskType

from transformers import (
    AutoTokenizer, 
    AutoModelForMaskedLM, 
    TrainingArguments, 
    Trainer, 
    DataCollatorForLanguageModeling
)


class DomainTrainer:

    def __init__(self, model_name: str, path: str):
        self.path = path
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForMaskedLM.from_pretrained(model_name)

        self.lora_config = LoraConfig(
            r=8,             # Rank
            lora_alpha=32,   # LoRA alpha
            target_modules=["query", "value"], # BERT-based models
            lora_dropout=0.05,
            bias="none",
            task_type=TaskType.MASKED_LM
        )

        self.training_args = TrainingArguments(
            output_dir="./bert-portuguese-asset-management",
            evaluation_strategy="epoch",
            learning_rate=1e-4,
            per_device_train_batch_size=16,
            per_device_eval_batch_size=16,
            num_train_epochs=3,
            weight_decay=0.01,
            logging_steps=100,
            save_steps=1000,
            remove_unused_columns=False,
            fp16=True
        )

    def _tokenize_function(self, examples):
        return self.tokenizer(
            examples["text"], padding="max_length", truncation=True, max_length=512
        )

    def _read_training_data(path: str) -> List[Dict]:
        data: List[Dict] = []

        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                data.append(json.loads(line))

        return data
    
    def _train_test_split(self, data: List[Dict], test_size: float = 0.2) -> DatasetDict:
        dataset = Dataset.from_list(data)

        train_test_split = dataset.train_test_split(test_size=test_size)
        validation_test_split = train_test_split['test'].train_test_split(test_size=0.5)

        train = train_test_split['train']
        validation = validation_test_split['train']
        test = validation_test_split['test']

        return DatasetDict({
            'train': train,
            'validation': validation,
            'test': test
        })
    
    def train(self):
        # read data and create train/validation/test split
        data = self._read_training_data(self.path)
        dataset_dict = self._train_test_split(data)

        # tokenize dataset
        tokenized_dataset = dataset_dict.map(self._tokenize_function, batched=True)

        peft_model = get_peft_model(self.model, self.lora_config)
        print('Trainable parameters: ', peft_model.print_trainable_parameters())

        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer, 
            mlm=True, 
            mlm_probability=0.15
        )

        trainer = Trainer(
            model=peft_model,
            args=self.training_args,
            train_dataset=tokenized_dataset['train'],
            eval_dataset=tokenized_dataset['validation'],
            data_collator=data_collator
        )


        trainer.train()

        results = trainer.evaluate()
        print(results)

if __name__ == '__main__':
    model_name = "neuralmind/bert-base-portuguese-cased"
    path = 'data/domain_training.jsonl'

    trainer = DomainTrainer(model_name, path)
    # trainer.train()

