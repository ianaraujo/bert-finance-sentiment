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
==========
== CUDA ==
==========

CUDA Version 12.6.3

Container image Copyright (c) 2016-2023, NVIDIA CORPORATION & AFFILIATES. All rights reserved.

This container image and its contents are governed by the NVIDIA Deep Learning Container License.
By pulling and using the container, you accept the terms and conditions of this license:
https://developer.nvidia.com/ngc/nvidia-deep-learning-container-license

A copy of this license is made available in this container at /NGC-DL-CONTAINER-LICENSE for your convenience.

config.json: 100%|█████████████████████████████████████████████████████████████████| 647/647 [00:00<00:00, 4.70MB/s]
pytorch_model.bin: 100%|█████████████████████████████████████████████████████████| 438M/438M [00:05<00:00, 80.6MB/s]
tokenizer_config.json: 100%|██████████████████████████████████████████████████████| 43.0/43.0 [00:00<00:00, 227kB/s]
vocab.txt: 100%|█████████████████████████████████████████████████████████████████| 210k/210k [00:00<00:00, 76.5MB/s]
added_tokens.json: 100%|█████████████████████████████████████████████████████████| 2.00/2.00 [00:00<00:00, 10.6kB/s]
special_tokens_map.json: 100%|██████████████████████████████████████████████████████| 112/112 [00:00<00:00, 551kB/s]
model.safetensors:  34%|███████████████████▍                                      | 147M/438M [00:00<00:01, 195MB/s]Using device: cuda
GPU: Tesla T4
model.safetensors: 100%|██████████████████████████████████████████████████████████| 438M/438M [00:02<00:00, 187MB/s]
Map: 100%|███████████████████████████████████████████████████████████| 29144/29144 [00:09<00:00, 3041.21 examples/s]
Map: 100%|█████████████████████████████████████████████████████████████| 3643/3643 [00:01<00:00, 2806.39 examples/s]
Map: 100%|█████████████████████████████████████████████████████████████| 3644/3644 [00:01<00:00, 3152.52 examples/s]
{'loss': 2.1037, 'grad_norm': 11.860575675964355, 'learning_rate': 9.822539334065131e-05, 'epoch': 0.054884742041712405}
{'loss': 1.9968, 'grad_norm': 12.030468940734863, 'learning_rate': 9.63959019392609e-05, 'epoch': 0.10976948408342481}
{'loss': 1.9211, 'grad_norm': 13.596546173095703, 'learning_rate': 9.456641053787048e-05, 'epoch': 0.16465422612513722}
{'loss': 1.995, 'grad_norm': 12.904857635498047, 'learning_rate': 9.273691913648006e-05, 'epoch': 0.21953896816684962}
{'loss': 1.9074, 'grad_norm': 13.937590599060059, 'learning_rate': 9.090742773508965e-05, 'epoch': 0.27442371020856204}
{'loss': 1.9039, 'grad_norm': 10.837482452392578, 'learning_rate': 8.907793633369924e-05, 'epoch': 0.32930845225027444}
{'loss': 1.9107, 'grad_norm': 10.09453296661377, 'learning_rate': 8.724844493230883e-05, 'epoch': 0.38419319429198684}
{'loss': 1.8785, 'grad_norm': 9.419754981994629, 'learning_rate': 8.541895353091841e-05, 'epoch': 0.43907793633369924}
{'loss': 1.882, 'grad_norm': 12.112176895141602, 'learning_rate': 8.358946212952799e-05, 'epoch': 0.49396267837541163}
{'loss': 1.821, 'grad_norm': 10.500834465026855, 'learning_rate': 8.175997072813758e-05, 'epoch': 0.5488474204171241}
{'loss': 1.9222, 'grad_norm': 11.72229290008545, 'learning_rate': 7.993047932674716e-05, 'epoch': 0.6037321624588364}
{'loss': 1.8617, 'grad_norm': 9.335447311401367, 'learning_rate': 7.810098792535676e-05, 'epoch': 0.6586169045005489}
{'loss': 1.8902, 'grad_norm': 9.3919038772583, 'learning_rate': 7.627149652396634e-05, 'epoch': 0.7135016465422612}
{'loss': 1.8292, 'grad_norm': 11.963886260986328, 'learning_rate': 7.444200512257594e-05, 'epoch': 0.7683863885839737}
{'loss': 1.7979, 'grad_norm': 12.9717378616333, 'learning_rate': 7.261251372118552e-05, 'epoch': 0.823271130625686}
{'loss': 1.7764, 'grad_norm': 10.310154914855957, 'learning_rate': 7.07830223197951e-05, 'epoch': 0.8781558726673985}
{'loss': 1.7951, 'grad_norm': 10.333605766296387, 'learning_rate': 6.895353091840469e-05, 'epoch': 0.9330406147091108}
{'loss': 1.779, 'grad_norm': 11.906965255737305, 'learning_rate': 6.712403951701427e-05, 'epoch': 0.9879253567508233}
{'eval_loss': 1.6375153064727783, 'eval_runtime': 35.1511, 'eval_samples_per_second': 103.638, 'eval_steps_per_second': 6.486, 'epoch': 1.0}
{'loss': 1.7323, 'grad_norm': 12.968351364135742, 'learning_rate': 6.529454811562385e-05, 'epoch': 1.0428100987925357}
{'loss': 1.669, 'grad_norm': 10.526283264160156, 'learning_rate': 6.348335162824734e-05, 'epoch': 1.0976948408342482}
{'loss': 1.6898, 'grad_norm': 12.602726936340332, 'learning_rate': 6.165386022685694e-05, 'epoch': 1.1525795828759604}
{'loss': 1.7071, 'grad_norm': 10.139097213745117, 'learning_rate': 5.982436882546653e-05, 'epoch': 1.2074643249176729}
{'loss': 1.647, 'grad_norm': 10.178239822387695, 'learning_rate': 5.799487742407611e-05, 'epoch': 1.2623490669593853}
{'loss': 1.6872, 'grad_norm': 10.57042407989502, 'learning_rate': 5.6165386022685695e-05, 'epoch': 1.3172338090010978}
{'loss': 1.6027, 'grad_norm': 11.031705856323242, 'learning_rate': 5.433589462129528e-05, 'epoch': 1.37211855104281}
{'loss': 1.6946, 'grad_norm': 9.9917631149292, 'learning_rate': 5.250640321990486e-05, 'epoch': 1.4270032930845225}
{'loss': 1.6945, 'grad_norm': 11.427775382995605, 'learning_rate': 5.067691181851446e-05, 'epoch': 1.481888035126235}
{'loss': 1.6589, 'grad_norm': 11.042301177978516, 'learning_rate': 4.884742041712404e-05, 'epoch': 1.5367727771679474}
{'loss': 1.6787, 'grad_norm': 9.701554298400879, 'learning_rate': 4.701792901573363e-05, 'epoch': 1.5916575192096598}
{'loss': 1.6332, 'grad_norm': 8.696869850158691, 'learning_rate': 4.5188437614343216e-05, 'epoch': 1.6465422612513723}
{'loss': 1.5674, 'grad_norm': 9.257272720336914, 'learning_rate': 4.33589462129528e-05, 'epoch': 1.7014270032930845}
{'loss': 1.6787, 'grad_norm': 11.03594970703125, 'learning_rate': 4.152945481156238e-05, 'epoch': 1.756311745334797}
{'loss': 1.5964, 'grad_norm': 11.409895896911621, 'learning_rate': 3.969996341017197e-05, 'epoch': 1.8111964873765092}
{'loss': 1.5722, 'grad_norm': 7.677157402038574, 'learning_rate': 3.787047200878156e-05, 'epoch': 1.8660812294182216}
{'loss': 1.5453, 'grad_norm': 10.108222007751465, 'learning_rate': 3.6040980607391146e-05, 'epoch': 1.920965971459934}
{'loss': 1.6619, 'grad_norm': 11.023812294006348, 'learning_rate': 3.4211489206000736e-05, 'epoch': 1.9758507135016465}
{'eval_loss': 1.5411205291748047, 'eval_runtime': 35.3307, 'eval_samples_per_second': 103.112, 'eval_steps_per_second': 6.453, 'epoch': 2.0}
{'loss': 1.582, 'grad_norm': 9.620518684387207, 'learning_rate': 3.238199780461032e-05, 'epoch': 2.030735455543359}
{'loss': 1.5083, 'grad_norm': 10.013246536254883, 'learning_rate': 3.05525064032199e-05, 'epoch': 2.0856201975850714}
{'loss': 1.4899, 'grad_norm': 13.762847900390625, 'learning_rate': 2.8723015001829497e-05, 'epoch': 2.140504939626784}
{'loss': 1.525, 'grad_norm': 11.459778785705566, 'learning_rate': 2.689352360043908e-05, 'epoch': 2.1953896816684964}
{'loss': 1.5173, 'grad_norm': 9.31627082824707, 'learning_rate': 2.5064032199048663e-05, 'epoch': 2.2502744237102084}
{'loss': 1.4729, 'grad_norm': 9.948030471801758, 'learning_rate': 2.3234540797658254e-05, 'epoch': 2.305159165751921}
{'loss': 1.4642, 'grad_norm': 8.625332832336426, 'learning_rate': 2.1405049396267837e-05, 'epoch': 2.3600439077936333}
{'loss': 1.4236, 'grad_norm': 10.376747131347656, 'learning_rate': 1.9575557994877424e-05, 'epoch': 2.4149286498353457}
{'loss': 1.4669, 'grad_norm': 8.949347496032715, 'learning_rate': 1.7746066593487014e-05, 'epoch': 2.469813391877058}
{'loss': 1.4667, 'grad_norm': 17.917694091796875, 'learning_rate': 1.5916575192096597e-05, 'epoch': 2.5246981339187706}
{'loss': 1.4848, 'grad_norm': 12.417656898498535, 'learning_rate': 1.4087083790706184e-05, 'epoch': 2.579582875960483}
{'loss': 1.4501, 'grad_norm': 11.907938003540039, 'learning_rate': 1.2257592389315771e-05, 'epoch': 2.6344676180021955}
{'loss': 1.4092, 'grad_norm': 11.670516967773438, 'learning_rate': 1.0428100987925358e-05, 'epoch': 2.689352360043908}
{'loss': 1.4614, 'grad_norm': 11.412532806396484, 'learning_rate': 8.598609586534943e-06, 'epoch': 2.74423710208562}
{'loss': 1.4351, 'grad_norm': 9.073331832885742, 'learning_rate': 6.7691181851445296e-06, 'epoch': 2.7991218441273324}
{'loss': 1.4691, 'grad_norm': 11.75009536743164, 'learning_rate': 4.939626783754116e-06, 'epoch': 2.854006586169045}
{'loss': 1.4541, 'grad_norm': 9.405517578125, 'learning_rate': 3.110135382363703e-06, 'epoch': 2.9088913282107574}
{'loss': 1.357, 'grad_norm': 9.749642372131348, 'learning_rate': 1.2806439809732895e-06, 'epoch': 2.96377607025247}
{'eval_loss': 1.4777565002441406, 'eval_runtime': 35.2411, 'eval_samples_per_second': 103.374, 'eval_steps_per_second': 6.47, 'epoch': 3.0}
{'train_runtime': 2612.316, 'train_samples_per_second': 33.469, 'train_steps_per_second': 2.092, 'train_loss': 1.666383633716526, 'epoch': 3.0}
{'eval_loss': 1.456459641456604, 'eval_runtime': 35.2436, 'eval_samples_per_second': 103.366, 'eval_steps_per_second': 6.469, 'epoch': 3.0}
Fine-tuned model Perplexity: 4.29
{'eval_loss': 2.393387794494629, 'eval_model_preparation_time': 0.003, 'eval_runtime': 35.2716, 'eval_samples_per_second': 103.284, 'eval_steps_per_second': 6.464}
Base model Perplexity: 10.95
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

