# Errors: collect_flash_lite

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
- missed: optimizer = mini-batch gradient descent with momentum [p. 4]
- missed: image_size = 224 [p. 4] (224x224 crops)

### code_urls
- missed: http://www.robots.ox.ac.uk/~vgg/research/very_deep/ [p. 1] (released models page)

## 1502.03167

### task
- missed: digit classification [p. 5]

### baselines
- missed: Inception [p. 6]
- missed: GoogLeNet ensemble [p. 8]
- missed: Deep Image low-res [p. 8]
- missed: Deep Image high-res [p. 8]
- not in gold: Inception network _[verified]_

### metrics
- missed: top-1 error [p. 8]
- missed: training steps to reach accuracy [p. 7]
- missed: test accuracy [p. 6] (MNIST)

### hyperparameters
- missed: num_layers = 3 [p. 6] (MNIST network)
- missed: hidden_size = 100 [p. 6] (MNIST network)
- missed: model_size = 13.6M [p. 6]
- missed: train_steps = 6000000 [p. 7] (BN-x30 and ensemble members)
- missed: ensemble_size = 6 [p. 7]
- missed: image_size = 224 [p. 8]
- missed: test_crops = 144 [p. 8] (multicrop and ensemble)
- missed: depth_multiplier = 8 [p. 10] (first convolutional layer)

### compute
- not in gold: large-scale distributed architecture used for training _[verified]_

## 1505.04597

### task
- not in gold: cell tracking _[verified]_

### baselines
- missed: DIVE [p. 6]
- missed: IDSIA-SCI [p. 6]
- not in gold: second-best algorithm (2015) on PhC-U373 _[verified]_

### hyperparameters
- missed: optimizer = SGD [p. 4]
- missed: batch_size = 1 [p. 4]
- missed: num_layers = 23 [p. 4]
- missed: loss_weight_w0 = 10 [p. 5] (border weight map)
- missed: loss_weight_sigma = 5 [p. 5] (pixels)
- missed: augmentation_displacement_std = 10 [p. 6] (elastic deformation in pixels on a 3x3 grid)
- missed: test_time_augmentation = 7 [p. 6] (EM challenge)
- not in gold: batch size = a single image _[verified]_

### compute
- missed: NVidia Titan GPU (6 GB) [p. 8]
- missed: 10 hours training [p. 8]
- not in gold: GPU memory utilization optimized via large input tiles and a batch size of a single image. _[verified]_

### code_urls
- missed: http://lmb.informatik.uni-freiburg.de/people/ronneber/u-net [p. 1]

## 1506.01497

### task
- missed: region proposal generation [p. 1]

### datasets
- missed: ImageNet [p. 5] (pre-trained networks)

### baselines
- missed: Fast R-CNN [p. 10]

### metrics
- missed: running time [p. 8]

### hyperparameters
- missed: optimizer = SGD [p. 5]
- missed: anchors_per_image = 256 [p. 5]
- missed: train_steps = 60k [p. 5] (PASCAL VOC)
- missed: train_steps = 20k [p. 5] (PASCAL VOC)
- missed: init_std = 0.01 [p. 5] (new layers)
- missed: image_size = 600 [p. 6]
- missed: anchor_scales = 128², 256², 512² [p. 6]
- missed: anchor_ratios = 1:1, 1:2, 2:1 [p. 6]
- missed: nms_threshold = 0.7 [p. 7]
- missed: num_proposals = 2000 [p. 7] (train-time)
- missed: num_proposals = 300 [p. 7] (test-time)
- missed: loss_weight_lambda = 10 [p. 9]
- missed: batch_size = 8 [p. 10] (COCO RPN)
- missed: batch_size = 16 [p. 10] (COCO Fast R-CNN)
- missed: train_steps = 240k [p. 10] (COCO)
- missed: train_steps = 80k [p. 10] (COCO)
- missed: anchor_scales = 64², 128², 256², 512² [p. 10] (COCO)
- missed: stride = 16 [p. 6]
- not in gold: lambda = 10 _[verified]_

### compute
- missed: K40 GPU [p. 8] (timing)

## 1512.03385

### task
- missed: object detection [p. 8]
- missed: object localization [p. 12]
- not in gold: visual recognition tasks _[verified]_

### datasets
- missed: ImageNet detection (DET) [p. 11]

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
- not in gold: iterations = 240k, 80k _[verified]_

### compute
- missed: two GPUs [p. 7] (CIFAR-10 training)

## 1609.02907

### task
- missed: semi-supervised entity classification in a knowledge graph [p. 5]

### baselines
- missed: Chebyshev filter [p. 7] (propagation-model comparison)
- missed: multi-layer perceptron [p. 7] (propagation-model comparison)

### metrics
- missed: wall-clock training time [p. 7]

### hyperparameters
- missed: num_layers = 2 [p. 6]
- missed: early_stopping_patience = 10 [p. 6] (epochs)
- missed: hidden_size = 16 [p. 7] (citation networks)
- missed: hidden_size = 64 [p. 7] (NELL)
- missed: hidden_size = 32 [p. 6] (random graphs)
- missed: epochs = 400 [p. 14] (model-depth experiments)
- missed: epochs = 300 [p. 12] (karate club)
- missed: hidden_size = 4 [p. 12] (karate club)
- not in gold: number of hidden units = 16 _[verified]_
- not in gold: number of hidden units = 64 _[verified]_
- not in gold: early stopping window size = 10 _[verified]_

### compute
- missed: 16-core Intel Xeon CPU E5-2640 v3 [p. 8]
- missed: GeForce GTX TITAN X [p. 8]
- not in gold: GPU-based implementation using TensorFlow _[verified]_

### code_urls
- not in gold: https://github.com/kimiyoung/planetoid _[verified]_

## 1706.03762

### task
- missed: English constituency parsing [p. 9]

### datasets
- missed: WMT 2014 English-French [p. 7]
- missed: BerkeleyParser high-confidence corpora [p. 9] (semi-supervised parsing data)
- not in gold: Section 22 development set _[verified]_

### metrics
- missed: training cost (FLOPs) [p. 8]

### hyperparameters
- missed: optimizer = Adam [p. 7]
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
- not in gold: maximum output length = input length + 300 _[verified]_

## 1706.06083

### task
- missed: adversarial robustness [p. 1]
- missed: image classification [p. 9]
- not in gold: computer vision _[partial]_

### baselines
- missed: standard training [p. 11]
- missed: FGSM adversarial training [p. 11]

### metrics
- missed: cross-entropy loss [p. 12]

### hyperparameters
- missed: pgd_steps = 40 [p. 11] (MNIST)
- missed: pgd_steps = 7 [p. 12] (CIFAR10 training)
- missed: pgd_steps = 20 [p. 12] (CIFAR10 hardest adversary)
- missed: num_restarts = 20 [p. 13] (MNIST evaluation)
- missed: cw_confidence = 50 [p. 11] (CW+)
- missed: conv_filters = 32 and 64 [p. 11] (MNIST network)
- missed: width_multiplier = 10 [p. 9] (CIFAR10 ResNet)
- missed: resnet_filters = (16, 160, 320, 640) [p. 9] (CIFAR10 wide ResNet)
- missed: num_residual_units = 5 [p. 9] (CIFAR10)
- missed: hidden_size = 64 [p. 9] (MNIST capacity study initial network)
- missed: dba_steps = 2000 [p. 14]

## 1707.06347

### task
- missed: Atari game playing [p. 1]

### datasets
- missed: OpenAI Gym MuJoCo tasks [p. 6] (7 environments v1)
- missed: Roboschool humanoid tasks [p. 7]
- not in gold: continuous control benchmark _[verified]_

### baselines
- missed: TRPO [p. 6]
- missed: cross-entropy method [p. 6]
- missed: vanilla policy gradient with adaptive stepsize [p. 6]
- missed: A2C with trust region [p. 7]
- missed: ACER [p. 8]

### metrics
- missed: number of games won [p. 8] (Atari)
- not in gold: Mean performance _[verified]_

### hyperparameters
- missed: optimizer = Adam [p. 5]
- missed: horizon = 2048 [p. 10] (MuJoCo)
- missed: learning_rate = 3e-4 [p. 10] (MuJoCo)
- missed: epochs = 10 [p. 10] (MuJoCo)
- missed: batch_size = 64 [p. 10] (MuJoCo)
- missed: gamma = 0.99 [p. 10] (all)
- missed: gae_lambda = 0.95 [p. 10] (all)
- missed: clip_epsilon = 0.2 [p. 7] (MuJoCo comparison)
- missed: clip_epsilon = 0.3 [p. 6] (searched)
- missed: kl_beta = 0.3 [p. 6] (searched)
- missed: kl_beta = 1 [p. 6] (searched; initial β)
- missed: kl_beta = 3 [p. 6] (searched)
- missed: kl_beta = 10 [p. 6] (searched)
- missed: hidden_size = 64 [p. 6] (MuJoCo policy MLP)
- missed: num_layers = 2 [p. 6] (MuJoCo policy MLP)
- missed: train_steps = 1000000 [p. 6] (MuJoCo)
- missed: horizon = 512 [p. 10] (Roboschool)
- missed: epochs = 15 [p. 10] (Roboschool)
- missed: batch_size = 4096 [p. 10] (Roboschool)
- missed: num_actors = 32 [p. 10] (Roboschool locomotion)
- missed: num_actors = 128 [p. 10] (Roboschool flagrun)
- missed: horizon = 128 [p. 10] (Atari)
- missed: learning_rate = 2.5e-4 [p. 10] (Atari (times annealed α))
- missed: epochs = 3 [p. 10] (Atari)
- missed: batch_size = 256 [p. 10] (Atari)
- missed: num_actors = 8 [p. 10] (Atari)
- missed: clip_epsilon = 0.1 [p. 10] (Atari (times annealed α); also searched on MuJoCo)
- missed: value_coef = 1 [p. 10] (Atari)
- missed: entropy_coef = 0.01 [p. 10] (Atari)
- missed: train_steps = 10M timesteps [p. 12] (Atari)
- not in gold: epochs = K _[verified]_
- not in gold: ϵ = 0.1 _[verified]_
- not in gold: ϵ = 0.2 _[verified]_
- not in gold: ϵ = 0.3 _[verified]_
- not in gold: β = 1. _[verified]_
- not in gold: β = 3. _[verified]_
- not in gold: β = 10. _[verified]_
- not in gold: β initialization = 1 _[verified]_

### code_urls
- not in gold: https://github.com/berkeleydeeprlcourse/homework/tree/master/hw4 _[verified]_

## 1710.10903

### baselines
- missed: GCN [p. 6]
- missed: Chebyshev [p. 6]
- missed: MLP [p. 7]
- missed: Random [p. 8] (PPI)
- not in gold: GCNs _[verified]_
- not in gold: Chebyshev filters graph convolutional models _[verified]_
- not in gold: Per-node shared multilayer perceptron (MLP) classifier _[verified]_

### hyperparameters
- missed: num_layers = 2 [p. 7] (transductive)
- missed: num_layers = 3 [p. 7] (inductive)
- missed: num_heads = 8 [p. 7] (transductive first layer)
- missed: num_heads = 4 [p. 7] (inductive first two layers)
- missed: num_heads = 6 [p. 7] (inductive output layer)
- missed: hidden_size = 8 [p. 7] (transductive (64 total))
- missed: hidden_size = 256 [p. 7] (inductive (1024 total))
- missed: optimizer = Adam [p. 7]

## 1711.05101

### datasets
- not in gold: WIDER FACE _[verified]_

### baselines
- missed: Adam with L2 regularization [p. 5]
- missed: SGD with momentum and L2 regularization [p. 6]
- not in gold: Standard SGD with L2 regularization _[verified]_

### metrics
- missed: top-5 test error [p. 8] (ImageNet32x32)
- not in gold: Test set accuracy _[verified]_

### hyperparameters
- missed: optimizer = AdamW [p. 3]
- missed: epochs = 100 [p. 5]
- missed: epochs = 1800 [p. 7] (long runs)
- missed: lr_schedule = cosine annealing [p. 6]
- missed: lr_drop_epochs = 30 [p. 5] (drops at epochs 30 60 80)
- missed: lr_drop_epochs = 60 [p. 5]
- missed: lr_drop_epochs = 80 [p. 5]
- missed: weight_decay = 0.025 [p. 14] (normalized weight decay)
- missed: weight_decay = 0.05 [p. 14] (normalized weight decay)
- missed: restart_period = 100 [p. 13] (warm restarts example setting)
- missed: restart_mult = 2 [p. 13] (warm restarts example setting)
- missed: num_layers = 26 [p. 5] (26 2x64d ResNet)
- missed: hidden_size = 64 [p. 5] (26 2x64d ResNet)
- missed: hidden_size = 96 [p. 5] (26 2x96d ResNet)
- missed: model_size = 11.6M [p. 5] (26 2x64d ResNet)
- missed: model_size = 25.6M [p. 5] (26 2x96d ResNet)

### code_urls
- missed: https://github.com/loshchil/AdamW-and-SGDW [p. 1]
- not in gold: https://github.com/xgastaldi/shake-shake _[verified]_
- not in gold: https://github.com/pytorch/pytorch/pull/4429 _[verified]_
- not in gold: https://github.com/sgugger/Adam-experiments _[verified]_
- not in gold: https://github.com/GLambard/AdamW_Keras _[verified]_
- not in gold: https://github.com/Yagami123/Caffe-AdamW-AdamWR _[verified]_

