# LLM Equity Market Sentiment Analysis

```bash
docker build -t trainer .
```

```bash
docker run -it --gpus all \
  -v /home/ubuntu/bert-finance-sentiment/data:/app/data \
  -v /home/ubuntu/bert-finance-sentiment/models:/app/models \
  trainer \
  python3 train_domain.py
```

## Domain Fine-Tuning

Total training time: 1h24m

```bash
CUDA Version 12.6.3
GPU: Tesla T4

{'loss': 2.1037, 'grad_norm': 11.860575675964355, 'learning_rate': 9.822539334065131e-05, 'epoch': 0.054884742041712405}
{'loss': 1.9968, 'grad_norm': 12.030468940734863, 'learning_rate': 9.63959019392609e-05, 'epoch': 0.10976948408342481}
{'loss': 1.9211, 'grad_norm': 13.596546173095703, 'learning_rate': 9.456641053787048e-05, 'epoch': 0.16465422612513722}
{'loss': 1.995, 'grad_norm': 12.904857635498047, 'learning_rate': 9.273691913648006e-05, 'epoch': 0.21953896816684962}
{'loss': 1.9074, 'grad_norm': 13.937590599060059, 'learning_rate': 9.090742773508965e-05, 'epoch': 0.27442371020856204}

{...}

{'loss': 1.4351, 'grad_norm': 9.073331832885742, 'learning_rate': 6.7691181851445296e-06, 'epoch': 2.7991218441273324}
{'loss': 1.4691, 'grad_norm': 11.75009536743164, 'learning_rate': 4.939626783754116e-06, 'epoch': 2.854006586169045}
{'loss': 1.4541, 'grad_norm': 9.405517578125, 'learning_rate': 3.110135382363703e-06, 'epoch': 2.9088913282107574}
{'loss': 1.357, 'grad_norm': 9.749642372131348, 'learning_rate': 1.2806439809732895e-06, 'epoch': 2.96377607025247}

{'eval_loss': 1.4777565002441406, 'eval_runtime': 35.2411, 'eval_samples_per_second': 103.374, 'eval_steps_per_second': 6.47, 'epoch': 3.0}

{'train_runtime': 2612.316, 'train_samples_per_second': 33.469, 'train_steps_per_second': 2.092, 'train_loss': 1.666383633716526, 'epoch': 3.0}

Base model Perplexity: 10.95
Fine-tuned model Perplexity: 4.29
```

```bash
Using device: cuda
GPU: Tesla T4

trainable params: 1,181,955 || all params: 110,107,398 || trainable%: 1.0735

{'eval_loss': 1.0101139545440674, 'eval_runtime': 0.7377, 'eval_samples_per_second': 135.557, 'eval_steps_per_second': 5.422, 'epoch': 1.0}
{'loss': 0.9971, 'grad_norm': 1.6517367362976074, 'learning_rate': 7.2e-05, 'epoch': 2.0}
{'eval_loss': 0.9652484059333801, 'eval_runtime': 0.7308, 'eval_samples_per_second': 136.834, 'eval_steps_per_second': 5.473, 'epoch': 2.0}
{'eval_loss': 0.9156267046928406, 'eval_runtime': 0.7314, 'eval_samples_per_second': 136.717, 'eval_steps_per_second': 5.469, 'epoch': 3.0}
{'loss': 0.8824, 'grad_norm': 1.7996125221252441, 'learning_rate': 4.342857142857143e-05, 'epoch': 4.0}
{'eval_loss': 0.8471986651420593, 'eval_runtime': 0.7362, 'eval_samples_per_second': 135.831, 'eval_steps_per_second': 5.433, 'epoch': 4.0}
{'eval_loss': 0.8047136068344116, 'eval_runtime': 0.7361, 'eval_samples_per_second': 135.856, 'eval_steps_per_second': 5.434, 'epoch': 5.0}
{'loss': 0.7747, 'grad_norm': 1.119484782218933, 'learning_rate': 1.4857142857142858e-05, 'epoch': 6.0}
{'eval_loss': 0.7893567681312561, 'eval_runtime': 0.7396, 'eval_samples_per_second': 135.207, 'eval_steps_per_second': 5.408, 'epoch': 6.0}
{'eval_loss': 0.782565712928772, 'eval_runtime': 0.7395, 'eval_samples_per_second': 135.232, 'eval_steps_per_second': 5.409, 'epoch': 7.0}
{'train_runtime': 108.0543, 'train_samples_per_second': 51.826, 'train_steps_per_second': 1.62, 'train_loss': 0.8642222377232143, 'epoch': 7.0}

Base Model - Accuracy: 0.3200, F1: 0.2249

Domain Adapted Model - Accuracy: 0.7300, F1: 0.4582
Benchmark Model FinBERT-PT-BR - Accuracy: 0.4800, F1: 0.3401
```

## Scraper

Número de cartas por gestora:

- [x] Guepardo (111)
- [x] IP Capital (95)
- [x] Dahlia Capital (81)
- [x] Dynamo (80)
- [x] Kapitalo (74)
- [x] Ártica (62)
- [x] Encore (58)
- [x] Genoa Capital (56)
- [x] Alpha Key (35)
- [x] Mar Asset (20)
- [x] Alaska (18)
- [x] Squadra (17)

Total: 707 cartas
