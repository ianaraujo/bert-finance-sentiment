# LLM Equity Market Sentiment Analysis

```bash
docker run -it --gpus all \
  -v /home/ubuntu/llm-asset-sentiment/data:/app/data \
  -v /home/ubuntu/llm-asset-sentiment/models:/app/models \
  trainer \
  python3 train_domain.py
```

14:36

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