## 1801.01290

### datasets
- missed: OpenAI Gym MuJoCo tasks [p. 6]
- missed: Humanoid (rllab) [p. 6]
- not in gold: OpenAI gym benchmark suite _[partial]_
- not in gold: rllab implementation of the Humanoid task _[partial]_

### hyperparameters
- missed: optimizer = Adam [p. 13]
- missed: learning_rate = 3e-4 [p. 13]
- missed: gamma = 0.99 [p. 13]
- missed: replay_buffer_size = 1e6 [p. 13]
- missed: num_layers = 2 [p. 13] (all networks)
- missed: hidden_size = 256 [p. 13]
- missed: batch_size = 256 [p. 13]
- missed: target_smoothing_tau = 1 [p. 13] (SAC hard target update)
- missed: target_update_interval = 1 [p. 13] (SAC)
- missed: target_update_interval = 1000 [p. 13] (SAC hard target update)
- missed: gradient_steps = 1 [p. 13] (SAC; hard-update humanoids)
- missed: gradient_steps = 4 [p. 13] (hard target update except humanoids)
- missed: reward_scale = 5 [p. 13] (Hopper Walker2d HalfCheetah Ant)
- missed: reward_scale = 20 [p. 13] (Humanoid-v1)
- missed: reward_scale = 10 [p. 13] (Humanoid (rllab); also Fig. 3 sweep)
- missed: reward_scale = 1 [p. 8] (sensitivity sweep (Fig. 3))
- missed: reward_scale = 3 [p. 8] (sensitivity sweep (Fig. 3))
- missed: reward_scale = 30 [p. 8] (sensitivity sweep (Fig. 3))
- missed: reward_scale = 100 [p. 8] (sensitivity sweep (Fig. 3))
- missed: target_smoothing_tau = 0.0001 [p. 8] (sensitivity sweep (Fig. 3))
- missed: target_smoothing_tau = 0.001 [p. 8] (sensitivity sweep (Fig. 3))
- missed: target_smoothing_tau = 0.01 [p. 8] (sensitivity sweep (Fig. 3))
- missed: target_smoothing_tau = 0.1 [p. 8] (sensitivity sweep (Fig. 3))

### code_urls
- missed: https://github.com/haarnoja/sac [p. 6]

## 1803.03635

### task
- missed: image classification [p. 3]

### baselines
- missed: randomly reinitialized networks [p. 3]
- missed: randomly sampled sparse networks [p. 2]
- missed: one-shot pruning [p. 2]
- missed: unpruned network [p. 3]

### metrics
- missed: early-stopping iteration [p. 1]
- not in gold: validation loss _[verified]_

### hyperparameters
- missed: architecture = Lenet-300-100 [p. 3] (MNIST)
- missed: architecture = Conv-2 [p. 3] (CIFAR10)
- missed: architecture = Conv-4 [p. 3] (CIFAR10)
- missed: architecture = Conv-6 [p. 3] (CIFAR10)
- missed: architecture = Resnet-18 [p. 3] (CIFAR10)
- missed: architecture = VGG-19 [p. 3] (CIFAR10)
- missed: train_steps = 50K [p. 3] (Lenet)
- missed: train_steps = 25K [p. 3] (Conv-4)
- missed: train_steps = 112K [p. 3] (VGG-19)
- missed: batch_size = 60 [p. 3] (Lenet and Conv-2/4/6)
- missed: batch_size = 64 [p. 3] (VGG-19)
- missed: optimizer = Adam [p. 3] (Lenet and Conv-2/4/6)
- missed: learning_rate = 1.2e-3 [p. 3] (Lenet)
- missed: learning_rate = 2e-4 [p. 3] (Conv-2)
- missed: learning_rate = 3e-4 [p. 3] (Conv-4 and Conv-6)
- missed: learning_rate = 0.001 [p. 3]
- missed: learning_rate = 0.03 [p. 8] (Resnet-18 with warmup)
- missed: pruning_rate = 20% [p. 3] (fully-connected layers)
- missed: pruning_rate = 10% [p. 3] (Conv-2 and Conv-4 conv layers)
- missed: pruning_rate = 15% [p. 3] (Conv-6 conv layers)
- missed: pruning_rate = 0% [p. 3] (Resnet-18 and VGG-19 output layer)
- missed: hidden_size = 300 [p. 3] (Lenet FC layers)
- missed: hidden_size = 100 [p. 3] (Lenet FC layers)
- missed: hidden_size = 256 [p. 3] (Conv-2/4/6 FC layers)

## 1810.04805

### task
- missed: language representation pre-training [p. 1]
- missed: commonsense inference [p. 7]
- not in gold: paraphrasing _[verified]_

### datasets
- missed: BooksCorpus [p. 5] (pre-training)
- missed: English Wikipedia [p. 5] (pre-training)

### baselines
- missed: OpenAI GPT [p. 6]
- missed: ELMo [p. 6]
- missed: Pre-OpenAI SOTA [p. 6]
- missed: BiDAF+ELMo [p. 7]
- missed: R.M. Reader [p. 7]
- missed: nlnet [p. 7]
- missed: QANet [p. 7]
- missed: MIR-MRC (F-Net) [p. 7]
- missed: unet [p. 7]
- missed: SLQA+ [p. 7]
- missed: ESIM+ELMo [p. 7]
- missed: ESIM+GloVe [p. 7]
- missed: CVT [p. 9]
- missed: CSE [p. 9]
- not in gold: OpenAI GPT on GLUE _[verified]_
- not in gold: ESIM+ELMo system on SWAG _[verified]_
- not in gold: OpenAI GPT on SWAG _[verified]_

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
- missed: batch_size = 16 [p. 7] (SWAG)
- not in gold: epochs = 16 _[partial]_
- not in gold: feed-forward/filter size = 4H _[verified]_

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
- missed: BERT [p. 5]
- missed: XLNet [p. 5]
- missed: ALICE [p. 8] (GLUE leaderboard)
- missed: MT-DNN [p. 8] (GLUE leaderboard)
- missed: XLNet + SG-Net Verifier [p. 9] (SQuAD leaderboard)
- not in gold: Original BERT model and its variants _[partial]_
- not in gold: XLNet architecture _[verified]_

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
- missed: max_grad_norm = 0.0 [p. 13]
- missed: num_layers = 24 [p. 13] (LARGE; BASE 12)
- missed: hidden_size = 1024 [p. 13] (LARGE; BASE 768)
- missed: num_heads = 16 [p. 13] (LARGE; BASE 12)
- missed: ffn_size = 4096 [p. 13] (LARGE; BASE 3072)
- missed: vocab_size = 50000 [p. 6]
- missed: learning_rate = 1.5e-5 [p. 13] (SQuAD fine-tuning)
- missed: batch_size = 48 [p. 13] (SQuAD)
- not in gold: model size = L = 24, H = 1024, A = 16, 355M parameters _[verified]_

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

## 1910.10683

### task
- missed: transfer learning for NLP [p. 1]
- missed: machine translation [p. 7]

### datasets
- missed: WMT English to French [p. 8]
- missed: WMT English to Romanian [p. 8]
- missed: Unfiltered C4 [p. 25] (pre-training data ablation)
- missed: RealNews-like [p. 26] (pre-training data ablation)
- missed: WebText-like [p. 26] (pre-training data ablation)
- missed: Wikipedia [p. 26] (pre-training data ablation)
- missed: Wikipedia + Toronto Books Corpus [p. 26] (pre-training data ablation)

### baselines
- missed: previous state of the art [p. 39] (Table 14 first row)
- missed: ALBERT [p. 38]
- missed: RoBERTa [p. 39] (Table 14 source)
- missed: FreeLB [p. 39] (Table 14 source)
- missed: XLM [p. 39] (Table 14 source)
- missed: UniLM [p. 39] (Table 14 source)
- missed: back-translation [p. 39] (Table 14 source)
- missed: BERT-base [p. 14]

### metrics
- missed: GLUE average score [p. 14]
- missed: SuperGLUE average score [p. 14]
- missed: ROUGE-1 [p. 39]
- missed: ROUGE-L [p. 39]
- missed: F1 [p. 39]
- missed: accuracy [p. 39]
- missed: Matthews correlation [p. 39] (CoLA)
- missed: Pearson correlation [p. 39] (STS-B)
- missed: Spearman correlation [p. 39] (STS-B)

### hyperparameters
- missed: num_layers = 12 [p. 11] (baseline encoder and decoder each)
- missed: ffn_size = 3072 [p. 11] (baseline)
- missed: head_dim = 64 [p. 11] (baseline)
- missed: num_heads = 12 [p. 11] (baseline)
- missed: hidden_size = 768 [p. 11] (baseline)
- missed: model_size = 220M [p. 11] (baseline / T5-Base)
- missed: optimizer = AdaFactor [p. 11]
- missed: tokens_per_batch = 65536 [p. 12]
- missed: lr_schedule = inverse square root [p. 12] (pre-training)
- missed: warmup_steps = 10000 [p. 12]
- missed: checkpoint_interval = 5000 [p. 12]
- missed: vocab_size = 32000 [p. 12] (SentencePiece)
- missed: pretrain_tokens = 34B [p. 12] (baseline)
- missed: corruption_rate = 0.15 [p. 23] (span corruption)
- missed: mean_span_length = 3 [p. 36] (final T5 objective)
- missed: train_steps = 1000000 [p. 36] (final T5 pre-training)
- missed: batch_size = 2048 [p. 36] (final T5 pre-training)
- missed: pretrain_tokens = 1T [p. 36] (final T5)
- missed: hidden_size = 512 [p. 36] (T5-Small)
- missed: ffn_size = 2048 [p. 36] (T5-Small)
- missed: num_heads = 8 [p. 36] (T5-Small)
- missed: num_layers = 6 [p. 36] (T5-Small)
- missed: model_size = 60M [p. 36] (T5-Small)
- missed: hidden_size = 1024 [p. 36] (T5-Large / 3B / 11B)
- missed: ffn_size = 4096 [p. 36] (T5-Large)
- missed: num_heads = 16 [p. 36] (T5-Large)
- missed: num_layers = 24 [p. 36] (T5-Large / 3B / 11B)
- missed: model_size = 770M [p. 36] (T5-Large)
- missed: head_dim = 128 [p. 37] (T5-3B / 11B)
- missed: ffn_size = 16384 [p. 37] (T5-3B)
- missed: num_heads = 32 [p. 37] (T5-3B)
- missed: model_size = 3B [p. 37] (T5-3B)
- missed: ffn_size = 65536 [p. 37] (T5-11B)
- missed: num_heads = 128 [p. 37] (T5-11B)
- missed: model_size = 11B [p. 37] (T5-11B)
- missed: batch_size = 8 [p. 37] (low-resource GLUE/SuperGLUE fine-tuning)
- missed: checkpoint_interval = 1000 [p. 37]
- missed: beam_size = 4 [p. 38]
- missed: length_penalty = 0.6 [p. 38] (WMT and CNN/DM)
- not in gold: warm-up steps = 10 4 _[verified]_
- not in gold: vocabulary size = 32,000 _[verified]_
- not in gold: token dropout percentage = 15% _[verified]_

### code_urls
- missed: https://github.com/google-research/text-to-text-transfer-transformer [p. 1]
- not in gold: https://github.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words _[verified]_
- not in gold: https://github.com/jcpeterson/openwebtext13 _[verified]_
- not in gold: https://github.com/google-research/bert/blob/master/multilingual.md _[verified]_

## 2001.08361

### task
- missed: scaling laws [p. 1]

### datasets
- missed: Books Corpus [p. 7] (evaluation)
- missed: Common Crawl [p. 7] (evaluation)
- missed: English Wikipedia [p. 7] (evaluation)
- missed: Internet Books [p. 7] (evaluation)

### baselines
- missed: LSTM [p. 6]
- missed: Universal Transformer [p. 6]
- not in gold: LSTM models trained with the same dataset and context length _[partial]_
- not in gold: Recurrent Transformers that re-use parameters _[verified]_

### metrics
- missed: compute (PF-days) [p. 6]
- missed: critical batch size [p. 6]

### hyperparameters
- missed: vocab_size = 50257 [p. 6]
- missed: max_seq_length = 1024 [p. 6]
- missed: optimizer = Adam [p. 7]
- missed: optimizer = Adafactor [p. 7] (models above 1B parameters)
- missed: train_steps = 2.5 × 10^5 [p. 7]
- missed: batch_size = 512 [p. 7]
- missed: warmup_steps = 3000 [p. 7]
- missed: lr_schedule = cosine decay to zero [p. 7]
- missed: dataset_size = 22 million to 23 billion tokens [p. 7] (range studied)
- missed: model_shape = (36, 1280) [p. 9] (data-scaling experiments)
- not in gold: context length = 1024 _[verified]_
- not in gold: batch size = 2 19 _[verified]_

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

## 2003.10555

### task
- missed: natural language understanding [p. 4]
- missed: question answering [p. 4]

### baselines
- missed: TinyBERT [p. 15]
- missed: MobileBERT [p. 15]

### metrics
- missed: GLUE score [p. 4]
- missed: pre-training FLOPs [p. 6]

