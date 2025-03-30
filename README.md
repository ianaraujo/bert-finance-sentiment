# LLM Equity Market Sentiment Analysis

```bash
docker run -it --gpus all \
  -v /home/ubuntu/llm-asset-sentiment/data:/app/data \
  -v /home/ubuntu/llm-asset-sentiment/models:/app/models \
  trainer \
  python3 train_domain.py
```

## Domain Fine-Tuning

Total training time: 1h24m

```bash
CUDA: 12.6.3
GPU: Tesla T4

{'loss': 2.344, 'grad_norm': 16.87717628479004, 'learning_rate': 9.905513345022405e-05, 'epoch': 0.03}
{'loss': 2.2011, 'grad_norm': 14.40652084350586, 'learning_rate': 9.808104422365089e-05, 'epoch': 0.06}
{'loss': 2.1671, 'grad_norm': 11.090062141418457, 'learning_rate': 9.710695499707773e-05, 'epoch': 0.09}
{'loss': 2.1065, 'grad_norm': 12.624106407165527, 'learning_rate': 9.613286577050458e-05, 'epoch': 0.12}
{'loss': 2.2011, 'grad_norm': 11.588488578796387, 'learning_rate': 9.515877654393142e-05, 'epoch': 0.15}

[...]

{'loss': 1.5105, 'grad_norm': 9.222599983215332, 'learning_rate': 4.5977011494252875e-06, 'epoch': 2.86}
{'loss': 1.5086, 'grad_norm': 8.752577781677246, 'learning_rate': 3.623611922852133e-06, 'epoch': 2.89}
{'loss': 1.533, 'grad_norm': 7.782713890075684, 'learning_rate': 2.6495226962789796e-06, 'epoch': 2.92}
{'loss': 1.525, 'grad_norm': 9.998917579650879, 'learning_rate': 1.6754334697058252e-06, 'epoch': 2.95}
{'loss': 1.5437, 'grad_norm': 11.523236274719238, 'learning_rate': 7.01344243132671e-07, 'epoch': 2.98}

{'eval_loss': 1.5280498266220093, 'eval_runtime': 68.0097, 'eval_samples_per_second': 100.603, 'eval_steps_per_second': 6.293, 'epoch': 3.0}

{'train_runtime': 5047.6235, 'train_samples_per_second': 32.532, 'train_steps_per_second': 2.034, 'train_loss': 1.7659376937001159, 'epoch': 3.0}

Perplexity: 4.81
```

## Scraper

Número de cartas por gestora:

- [x] Guepardo (111)
- [x] IP Capital (94)
- [x] Dynamo (87)
- [x] Dahlia Capital (80)
- [x] Kapitalo (74)
- [x] Ártica (61)
- [x] Encore (58)
- [x] Genoa Capital (55)
- [x] Alpha Key (36)
- [x] Mar Asset (20)
- [x] Alaska (18)
- [x] Squadra (17)

Total: 711 cartas

## TO-DO

- Fix DahliaCapital scraper
