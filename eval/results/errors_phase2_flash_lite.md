# Errors: phase2_flash_lite

Missed = gold items no extracted item matched. Not in gold = extracted items matching no gold item (with their evidence status), to be classified for the error analysis (SCOPE.md section 8).

## 1409.0473

### hyperparameters
- missed: embedding_size = 620 [p. 14]
- missed: maxout_size = 500 [p. 14]
- missed: max_grad_norm = 1 [p. 15]
- missed: vocab_size = 30000 [p. 5] (most frequent words per language)
- missed: max_seq_length = 50 [p. 5] (also 30 (RNNsearch-30))

### compute
- missed: NVIDIA TITAN Black and Quadro K6000 GPUs [p. 14]

## 1409.1556

### task
- missed: object localisation [p. 10] (ILSVRC localisation (appendix A))

### datasets
- missed: PASCAL VOC-2007 [p. 12]
- missed: PASCAL VOC-2012 [p. 12] (also VOC-2012 action classification)
- missed: Caltech-101 [p. 13]
- missed: Caltech-256 [p. 13]

### baselines
- missed: Krizhevsky et al. 2012 [p. 8]
- missed: Chatfield et al. 2014 [p. 12]
- missed: Wei et al. 2014 [p. 12]
- missed: Oquab et al. 2014 [p. 14] (VOC action)
- missed: Gkioxari et al. 2014 [p. 14] (VOC action)
- missed: Hoai 2014 [p. 14] (VOC action)
- not in gold: Krizhevsky et al. _[verified]_

### metrics
- missed: localisation error [p. 11]
- missed: mean average precision [p. 12]
- missed: mean class recall [p. 13]

### hyperparameters
- missed: train_steps = 370000 [p. 4]
- missed: image_size = 224 [p. 4] (224x224 crops)

### code_urls
- missed: http://www.robots.ox.ac.uk/~vgg/research/very_deep/ [p. 1] (released models page)

## 1512.03385

### task
- missed: object detection [p. 8]
- missed: object localization [p. 12]
- not in gold: visual recognition tasks _[verified]_

### baselines
- missed: plain networks [p. 4] (own non-residual baselines)
- missed: OverFeat [p. 12] (localization)

### metrics
- missed: classification error [p. 7] (CIFAR-10)
- missed: localization error [p. 12]

### hyperparameters
- missed: image_size = 224 [p. 4]
- missed: batch_size = 128 [p. 7] (CIFAR-10)
- missed: train_steps = 64000 [p. 7] (CIFAR-10)
- missed: learning_rate = 0.01 [p. 7] (CIFAR-10 ResNet-110 warm-up)

### compute
- missed: two GPUs [p. 7] (CIFAR-10 training)

## 1706.03762

### datasets
- missed: WMT 2014 English-French [p. 7]
- missed: Penn Treebank WSJ [p. 9]
- missed: BerkeleyParser high-confidence corpora [p. 9] (semi-supervised parsing data)

### metrics
- missed: training cost (FLOPs) [p. 8]

### hyperparameters
- missed: optimizer = Adam [p. 7]
- missed: train_steps = 100000 [p. 7] (base model)
- missed: train_steps = 300000 [p. 7] (big model)
- missed: dropout = 0.1 [p. 8] (base; big EN-DE 0.3)
- missed: dropout = 0.3 [p. 9] (big model)
- missed: label_smoothing = 0.1 [p. 8]
- missed: batch_size = 25000 tokens [p. 7] (per batch source and target tokens)
- missed: hidden_size = 512 [p. 3] (base; big 1024)
- missed: hidden_size = 1024 [p. 9] (big model)
- missed: num_layers = 6 [p. 3]
- missed: num_heads = 8 [p. 5] (base; big 16)
- missed: num_heads = 16 [p. 9] (big model)
- missed: ffn_size = 2048 [p. 5] (base; big 4096)
- missed: ffn_size = 4096 [p. 9] (big model)
- missed: beam_size = 4 [p. 8]
- missed: length_penalty = 0.6 [p. 8]
- missed: vocab_size = 37000 [p. 7] (EN-DE; EN-FR 32000 word-piece)
- missed: vocab_size = 32000 [p. 7] (EN-FR)

### compute
- missed: 12 hours (base) / 3.5 days (big) training [p. 7]
- not in gold: Base models training time and steps _[verified]_

## 1810.04805

### task
- missed: language representation pre-training [p. 1]
- missed: named entity recognition [p. 9]
- missed: commonsense inference [p. 7]

### datasets
- missed: BooksCorpus [p. 5] (pre-training)
- missed: English Wikipedia [p. 5] (pre-training)

### baselines
- missed: ELMo [p. 6]
- missed: Pre-OpenAI SOTA [p. 6]
- missed: R.M. Reader [p. 7]
- missed: nlnet [p. 7]
- missed: QANet [p. 7]
- missed: MIR-MRC (F-Net) [p. 7]
- missed: unet [p. 7]
- missed: SLQA+ [p. 7]
- missed: ESIM+GloVe [p. 7]
- missed: CVT [p. 9]
- missed: CSE [p. 9]