### hyperparameters
- missed: num_layers = 12 [p. 14] (Small and Base)
- missed: num_layers = 24 [p. 14] (Large)
- missed: hidden_size = 768 [p. 14] (Base)
- missed: hidden_size = 1024 [p. 14] (Large)
- missed: ffn_size = 1024 [p. 14] (Small)
- missed: ffn_size = 3072 [p. 14] (Base)
- missed: ffn_size = 4096 [p. 14] (Large)
- missed: num_heads = 4 [p. 14] (Small)
- missed: num_heads = 12 [p. 14] (Base)
- missed: num_heads = 16 [p. 14] (Large)
- missed: embedding_size = 128 [p. 14] (Small)
- missed: generator_size = 1/4 [p. 14] (Small and Large)
- missed: generator_size = 1/3 [p. 14] (Base)
- missed: mask_prob = 15% [p. 14] (Small and Base)
- missed: mask_prob = 25% [p. 14] (Large)
- missed: warmup_steps = 10000 [p. 14] (pre-training)
- missed: learning_rate = 5e-4 [p. 14] (Small pre-training)
- missed: learning_rate = 2e-4 [p. 14] (Base and Large pre-training)
- missed: adam_epsilon = 1e-6 [p. 14]
- missed: adam_beta1 = 0.9 [p. 14]
- missed: adam_beta2 = 0.999 [p. 14]
- missed: dropout = 0.1 [p. 14]
- missed: attention_dropout = 0.1 [p. 14]
- missed: weight_decay = 0.01 [p. 14] (pre-training)
- missed: batch_size = 256 [p. 14] (Base pre-training)
- missed: train_steps = 766K [p. 14] (ELECTRA-Base)
- missed: max_seq_length = 512 [p. 6] (Base and Large; Small++)
- missed: disc_loss_weight = 50 [p. 13]
- missed: learning_rate = 3e-4 [p. 14] (Small fine-tuning)
- missed: learning_rate = 1e-4 [p. 14] (Base fine-tuning)
- missed: learning_rate = 5e-5 [p. 14] (Large fine-tuning)
- missed: learning_rate = 2e-5 [p. 13] (RTE test-set fine-tuning)
- missed: layerwise_lr_decay = 0.8 [p. 14] (Base and Small fine-tuning)
- missed: layerwise_lr_decay = 0.9 [p. 14] (Large fine-tuning)
- missed: warmup_ratio = 0.1 [p. 14] (fine-tuning)
- missed: weight_decay = 0 [p. 14] (fine-tuning)
- missed: batch_size = 32 [p. 14] (fine-tuning)
- missed: epochs = 10 [p. 14] (RTE and STS)
- missed: epochs = 2 [p. 14] (SQuAD)
- missed: epochs = 3 [p. 14] (other tasks)
- missed: lr_schedule = linear [p. 14]
- not in gold: token embeddings = 128 _[verified]_
- not in gold: masked token percentage = 15% _[verified]_

### compute
- missed: 1 V100 GPU (4 days) [p. 6] (ELECTRA-Small)
- missed: 16 TPUv3s (4 days) [p. 6] (ELECTRA-Base)
- not in gold: single GPU for small model training _[verified]_
- not in gold: training time for ELMo _[verified]_
- not in gold: training time for GPT _[verified]_
- not in gold: training time for BERT-Small _[verified]_
- not in gold: training time for BERT-Base _[verified]_
- not in gold: training time for ELECTRA-Small _[verified]_
- not in gold: training time for ELECTRA-Base _[verified]_

## 2005.11401

### task
- missed: abstractive question answering [p. 4]
- missed: Jeopardy question generation [p. 5]
- missed: fact verification [p. 5]

### datasets
- missed: Wikipedia December 2016 dump [p. 7] (index hot-swapping)

### baselines
- missed: T5-11B [p. 6]
- missed: T5-11B+SSM [p. 6]
- missed: REALM [p. 6]
- missed: DPR [p. 6]
- missed: state-of-the-art pipeline models [p. 6] (MS-MARCO and FEVER-3 SotA)
- missed: BM25 retriever [p. 7] (ablation retriever)
- missed: T5-large [p. 19] (parameters comparison)
- not in gold: Extractive QA paradigm _[verified]_
- not in gold: Closed-Book QA approaches _[verified]_
- not in gold: BART model for comparison on Jeopardy _[verified]_
- not in gold: DPR QA system _[verified]_

### metrics
- missed: human evaluation of factuality and specificity [p. 5]
- missed: distinct tri-gram ratio [p. 7]
- missed: answer recall @ K [p. 8]
- not in gold: Ratio of distinct ngrams to total ngrams _[verified]_

### hyperparameters
- missed: optimizer = Adam [p. 4]
- missed: beam_size = 4 [p. 17] (generation tasks)
- missed: chunk_size = 100 [p. 4] (Wikipedia documents)
- missed: model_size = 626M [p. 18]
- missed: model_size = 400M [p. 3] (generator)
- missed: model_size = 110M [p. 18] (each DPR encoder)
- not in gold: beam size = four _[verified]_

### compute
- missed: 100 GB CPU memory for the index [p. 17]
- not in gold: CPU memory required for FAISS index _[verified]_

### code_urls
- not in gold: https://github.com/pytorch/fairseq _[verified]_

## 2006.11477

### task
- missed: self-supervised speech representation learning [p. 1]

### datasets
- missed: Librispeech LM corpus [p. 5] (language model training)

### baselines
- missed: CTC Transformer [p. 7]
- missed: S2S Transformer [p. 7]
- missed: LARGE from scratch [p. 7]
- missed: PASE+ [p. 8] (TIMIT)
- missed: vq-wav2vec [p. 8] (TIMIT)
- not in gold: CTC Transformer supervised baseline _[verified]_
- not in gold: Sequence-to-sequence Transformer supervised baseline _[verified]_
- not in gold: PASE+ baseline for TIMIT _[verified]_

### hyperparameters
- missed: mask_prob = 0.065 [p. 4] (pre-training)
- missed: mask_length = 10 [p. 4]
- missed: mask_prob = 0.075 [p. 8] (ablation pre-training; 10 min and 1 hour fine-tuning)
- missed: num_layers = 12 [p. 4] (BASE)
- missed: num_layers = 24 [p. 4] (LARGE)
- missed: hidden_size = 768 [p. 4] (BASE)
- missed: hidden_size = 1024 [p. 4] (LARGE)
- missed: ffn_size = 3072 [p. 4] (BASE)
- missed: ffn_size = 4096 [p. 4] (LARGE)
- missed: num_heads = 8 [p. 4] (BASE)
- missed: num_heads = 16 [p. 4] (LARGE)
- missed: encoder_channels = 512 [p. 4] (feature encoder)
- missed: warmup_ratio = 0.08 [p. 5] (pre-training)
- missed: codebook_groups = 2 [p. 5]
- missed: codebook_entries = 320 [p. 5]
- missed: gumbel_temperature_min = 0.5 [p. 5] (BASE)
- missed: num_distractors = 100 [p. 5]
- missed: lr_schedule = tri-state [p. 5] (fine-tuning)
- missed: beam_size = 50 [p. 5] (4-gram LM model selection; Transformer LM tuning)
- missed: beam_size = 500 [p. 5] (4-gram LM tuning; Transformer LM test)
- missed: beam_size = 1500 [p. 5] (n-gram LM test)
- missed: lm_weight = 2 [p. 5] (model selection)
- missed: word_insertion_penalty = -1 [p. 5] (model selection)
- missed: channel_mask_prob = 0.008 [p. 13] (10 min and 100 hours)
- missed: channel_mask_prob = 0.004 [p. 13] (1 hour and 10 hours)
- missed: channel_mask_prob = 0.0016 [p. 13] (960 hours)
- missed: channel_mask_prob = 0.012 [p. 13] (TIMIT)
- missed: mask_prob = 0.05 [p. 13] (100 and 960 hours fine-tuning)
- missed: train_steps = 12k [p. 13] (10 min fine-tuning)
- missed: train_steps = 13k [p. 13] (1 hour fine-tuning)
- missed: train_steps = 20k [p. 13] (10 hours fine-tuning)
- missed: train_steps = 50k [p. 13] (100 hours fine-tuning)
- missed: train_steps = 320k [p. 13] (960 hours fine-tuning)
- missed: train_steps = 40k [p. 13] (TIMIT fine-tuning)
- missed: model_size = 95M [p. 6] (BASE)
- missed: model_size = 317M [p. 6] (LARGE)
- not in gold: quantization groups and codebook size = G = 2 and V = 320 _[verified]_
- not in gold: number of distractors = K = 100 _[verified]_
- not in gold: model size = 12 transformer blocks, model dimension 768, inner dimension (FFN) 3,072 and 8 attention heads _[verified]_
- not in gold: model size = 24 transformer blocks with model dimension 1,024, inner dimension 4,096 and 16 attention heads _[verified]_
- not in gold: masking probability = p = 0.075 _[verified]_

### compute
- missed: 8 / 24 GPUs fine-tuning [p. 5]

### code_urls
- not in gold: https://github.com/facebook/Ax _[verified]_

## 2010.11929

### task
- missed: transfer learning [p. 1]

### baselines
- missed: hybrid models [p. 7] (ResNet+ViT hybrids in the scaling study)

### metrics
- missed: VTAB score [p. 6]
- missed: TPUv3-core-days [p. 5]

### hyperparameters
- missed: adam_beta1 = 0.9 [p. 5]
- missed: adam_beta2 = 0.999 [p. 5]
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
- not in gold: beta_1 = 0.9 _[verified]_
- not in gold: beta_2 = 0.999 _[verified]_

### code_urls
- not in gold: https://github.com/csrhddlam/axial-deeplab _[verified]_

## 2103.14030

### task
- missed: instance segmentation [p. 6]

### baselines
- missed: EfficientNet [p. 6]
- missed: ViT [p. 6]
- missed: BiT ResNet [p. 6]
- missed: ResNet-50 [p. 7]
- missed: GCNet [p. 7]
- missed: RelationNet++ [p. 7]
- missed: SpineNet-190 [p. 7]
- missed: ResNeSt-200 [p. 7]
- missed: EfficientDet-D7 [p. 7]
- missed: DetectoRS [p. 7]
- missed: YOLOv4 P7 [p. 7]
- missed: Copy-paste [p. 7]
- missed: DANet [p. 7]
- missed: DeepLabv3+ [p. 7]
- missed: ACNet [p. 7]
- missed: DNL [p. 7]
- missed: OCRNet [p. 7]
- missed: UperNet ResNet-101 [p. 7]
- missed: MLP-Mixer [p. 11]
- missed: ResMLP [p. 11]
- not in gold: Improved HTC (denoted as HTC++) _[verified]_

### metrics
- missed: top-5 accuracy [p. 8]
- missed: throughput [p. 6]
- missed: FLOPs [p. 6]
- missed: parameters [p. 6]

### hyperparameters
- missed: lr_schedule = cosine decay [p. 5] (ImageNet-1K)
- missed: max_grad_norm = 1 [p. 9]
- missed: drop_path = 0.2 [p. 9] (Swin-T; COCO and ADE20K)
- missed: drop_path = 0.3 [p. 9] (Swin-S)
- missed: drop_path = 0.5 [p. 9] (Swin-B)
- missed: drop_path = 0.1 [p. 9] (higher-resolution fine-tuning)
- missed: lr_schedule = linear decay [p. 6] (ImageNet-22K and ADE20K)
- missed: epochs = 72 [p. 6] (COCO system-level)
- missed: learning_rate = 6e-5 [p. 10] (ADE20K)
- missed: warmup_steps = 1500 [p. 10] (ADE20K)
- missed: train_steps = 160K [p. 10] (ADE20K)
- missed: image_size = 224 [p. 9]
- missed: image_size = 384 [p. 9]
- missed: image_size = 512 [p. 10] (ADE20K Swin-T/S)
- missed: image_size = 640 [p. 10] (ADE20K Swin-B/L)
- missed: window_size = 7 [p. 10]
- missed: hidden_size = 96 [p. 10] (Swin-T and Swin-S)
- missed: hidden_size = 128 [p. 10] (Swin-B)
- missed: hidden_size = 192 [p. 10] (Swin-L)
- missed: layer_numbers = {2, 2, 6, 2} [p. 10] (Swin-T)
- missed: layer_numbers = {2, 2, 18, 2} [p. 10] (Swin-S/B/L)
- missed: model_size = 29M [p. 6] (Swin-T)
- missed: model_size = 50M [p. 6] (Swin-S)
- missed: model_size = 88M [p. 6] (Swin-B)
- missed: model_size = 197M [p. 6] (Swin-L)

### compute
- missed: 8 GPUs [p. 10] (ADE20K training)

## 2104.08821

### task
- missed: transfer tasks [p. 2] (SentEval)

### datasets
- missed: STS13 [p. 6]
- missed: STS14 [p. 6]
- missed: STS15 [p. 6]
- missed: MR [p. 15] (transfer task)
- missed: CR [p. 15] (transfer task)
- missed: SUBJ [p. 15] (transfer task)
- missed: MPQA [p. 15] (transfer task)
- missed: SST-2 [p. 15] (transfer task)
- missed: TREC [p. 15] (transfer task)
- missed: MRPC [p. 15] (transfer task)