```bash

==========
== CUDA ==
==========

CUDA Version 12.6.3

Container image Copyright (c) 2016-2023, NVIDIA CORPORATION & AFFILIATES. All rights reserved.

This container image and its contents are governed by the NVIDIA Deep Learning Container License.
By pulling and using the container, you accept the terms and conditions of this license:
https://developer.nvidia.com/ngc/nvidia-deep-learning-container-license

A copy of this license is made available in this container at /NGC-DL-CONTAINER-LICENSE for your convenience.

Using device: cuda
GPU: Tesla T4
Map: 100%|███████████████████████████████████████████████████████████████| 800/800 [00:00<00:00, 2971.31 examples/s]
Map: 100%|███████████████████████████████████████████████████████████████| 100/100 [00:00<00:00, 2632.91 examples/s]
Map: 100%|███████████████████████████████████████████████████████████████| 100/100 [00:00<00:00, 2843.48 examples/s]
trainable params: 297,219 || all params: 109,222,662 || trainable%: 0.2721
{'loss': 0.9034, 'grad_norm': 1.1748099327087402, 'learning_rate': 6.733333333333333e-05, 'epoch': 1.0}
{'eval_loss': 0.8304882645606995, 'eval_runtime': 0.7278, 'eval_samples_per_second': 137.391, 'eval_steps_per_second': 9.617, 'epoch': 1.0}
{'loss': 0.8087, 'grad_norm': 2.0064163208007812, 'learning_rate': 3.4000000000000007e-05, 'epoch': 2.0}
{'eval_loss': 0.8009655475616455, 'eval_runtime': 0.7387, 'eval_samples_per_second': 135.372, 'eval_steps_per_second': 9.476, 'epoch': 2.0}
{'loss': 0.7893, 'grad_norm': 1.0662009716033936, 'learning_rate': 6.666666666666667e-07, 'epoch': 3.0}
{'eval_loss': 0.7906897068023682, 'eval_runtime': 0.736, 'eval_samples_per_second': 135.868, 'eval_steps_per_second': 9.511, 'epoch': 3.0}
{'train_runtime': 47.4866, 'train_samples_per_second': 50.541, 'train_steps_per_second': 3.159, 'train_loss': 0.8337866719563802, 'epoch': 3.0}
Domain Adapted Model - Accuracy: 0.6700, F1: 0.2675
config.json: 100%|█████████████████████████████████████████████████████████████████| 647/647 [00:00<00:00, 3.67MB/s]
pytorch_model.bin: 100%|██████████████████████████████████████████████████████████| 438M/438M [00:01<00:00, 438MB/s]
model.safetensors:  36%|████████████████████▊                                     | 157M/438M [00:00<00:01, 250MB/s]Base Model - Accuracy: 0.5700, F1: 0.2865
config.json: 100%|█████████████████████████████████████████████████████████████| 1.14k/1.14k [00:00<00:00, 6.86MB/s]
model.safetensors: 100%|██████████████████████████████████████████████████████████| 438M/438M [00:01<00:00, 250MB/s]
pytorch_model.bin: 100%|█████████████████████████████████████████████████████████| 436M/436M [00:08<00:00, 52.5MB/s]
model.safetensors:   5%|██▋                                                     | 21.0M/436M [00:00<00:05, 76.9MB/s]Benchmark Model (FinBERT-PT-BR) - Accuracy: 0.4600, F1: 0.2965
model.safetensors: 100%|█████████████████████████████████████████████████████████| 436M/436M [00:07<00:00, 55.8MB/s]
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