### metrics
- missed: GLUE score [p. 6]
- missed: perplexity [p. 9]

### hyperparameters
- missed: optimizer = Adam [p. 13]
- missed: learning_rate = 1e-4 [p. 13] (pre-training)
- missed: adam_beta1 = 0.9 [p. 13]
- missed: adam_beta2 = 0.999 [p. 13]
- missed: weight_decay = 0.01 [p. 13]
- missed: warmup_steps = 10000 [p. 13]
- missed: dropout = 0.1 [p. 13]
- missed: batch_size = 256 [p. 13] (pre-training)
- missed: train_steps = 1000000 [p. 13] (pre-training)
- missed: epochs = 40 [p. 13] (pre-training)
- missed: max_seq_length = 512 [p. 13] (128 for 90% of steps)
- missed: max_seq_length = 128 [p. 13] (first 90% of steps)
- missed: mask_prob = 0.15 [p. 4]
- missed: num_layers = 12 [p. 3] (BASE; LARGE 24)
- missed: num_layers = 24 [p. 3] (LARGE)
- missed: hidden_size = 768 [p. 3] (BASE)
- missed: hidden_size = 1024 [p. 3] (LARGE)
- missed: num_heads = 12 [p. 3] (BASE)
- missed: num_heads = 16 [p. 3] (LARGE)
- missed: ffn_size = 3072 [p. 3] (BASE)
- missed: ffn_size = 4096 [p. 3] (LARGE)
- missed: vocab_size = 30000 [p. 4]

### compute
- missed: Cloud TPUs (4 for BASE / 16 for LARGE) [p. 13]
- missed: pre-training took 4 days [p. 13]

### code_urls
- not in gold: https://github.com/tensorflow/tensor2tensor _[verified]_

## 1907.11692

### task
- missed: question answering [p. 3]
- missed: natural language understanding [p. 3]

### baselines
- missed: ALICE [p. 8] (GLUE leaderboard)
- missed: MT-DNN [p. 8] (GLUE leaderboard)
- missed: XLNet + SG-Net Verifier [p. 9] (SQuAD leaderboard)

### metrics
- missed: perplexity [p. 6]
- missed: GLUE score [p. 8]

### hyperparameters
- missed: optimizer = Adam [p. 2]
- missed: adam_beta1 = 0.9 [p. 13]
- missed: adam_epsilon = 1e-6 [p. 13]
- missed: weight_decay = 0.01 [p. 13] (pretraining)
- missed: dropout = 0.1 [p. 13]
- missed: attention_dropout = 0.1 [p. 13]
- missed: warmup_steps = 30000 [p. 13] (LARGE; BASE 24k)
- missed: warmup_steps = 24000 [p. 13] (BASE)
- missed: learning_rate = 4e-4 [p. 13] (LARGE; BASE 6e-4)
- missed: learning_rate = 6e-4 [p. 13] (BASE)
- missed: batch_size = 8000 [p. 13]
- missed: train_steps = 500000 [p. 13] (also 100K/300K in Table 4)
- missed: max_grad_norm = 0.0 [p. 13]
- missed: ffn_size = 4096 [p. 13] (LARGE; BASE 3072)
- missed: vocab_size = 50000 [p. 6]
- missed: learning_rate = 1.5e-5 [p. 13] (SQuAD fine-tuning)
- missed: batch_size = 48 [p. 13] (SQuAD)
- missed: train_steps = 300000 [p. 7] (Table 4 (added in adjudication))
- not in gold: model_size = 355M _[verified]_

## 1910.01108

### task
- missed: knowledge distillation of a pre-trained language model [p. 1]
- missed: natural language understanding [p. 3]
- missed: sentiment classification [p. 3]
- missed: question answering [p. 3]
- not in gold: Natural Language Processing _[verified]_

### datasets
- missed: English Wikipedia [p. 3] (pre-training corpus)
- missed: Toronto Book Corpus [p. 3] (pre-training corpus)

### metrics
- missed: inference time [p. 3]
- missed: number of parameters [p. 3]