### baselines
- missed: BERT first-last avg. [p. 7]
- missed: CT-BERT [p. 7]
- missed: RoBERTa first-last avg. [p. 7]
- missed: RoBERTa-whitening [p. 7]
- missed: SBERT [p. 7]
- missed: CT-SBERT [p. 7]
- missed: SRoBERTa [p. 7]
- missed: SRoBERTa-whitening [p. 7]
- not in gold: Average BERT or RoBERTa embeddings _[verified]_
- not in gold: CT _[verified]_
- not in gold: SBERT/SRoBERTa _[verified]_

### metrics
- missed: accuracy [p. 16] (transfer tasks)

### hyperparameters
- missed: epochs = 1 [p. 13] (unsupervised SimCSE)
- missed: eval_interval = 250 [p. 13]
- missed: dropout = 0.1 [p. 4] (default dropout from Transformers)
- not in gold: epochs = one _[verified]_

### code_urls
- not in gold: https://github.com/huggingface/ _[verified]_
- not in gold: https://github.com/facebookresearch/ _[verified]_

## 2106.09685

### task
- missed: natural language understanding [p. 5]
- missed: natural language generation [p. 5]
- missed: NL to SQL [p. 2]
- missed: summarization [p. 2]

### metrics
- missed: Matthew's correlation [p. 6] (CoLA)
- missed: Pearson correlation [p. 6] (STS-B)
- missed: TER [p. 21] (DART / WebNLG)
- missed: number of trainable parameters [p. 6]
- missed: inference latency [p. 4]

### hyperparameters
- missed: optimizer = AdamW [p. 18]
- missed: lora_rank = 8 [p. 19] (RoBERTa / DeBERTa / GPT-3 37.7M budget)
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

## 2111.06377

### task
- missed: self-supervised visual representation learning [p. 1]
- missed: image classification [p. 6]
- missed: object detection [p. 8]
- missed: instance segmentation [p. 8]
- missed: semantic segmentation [p. 8]
- not in gold: computer vision _[verified]_

### datasets
- missed: ImageNet-C [p. 12] (robustness)
- missed: ImageNet-A [p. 12] (robustness)
- missed: ImageNet-R [p. 12] (robustness)
- missed: ImageNet-Sketch [p. 12] (robustness)

### baselines
- missed: DINO [p. 7]
- missed: BEiT [p. 7]
- missed: supervised pre-training [p. 7]
- missed: iGPT [p. 12] (linear probing)
- not in gold: ViT-Large backbone used in ablation studies _[verified]_
- not in gold: BEiT masked image modeling method _[verified]_
- not in gold: DINO self-supervised method _[partial]_
- not in gold: Supervised training baseline _[partial]_

### metrics
- missed: mean corruption error [p. 12] (IN-C)
- missed: wall-clock training time [p. 5]

### hyperparameters
- missed: epochs = 800 [p. 5] (ablations)
- missed: epochs = 1600 [p. 7] (final models)
- missed: optimizer = AdamW [p. 11] (pre-training and fine-tuning)
- missed: learning_rate = 1.5e-4 [p. 11] (pre-training)
- missed: weight_decay = 0.05 [p. 11] (pre-training and fine-tuning)
- missed: adam_beta2 = 0.95 [p. 11] (pre-training and supervised scratch)
- missed: adam_beta1 = 0.9 [p. 11]
- missed: batch_size = 4096 [p. 11] (pre-training and supervised scratch)
- missed: lr_schedule = cosine decay [p. 11]
- missed: warmup_epochs = 40 [p. 11] (pre-training)
- missed: learning_rate = 1e-3 [p. 11] (fine-tuning)
- missed: adam_beta2 = 0.999 [p. 11] (fine-tuning)
- missed: layerwise_lr_decay = 0.75 [p. 11] (fine-tuning)
- missed: batch_size = 1024 [p. 11] (fine-tuning)
- missed: warmup_epochs = 5 [p. 11] (fine-tuning)
- missed: randaugment = (9, 0.5) [p. 11]
- missed: label_smoothing = 0.1 [p. 11]
- missed: mixup = 0.8 [p. 11]
- missed: cutmix = 1.0 [p. 11]
- missed: drop_path = 0.1 [p. 11] (ViT-B/L fine-tuning; ViT-B scratch)
- missed: drop_path = 0.2 [p. 11] (ViT-H fine-tuning; L/H scratch)
- missed: optimizer = LARS [p. 11] (linear probing)
- missed: learning_rate = 0.1 [p. 11] (linear probing)
- missed: weight_decay = 0 [p. 11] (linear probing)
- missed: momentum = 0.9 [p. 11] (linear probing)
- missed: batch_size = 16384 [p. 11] (linear probing)
- missed: warmup_epochs = 10 [p. 11] (linear probing)
- missed: epochs = 90 [p. 11] (linear probing)
- missed: learning_rate = 1e-4 [p. 12] (supervised from scratch)
- missed: weight_decay = 0.3 [p. 11] (supervised from scratch)
- missed: warmup_epochs = 20 [p. 12] (supervised from scratch)
- missed: epochs = 300 [p. 12] (supervised ViT-B from scratch)
- missed: epochs = 200 [p. 12] (supervised ViT-L/H from scratch)
- missed: ema_decay = 0.9999 [p. 12] (supervised from scratch)
- missed: image_size = 224 [p. 7]
- missed: image_size = 448 [p. 7] (ViT-H448)
- missed: model_size = 304M [p. 12] (ViT-L)
- missed: model_size = 632M [p. 12] (ViT-H)
- missed: model_size = 86M [p. 12] (ViT-B)
- not in gold: pre-training length = 800 epochs _[verified]_
- not in gold: pre-training length = 1600 epochs _[verified]_

## 2112.10752

### task
- missed: high-resolution image synthesis [p. 1]
- missed: layout-to-image synthesis [p. 2]
- missed: semantic synthesis [p. 7]

### datasets
- missed: Landscapes [p. 7] (semantic synthesis)
- missed: DIV2K [p. 1] (figure only)

### baselines
- missed: StyleGAN2 [p. 6]
- missed: BigGan-deep [p. 7]
- missed: Pixel-DM [p. 8]

### metrics
- missed: FID [p. 5]
- missed: PSNR [p. 8]
- missed: SSIM [p. 8]
- missed: LPIPS [p. 9]
- missed: user study preference [p. 8]
- not in gold: Fréchet Inception Distance _[verified]_
- not in gold: Peak Signal-to-Noise Ratio _[verified]_
- not in gold: Structural Similarity Index _[verified]_
- not in gold: Learned Perceptual Image Patch Similarity _[verified]_

### hyperparameters
- missed: downsampling_factor = 4 [p. 5]
- missed: downsampling_factor = 8 [p. 5]
- missed: model_size = 1.45B [p. 7] (text-to-image LDM-KL-8)
- missed: model_size = 400M [p. 7] (class-conditional LDM-4)
- missed: model_size = 274M [p. 24] (unconditional LDMs)
- missed: diffusion_steps = 1000 [p. 24]
- missed: noise_schedule = linear [p. 24]
- missed: sampling_steps = 200 [p. 6]
- missed: sampling_steps = 250 [p. 6]
- missed: guidance_scale = 10.0 [p. 6] (text-to-image samples)
- missed: guidance_scale = 1.5 [p. 6] (LDM-KL-8-G and LDM-4-G)
- missed: ddim_eta = 1.0 [p. 6]
- missed: codebook_size = 8192 [p. 24]
- missed: channels = 224 [p. 24]
- missed: channels = 192 [p. 24]
- missed: channels = 320 [p. 25] (text-to-image)
- missed: depth = 2 [p. 24]
- missed: batch_size = 48 [p. 24]
- missed: batch_size = 42 [p. 24] (FFHQ)
- missed: batch_size = 96 [p. 24] (LSUN-Churches)
- missed: train_steps = 410k [p. 24] (CelebA-HQ)
- missed: train_steps = 635k [p. 24] (FFHQ)
- missed: train_steps = 500k [p. 24] (LSUN-Churches)
- missed: train_steps = 1.9M [p. 24] (LSUN-Bedrooms)
- missed: learning_rate = 9.6e-5 [p. 24] (CelebA-HQ and LSUN-Bedrooms)
- missed: learning_rate = 8.4e-5 [p. 24] (FFHQ)
- missed: learning_rate = 5.0e-5 [p. 24] (LSUN-Churches)
- missed: batch_size = 680 [p. 25] (text-to-image)
- missed: train_steps = 390K [p. 25] (text-to-image)
- missed: learning_rate = 1.0e-4 [p. 25] (text-to-image and class-conditional)
- missed: batch_size = 1200 [p. 25] (class-conditional ImageNet)
- missed: train_steps = 178K [p. 25] (class-conditional ImageNet)
- missed: num_heads = 8 [p. 25] (text-to-image)
- missed: hidden_size = 1280 [p. 25] (text-to-image)
- missed: dropout = 0.1 [p. 25] (layout-to-image COCO)
- missed: model_size = 387M [p. 8] (big inpainting model; added in adjudication)
- not in gold: parameters = 1.45B _[verified]_
- not in gold: parameters = 387M _[verified]_

### compute
- missed: eight V100 [p. 25] (inpainting model)

### code_urls
- missed: https://github.com/CompVis/latent-diffusion [p. 1]
- not in gold: https://github.com/lucidrains/x-transformers _[verified]_
- not in gold: https://huggingface.co/transformers/model_doc/bert.html _[verified]_

## 2201.03545

### task
- missed: instance segmentation [p. 8]
- missed: robustness evaluation [p. 10]

### datasets
- missed: ImageNet-A [p. 10] (robustness)
- missed: ImageNet-R [p. 10] (robustness)
- missed: ImageNet-Sketch [p. 10] (robustness)
- missed: ImageNet-C [p. 10] (robustness)

### baselines
- missed: EfficientNetV2 [p. 7]
- missed: ViT [p. 7]
- missed: BiT ResNet [p. 7]
- missed: ResNeXt-101 [p. 8]

### metrics
- missed: box AP [p. 8]
- missed: mask AP [p. 8]
- missed: throughput [p. 7]
- missed: FLOPs [p. 7]
- missed: mean corruption error [p. 10]
- missed: training memory [p. 8]
- not in gold: AP _[verified]_

### hyperparameters
- missed: adam_beta1 = 0.9 [p. 9]
- missed: adam_beta2 = 0.999 [p. 9]
- missed: lr_schedule = cosine decay [p. 9]
- missed: warmup_epochs = 50 [p. 9] (isotropic ConvNeXt)
- missed: randaugment = (9, 0.5) [p. 9]
- missed: mixup = 0.8 [p. 9] (pre-training)
- missed: cutmix = 1.0 [p. 9] (pre-training)
- missed: random_erasing = 0.25 [p. 9]
- missed: label_smoothing = 0.1 [p. 9]
- missed: drop_path = 0.1/0.4/0.5/0.5 [p. 9] (ImageNet-1K T/S/B/L)
- missed: drop_path = 0.0/0.0/0.1/0.1/0.2 [p. 9] (ImageNet-22K T/S/B/L/XL)
- missed: layer_scale_init = 1e-6 [p. 9]
- missed: ema_decay = 0.9999 [p. 9] (ImageNet-1K)
- missed: weight_init = trunc. normal (0.2) [p. 9]
- missed: layerwise_lr_decay = 0.7 [p. 10] (ImageNet-1K pre-trained fine-tuning)
- missed: layerwise_lr_decay = 0.8 [p. 10] (ImageNet-22K pre-trained fine-tuning)
- missed: head_init_scale = 0.001 [p. 10] (fine-tuning)
- missed: learning_rate = 1e-4 [p. 10] (COCO and ADE20K sweep)
- missed: learning_rate = 2e-4 [p. 10] (COCO sweep)
- missed: learning_rate = 8e-5 [p. 10] (ADE20K sweep)
- missed: kernel_size = 7 [p. 5]
- missed: hidden_size = (96, 192, 384, 768) [p. 6] (ConvNeXt-T and S)
- missed: hidden_size = (128, 256, 512, 1024) [p. 6] (ConvNeXt-B)
- missed: hidden_size = (192, 384, 768, 1536) [p. 6] (ConvNeXt-L)
- missed: hidden_size = (256, 512, 1024, 2048) [p. 6] (ConvNeXt-XL)
- missed: num_blocks = (3, 3, 9, 3) [p. 6] (ConvNeXt-T)
- missed: num_blocks = (3, 3, 27, 3) [p. 6] (ConvNeXt-S/B/L/XL)
- missed: image_size = 224 [p. 7]
- missed: image_size = 384 [p. 7]
- missed: model_size = 29M [p. 7] (ConvNeXt-T)
- missed: model_size = 50M [p. 7] (ConvNeXt-S)
- missed: model_size = 89M [p. 7] (ConvNeXt-B)
- missed: model_size = 198M [p. 7] (ConvNeXt-L)
- missed: model_size = 350M [p. 7] (ConvNeXt-XL)

### compute
- missed: V100 GPU [p. 7] (throughput)

### code_urls
- missed: https://github.com/facebookresearch/ConvNeXt [p. 1]

## 2201.11903

### task
- missed: chain-of-thought prompting [p. 1]
- missed: arithmetic reasoning [p. 2]
- missed: commonsense reasoning [p. 2]

### datasets
- missed: Last Letter Concatenation [p. 4] (symbolic)
- missed: Coin Flip [p. 4] (symbolic)

### baselines
- missed: finetuned GPT-3 with verifier [p. 2]
- missed: equation only [p. 5] (ablation)
- missed: variable compute only [p. 6] (ablation)
- missed: reasoning after answer [p. 6] (ablation)
- missed: GPT-3 [p. 4] (evaluated model)
- missed: LaMDA [p. 4] (evaluated model)
- missed: PaLM [p. 4] (evaluated model)
- missed: UL2 20B [p. 4] (evaluated model)
- missed: Codex [p. 4] (evaluated model)

### metrics
- missed: solve rate [p. 5] (math word problems)
- missed: accuracy [p. 6]

### hyperparameters
- missed: num_exemplars = 8 [p. 3] (math word problems)
- missed: num_exemplars = 4 [p. 4] (AQuA)
- missed: num_exemplars = 6 [p. 7] (SayCan)
- missed: decoding = greedy decoding [p. 4]
- missed: model_size = 540B [p. 1] (largest model)
- missed: model_size = 137B [p. 4]
- missed: model_size = 175B [p. 4]

### code_urls
- not in gold: https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/strategyqa _[verified]_
- not in gold: https://github.com/eladsegal/strategyqa _[verified]_
- not in gold: https://github.com/eladsegal/strategyqa/blob/main/LICENSE _[verified]_

## 2203.15556

### task
- missed: compute-optimal training of large language models [p. 1]
- missed: language modelling [p. 10]
- missed: reading comprehension [p. 10]
- missed: question answering [p. 10]
- missed: common sense reasoning [p. 10]
- not in gold: Training transformer language models under a given compute budget. _[verified]_

### datasets
- missed: Winogender [p. 14]
- missed: GitHub [p. 8] (IsoFLOP reproduction)
- not in gold: GitHub code _[verified]_

### baselines
- missed: Kaplan et al. (2020) scaling laws [p. 1] (scaling-law comparison)

### metrics
- missed: exact match [p. 13] (closed-book QA)

### hyperparameters
- missed: model_size = 70B [p. 1] (Chinchilla)
- missed: train_tokens = 1.4T [p. 2] (Chinchilla)
- missed: num_layers = 80 [p. 9] (Chinchilla and Gopher)
- missed: num_heads = 64 [p. 9] (Chinchilla)
- missed: head_dim = 128 [p. 9]
- missed: hidden_size = 8192 [p. 9] (Chinchilla)
- missed: learning_rate = 1e-4 [p. 9] (Chinchilla)
- missed: ffn_size = 4 × dmodel [p. 9]
- missed: lr_schedule = cosine [p. 5] (decays 10x over the training horizon)
- missed: precision = bfloat16 [p. 9] (float32 copy of weights in optimiser)
- missed: tokenizer = SentencePiece [p. 9] (no NFKC normalisation)
- missed: num_heads = 128 [p. 9] (Gopher 280B)
- missed: hidden_size = 16384 [p. 9] (Gopher 280B)
- missed: learning_rate = 4e-5 [p. 9] (Gopher 280B)
- not in gold: maximum learning rate = 4 × 10^−^5 _[partial]_
- not in gold: maximum learning rate = 1 × 10^−^4 _[partial]_

### compute
- missed: TPUv3/TPUv4 [p. 9]
- missed: 5.76 × 10^23 FLOPs [p. 5] (Gopher compute budget)
- not in gold: Hardware used for training models _[verified]_

## 2205.14135

### task
- missed: efficient exact attention [p. 1]
- missed: language modeling [p. 7]
- missed: long document classification [p. 7]
- missed: long-range sequence modeling [p. 7]
- not in gold: natural language processing _[verified]_
- not in gold: image classification _[verified]_

### datasets
- missed: ListOps [p. 8] (LRA task)
- missed: Text [p. 8] (LRA task)
- missed: Retrieval [p. 8] (LRA task)
- missed: Image [p. 8] (LRA task)
- missed: Pathfinder [p. 8] (LRA task)

### baselines
- missed: Transformer [p. 8] (LRA)
- missed: Linformer [p. 8]
- missed: Linear Attention [p. 8]
- missed: Performer [p. 8]
- missed: Local Attention [p. 8]
- missed: Reformer [p. 8]
- missed: Smyrf [p. 8]
- missed: PyTorch attention [p. 2] (attention runtime)
- not in gold: Rabe and Staats _[verified]_
- not in gold: Apex FMHA _[verified]_

### metrics
- missed: runtime [p. 9] (attention benchmarks)
- missed: memory footprint [p. 9]

### hyperparameters
- missed: precision = FP16 [p. 26] (BERT-large)
- missed: max_seq_length = 512 [p. 1] (BERT-large)
- missed: precision = mixed-precision [p. 26] (GPT-2)
- missed: tokenizer = GPT-2 BPE [p. 26]
- missed: max_seq_length = 1024 [p. 1] (GPT-2)
- missed: max_seq_length = 4096 [p. 8] (GPT-2 long context)
- missed: max_seq_length = 16384 [p. 1] (Path-X)
- missed: max_seq_length = 65536 [p. 1] (Path-256)
- missed: head_dim = 64 [p. 6] (benchmark)
- missed: num_heads = 16 [p. 6] (benchmark)
- missed: batch_size = 64 [p. 6] (benchmark)
- not in gold: dropout = 0.1 _[verified]_

### compute
- missed: 8×A100-80GB GPUs [p. 26] (BERT-large)
- missed: 8×A100-40GB GPUs [p. 26] (GPT-2)
- not in gold: 8x A100 GPUs for BERT-large _[verified]_
- not in gold: 8x A100-80GB GPUs for training _[verified]_
- not in gold: 8x A100-40GB GPUs for GPT-2 training _[verified]_

### code_urls
- not in gold: https://github.com/NVIDIA/apex/tree/master/apex/contrib/csrc/fmha _[verified]_

## 2210.02747

### task
- missed: image super-resolution [p. 9] (64×64 to 256×256)

### datasets
- missed: 2D checkerboard [p. 9] (toy example)

### hyperparameters
- missed: optimizer = Adam [p. 20]
- missed: adam_beta1 = 0.9 [p. 20]
- missed: adam_beta2 = 0.999 [p. 20]
- missed: weight_decay = 0.0 [p. 20]
- missed: adam_epsilon = 1e-8 [p. 20]
- missed: ode_tolerance = 1e-5 [p. 7] (dopri5)
- missed: hidden_size = 256 [p. 20] (CIFAR10 ImageNet-32 ImageNet-128)
- missed: hidden_size = 192 [p. 20] (ImageNet-64)
- missed: depth = 2 [p. 20] (CIFAR10)
- missed: depth = 3 [p. 20] (ImageNet)
- missed: num_heads = 4 [p. 20]
- missed: head_channels = 64 [p. 20]
- missed: dropout = 0.0 [p. 20]
- missed: batch_size = 256 [p. 20] (CIFAR10)
- missed: batch_size = 1024 [p. 20] (ImageNet-32)
- missed: batch_size = 2048 [p. 20] (ImageNet-64)
- missed: batch_size = 1536 [p. 20] (ImageNet-128)
- missed: epochs = 1000 [p. 20] (CIFAR10)
- missed: epochs = 200 [p. 20] (ImageNet-32)
- missed: epochs = 250 [p. 20] (ImageNet-64)
- missed: epochs = 571 [p. 20] (ImageNet-128)
- missed: train_steps = 391k [p. 20] (CIFAR10)
- missed: train_steps = 250k [p. 20] (ImageNet-32)
- missed: train_steps = 157k [p. 20] (ImageNet-64)
- missed: train_steps = 500k [p. 20] (ImageNet-128)
- missed: learning_rate = 5e-4 [p. 20] (CIFAR10)
- missed: learning_rate = 1e-4 [p. 20] (ImageNet)
- missed: lr_schedule = polynomial decay [p. 20] (CIFAR10 ImageNet-32 ImageNet-128)
- missed: lr_schedule = constant [p. 20] (ImageNet-64)
- missed: warmup_steps = 45k [p. 20] (CIFAR10)
- missed: warmup_steps = 20k [p. 20] (ImageNet-32 and ImageNet-128)
- missed: beta_min = 0.1 [p. 20] (diffusion path)
- missed: beta_max = 20 [p. 20] (diffusion path)
- missed: num_layers = 5 [p. 19] (2D example)
- missed: hidden_size = 512 [p. 19] (2D example MLP)
- missed: precision = 16-bit mixed precision [p. 20] (ImageNet-64/128/256; 32-bit for CIFAR10 and ImageNet-32)

### compute
- missed: 2 / 4 / 16 / 32 GPUs [p. 20] (CIFAR10 / ImageNet-32 / 64 / 128)

### code_urls
- not in gold: https://github.com/tensorflow/gan _[verified]_
- not in gold: https://github.com/openai/guided-diffusion _[verified]_

## 2210.03629

### task
- missed: synergizing reasoning and acting in language models [p. 1]

### baselines
- missed: BUTLER [p. 7] (ALFWorld imitation learning)
- missed: IL [p. 7] (WebShop)
- missed: IL+RL [p. 8] (WebShop)
- missed: ReAct-IM [p. 8] (ALFWorld)
- not in gold: BUTLER imitation learning agent _[verified]_

### metrics
- missed: accuracy [p. 5] (FEVER)

### hyperparameters
- missed: model_size = 540B [p. 3] (prompted model)
- missed: num_exemplars = 6 [p. 4] (HotpotQA)
- missed: num_exemplars = 3 [p. 4] (FEVER)
- missed: num_samples = 21 [p. 5] (CoT-SC)
- missed: num_trajectories = 3000 [p. 5] (fine-tuning data)
- missed: num_exemplars = 2 [p. 7] (ALFWorld)
- missed: num_exemplars = 1 [p. 8] (WebShop)
- missed: decoding = greedy decoding [p. 8]
- missed: batch_size = 64 [p. 15] (fine-tuning)
- missed: train_steps = 4000 [p. 15] (ReAct and Act fine-tuning)
- missed: train_steps = 2000 [p. 15] (PaLM-8B Standard and CoT)
- missed: train_steps = 1000 [p. 15] (PaLM-62B Standard and CoT)
- missed: model_size = 8B [p. 5] (fine-tuned)
- missed: model_size = 62B [p. 5] (fine-tuned)

### code_urls
- missed: https://react-lm.github.io/ [p. 1] (project page with code)

## 2211.14730

### task
- missed: transfer learning [p. 7]

### metrics
- missed: MSE [p. 6]
- missed: MAE [p. 6]
- not in gold: Mean Squared Error _[verified]_
- not in gold: Mean Absolute Error _[verified]_

### hyperparameters
- missed: patch_length = 16 [p. 2]
- missed: stride = 8 [p. 2]
- missed: lookback_window = 336 [p. 6] (PatchTST/42)
- missed: lookback_window = 512 [p. 6] (PatchTST/64)
- missed: num_patches = 42 [p. 6]
- missed: num_patches = 64 [p. 6]
- missed: prediction_length = 96 [p. 6]
- missed: prediction_length = 192 [p. 6]
- missed: prediction_length = 336 [p. 6]
- missed: prediction_length = 720 [p. 6]
- missed: prediction_length = 24 [p. 6] (ILI)
- missed: prediction_length = 36 [p. 6] (ILI)
- missed: prediction_length = 48 [p. 6] (ILI)
- missed: prediction_length = 60 [p. 6] (ILI)
- missed: mask_ratio = 40% [p. 6] (self-supervised)
- missed: num_layers = 3 [p. 14]
- missed: num_heads = 16 [p. 14]
- missed: hidden_size = 128 [p. 14]
- missed: ffn_size = 256 [p. 14]
- missed: num_heads = 4 [p. 14] (ILI / ETTh1 / ETTh2)
- missed: hidden_size = 16 [p. 14] (ILI / ETTh1 / ETTh2)
- missed: ffn_size = 128 [p. 14] (ILI / ETTh1 / ETTh2)
- missed: dropout = 0.2 [p. 14]
- missed: activation = GELU [p. 14]
- missed: normalization = BatchNorm [p. 5]
- missed: patch_length = 12 [p. 6] (self-supervised (non-overlapping))
- not in gold: input sequence length = 512 _[verified]_
- not in gold: patch size = 12 _[verified]_
- not in gold: masking ratio = 40% _[verified]_

### compute
- missed: NVIDIA A40 48GB [p. 9]

### code_urls
- not in gold: https://github.com/zhouhaoyi/ETDataset _[verified]_
- not in gold: https://github.com/laiguokun/multivariate-time-series-data _[verified]_

## 2212.04356

### task
- missed: speech translation [p. 2]
- missed: language identification [p. 8]
- missed: long-form transcription [p. 9]

### datasets
- missed: Whisper training data [p. 1] (weakly supervised web audio)
- missed: LibriSpeech [p. 5]
- missed: TED-LIUM 3 [p. 3]
- missed: Artie [p. 6]
- missed: Common Voice [p. 6]
- missed: CHiME6 [p. 6]
- missed: CORAAL [p. 6]
- missed: AMI IHM [p. 6]
- missed: AMI SDM1 [p. 6]
- missed: Switchboard [p. 6]
- missed: CallHome [p. 6]
- missed: WSJ [p. 6]
- missed: Meanwhile [p. 9] (long-form)
- missed: Rev16 [p. 9] (long-form)
- missed: Kincaid46 [p. 9] (long-form)
- missed: Earnings-21 [p. 9] (long-form)
- missed: Earnings-22 [p. 9] (long-form)