### hyperparameters
- missed: batch_size = 4000 [p. 3] (via gradient accumulation)
- missed: num_layers = 6 [p. 2] (half of BERT-base's 12)
- missed: temperature = T [p. 2] (value not stated)

### compute
- missed: 8 x 16GB V100 GPUs [p. 3]
- missed: approximately 90 hours of training [p. 3]

## 2002.05709

### task
- missed: semi-supervised learning [p. 1]
- missed: transfer learning [p. 2]
- missed: image classification [p. 1]

### baselines
- missed: random initialization [p. 8] (transfer)

### hyperparameters
- missed: epochs = 1000 [p. 7] (best models)
- missed: temperature = 0.5 [p. 7] (also 0.1)
- missed: temperature = 0.1 [p. 7] (Table 5 best at batch 4096)
- missed: projection_dim = 128 [p. 3]
- missed: image_size = 224 [p. 12]
- missed: learning_rate = 1.6 [p. 15] (linear evaluation)
- missed: epochs = 90 [p. 15] (linear evaluation)
- missed: train_steps = 20000 [p. 17] (transfer fine-tuning)

## 2010.11929

### task
- missed: transfer learning [p. 1]

### datasets
- missed: ImageNet-21k [p. 4]

### baselines
- missed: hybrid models [p. 7] (ResNet+ViT hybrids in the scaling study)

### metrics
- missed: VTAB score [p. 6]
- missed: TPUv3-core-days [p. 5]

### hyperparameters
- missed: warmup_steps = 10000 [p. 13]
- missed: learning_rate = 8e-4 [p. 13] (ViT-B JFT)
- missed: learning_rate = 4e-4 [p. 13] (ViT-L/16 JFT)
- missed: learning_rate = 3e-4 [p. 13] (ViT-H/14 JFT)
- missed: epochs = 7 [p. 13] (JFT pre-training (also 14))
- missed: epochs = 14 [p. 13] (JFT pre-training ViT-H/14)
- missed: dropout = 0.1 [p. 13] (ImageNet / ImageNet-21k; 0.0 on JFT)
- missed: image_size = 224 [p. 13]
- missed: image_size = 384 [p. 14]
- missed: max_grad_norm = 1 [p. 14]
- missed: num_layers = 12 [p. 5] (ViT-Base; Large 24; Huge 32)
- missed: num_layers = 24 [p. 5] (ViT-Large)
- missed: num_layers = 32 [p. 5] (ViT-Huge)
- missed: hidden_size = 768 [p. 5] (ViT-Base)
- missed: hidden_size = 1024 [p. 5] (ViT-Large)
- missed: hidden_size = 1280 [p. 5] (ViT-Huge)
- missed: ffn_size = 3072 [p. 5] (ViT-Base)
- missed: num_heads = 12 [p. 5] (ViT-Base; Large/Huge 16)
- missed: num_heads = 16 [p. 5] (ViT-Large / Huge)
- missed: patch_size = 16 [p. 5] (also 14 and 32)

### code_urls
- not in gold: https://github.com/csrhddlam/axial-deeplab.In _[verified]_

## 2106.09685

### task
- missed: parameter-efficient adaptation of large language models [p. 1]
- missed: natural language understanding [p. 5]
- missed: natural language generation [p. 5]
- missed: NL to SQL [p. 2]
- missed: summarization [p. 2]
- not in gold: Natural language processing model pretraining and adaptation to downstream tasks. _[verified]_

### metrics
- missed: Matthew's correlation [p. 6] (CoLA)
- missed: Pearson correlation [p. 6] (STS-B)
- missed: TER [p. 21] (DART / WebNLG)
- missed: number of trainable parameters [p. 6]
- missed: inference latency [p. 4]

### hyperparameters
- missed: optimizer = AdamW [p. 18]
- missed: lora_rank = 8 [p. 19] (RoBERTa / DeBERTa / GPT-3 37.7M budget)
- missed: lora_rank = 4 [p. 20] (GPT-2)
- missed: lora_rank = 1 [p. 20] (GPT-3 4.7M budget)
- missed: lora_alpha = 8 [p. 19] (RoBERTa base / DeBERTa)
- missed: lora_alpha = 16 [p. 19] (RoBERTa large)
- missed: lora_alpha = 32 [p. 20] (GPT-2)
- missed: warmup_ratio = 0.06 [p. 19] (RoBERTa; DeBERTa 0.1)
- missed: warmup_ratio = 0.1 [p. 20] (DeBERTa)
- missed: learning_rate = 5e-4 [p. 19] (RoBERTa base grid (4e-4 / 5e-4))
- missed: learning_rate = 4e-4 [p. 19]
- missed: learning_rate = 3e-4 [p. 19] (RoBERTa large grid)
- missed: learning_rate = 2e-4 [p. 20] (GPT-2 / GPT-3 LoRA)
- missed: learning_rate = 1e-4 [p. 20] (DeBERTa)
- missed: batch_size = 16 [p. 19] (RoBERTa base (also 32))
- missed: batch_size = 32 [p. 19]
- missed: batch_size = 4 [p. 19] (RoBERTa large)
- missed: batch_size = 8 [p. 20] (GPT-2 / DeBERTa)
- missed: batch_size = 128 [p. 19] (GPT-3)
- missed: epochs = 5 [p. 19] (GPT-2)
- missed: epochs = 2 [p. 19] (GPT-3)
- missed: epochs = 30 [p. 19] (RoBERTa base MNLI (per task 25-80))
- missed: weight_decay = 0.1 [p. 19] (GPT-3)
- missed: weight_decay = 0.01 [p. 20] (GPT-2 E2E / WebNLG)
- missed: dropout = 0.1 [p. 20] (GPT-2)
- missed: label_smoothing = 0.1 [p. 20] (GPT-2)
- missed: warmup_steps = 500 [p. 20] (GPT-2)
- missed: max_seq_length = 512 [p. 19] (RoBERTa (128 in the restricted setup))
- missed: beam_size = 10 [p. 20] (GPT-2 inference)
- missed: length_penalty = 0.9 [p. 20] (E2E (0.8 WebNLG/DART))