### baselines
- missed: wav2vec 2.0 [p. 6]
- missed: supervised LibriSpeech models [p. 6]
- missed: XMEF-X [p. 8]
- missed: w2v-bert-51 [p. 8]
- missed: NVIDIA STT [p. 8]
- missed: commercial ASR systems [p. 10]
- missed: human transcribers [p. 10]

### metrics
- missed: accuracy [p. 8]
- missed: effective robustness [p. 6]

### hyperparameters
- missed: num_layers = 4 [p. 5] (Tiny)
- missed: num_layers = 6 [p. 5] (Base)
- missed: num_layers = 12 [p. 5] (Small)
- missed: num_layers = 24 [p. 5] (Medium)
- missed: num_layers = 32 [p. 5] (Large)
- missed: hidden_size = 384 [p. 5] (Tiny)
- missed: hidden_size = 512 [p. 5] (Base)
- missed: hidden_size = 768 [p. 5] (Small)
- missed: hidden_size = 1024 [p. 5] (Medium)
- missed: hidden_size = 1280 [p. 5] (Large)
- missed: num_heads = 6 [p. 5] (Tiny)
- missed: num_heads = 8 [p. 5] (Base)
- missed: num_heads = 12 [p. 5] (Small)
- missed: num_heads = 16 [p. 5] (Medium)
- missed: num_heads = 20 [p. 5] (Large)
- missed: model_size = 39M [p. 5] (Tiny)
- missed: model_size = 74M [p. 5] (Base)
- missed: model_size = 244M [p. 5] (Small)
- missed: model_size = 769M [p. 5] (Medium)
- missed: model_size = 1550M [p. 5] (Large)
- missed: sample_rate = 16000 Hz [p. 3]
- missed: num_mel_channels = 80 [p. 3]
- missed: window_size = 25 ms [p. 3]
- missed: stride = 10 ms [p. 3]
- missed: segment_length = 30 seconds [p. 2]
- missed: tokenizer = byte-level BPE [p. 3]
- missed: train_steps = 1048576 [p. 28]
- missed: grad_clip = 1.0 [p. 28]
- missed: adam_beta1 = 0.9 [p. 28]
- missed: adam_beta2 = 0.98 [p. 28]
- missed: adam_epsilon = 1e-6 [p. 28]
- missed: weight_decay = 0.1 [p. 28]
- missed: initialization = Gaussian Fan-In [p. 28]
- missed: lr_schedule = linear decay [p. 28]
- missed: precision = FP16 [p. 4]
- missed: train_steps = 655360 [p. 28] (Large V2)
- missed: batch_size = 1024 [p. 28] (Large V2)
- missed: bpe_dropout = 0.1 [p. 28] (Large V2)
- missed: drop_path = 0.1 [p. 28] (Large V2)
- missed: specaugment = LibriSpeech Basic [p. 28] (Large V2)
- missed: learning_rate = 2.0e-4 [p. 28] (Large V2)

## 2212.09748

### task
- missed: class-conditional image generation [p. 5]
- not in gold: image-level generative modeling _[verified]_

### metrics
- missed: Gflops [p. 8]

### hyperparameters
- missed: num_layers = 12 [p. 5] (DiT-S and DiT-B)
- missed: num_layers = 24 [p. 5] (DiT-L)
- missed: num_layers = 28 [p. 5] (DiT-XL)
- missed: hidden_size = 384 [p. 5] (DiT-S)
- missed: hidden_size = 768 [p. 5] (DiT-B)
- missed: hidden_size = 1024 [p. 5] (DiT-L)
- missed: hidden_size = 1152 [p. 5] (DiT-XL)
- missed: num_heads = 6 [p. 5] (DiT-S)
- missed: num_heads = 12 [p. 5] (DiT-B)
- missed: num_heads = 16 [p. 5] (DiT-L and DiT-XL)
- missed: patch_size = 2 [p. 8]
- missed: patch_size = 4 [p. 8]
- missed: patch_size = 8 [p. 8]
- missed: weight_decay = 0 [p. 6]
- missed: diffusion_steps = 1000 [p. 6]
- missed: beta_start = 1e-4 [p. 6]
- missed: beta_end = 2e-2 [p. 6]
- missed: vae_downsample = 8 [p. 6]
- missed: sampling_steps = 250 [p. 6]
- missed: train_steps = 400K [p. 8] (scaling study)
- missed: train_steps = 7M [p. 8] (DiT-XL/2 256×256)
- missed: train_steps = 3M [p. 9] (DiT-XL/2 512×512)
- missed: cfg_scale = 1.25 [p. 9]
- missed: cfg_scale = 1.50 [p. 9]
- missed: image_size = 256 [p. 5]
- missed: image_size = 512 [p. 5]
- not in gold: weight decay = no weight decay _[verified]_

## 2302.13971

### task
- missed: common sense reasoning [p. 4]
- missed: closed-book question answering [p. 5]
- missed: reading comprehension [p. 5]
- missed: mathematical reasoning [p. 5]
- missed: code generation [p. 5]

### datasets
- missed: RealToxicityPrompts [p. 8]
- missed: CrowS-Pairs [p. 9]
- missed: WinoGender [p. 9]
- missed: TruthfulQA [p. 9]

### baselines
- missed: PaLM-cont [p. 4]
- missed: OPT-IML [p. 7] (instruction-tuned comparison)
- missed: Flan-T5-XXL [p. 7] (instruction-tuned comparison)

### metrics
- missed: maj1@k [p. 5] (MATH and GSM8k)
- missed: toxicity score [p. 8] (RealToxicityPrompts)
- missed: truthful and informative fraction [p. 10] (TruthfulQA)

### hyperparameters
- missed: model_size = 6.7B [p. 3]
- missed: model_size = 13.0B [p. 3]
- missed: model_size = 32.5B [p. 3]
- missed: model_size = 65.2B [p. 3]
- missed: hidden_size = 4096 [p. 3] (7B)
- missed: hidden_size = 5120 [p. 3] (13B)
- missed: hidden_size = 6656 [p. 3] (33B)
- missed: hidden_size = 8192 [p. 3] (65B)
- missed: num_heads = 32 [p. 3] (7B)
- missed: num_heads = 40 [p. 3] (13B)
- missed: num_heads = 52 [p. 3] (33B)
- missed: num_heads = 64 [p. 3] (65B)
- missed: num_layers = 32 [p. 3] (7B)
- missed: num_layers = 40 [p. 3] (13B)
- missed: num_layers = 60 [p. 3] (33B)
- missed: num_layers = 80 [p. 3] (65B)
- missed: learning_rate = 3.0e-4 [p. 3] (7B and 13B)
- missed: learning_rate = 1.5e-4 [p. 3] (33B and 65B)
- missed: train_tokens = 1.0T [p. 3] (7B and 13B)
- missed: train_tokens = 1.4T [p. 3] (33B and 65B)
- missed: optimizer = AdamW [p. 3]
- missed: adam_beta1 = 0.9 [p. 3]
- missed: adam_beta2 = 0.95 [p. 3]
- missed: lr_schedule = cosine [p. 3] (final lr 10% of maximum)
- missed: weight_decay = 0.1 [p. 3]
- missed: grad_clip = 1.0 [p. 3]
- missed: warmup_steps = 2000 [p. 3]
- missed: activation = SwiGLU [p. 3]
- missed: normalization = RMSNorm [p. 3]
- missed: position_encoding = rotary [p. 3]
- missed: tokenizer = BPE [p. 2]
- missed: num_samples = 256 [p. 6] (MATH maj1@k)
- not in gold: learning rate = 3.0e^−^4 _[verified]_
- not in gold: tokens = 1.0T _[verified]_
- not in gold: learning rate = 1.5e^−^4 _[verified]_

### compute
- missed: 2048 A100 GPUs (80GB) [p. 4]
- missed: 21 days [p. 4] (65B on 1.4T tokens)
- not in gold: A100-80GB GPU power consumption for LLaMA-7B _[verified]_
- not in gold: A100-80GB GPU power consumption for LLaMA-13B _[verified]_
- not in gold: A100-80GB GPU power consumption for LLaMA-33B _[verified]_
- not in gold: A100-80GB GPU power consumption for LLaMA-65B _[verified]_

### code_urls
- not in gold: https://github.com/facebookresearch/xformers _[verified]_
- not in gold: https://github.com/facebookresearch/metaseq/tree/main/projects/OPT/chronicles _[verified]_

## 2303.15343

### task
- missed: zero-shot image classification [p. 4]
- missed: image-text retrieval [p. 4]

### datasets
- missed: ObjectNet [p. 7]
- missed: ImageNet-v2 [p. 7]
- missed: ImageNet ReaL [p. 7]
- missed: MSCOCO [p. 7] (retrieval)
- not in gold: C4 _[verified]_

### baselines
- missed: LiT [p. 1]
- missed: FLIP [p. 2]
- missed: ALIGN [p. 2]
- not in gold: CLIP baseline pre-trained on WebLI with standard softmax loss _[verified]_

### metrics
- not in gold: Zero-shot retrieval results across 36 languages _[verified]_

### hyperparameters
- missed: adam_beta1 = 0.9 [p. 14]
- missed: adam_beta2 = 0.95 [p. 14]
- missed: warmup_examples = 200M [p. 14] (SigLiT)
- missed: lr_schedule = cosine [p. 14]
- missed: vocab_size = 32000 [p. 14]
- missed: max_seq_length = 16 [p. 14]
- missed: vocab_size = 250000 [p. 5] (multilingual)
- missed: image_size = 288 [p. 14] (SigLiT precomputed embeddings)
- missed: image_size = 224 [p. 5] (SigLIP)
- missed: train_steps = 65000 [p. 6] (LION)
- missed: batch_size = 1M [p. 1] (largest SigLiT batch)
- missed: temperature_init = log 10 [p. 3]
- missed: bias_init = -10 [p. 3]
- missed: backbone = ViT-B/16 [p. 5] (SigLIP)
- missed: backbone = ViT-g [p. 4] (SigLiT frozen image tower)
- missed: backbone = So-400m [p. 7]
- missed: train_examples = 40B [p. 7] (Table 3 models)
- missed: train_examples = 2.4B [p. 7] (unlocked fine-tuning; added in adjudication)
- not in gold: epochs/steps = 65 000 steps _[verified]_
- not in gold: epochs/steps = 2.4 B examples _[verified]_
- not in gold: learning rate = 100x smaller _[verified]_
- not in gold: optimizer = β 2 = 0.95 _[verified]_
- not in gold: optimizer = ScalingViT-Adafactor with β 1 = 0.9 and β 2 = 0.95 _[verified]_
- not in gold: batch size = 16384 _[verified]_

### compute
- missed: 32 TPUv4 chips [p. 2]
- not in gold: 32 TPU-v4 chips for two days for from-scratch SigLIP _[verified]_
- not in gold: Comparison training cost of approximately 2500 TPUv3-days reported in [30] _[verified]_
- not in gold: Google Cloud TPUs used for training models developed in big vision codebase _[verified]_

## 2304.02643

### task
- missed: zero-shot single point valid mask evaluation [p. 8]
- missed: edge detection [p. 10]
- missed: object proposal generation [p. 10]
- missed: instance segmentation [p. 10]
- missed: text-to-mask [p. 11]

### datasets
- missed: MIAP [p. 8] (fairness)
- missed: Cityscapes [p. 9] (23-dataset suite)
- missed: DOORS [p. 9] (23-dataset suite)
- missed: DRAM [p. 9] (23-dataset suite)
- missed: EgoHOS [p. 9] (23-dataset suite)
- missed: GTEA [p. 9] (23-dataset suite)
- missed: Hypersim [p. 9] (23-dataset suite)
- missed: IBD [p. 9] (23-dataset suite)
- missed: iShape [p. 9] (23-dataset suite)
- missed: NDISPark [p. 9] (23-dataset suite)
- missed: OVIS [p. 9] (23-dataset suite)
- missed: PPDLS [p. 9] (23-dataset suite)
- missed: Plittersdorf [p. 9] (23-dataset suite)
- missed: STREETS [p. 9] (23-dataset suite)
- missed: TimberSeg [p. 9] (23-dataset suite)
- missed: TrashCan [p. 9] (23-dataset suite)
- missed: VISOR [p. 9] (23-dataset suite)
- missed: WoodScape [p. 9] (23-dataset suite)
- missed: PIDRay [p. 9] (23-dataset suite)
- missed: ZeroWaste-f [p. 9] (23-dataset suite)
- not in gold: Open Images V5 _[verified]_

### baselines
- missed: RITM [p. 8]
- missed: SimpleClick [p. 9]
- missed: FocalClick [p. 9]
- missed: HED [p. 10] (edge detection)
- missed: Canny [p. 10] (edge detection)
- missed: Felz-Hutt [p. 10] (edge detection)
- missed: ViTDet-H [p. 10] (proposals and instance segmentation)
- not in gold: RITM interactive segmentation model _[verified]_
- not in gold: SimpleClick interactive segmentation model _[verified]_
- not in gold: FocalClick interactive segmentation model _[verified]_
- not in gold: ViTDet-H detector acting as proposal generator _[verified]_
- not in gold: HED deep learning edge detection method _[verified]_

### metrics
- missed: mask quality rating [p. 9] (1 to 10)
- missed: ODS [p. 10] (edge detection)
- missed: OIS [p. 10] (edge detection)
- missed: mask AR@1000 [p. 10] (object proposals)
- not in gold: Human evaluation score from 1 to 10 _[verified]_
- not in gold: Average recall (AR) metric _[verified]_

### hyperparameters
- missed: backbone = ViT-H [p. 8] (image encoder)
- missed: image_size = 1024 [p. 16]
- missed: hidden_size = 256 [p. 17] (mask decoder)
- missed: num_layers = 2 [p. 17] (mask decoder)
- missed: num_heads = 8 [p. 17] (mask decoder)
- missed: loss_ratio = 20:1 [p. 17]
- missed: num_iterations_per_mask = 11 [p. 17] (interactive training)
- missed: optimizer = AdamW [p. 17]
- missed: adam_beta1 = 0.9 [p. 17]
- missed: adam_beta2 = 0.999 [p. 17]
- missed: lr_schedule = step-wise decay [p. 17] (÷10 at 60k and 86666)
- missed: learning_rate = 8e-4 [p. 17] (ViT-H and ViT-B)
- missed: epochs = 2 [p. 17]
- missed: masks_per_gpu = 64 [p. 18]
- missed: learning_rate = 4e-4 [p. 18] (ViT-L)
- missed: layer_decay = 0.6 [p. 18] (ViT-B)
- not in gold: optimizer = AdamW (β 1 = 0.9, β 2 = 0.999) _[verified]_
- not in gold: learning rate = 8e -4 _[verified]_
- not in gold: model size = ViT-H _[verified]_
- not in gold: learning rate = 8e -4 /4e -4 _[verified]_

### compute
- missed: 68 hours [p. 28]
- not in gold: Training with up to 64 randomly sampled masks per GPU _[verified]_

### code_urls
- missed: https://segment-anything.com [p. 1] (project page; model and dataset release)
- not in gold: https://github.com/serengil/retinaface _[verified]_
- not in gold: https://github.com/facebookresearch/segment-anything _[verified]_

## 2304.07193

### task
- missed: self-supervised visual representation learning [p. 1]
- missed: monocular depth estimation [p. 16]
- missed: instance retrieval [p. 14]
- missed: video classification [p. 13]

### datasets
- missed: ImageNet-A [p. 32] (Table 18)
- missed: ImageNet-C [p. 32] (Table 18)
- missed: ImageNet-R [p. 32] (Table 18)
- missed: ImageNet-Sketch [p. 32] (Table 18)
- missed: Food-101 [p. 32] (Table 18)
- missed: CIFAR-10 [p. 32] (Table 18)
- missed: CIFAR-100 [p. 32] (Table 18)
- missed: SUN397 [p. 32] (Table 18)
- missed: StanfordCars [p. 32] (Table 18)
- missed: FGVC-Aircraft [p. 32] (Table 18)
- missed: VOC 2007 [p. 32] (Table 18)
- missed: DTD [p. 32] (Table 18)
- missed: Oxford Pets [p. 32] (Table 18)
- missed: Caltech101 [p. 32] (Table 18)
- missed: Flowers [p. 32] (Table 18)
- missed: CUB200 [p. 32] (Table 18)
- missed: SSv2 [p. 32] (Table 18)
- missed: GLD v2 [p. 32] (Table 18)
- missed: R-Paris [p. 32] (Table 18)
- missed: R-Oxford [p. 32] (Table 18)
- missed: Met [p. 32] (Table 18)
- missed: Amstertime [p. 32] (Table 18)
- missed: Cityscapes [p. 32] (Table 18)
- missed: VOC 2012 [p. 32] (Table 18)
- missed: Mapillary SLS [p. 32] (Table 18)
- missed: NYU-Depth V2 [p. 32] (Table 18)
- missed: SUN-RGBD [p. 32] (Table 18)
- missed: DollarStreet [p. 32] (Table 18)
- missed: Casual Conversations [p. 32] (Table 18)
- not in gold: Google Landmarks _[verified]_
- not in gold: uncurated web data _[verified]_
- not in gold: uncurated dataset _[verified]_
- not in gold: Oxford-M _[unsupported]_
- not in gold: Something-Something v2 _[verified]_
- not in gold: NYUd _[unsupported]_

### baselines
- missed: EVA-CLIP [p. 11]

### metrics
- missed: k-NN accuracy [p. 8]
- missed: mAP [p. 9] (retrieval)

### hyperparameters
- missed: precision = float16 [p. 31]
- missed: drop_path = 0 [p. 31] (distilled models)
- missed: drop_path = 0.4 [p. 31] (from scratch)
- missed: learning_rate = 3.5e-4 [p. 31] (from scratch)
- missed: batch_size = 3072 [p. 31] (from scratch)
- missed: hidden_size = 384 [p. 31] (ViT-S/14)
- missed: hidden_size = 768 [p. 31] (ViT-B/14)
- missed: hidden_size = 1024 [p. 31] (ViT-L/14)
- missed: hidden_size = 1536 [p. 31] (ViT-g/14)
- missed: num_heads = 6 [p. 31] (ViT-S/14)
- missed: num_heads = 12 [p. 31] (ViT-B/14)
- missed: num_heads = 16 [p. 31] (ViT-L/14)
- missed: num_heads = 24 [p. 31] (ViT-g/14)
- missed: num_layers = 12 [p. 31] (ViT-S/14)
- missed: num_layers = 18 [p. 31] (ViT-B/14)
- missed: num_layers = 24 [p. 31] (ViT-L/14)
- missed: num_layers = 40 [p. 31] (ViT-g/14)
- missed: activation = SwiGLU [p. 31] (from scratch)
- missed: patch_size = 14 [p. 8]
- missed: num_prototypes = 128k [p. 8]
- missed: koleo_weight = 0.1 [p. 29]
- missed: sinkhorn_iterations = 3 [p. 6]
- missed: image_size = 224 [p. 6] (global crops)
- missed: image_size = 98 [p. 6] (local crops)
- missed: image_size = 518 [p. 6] (high-resolution adaptation)
- missed: train_steps = 10000 [p. 31] (high-resolution adaptation)
- missed: model_size = 1B [p. 1] (ViT-g)
- missed: train_steps = 12500 [p. 31] (linear probing)
- not in gold: drop rate = 40% _[verified]_
- not in gold: KoLeo regularizer weight = 0.1 _[verified]_

### compute
- missed: A100 GPUs [p. 6]
- missed: 22,016 GPU-hours [p. 20] (DINOv2-g)
- missed: 20 nodes with 8 V100-32GB GPUs [p. 5] (data curation)
- not in gold: Compute cluster for LVD-142M dataset creation _[verified]_
- not in gold: Hardware used for model training _[verified]_
- not in gold: Segmentation training compute time and hardware _[verified]_
- not in gold: GPU-hours and carbon emission for ViT-g pre-training _[verified]_

### code_urls
- not in gold: https://github.com/facebookresearch/xformers _[verified]_

## 2304.08485

### task
- missed: science question answering [p. 5]

### datasets
- missed: LLaVA-Bench (COCO) [p. 7] (30 images 90 questions)
- missed: LLaVA-Bench (In-the-Wild) [p. 7] (24 images 60 questions)

### baselines
- missed: GPT-4 [p. 6]
- missed: GPT-3.5 w/ CoT [p. 8]
- missed: Human [p. 9] (ScienceQA)

### hyperparameters
- missed: weight_decay = 0 [p. 20]
- missed: lr_schedule = cosine [p. 20]
- missed: precision = BF16 [p. 20]
- missed: model_size = 13B [p. 9] (LLM; 7B in ablation)
- missed: model_size = 7B [p. 9] (ablation)
- missed: patch_size = 14 [p. 4] (CLIP vision encoder)
- not in gold: weight decay = no weight decay _[verified]_

### compute
- missed: 8 A100 GPUs [p. 5]
- missed: 4 hours pre-training / 10 hours fine-tuning [p. 20] (ScienceQA fine-tuning 4 hours)
- not in gold: Hardware used for training models _[verified]_
- not in gold: Pre-training completion time _[verified]_
- not in gold: Instruct-158K finetuning completion time _[verified]_
- not in gold: ScienceQA finetuning completion time _[verified]_

### code_urls
- missed: https://llava-vl.github.io [p. 1] (project page with code)

## 2305.14314

### task
- missed: instruction finetuning [p. 1]
- missed: natural language understanding [p. 6]
- missed: language modeling with quantized models [p. 6] (4-bit data types)

### datasets
- missed: Winogrande [p. 6] (zero-shot)
- missed: HellaSwag [p. 6] (zero-shot)
- missed: PiQA [p. 6] (zero-shot)
- missed: Arc-Easy [p. 6] (zero-shot)
- missed: Arc-Challenge [p. 6] (zero-shot)
- not in gold: OPT _[verified]_
- not in gold: LLaMA _[verified]_
- not in gold: BLOOM _[verified]_
- not in gold: Pythia _[verified]_

### baselines
- missed: 16-bit full finetuning [p. 6]
- missed: 16-bit LoRA [p. 6]
- missed: QLoRA Int8 and FP4 [p. 7] (data type comparison)
- missed: Bard [p. 8]
- missed: Vicuna [p. 8]
- missed: Open Assistant [p. 8]
- missed: LLaMA no tuning [p. 8]
- not in gold: Vicuna chatbot system _[verified]_
- not in gold: Open Assistant chatbot system _[verified]_
- not in gold: Bard commercial chatbot system _[verified]_

### metrics
- missed: memory footprint [p. 10]

### hyperparameters
- missed: quantization = NF4 [p. 23] (with double quantization)
- missed: compute_dtype = bf16 [p. 23]
- missed: lora_alpha = 64 [p. 22] (Super-NaturalInstructions)
- missed: lr_schedule = constant [p. 23]
- missed: batch_size = 16 [p. 23] (7B and 13B; OASST1)
- missed: batch_size = 32 [p. 23] (33B)
- missed: batch_size = 64 [p. 23] (65B)
- missed: learning_rate = 2e-4 [p. 23] (7B and 13B)
- missed: learning_rate = 1e-4 [p. 23] (33B and 65B)
- missed: train_steps = 10000 [p. 23] (7B/13B)
- missed: train_steps = 1875 [p. 23] (OASST1)
- missed: train_steps = 4000 [p. 23] (Longform 7B/13B)
- missed: train_steps = 5000 [p. 23] (33B)
- missed: train_steps = 2343 [p. 23] (Longform 33B/65B)
- missed: train_steps = 2500 [p. 23] (65B)
- missed: max_source_length = 384 [p. 23]
- missed: max_source_length = 512 [p. 23] (Longform)
- missed: max_target_length = 128 [p. 23]
- missed: max_target_length = 512 [p. 23] (OASST1)
- missed: max_target_length = 768 [p. 23] (HH-RLHF)
- missed: max_target_length = 1024 [p. 23] (Longform)
- missed: elo_initial = 1000 [p. 9] (Elo start score)
- missed: model_size = 7B [p. 8] (LLaMA)
- missed: model_size = 13B [p. 8] (LLaMA)
- missed: model_size = 33B [p. 8] (LLaMA)
- missed: model_size = 65B [p. 8] (LLaMA)
- not in gold: LoRA layers = {key+query, all attention layers, all FFN layers, all layers, attention + FFN output layers} _[verified]_

### compute
- missed: single 48GB GPU [p. 1] (65B finetuning)

### code_urls
- missed: https://github.com/artidoro/qlora [p. 1]
- missed: https://github.com/TimDettmers/bitsandbytes [p. 1]

## 2305.18290

### task
- missed: controlled sentiment generation [p. 7]
- missed: learning from human preferences [p. 1]
- not in gold: Sentiment modulation in language models _[verified]_

### baselines
- missed: PPO-GT [p. 8] (oracle reward)
- not in gold: DPO _[unsupported]_

### metrics
- missed: agreement [p. 10]
- not in gold: TL;DR summarization win rates vs human-written summaries using GPT-4 as evaluator _[verified]_

### hyperparameters
- missed: dpo_beta = 0.1 [p. 20] (default)
- missed: dpo_beta = 0.5 [p. 20] (TL;DR summarization)
- missed: dpo_beta = 0.05 [p. 8] (sentiment sweep)
- missed: dpo_beta = 1 [p. 8] (sentiment sweep)
- missed: dpo_beta = 5 [p. 8] (sentiment sweep)
- missed: batch_size = 64 [p. 20]
- missed: optimizer = RMSprop [p. 20]
- missed: learning_rate = 1e-6 [p. 20]
- missed: warmup_steps = 150 [p. 20]
- missed: epochs = 1 [p. 20] (IMDb SFT)
- missed: epochs = 3 [p. 20] (IMDb reward model)
- missed: ppo_batch_size = 1024 [p. 20] (IMDb)
- missed: num_samples = 128 [p. 9] (dialogue Best of N)
- missed: temperature = 0.25 [p. 9] (DPO human evaluation)
- missed: base_model = GPT-2-large [p. 7] (sentiment)
- missed: base_model = GPT-J [p. 9] (summarization SFT)
- missed: base_model = Pythia-2.8B [p. 9] (dialogue)
- not in gold: β = {0.05, 0.1, 1, 5} _[verified]_

### code_urls
- not in gold: https://huggingface.co/CarperAI/openai_summarize_tldr_sft _[verified]_
- not in gold: https://huggingface.co/reciprocate/ppo_hh_pythia-6B _[verified]_
- not in gold: https://github.com/CarperAI/trlx/tree/main/examples/hh _[verified]_

## 2309.16588

### task
- missed: image classification [p. 6]
- missed: semantic segmentation [p. 6] (ADE20k linear probing)
- missed: monocular depth estimation [p. 6] (NYUd)
- missed: unsupervised object discovery [p. 7] (LOST)
- missed: zero-shot classification [p. 6] (OpenCLIP)
- not in gold: learning visual representations with Vision Transformers _[verified]_

### datasets
- missed: ImageNet-1k [p. 7] (evaluation)
- missed: Shutterstock image-text corpus [p. 6] (OpenCLIP training)
- missed: Places205 [p. 5] (linear probing of tokens)
- missed: CIFAR-10 [p. 5]
- missed: CIFAR-100 [p. 5]
- missed: CUB [p. 5]
- missed: Caltech101 [p. 5]
- missed: Stanford Cars [p. 5]
- missed: DTD [p. 5]
- missed: Flowers [p. 5]
- missed: Food-101 [p. 5]
- missed: Oxford Pets [p. 5]
- missed: SUN397 [p. 5]
- missed: PASCAL VOC [p. 5] (classification probing)

### baselines
- missed: DeiT-III [p. 6] (without registers)
- missed: OpenCLIP [p. 6] (without registers)
- missed: DINOv2 [p. 6] (without registers)
- missed: DINO [p. 8] (LOST reference)

### metrics
- missed: CorLoc [p. 8] (object discovery)

### hyperparameters
- missed: num_registers = 4 [p. 7] (used in all experiments)
- missed: num_registers = 1 [p. 7] (ablation)
- missed: num_registers = 2 [p. 7] (ablation)
- missed: num_registers = 8 [p. 7] (ablation)
- missed: num_registers = 16 [p. 7] (ablation)
- missed: norm_threshold = 150 [p. 3] (outlier definition)
- missed: patch_size = 14 [p. 7] (DINOv2)
- missed: patch_size = 16 [p. 6] (OpenCLIP)

### code_urls
- not in gold: https://github.com/facebookresearch/deit _[verified]_
- not in gold: https://github.com/mlfoundations/open_clip _[verified]_

## 2310.06625

### baselines
- missed: RLinear [p. 6]
- missed: Transformer [p. 6] (inverted framework)
- missed: Reformer [p. 6] (inverted framework)
- missed: Informer [p. 6] (inverted framework)
- missed: Flowformer [p. 6] (inverted framework)
- missed: Flashformer [p. 6] (inverted framework)

### hyperparameters
- missed: lookback_window = 96 [p. 6]
- missed: prediction_length = 96 [p. 6]
- missed: prediction_length = 192 [p. 6]
- missed: prediction_length = 336 [p. 6]
- missed: prediction_length = 720 [p. 6]
- missed: prediction_length = 12 [p. 6] (PEMS)
- missed: prediction_length = 24 [p. 6] (PEMS)
- missed: prediction_length = 36 [p. 6] (PEMS)
- missed: prediction_length = 48 [p. 6] (PEMS)
- missed: loss = L2 loss [p. 14]
- missed: num_layers = 2 [p. 14]
- missed: num_layers = 3 [p. 14]
- missed: num_layers = 4 [p. 14]
- not in gold: number of Transformer blocks = {2, 3, 4} _[verified]_

## 2312.00752

### task
- missed: sequence modeling [p. 1]
- missed: DNA modeling [p. 12]
- missed: audio modeling and generation [p. 14]
- missed: selective copying [p. 5] (synthetic)
- missed: induction heads [p. 5] (synthetic)
- not in gold: audio modeling _[verified]_
- not in gold: genomics modeling _[verified]_

### datasets
- missed: LAMBADA [p. 12]
- missed: HellaSwag [p. 12]
- missed: PIQA [p. 12]
- missed: ARC-easy [p. 12]
- missed: ARC-challenge [p. 12]
- missed: WinoGrande [p. 12]
- missed: Great Apes DNA classification [p. 13]
- missed: SC09 [p. 14]

### baselines
- missed: Transformer++ [p. 11]
- missed: H3 [p. 4]
- missed: Hyena [p. 4]
- missed: RetNet [p. 4]
- missed: RWKV [p. 4]
- missed: S4 [p. 10] (synthetics)
- missed: Pythia [p. 12]
- missed: GPT-Neo [p. 12]
- missed: OPT [p. 12]
- missed: SaShiMi [p. 14]
- missed: SampleRNN [p. 15]
- missed: WaveNet [p. 15]
- missed: WaveGAN [p. 15]
- missed: DiffWave [p. 15]
- missed: multi-head attention [p. 10] (induction heads)
- not in gold: Transformer++ architecture _[verified]_
- not in gold: Pythia open source models _[verified]_
- not in gold: RWKV open source models _[verified]_
- not in gold: SaShiMi architecture for audio waveform modeling _[verified]_

### metrics
- missed: throughput [p. 15]

### hyperparameters
- missed: expansion_factor = 2 [p. 7]
- missed: state_dim = 16 [p. 15]
- missed: num_layers = 2 [p. 29] (synthetic tasks)
- missed: hidden_size = 64 [p. 29] (selective copying)
- missed: vocab_size = 16 [p. 29] (synthetic tasks)
- missed: max_seq_length = 4096 [p. 29] (selective copying)
- missed: train_steps = 400K [p. 29] (selective copying)
- missed: learning_rate = 0.0001 [p. 29] (selective copying; Great Apes fine-tuning)
- missed: batch_size = 8 [p. 29] (induction heads)
- missed: optimizer = AdamW [p. 29] (language modeling)
- missed: learning_rate = 2e-4 [p. 29] (induction heads; 1.3B scaling)
- missed: num_layers = 12 [p. 30] (125M)
- missed: num_layers = 24 [p. 30] (350M / 760M / 1.3B)
- missed: hidden_size = 768 [p. 30] (125M)
- missed: hidden_size = 1024 [p. 30] (350M)
- missed: hidden_size = 1536 [p. 30] (760M)
- missed: hidden_size = 2048 [p. 30] (1.3B)
- missed: train_steps = 4800 [p. 30] (125M)
- missed: train_steps = 13500 [p. 30] (350M)
- missed: train_steps = 29000 [p. 30] (760M)
- missed: train_steps = 50000 [p. 30] (1.3B)
- missed: learning_rate = 6e-4 [p. 30] (125M)
- missed: learning_rate = 3e-4 [p. 30] (350M)
- missed: learning_rate = 2.5e-4 [p. 30] (760M)
- missed: batch_size = 0.5M tokens [p. 30] (scaling laws)
- missed: batch_size = 1M tokens [p. 31] (1.3B downstream)
- missed: grad_clip = 1.0 [p. 30]
- missed: weight_decay = 0.1 [p. 30]
- missed: dropout = 0 [p. 30]
- missed: lr_schedule = linear warmup with cosine decay [p. 30]
- missed: adam_beta1 = 0.9 [p. 30]
- missed: adam_beta2 = 0.95 [p. 30] (improved recipe)
- missed: train_tokens = 300B [p. 12] (downstream models)
- missed: tokenizer = GPT-NeoX [p. 31] (downstream; GPT2 tokenizer for scaling laws)
- missed: train_steps = 20K [p. 13] (DNA sequence length scaling)
- missed: num_layers = 6 [p. 13] (DNA sequence length scaling)
- missed: hidden_size = 128 [p. 13] (DNA sequence length scaling)
- missed: epochs = 10 [p. 33] (Great Apes fine-tuning)
- missed: learning_rate = 4e-3 [p. 33] (DNA sweep; added in adjudication)
- missed: batch_size = 16M tokens [p. 33] (DNA sequence-length scaling; added in adjudication)
- missed: learning_rate = 4e-5 [p. 33] (Hyena species fine-tuning; added in adjudication)
- not in gold: learning rate = {1 -3, 2 -3, 4 -3, 8 -3} _[verified]_
- not in gold: batch size = 2 24 _[verified]_
- not in gold: learning rate = 4e -5 _[verified]_
- not in gold: learning rate = 1e -4 _[verified]_

### compute
- missed: A100 GPUs [p. 2]
- not in gold: Machine with 8 GPUs _[verified]_

## 2402.03300

### task
- missed: tool-integrated mathematical reasoning [p. 9]
- missed: formal theorem proving [p. 9]
- missed: language understanding and code generation [p. 9]

### datasets
- missed: GSM8K [p. 8]
- missed: MATH [p. 8]
- missed: OCW Courses [p. 6]
- missed: SAT [p. 6]
- missed: MMLU-STEM [p. 6]
- missed: CMATH [p. 8]
- missed: Gaokao-MathCloze [p. 6]
- missed: Gaokao-MathQA [p. 6]
- missed: MGSM-zh [p. 12]
- missed: miniF2F [p. 9]
- missed: MMLU [p. 9]
- missed: BIG-Bench Hard [p. 9]
- missed: HumanEval [p. 9]
- missed: MBPP [p. 9]
- missed: MathInstruct [p. 10] (SFT data)
- missed: Lila-OOD [p. 10] (SFT data)

### baselines
- missed: DeepSeek-Coder-Base-v1.5 [p. 9]
- missed: GPT-4 [p. 12]
- missed: GPT-4 Code Interpreter [p. 12]
- missed: GPT-3.5 [p. 12]
- missed: Gemini Ultra [p. 12]
- missed: Gemini Pro [p. 12]
- missed: Inflection-2 [p. 12]
- missed: Grok-1 [p. 12]
- missed: Baichuan-3 [p. 12]
- missed: GLM-4 [p. 12]
- missed: Math-Shepherd-Mistral 7B [p. 12]
- missed: DeepSeek-LLM-Chat 67B [p. 12]
- missed: SeaLLM-v2 7B [p. 12]
- missed: ChatGLM3 6B [p. 12]
- missed: ToRA 34B [p. 12]
- missed: MAmmoTH 70B [p. 12]
- missed: PPO [p. 11]

### metrics
- missed: accuracy [p. 12]
- missed: majority voting accuracy [p. 12]
- missed: Pass@K [p. 19] (RL analysis)

### hyperparameters
- missed: adam_beta1 = 0.9 [p. 6]
- missed: adam_beta2 = 0.95 [p. 6]
- missed: lr_schedule = multi-step [p. 6]
- missed: model_size = 7B [p. 8] (DeepSeekMath)
- missed: replay_ratio = 10% [p. 15] (iterative reward model)
- missed: epochs = 3 [p. 5] (fastText classifier)
- missed: vocab_size = 100K [p. 6] (tokenizer)

### code_urls
- missed: https://github.com/deepseek-ai/DeepSeek-Math [p. 1]
- not in gold: https://github.com/InternLM/InternLM-Math _[verified]_
- not in gold: https://github.com/openai/prm800k/issues/12 _[verified]_

## 2404.19756

### task
- missed: function fitting [p. 1]
- missed: PDE solving [p. 3] (Poisson equation)
- missed: symbolic regression [p. 13]
- missed: continual learning [p. 18]
- missed: knot invariant classification [p. 22]
- missed: Anderson localization mobility edges [p. 26] (physics application)
- not in gold: Small-scale AI and Science tasks including function fitting. _[verified]_

### datasets
- missed: Poisson equation [p. 18] (PDE example)
- missed: Mosaic model [p. 26] (mobility edges)
- missed: generalized Aubry-André model [p. 26] (mobility edges)
- missed: modified Aubry-André model [p. 26] (mobility edges)

### baselines
- missed: MLP [p. 1]
- missed: PINN [p. 18]
- missed: human-constructed KAN [p. 17] (Feynman)
- not in gold: MLPs with different depths and widths _[verified]_
- not in gold: MLPs with fixed width 5 or 100 and depths swept in {2, 3, 4, 5, 6} _[verified]_

### metrics
- missed: L2 squared loss [p. 18] (PDE)
- missed: H1 squared loss [p. 18] (PDE)
- not in gold: Error in the L2 norm and energy (H1) norm _[verified]_
- not in gold: MSE _[verified]_
- not in gold: Cross-entropy loss _[verified]_

### hyperparameters
- missed: spline_order = 3 [p. 7]
- missed: grid_size = 3 [p. 10] (initial grid)
- missed: grid_size = 1000 [p. 10] (final grid in grid-extension demo)
- missed: grid_update_interval = 200 [p. 10]
- missed: num_train_samples = 1000 [p. 10]
- missed: architecture = [2, 5, 1] [p. 9]
- missed: architecture = [2, 1, 1] [p. 9]
- missed: architecture = [17, 1, 14] [p. 23] (knot dataset)
- missed: architecture = [3, 1, 14] [p. 23] (knot dataset three variables)
- missed: regularization_lambda = 1e-2 [p. 15] (sparsification)
- missed: regularization_lambda = 1e-3 [p. 15] (sparsification)
- missed: mu = 1 [p. 11]
- missed: beta = 3 [p. 12]
- missed: mlp_depth = {2,3,4,5,6} [p. 15] (MLP baselines)
- missed: activation = {Tanh, ReLU, SiLU} [p. 17] (MLP baselines)
- missed: prune_threshold = 1e-2 [p. 12]
- not in gold: grid points = {3, 5, 10, 20, 50, 100, 200, 500, 1000} _[verified]_
- not in gold: sparsification lambda = 10 -2 or 10 -3 _[verified]_
