# PaperLens extraction (app.eval.collect)

## 1409.0473

# NEURAL MACHINE TRANSLATION BY JOINTLY LEARNING TO ALIGN AND TRANSLATE

Dzmitry Bahdanau, Kyunghyun Cho, Yoshua Bengio
2016 · arXiv:1409.0473v7[cs.CL]

## Problem

- Using a fixed-length vector in encoder-decoder neural machine translation models creates a performance bottleneck, especially for long sentences. _[verified]_
  > p. 1: “In this paper, we conjecture that the use of a fixed-length vector is a bottleneck in improving the performance of this basic encoder-decoder architecture, and propose to extend this by allowing a model to automatically (soft-)search for parts of a source sentence that are relevant to predicting a target word, without having to form these parts as a hard segment explicitly.”

## Task

- Neural machine translation _[verified]_
  > p. 1: “Neural machine translation is a recently proposed approach to machine translation.”
- English-to-French translation _[verified]_
  > p. 2: “On the task of English-to-French translation, the proposed approach achieves, with a single model, a translation performance comparable, or close, to the conventional phrase-based system.”

## Contributions

- Extend the encoder-decoder model by allowing it to automatically search for relevant parts of the source sentence when predicting a target word. _[verified]_
  > p. 1: “In this paper, we conjecture that the use of a fixed-length vector is a bottleneck in improving the performance of this basic encoder-decoder architecture, and propose to extend this by allowing a model to automatically (soft-)search for parts of a source sentence that are relevant to predicting a target word, without having to form these parts as a hard segment explicitly.”
- Encode the input sentence into a sequence of vectors and choose a subset of these vectors adaptively during decoding. _[verified]_
  > p. 2: “Instead, it encodes the input sentence into a sequence of vectors and chooses a subset of these vectors adaptively while decoding the translation.”

## Method

- The proposed architecture consists of a bidirectional RNN encoder and a decoder that computes a distinct context vector for each target word by emulating searching through the source sentence. _[partial]_
  > p. 3: “The new architecture consists of a bidirectional RNN as an encoder (Sec. 3.2) and a decoder that emulates searching through a source sentence during decoding a translation (Sec. 3.1).”
- An alignment model parameterized as a feedforward neural network computes soft alignments to score how well input positions and output positions match, allowing the model to be trained jointly. _[verified]_
  > p. 3: “We parametrize the alignment model a as a feedforward neural network which is jointly trained with all the other components of the proposed system.”
- The encoder utilizes a bidirectional RNN composed of forward and backward RNNs to generate annotations that summarize both preceding and following words for each input word. _[partial]_
  > p. 4: “Hence, we propose to use a bidirectional RNN (BiRNN, Schuster and Paliwal, 1997), which has been successfully used recently in speech recognition (see, e.g., Graves et al., 2013).”
- Training is performed using the stochastic gradient descent algorithm together with Adadelta to automatically adapt the learning rate for each parameter. _[partial]_
  > p. 14: “We used the stochastic gradient descent (SGD) algorithm.”

## Novelty

- Unlike existing encoder-decoder approaches that use a single fixed-length vector, the proposed model conditions each target word probability on a distinct context vector derived from an attention mechanism. _[verified]_
  > p. 3: “It should be noted that unlike the existing encoder-decoder approach (see Eq. ( 2)), here the probability is conditioned on a distinct context vector c i for each target word y i .”
- The alignment is computed as a soft alignment directly by a neural network rather than treated as a latent variable, enabling backpropagation of the cost function gradient for joint training. _[verified]_
  > p. 4: “Instead, the alignment model directly computes a soft alignment, which allows the gradient of the cost function to be backpropagated through.”

## Datasets

- ACL WMT '14 (850M words) _[partial]_
  > p. 4: “We use the bilingual, parallel corpora provided by ACL WMT '14.”

## Baselines

- RNN Encoder-Decoder proposed by Cho et al. (2014a) _[verified]_
  > p. 4: “As a comparison, we also report the performance of an RNN Encoder-Decoder which was proposed recently by Cho et al. (2014a).”
- Conventional phrase-based translation system (Moses) _[verified]_
  > p. 5: “More importantly, the performance of the RNNsearch is as high as that of the conventional phrase-based translation system (Moses), when only the sentences consisting of known words are considered.”

## Metrics

- BLEU score _[verified]_
  > p. 5: “In Table 1, we list the translation performances measured in BLEU score.”

## Hyperparameters

- hidden units: 1000 _[verified]_
  > p. 5: “The encoder and decoder of the RNNencdec have 1000 hidden units each.”
- optimizer: minibatch stochastic gradient descent (SGD) algorithm together with Adadelta _[verified]_
  > p. 5: “We use a minibatch stochastic gradient descent (SGD) algorithm together with Adadelta (Zeiler, 2012) to train each model.”
- batch size: 80 _[verified]_
  > p. 5: “Each SGD update direction is computed using a minibatch of 80 sentences.”
- epsilon: 10 -6 _[verified]_
  > p. 14: “Adadelta (Zeiler, 2012) was used to automatically adapt the learning rate of each parameter ( = 10 -6 and ρ = 0.95).”
- rho: 0.95 _[verified]_
  > p. 14: “Adadelta (Zeiler, 2012) was used to automatically adapt the learning rate of each parameter ( = 10 -6 and ρ = 0.95).”

## Compute

- Training time of approximately 5 days per model _[verified]_
  > p. 5: “We trained each model for approximately 5 days.”

## Ablations

- Training models with sentences of length up to 30 words versus length up to 50 words _[verified]_
  > p. 5: “We train each model twice: first with the sentences of length up to 30 words (RNNencdec-30, RNNsearch-30) and then with the sentences of length up to 50 word (RNNencdec-50, RNNsearch-50).”

## Claims

- The new approach achieves translation performance comparable to existing state-of-the-art phrase-based systems on English-to-French translation. _[verified]_
  > p. 1: “With this new approach, we achieve a translation performance comparable to the existing state-of-the-art phrase-based system on the task of English-to-French translation.”
- Qualitative analysis shows that the soft-alignments found by the model agree well with intuition. _[verified]_
  > p. 1: “Furthermore, qualitative analysis reveals that the (soft-)alignments found by the model agree well with our intuition.”
- The proposed approach of jointly learning to align and translate achieves significantly improved translation performance over the basic encoder-decoder approach. _[verified]_
  > p. 2: “In this paper, we show that the proposed approach of jointly learning to align and translate achieves significantly improved translation performance over the basic encoder-decoder approach.”

## Future work

- Improving handling of rare and unknown words _[verified]_
  > p. 9: “One of challenges left for the future is to better handle unknown, or rare words.”

## Code

- https://github.com/lisa-groundhog/GroundHog _[verified]_
  > p. 4: “Implementations are available at https://github.com/lisa-groundhog/GroundHog.”


## 1409.1556

# VERY DEEP CONVOLUTIONAL NETWORKS FOR LARGE-SCALE IMAGE RECOGNITION

Karen Simonyan, Andrew Zisserman
2015 · arXiv:1409.1556v6[cs.CV]

## Problem

- Investigating the effect of convolutional network depth on accuracy in large-scale image recognition. _[verified]_
  > p. 1: “In this work we investigate the effect of the convolutional network depth on its accuracy in the large-scale image recognition setting.”

## Task

- Large-scale image recognition and classification. _[verified]_
  > p. 1: “In this work we investigate the effect of the convolutional network depth on its accuracy in the large-scale image recognition setting.”

## Contributions

- Evaluation of networks of increasing depth using very small convolution filters. _[verified]_
  > p. 1: “Our main contribution is a thorough evaluation of networks of increasing depth using an architecture with very small (3 × 3) convolution filters, which shows that a significant improvement on the prior-art configurations can be achieved by pushing the depth to 16-19 weight layers.”
- Making two best-performing ConvNet models publicly available. _[verified]_
  > p. 1: “We have made our two best-performing ConvNet models publicly available to facilitate further research on the use of deep visual representations in computer vision.”

## Method

- The network architecture consists of a stack of convolutional layers using small 3x3 receptive fields and spatial max-pooling, followed by three fully-connected layers and a final soft-max layer. _[partial]_
  > p. 2: “The image is passed through a stack of convolutional (conv.) layers, where we use filters with a very small receptive field: 3 × 3 (which is the smallest size to capture the notion of left/right, up/down, center).”
- All hidden layers are equipped with ReLU non-linearity, and training is regularized with weight decay and dropout on the first two fully-connected layers. _[verified]_
  > p. 4: “The training was regularised by weight decay (the L 2 penalty multiplier set to 5 • 10 -4 ) and dropout regularisation for the first two fully-connected layers (dropout ratio set to 0.5).”
- Training is performed via mini-batch gradient descent with momentum by optimizing the multinomial logistic regression objective. _[verified]_
  > p. 4: “Namely, the training is carried out by optimising the multinomial logistic regression objective using mini-batch gradient descent (based on back-propagation (LeCun et al., 1989)) with momentum.”
- Data augmentation during training includes random image cropping, horizontal flipping, and RGB colour shifts, alongside scaling approaches such as single-scale and multi-scale training. _[partial]_
  > p. 4: “To further augment the training set, the crops underwent random horizontal flipping and random RGB colour shift (Krizhevsky et al., 2012).”
- At test time, fully-connected layers are converted to convolutional layers to perform dense evaluation over whole images combined with image flipping for score averaging. _[partial]_
  > p. 5: “Namely, the fully-connected layers are first converted to convolutional layers (the first FC layer to a 7 × 7 conv. layer, the last two FC layers to 1 × 1 conv. layers).”

## Datasets

- ILSVRC (validation / test) _[verified]_
  > p. 6: “For the majority of experiments, we used the validation set as the test set.”

## Baselines

- GoogLeNet _[verified]_
  > p. 8: “Our result is also competitive with respect to the classification task winner (GoogLeNet with 6.7% error) and substantially outperforms the ILSVRC-2013 winning submission Clarifai, which achieved 11.2% with outside training data and 11.7% without it.”
- Clarifai _[verified]_
  > p. 8: “Our result is also competitive with respect to the classification task winner (GoogLeNet with 6.7% error) and substantially outperforms the ILSVRC-2013 winning submission Clarifai, which achieved 11.2% with outside training data and 11.7% without it.”
- MSRA _[verified]_
  > p. 8: “MSRA (He et al., 2014) (11 nets)”
- Zeiler & Fergus _[verified]_
  > p. 8: “Zeiler & Fergus (Zeiler & Fergus, 2013) (6 nets)”
- OverFeat _[verified]_
  > p. 8: “OverFeat (Sermanet et al., 2014) (7 nets)”
- Krizhevsky et al. _[verified]_
  > p. 8: “Krizhevsky et al. (Krizhevsky et al., 2012) (5 nets)”

## Metrics

- top-1 validation error _[verified]_
  > p. 7: “Our best single-network performance on the validation set is 24.8%/7.5% top-1/top-5 error (highlighted in bold in Table 4).”
- top-5 validation error _[verified]_
  > p. 7: “Our best single-network performance on the validation set is 24.8%/7.5% top-1/top-5 error (highlighted in bold in Table 4).”
- top-5 test error _[verified]_
  > p. 7: “On the test set, the configuration E achieves 7.3% top-5 error.”

## Hyperparameters

- momentum: 0.9 _[verified]_
  > p. 4: “The batch size was set to 256, momentum to 0.9.”
- batch size: 256 _[verified]_
  > p. 4: “The batch size was set to 256, momentum to 0.9.”
- weight decay: 5 • 10 -4 _[verified]_
  > p. 4: “The training was regularised by weight decay (the L 2 penalty multiplier set to 5 • 10 -4 ) and dropout regularisation for the first two fully-connected layers (dropout ratio set to 0.5).”
- dropout ratio: 0.5 _[verified]_
  > p. 4: “The training was regularised by weight decay (the L 2 penalty multiplier set to 5 • 10 -4 ) and dropout regularisation for the first two fully-connected layers (dropout ratio set to 0.5).”
- learning rate: 10 -2 _[verified]_
  > p. 4: “The learning rate was initially set to 10 -2 , and then decreased by a factor of 10 when the validation set accuracy stopped improving.”
- epochs: 74 _[verified]_
  > p. 4: “In total, the learning rate was decreased 3 times, and the learning was stopped after 370K iterations (74 epochs).”
- iterations: 370K _[verified]_
  > p. 4: “In total, the learning rate was decreased 3 times, and the learning was stopped after 370K iterations (74 epochs).”
- learning rate: 10 -3 _[verified]_
  > p. 4: “To speed-up training of the S = 384 network, it was initialised with the weights pre-trained with S = 256, and we used a smaller initial learning rate of 10 -3 .”

## Compute

- four NVIDIA Titan Black GPUs _[verified]_
  > p. 5: “On a system equipped with four NVIDIA Titan Black GPUs, training a single net took 2-3 weeks depending on the architecture.”
- training time of 2-3 weeks _[verified]_
  > p. 5: “On a system equipped with four NVIDIA Titan Black GPUs, training a single net took 2-3 weeks depending on the architecture.”

## Ablations

- ConvNet depth varying from 11 to 19 layers _[verified]_
  > p. 6: “Second, we observe that the classification error decreases with the increased ConvNet depth: from 11 layers in A to 19 layers in E.”
- Comparison of configuration C with 1x1 conv layers and configuration D with 3x3 conv layers _[verified]_
  > p. 6: “Notably, in spite of the same depth, the configuration C (which contains three 1 × 1 conv. layers), performs worse than the configuration D, which uses 3 × 3 conv. layers throughout the network.”

## Claims

- Secured first and second places in localisation and classification tracks of ImageNet Challenge 2014. _[verified]_
  > p. 1: “These findings were the basis of our ImageNet Challenge 2014 submission, where our team secured the first and the second places in the localisation and classification tracks respectively.”


## 1512.03385

# Deep Residual Learning for Image Recognition

Kaiming He, Xiangyu Zhang, Shaoqing Ren, Jian Sun
2015 · arXiv:1512.03385v1[cs.CV]

## Problem

- Deeper neural networks are difficult to train due to vanishing or exploding gradients and a degradation problem where accuracy saturates and then degrades rapidly. _[partial]_
  > p. 1: “Deeper neural networks are more difficult to train.”

## Task

- image classification _[verified]_
  > p. 1: “This result won the 1st place on the ILSVRC 2015 classification task.”
- visual recognition tasks _[verified]_
  > p. 1: “The depth of representations is of central importance for many visual recognition tasks.”

## Contributions

- We present a residual learning framework to ease the training of networks that are substantially deeper than those used previously. _[verified]_
  > p. 1: “We present a residual learning framework to ease the training of networks that are substantially deeper than those used previously.”

## Method

- Instead of expecting stacked layers to approximate an underlying mapping H(x), the network is formulated to explicitly approximate a residual function F(x) := H(x) - x, with the original function represented as F(x) + x. _[partial]_
  > p. 3: “So rather than expect stacked layers to approximate H(x), we explicitly let these layers approximate a residual function F(x) := H(x)x.”
- The building block of the residual network is defined by y = F(x, {Wi}) + x, where x and y are input and output vectors, and F represents the residual mapping learned by stacked layers connected via shortcut connections and element-wise addition. _[verified]_
  > p. 3: “Formally, in this paper we consider a building block defined as: y = F(x, {W i }) + x.”
- Plain network baselines use 3x3 filters inspired by VGG nets, maintaining equal filter counts for the same feature map sizes and doubling filters when spatial size is halved, ending with global average pooling and a fully-connected softmax layer. _[verified]_
  > p. 3: “Our plain baselines (Fig. 3, middle) are mainly inspired by the philosophy of VGG nets [41] (Fig. 3, left).”
- Residual networks are created by inserting shortcut connections into the plain networks, utilizing either identity mappings with zero padding or projection shortcuts via 1x1 convolutions to handle dimension changes. _[verified]_
  > p. 4: “Based on the above plain network, we insert shortcut connections (Fig. 3, right) which turn the network into its counterpart residual version.”
- Training is performed from scratch using SGD with mini-batches of 256, batch normalization after convolutions and before activation, weight decay, momentum, and a decaying learning rate schedule. _[partial]_
  > p. 4: “We initialize the weights as in [13] and train all plain/residual nets from scratch.”

## Datasets

- ImageNet 2012 classification dataset (training, validation, test, 1.28 million training images, 50k validation images, 100k test images) _[verified]_
  > p. 4: “We evaluate our method on the ImageNet 2012 classification dataset [36] that consists of 1000 classes.”
- PASCAL VOC 2007 (trainval, test, 5k trainval images in VOC 2007 and 16k trainval images in VOC 2012 for training) _[verified]_
  > p. 8: “Table 7 and8 show the object detection baseline results on PASCAL VOC 2007 and 2012 [5] and COCO [26].”
- PASCAL VOC 2012 (trainval, test, 10k trainval+test images in VOC 2007 and 16k trainval images in VOC 2012 for training) _[verified]_
  > p. 8: “Table 7 and8 show the object detection baseline results on PASCAL VOC 2007 and 2012 [5] and COCO [26].”
- COCO (train, val, test-dev, 80k images on the train set and 40k images on the val set) _[verified]_
  > p. 8: “Table 7 and8 show the object detection baseline results on PASCAL VOC 2007 and 2012 [5] and COCO [26].”
- CIFAR-10 (test) _[unsupported]_
  > p. 6: “Deeper non-bottleneck ResNets (e.g., Fig.”

## Baselines

- VGG-16 _[verified]_
  > p. 8: “Here we are interested in the improvements of replacing VGG-16 [41] with ResNet-101.”
- GoogLeNet _[verified]_
  > p. 6: “GoogLeNet [44] (ILSVRC’14)”
- PReLU-net _[verified]_
  > p. 6: “PReLU-net [13]”
- BN-inception _[verified]_
  > p. 6: “BN-inception [16]”
- Highway networks _[verified]_
  > p. 7: “Highway [42, 43]”
- FitNet _[verified]_
  > p. 7: “FitNet [35]”
- Maxout _[verified]_
  > p. 7: “Maxout [10]”
- NIN _[verified]_
  > p. 7: “NIN [25]”
- DSN _[verified]_
  > p. 7: “DSN [24]”

## Metrics

- top-1 and top-5 error rates _[verified]_
  > p. 4: “We evaluate both top-1 and top-5 error rates.”
- mAP@[.5, .95] and mAP@.5 _[verified]_
  > p. 10: “We evaluate the PASCAL VOC metric (mAP @ IoU = 0.5) and the standard COCO metric (mAP @ IoU = .5:.05:.95).”

## Hyperparameters

- optimizer: SGD _[verified]_
  > p. 4: “We use SGD with a mini-batch size of 256.”
- batch_size: 256 _[verified]_
  > p. 4: “We use SGD with a mini-batch size of 256.”
- learning rate: 0.1 _[verified]_
  > p. 4: “The learning rate starts from 0.1 and is divided by 10 when the error plateaus, and the models are trained for up to 60 × 10 4 iterations.”
- iterations: 60 × 10 4 _[verified]_
  > p. 4: “The learning rate starts from 0.1 and is divided by 10 when the error plateaus, and the models are trained for up to 60 × 10 4 iterations.”
- weight decay: 0.0001 _[verified]_
  > p. 4: “We use a weight decay of 0.0001 and a momentum of 0.9.”
- momentum: 0.9 _[verified]_
  > p. 4: “We use a weight decay of 0.0001 and a momentum of 0.9.”
- dropout: none _[verified]_
  > p. 4: “We do not use dropout [14], following the practice in [16].”
- batch_size (detection): 8 (RPN), 16 (Fast R-CNN) _[verified]_
  > p. 10: “We train the COCO models with an 8-GPU implementation, and thus the RPN step has a mini-batch size of 8 images (i.e., 1 per GPU) and the Fast R-CNN step has a mini-batch size of 16 images.”
- learning rate (detection): 0.001, 0.0001 _[verified]_
  > p. 10: “The RPN step and Fast R-CNN step are both trained for 240k iterations with a learning rate of 0.001 and then for 80k iterations with 0.0001.”
- iterations (detection): 240k, 80k _[verified]_
  > p. 10: “The RPN step and Fast R-CNN step are both trained for 240k iterations with a learning rate of 0.001 and then for 80k iterations with 0.0001.”

## Compute

- 8-GPU implementation _[verified]_
  > p. 10: “We train the COCO models with an 8-GPU implementation, and thus the RPN step has a mini-batch size of 8 images (i.e., 1 per GPU) and the Fast R-CNN step has a mini-batch size of 16 images.”

## Seeds and runs

- ResNet-110 run 5 times on CIFAR-10 _[verified]_
  > p. 7: “For ResNet-110, we run it 5 times and show "best (mean±std)" as in[43].”

## Ablations

- Identity vs. Projection Shortcuts comparison _[verified]_
  > p. 6: “In Table 3 we compare three options: (A) zero-padding shortcuts are used for increasing dimensions, and all shortcuts are parameterfree (the same as Table 2 and Fig. 4 right); (B) projection shortcuts are used for increasing dimensions, and other shortcuts are identity; and (C) all shortcuts are projections.”

## Claims

- An ensemble of these residual nets achieves 3.57% error on the ImageNet test set. _[verified]_
  > p. 1: “An ensemble of these residual nets achieves 3.57% error on the ImageNet test set.”
- Solely due to extremely deep representations, a 28% relative improvement on the COCO object detection dataset is obtained. _[verified]_
  > p. 1: “Solely due to our extremely deep representations, we obtain a 28% relative improvement on the COCO object detection dataset.”
- Residual networks are easier to optimize and can gain accuracy from considerably increased depth. _[verified]_
  > p. 1: “We provide comprehensive empirical evidence showing that these residual networks are easier to optimize, and can gain accuracy from considerably increased depth.”

## Future work

- Combining deep architectures with stronger regularization to potentially improve results _[verified]_
  > p. 8: “But combining with stronger regularization may improve results, which we will study in the future.”


## 1706.03762

# Attention Is All You Need

Ashish Vaswani, Noam Shazeer, Google Brain, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N Gomez, Łukasz Kaiser
2023 · arXiv:1706.03762v7[cs.CL]

## Problem

- Recurrent neural models have an inherently sequential nature that precludes parallelization within training examples. _[verified]_
  > p. 2: “This inherently sequential nature precludes parallelization within training examples, which becomes critical at longer sequence lengths, as memory constraints limit batching across examples.”

## Task

- Machine translation _[verified]_
  > p. 1: “Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train.”

## Contributions

- Proposing the Transformer, a new simple network architecture based solely on attention mechanisms. _[verified]_
  > p. 1: “We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.”

## Method

- The model follows an encoder-decoder structure using stacked self-attention and point-wise fully connected layers. _[verified]_
  > p. 3: “The Transformer follows this overall architecture using stacked self-attention and point-wise, fully connected layers for both the encoder and decoder, shown in the left and right halves of Figure 1, respectively.”
- The encoder consists of 6 identical layers with a multi-head self-attention mechanism and a position-wise fully connected feed-forward network, using residual connections and layer normalization. _[partial]_
  > p. 3: “Each layer has two sub-layers.”
- The decoder contains 6 identical layers with an additional multi-head attention sub-layer over the encoder output, alongside masked self-attention and feed-forward networks. _[verified]_
  > p. 3: “In addition to the two sub-layers in each encoder layer, the decoder inserts a third sub-layer, which performs multi-head attention over the output of the encoder stack.”
- Scaled dot-product attention computes query, key, and value dot products scaled by the square root of the key dimension and a softmax function. _[verified]_
  > p. 4: “Attention(Q, K, V ) = softmax( QK T √ d k )V(1)”
- Multi-head attention linearly projects queries, keys, and values multiple times in parallel to perform attention functions simultaneously. _[verified]_
  > p. 4: “Instead of performing a single attention function with d model -dimensional keys, values and queries, we found it beneficial to linearly project the queries, keys and values h times with different, learned linear projections to d k , d k and d v dimensions, respectively.”
- Positional encodings using sine and cosine functions of different frequencies are added to the input embeddings to inject sequence order information. _[partial]_
  > p. 6: “To this end, we add "positional encodings" to the input embeddings at the bottoms of the encoder and decoder stacks.”

## Novelty

- The Transformer is the first transduction model relying entirely on self-attention to compute representations without sequence-aligned RNNs or convolutions. _[verified]_
  > p. 2: “To the best of our knowledge, however, the Transformer is the first transduction model relying entirely on self-attention to compute representations of its input and output without using sequence-aligned RNNs or convolution.”

## Datasets

- WMT 2014 English-to-German _[verified]_
  > p. 8: “On the WMT 2014 English-to-German translation task, the big transformer model (Transformer (big) in Table 2) outperforms the best previously reported models (including ensembles) by more than 2.0 BLEU, establishing a new state-of-the-art BLEU score of 28.4.”
- newstest2014 _[verified]_
  > p. 8: “Table 2: The Transformer achieves better BLEU scores than previous state-of-the-art models on the English-to-German and English-to-French newstest2014 tests at a fraction of the training cost.”
- Section 22 development set _[verified]_
  > p. 9: “We performed only a small number of experiments to select the dropout, both attention and residual (section 5.4), learning rates and beam size on the Section 22 development set, all other parameters remained unchanged from the English-to-German base translation model.”
- newstest2013 _[verified]_
  > p. 9: “All metrics are on the English-to-German translation development set, newstest2013.”
- Section 23 of WSJ (Section 23) _[verified]_
  > p. 10: “Table 4: The Transformer generalizes well to English constituency parsing (Results are on Section 23 of WSJ)”

## Baselines

- ByteNet _[verified]_
  > p. 8: “ByteNet [18] | 23.75 |  |  |”
- Deep-Att + PosUnk _[verified]_
  > p. 8: “Deep-Att + PosUnk [39] |  | 39.2 |  | 1.0 · 10^20”
- GNMT + RL _[verified]_
  > p. 8: “GNMT + RL [38] | 24.6 | 39.92 | 2.3 · 10^19 | 1.4 · 10^20”
- ConvS2S _[verified]_
  > p. 8: “ConvS2S [9] | 25.16 | 40.46 | 9.6 · 10^18 | 1.5 · 10^20”
- MoE _[verified]_
  > p. 8: “MoE [32] | 26.03 | 40.56 | 2.0 · 10^19 | 1.2 · 10^20”
- Deep-Att + PosUnk Ensemble _[verified]_
  > p. 8: “Deep-Att + PosUnk Ensemble [39] |  | 40.4 |  | 8.0 · 10^20”
- GNMT + RL Ensemble _[verified]_
  > p. 8: “GNMT + RL Ensemble [38] | 26.30 | 41.16 | 1.8 · 10^20 | 1.1 · 10^21”
- ConvS2S Ensemble _[verified]_
  > p. 8: “ConvS2S Ensemble [9] | 26.36 | 41.29 | 7.7 · 10^19 | 1.2 · 10^21”
- Vinyals & Kaiser el al. (2014) _[verified]_
  > p. 10: “Vinyals & Kaiser el al. (2014) [37] | WSJ only, discriminative | 88.3”
- Petrov et al. (2006) _[verified]_
  > p. 10: “Petrov et al. (2006) [29] | WSJ only, discriminative | 90.4”
- Zhu et al. (2013) _[verified]_
  > p. 10: “Zhu et al. (2013) [40] | WSJ only, discriminative | 90.4”
- Dyer et al. (2016) _[verified]_
  > p. 10: “Dyer et al. (2016) [8] | WSJ only, discriminative | 91.7”
- Huang & Harper (2009) _[verified]_
  > p. 10: “Huang & Harper (2009) [14] | semi-supervised | 91.3”
- McClosky et al. (2006) _[verified]_
  > p. 10: “McClosky et al. (2006) [26] | semi-supervised | 92.1”
- Luong et al. (2015) _[verified]_
  > p. 10: “Luong et al. (2015) [23] | multi-task | 93.0”

## Metrics

- BLEU score _[verified]_
  > p. 8: “On the WMT 2014 English-to-German translation task, the big transformer model (Transformer (big) in Table 2) outperforms the best previously reported models (including ensembles) by more than 2.0 BLEU, establishing a new state-of-the-art BLEU score of 28.4.”
- Perplexity (PPL) _[verified]_
  > p. 9: “Listed perplexities are per-wordpiece, according to our byte-pair encoding, and should not be compared to per-word perplexities.”
- F1 score _[verified]_
  > p. 10: “Parser | Training | WSJ 23 F1”

## Hyperparameters

- beta 1: 0.9 _[verified]_
  > p. 7: “We used the Adam optimizer [20] with β 1 = 0.9, β 2 = 0.98 and ϵ = 10 -9 .”
- beta 2: 0.98 _[verified]_
  > p. 7: “We used the Adam optimizer [20] with β 1 = 0.9, β 2 = 0.98 and ϵ = 10 -9 .”
- epsilon: 10 -9 _[verified]_
  > p. 7: “We used the Adam optimizer [20] with β 1 = 0.9, β 2 = 0.98 and ϵ = 10 -9 .”
- warmup_steps: 4000 _[verified]_
  > p. 7: “We used warmup_steps = 4000.”
- training steps (base model): 100,000 _[verified]_
  > p. 7: “We trained the base models for a total of 100,000 steps or 12 hours.”
- training steps (big model): 300,000 _[verified]_
  > p. 7: “The big models were trained for 300,000 steps (3.5 days).”
- maximum output length (inference): input length + 300 _[verified]_
  > p. 9: “During inference, we increased the maximum output length to input length + 300.”
- beam size: 21 _[verified]_
  > p. 10: “We used a beam size of 21 and α = 0.3 for both WSJ only and the semi-supervised setting.”
- alpha: 0.3 _[verified]_
  > p. 10: “We used a beam size of 21 and α = 0.3 for both WSJ only and the semi-supervised setting.”

## Compute

- Training hardware consisting of one machine with 8 NVIDIA P100 GPUs _[verified]_
  > p. 7: “We trained our models on one machine with 8 NVIDIA P100 GPUs.”
- Base models training time of 12 hours _[verified]_
  > p. 7: “We trained the base models for a total of 100,000 steps or 12 hours.”
- Big models training time of 3.5 days _[verified]_
  > p. 7: “The big models were trained for 300,000 steps (3.5 days).”

## Ablations

- Variations on the Transformer architecture including number of layers, representation dimensions, feed-forward dimensions, attention heads, key/value dimensions, dropout, label smoothing, and positional embeddings _[verified]_
  > p. 9: “Table 3: Variations on the Transformer architecture.Unlisted values are identical to those of the base model.All metrics are on the English-to-German translation development set, newstest2013.Listed perplexities are per-wordpiece, according to our byte-pair encoding, and should not be compared to per-word perplexities.”

## Claims

- The model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task, improving over existing best results by over 2 BLEU. _[verified]_
  > p. 1: “Our model achieves 28.4 BLEU on the WMT 2014 Englishto-German translation task, improving over the existing best results, including ensembles, by over 2 BLEU.”
- On WMT 2014 English-to-French, the model establishes a new single-model state-of-the-art BLEU score of 41.8. _[verified]_
  > p. 1: “On the WMT 2014 English-to-French translation task, our model establishes a new single-model state-of-the-art BLEU score of 41.8 after training for 3.5 days on eight GPUs, a small fraction of the training costs of the best models from the literature.”
- The Transformer generalizes well to other tasks such as English constituency parsing. _[verified]_
  > p. 1: “We show that the Transformer generalizes well to other tasks by applying it successfully to English constituency parsing both with large and limited training data.”

## Future work

- Extend the Transformer to problems with input and output modalities other than text _[verified]_
  > p. 10: “We plan to extend the Transformer to problems involving input and output modalities other than text and to investigate local, restricted attention mechanisms to efficiently handle large inputs and outputs such as images, audio and video.”
- Investigate local, restricted attention mechanisms to handle large inputs and outputs _[verified]_
  > p. 10: “We plan to extend the Transformer to problems involving input and output modalities other than text and to investigate local, restricted attention mechanisms to efficiently handle large inputs and outputs such as images, audio and video.”
- Make generation less sequential _[verified]_
  > p. 10: “Making generation less sequential is another research goals of ours.”

## Code

- https://github.com/tensorflow/tensor2tensor _[verified]_
  > p. 10: “The code we used to train and evaluate our models is available at https://github.com/ tensorflow/tensor2tensor.”


## 1810.04805

# BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding

Jacob Devlin, Ming-Wei Chang, Kenton Lee, Kristina Toutanova
2019 · arXiv:1810.04805v2[cs.CL]

## Problem

- Current language representation models are unidirectional, which restricts the power of pre-trained representations and the choice of architectures. _[partial]_
  > p. 1: “The major limitation is that standard language models are unidirectional, and this limits the choice of architectures that can be used during pre-training.”

## Task

- question answering _[verified]_
  > p. 1: “As a result, the pre-trained BERT model can be finetuned with just one additional output layer to create state-of-the-art models for a wide range of tasks, such as question answering and language inference, without substantial taskspecific architecture modifications.”
- language inference _[verified]_
  > p. 1: “As a result, the pre-trained BERT model can be finetuned with just one additional output layer to create state-of-the-art models for a wide range of tasks, such as question answering and language inference, without substantial taskspecific architecture modifications.”
- natural language inference _[verified]_
  > p. 1: “These include sentence-level tasks such as natural language inference (Bowman et al., 2015;Williams et al., 2018) and paraphrasing (Dolan and Brockett, 2005), which aim to predict the relationships between sentences by analyzing them holistically, as well as token-level tasks such as named entity recognition and question answering, where models are required to produce fine-grained output at the token level (Tjong Kim Sang and De Meulder, 2003;Rajpurkar et al., 2016).”
- paraphrasing _[verified]_
  > p. 1: “These include sentence-level tasks such as natural language inference (Bowman et al., 2015;Williams et al., 2018) and paraphrasing (Dolan and Brockett, 2005), which aim to predict the relationships between sentences by analyzing them holistically, as well as token-level tasks such as named entity recognition and question answering, where models are required to produce fine-grained output at the token level (Tjong Kim Sang and De Meulder, 2003;Rajpurkar et al., 2016).”
- named entity recognition _[verified]_
  > p. 1: “These include sentence-level tasks such as natural language inference (Bowman et al., 2015;Williams et al., 2018) and paraphrasing (Dolan and Brockett, 2005), which aim to predict the relationships between sentences by analyzing them holistically, as well as token-level tasks such as named entity recognition and question answering, where models are required to produce fine-grained output at the token level (Tjong Kim Sang and De Meulder, 2003;Rajpurkar et al., 2016).”

## Contributions

- Demonstrating the importance of bidirectional pre-training for language representations. _[verified]_
  > p. 2: “• We demonstrate the importance of bidirectional pre-training for language representations.”
- Showing that pre-trained representations reduce the need for heavily-engineered task-specific architectures. _[verified]_
  > p. 2: “• We show that pre-trained representations reduce the need for many heavily-engineered taskspecific architectures.”
- Advancing the state of the art for eleven natural language processing tasks. _[verified]_
  > p. 2: “• BERT advances the state of the art for eleven NLP tasks.”

## Method

- The framework consists of two main steps: pre-training on unlabeled data and fine-tuning using labeled data for downstream tasks. _[partial]_
  > p. 3: “There are two steps in our framework: pre-training and fine-tuning.”
- The model architecture is a multi-layer bidirectional Transformer encoder based on the original Transformer implementation. _[partial]_
  > p. 3: “BERT's model architecture is a multi-layer bidirectional Transformer encoder based on the original implementation described in Vaswani et al. (2017) and released in the tensor2tensor library.”
- BERT is pre-trained using two unsupervised tasks: Masked LM (MLM) and Next Sentence Prediction (NSP). _[verified]_
  > p. 4: “Instead, we pre-train BERT using two unsupervised tasks, described in this section.”
- During fine-tuning, the pre-trained parameters are used to initialize the model, and all parameters are fine-tuned end-to-end on downstream tasks. _[verified]_
  > p. 5: “For each task, we simply plug in the task-specific inputs and outputs into BERT and finetune all the parameters end-to-end.”

## Novelty

- Unlike previous models that use traditional left-to-right or right-to-left language models, BERT uses a deep bidirectional architecture trained with masked language modeling. _[partial]_
  > p. 4: “Unlike Peters et al. (2018a) and Radford et al. (2018), we do not use traditional left-to-right or right-to-left language models to pre-train BERT.”
- Unlike prior work that transfers only sentence embeddings, BERT transfers all pre-trained parameters to initialize end-task models. _[verified]_
  > p. 5: “However, in prior work, only sentence embeddings are transferred to down-stream tasks, where BERT transfers all parameters to initialize end-task model parameters.”

## Datasets

- GLUE _[verified]_
  > p. 5: “Detailed descriptions of GLUE datasets are included in Appendix B.1.”
- SQuAD v1.1 (100k) _[verified]_
  > p. 6: “The Stanford Question Answering Dataset (SQuAD v1.1) is a collection of 100k crowdsourced question/answer pairs (Rajpurkar et al., 2016).”
- TriviaQA _[verified]_
  > p. 6: “We therefore use modest data augmentation in our system by first fine-tuning on TriviaQA (Joshi et al., 2017) befor fine-tuning on SQuAD.”
- SQuAD 2.0 _[verified]_
  > p. 7: “The SQuAD 2.0 task extends the SQuAD 1.1 problem definition by allowing for the possibility that no short answer exists in the provided paragraph, making the problem more realistic.”
- SWAG (113k) _[verified]_
  > p. 7: “The Situations With Adversarial Generations (SWAG) dataset contains 113k sentence-pair completion examples that evaluate grounded commonsense inference (Zellers et al., 2018).”
- CoNLL-2003 Named Entity Recognition _[verified]_
  > p. 9: “In this section, we compare the two approaches by applying BERT to the CoNLL-2003 Named Entity Recognition (NER) task (Tjong Kim Sang and De Meulder, 2003).”

## Baselines

- OpenAI GPT on GLUE _[verified]_
  > p. 6: “On the official GLUE leaderboard 10 , BERT LARGE obtains a score of 80.5, compared to OpenAI GPT, which obtains 72.8 as of the date of writing.”
- ESIM+ELMo system on SWAG _[verified]_
  > p. 7: “BERT LARGE outperforms the authors' baseline ESIM+ELMo system by +27.1% and OpenAI GPT by 8.3%.”
- OpenAI GPT on SWAG _[verified]_
  > p. 7: “BERT LARGE outperforms the authors' baseline ESIM+ELMo system by +27.1% and OpenAI GPT by 8.3%.”

## Metrics

- F1 score for QQP and MRPC _[verified]_
  > p. 6: “F1 scores are reported for QQP and MRPC, Spearman correlations are reported for STS-B, and accuracy scores are reported for the other tasks.”
- Spearman correlation for STS-B _[verified]_
  > p. 6: “F1 scores are reported for QQP and MRPC, Spearman correlations are reported for STS-B, and accuracy scores are reported for the other tasks.”
- Accuracy scores for other tasks _[verified]_
  > p. 6: “F1 scores are reported for QQP and MRPC, Spearman correlations are reported for STS-B, and accuracy scores are reported for the other tasks.”
- Exact Match (EM) and F1 for SQuAD _[unlocated]_
  > p. 7: “System | Dev | Test | EM | F1”
- Accuracy for SWAG _[verified]_
  > p. 7: “Table 4: SWAG Dev and Test accuracies.”
- F1 score for CoNLL-2003 NER _[partial]_
  > p. 9: “Table 7: CoNLL-2003Named Entity Recognition results.”

## Hyperparameters

- batch size (fine-tuning): 32 _[verified]_
  > p. 6: “We use a batch size of 32 and fine-tune for 3 epochs over the data for all GLUE tasks.”
  > p. 6: “We fine-tune for 3 epochs with a learning rate of 5e-5 and a batch size of 32.”
- epochs (fine-tuning): 3 _[verified]_
  > p. 6: “We use a batch size of 32 and fine-tune for 3 epochs over the data for all GLUE tasks.”
  > p. 6: “We fine-tune for 3 epochs with a learning rate of 5e-5 and a batch size of 32.”
  > p. 7: “We fine-tune the model for 3 epochs with a learning rate of 2e-5 and a batch size of 16.”
- learning rate (fine-tuning): 5e-5, 4e-5, 3e-5, and 2e-5 _[verified]_
  > p. 6: “For each task, we selected the best fine-tuning learning rate (among 5e-5, 4e-5, 3e-5, and 2e-5) on the Dev set.”
- learning rate (fine-tuning): 5e-5 _[partial]_
  > p. 6: “We fine-tune for 3 epochs with a learning rate of 5e-5 and a batch size of 32.”
  > p. 7: “We fine-tuned for 2 epochs with a learning rate of 5e-5 and a batch size of 48.”
- epochs (fine-tuning): 2 _[partial]_
  > p. 7: “We fine-tuned for 2 epochs with a learning rate of 5e-5 and a batch size of 48.”
- batch size (fine-tuning): 48 _[partial]_
  > p. 7: “We fine-tuned for 2 epochs with a learning rate of 5e-5 and a batch size of 48.”
- learning rate (fine-tuning): 2e-5 _[partial]_
  > p. 7: “We fine-tune the model for 3 epochs with a learning rate of 2e-5 and a batch size of 16.”
- epochs (fine-tuning): 16 _[partial]_
  > p. 7: “We fine-tune the model for 3 epochs with a learning rate of 2e-5 and a batch size of 16.”
- feed-forward/filter size: 4H _[verified]_
  > p. 3: “In all cases we set the feed-forward/filter size to be 4H, i.e., 3072 for the H = 768 and 4096 for the H = 1024.”

## Compute

- Replication time of at most 1 hour on a single Cloud TPU or a few hours on a GPU _[verified]_
  > p. 5: “All of the results in the paper can be replicated in at most 1 hour on a single Cloud TPU, or a few hours on a GPU, starting from the exact same pre-trained model.”
- Training time of around 30 minutes on a single Cloud TPU for BERT SQuAD model _[verified]_
  > p. 5: “For example, the BERT SQuAD model can be trained in around 30 minutes on a single Cloud TPU to achieve a Dev F1 score of 91.0%.”

## Seeds and runs

- Random restarts for BERT LARGE on small datasets with GLUE, using different data shuffling and classifier layer initialization _[verified]_
  > p. 6: “Additionally, for BERT LARGE we found that finetuning was sometimes unstable on small datasets, so we ran several random restarts and selected the best model on the Dev set.”
- BERT ensemble consisting of 7x systems using different pre-training checkpoints and fine-tuning seeds _[verified]_
  > p. 7: “The BERT ensemble is 7x systems which use different pre-training checkpoints and fine-tuning seeds.”
- Scores averaged over 5 random restarts for CoNLL-2003 NER _[verified]_
  > p. 9: “The reported Dev and Test scores are averaged over 5 random restarts using those hyperparameters.”

## Ablations

- Ablation study on pretraining objectives evaluating No NSP and LTR _[partial]_
  > p. 8: “We demonstrate the importance of the deep bidirectionality of BERT by evaluating two pretraining objectives using exactly the same pretraining data, fine-tuning scheme, and hyperparameters as BERT BASE”
- Ablation study on model size (layers, hidden units, attention heads) on GLUE tasks _[verified]_
  > p. 8: “In this section, we explore the effect of model size on fine-tuning task accuracy.”
- Ablation comparing fine-tuning approach and feature-based approach on CoNLL-2003 NER _[partial]_
  > p. 9: “In this section, we compare the two approaches by applying BERT to the CoNLL-2003 Named Entity Recognition (NER) task (Tjong Kim Sang and De Meulder, 2003).”
- Ablation study to evaluate the effect of different masking strategies _[verified]_
  > p. 16: “The following is an ablation study to evaluate the effect of different masking strategies.”

## Claims

- BERT obtains new state-of-the-art results on eleven natural language processing tasks. _[verified]_
  > p. 1: “It obtains new state-of-the-art results on eleven natural language processing tasks, including pushing the GLUE score to 80.5% (7.7% point absolute improvement), MultiNLI accuracy to 86.7% (4.6% absolute improvement), SQuAD v1.1 question answering Test F1 to 93.2 (1.5 point absolute improvement) and SQuAD v2.0 Test F1 to 83.1 (5.1 point absolute improvement).”

## Code

- https://github.com/google-research/bert _[verified]_
  > p. 2: “The code and pre-trained models are available at https://github.com/ google-research/bert.”
- https://github.com/tensorflow/tensor2tensor _[verified]_
  > p. 3: “https://github.com/tensorflow/tensor2tensor”


## 1907.11692

# RoBERTa: A Robustly Optimized BERT Pretraining Approach

Yinhan Liu, Myle Ott, Naman Goyal, Jingfei Du, Mandar Joshi, Danqi Chen, Omer Levy, Mike Lewis, Luke Zettlemoyer, Veselin Stoyanov
2019 · arXiv:1907.11692v1[cs.CL]

## Problem

- Comparing different language model pretraining approaches is challenging. _[verified]_
  > p. 1: “Language model pretraining has led to significant performance gains but careful comparison between different approaches is challenging.”
- Training is computationally expensive and often done on private datasets of varying sizes. _[verified]_
  > p. 1: “Training is computationally expensive, often done on private datasets of different sizes, and, as we will show, hyperparameter choices have significant impact on the final results.”

## Task

- language model pretraining _[verified]_
  > p. 1: “Language model pretraining has led to significant performance gains but careful comparison between different approaches is challenging.”

## Contributions

- Presented a replication study of BERT pretraining measuring the impact of hyperparameters and training data size. _[verified]_
  > p. 1: “We present a replication study of BERT pretraining (Devlin et al., 2019) that carefully measures the impact of many key hyperparameters and training data size.”
- Introduced RoBERTa, an improved recipe for training BERT models. _[verified]_
  > p. 1: “We find that BERT was significantly undertrained and propose an improved recipe for training BERT models, which we call RoBERTa, that can match or exceed the performance of all of the post-BERT methods.”
- Collected a large new dataset (CC-NEWS) to better control for training set size effects. _[verified]_
  > p. 1: “We also collect a large new dataset (CC-NEWS) of comparable size to other privately used datasets, to better control for training set size effects.”

## Method

- BERT takes a concatenation of two segments as input separated by special tokens. _[verified]_
  > p. 2: “The two segments are presented as a single input sequence to BERT with special tokens delimiting them:”
- The model utilizes a transformer architecture consisting of L layers, A self-attention heads, and hidden dimension H. _[partial]_
  > p. 2: “We use a transformer architecture with L layers.”
- Pretraining uses two objectives: masked language modeling and next sentence prediction. _[verified]_
  > p. 2: “During pretraining, BERT uses two objectives: masked language modeling and next sentence prediction.”
- Optimization is performed using Adam with specific parameter settings, learning rate warmup, linear decay, and dropout. _[partial]_
  > p. 2: “BERT is optimized with Adam (Kingma and Ba, 2015) using the following parameters: β 1 = 0.9, β 2 = 0.999, ǫ = 1e-6 and L 2 weight decay of 0.01.”

## Datasets

- BOOKCORPUS plus English WIKIPEDIA (16GB) _[partial]_
  > p. 3: “• BOOKCORPUS (Zhu et al., 2015) plus English WIKIPEDIA.”
- CC-NEWS (76GB after filtering) _[partial]_
  > p. 3: “• CC-NEWS, which we collected from the English portion of the CommonCrawl News dataset (Nagel, 2016).”
- OPENWEBTEXT (38GB) _[partial]_
  > p. 3: “• OPENWEBTEXT (Gokaslan and Cohen, 2019), an open-source recreation of the WebText cor-pus described in Radford et al. (2019).”
- STORIES (31GB) _[partial]_
  > p. 3: “• STORIES, a dataset introduced in Trinh and Le (2018) containing a subset of CommonCrawl data filtered to match the story-like style of Winograd schemas.”
- GLUE (training and development data splits, 9 datasets) _[verified]_
  > p. 3: “The General Language Understanding Evaluation (GLUE) benchmark (Wang et al., 2019b) is a collection of 9 datasets for evaluating natural language understanding systems.”
- SQuAD _[verified]_
  > p. 3: “We evaluate on two versions of SQuAD: V1.1 and V2.0 (Rajpurkar et al., 2016(Rajpurkar et al., , 2018)).”
- RACE (more than 28,000 passages and nearly 100,000 questions) _[verified]_
  > p. 4: “The ReAding Comprehension from Examinations (RACE) (Lai et al., 2017) task is a large-scale reading comprehension dataset with more than 28,000 passages and nearly 100,000 questions.”

## Baselines

- Original BERT model and its variants _[partial]_
  > p. 2: “We reimplement BERT in FAIRSEQ (Ott et al., 2019).”
- XLNet architecture _[verified]_
  > p. 6: “For example, the recently proposed XLNet architecture (Yang et al., 2019) is pretrained using nearly 10 times more data than the original BERT (Devlin et al., 2019).”

## Metrics

- F1 score and Exact Match (EM) for SQuAD _[partial]_
  > p. 5: “We report F1 for SQuAD and accuracy for MNLI-m, SST-2 and RACE.”
- Accuracy for classification tasks _[partial]_
  > p. 5: “We report F1 for SQuAD and accuracy for MNLI-m, SST-2 and RACE.”

## Hyperparameters

- sequence length (pretraining): 512 _[verified]_
  > p. 3: “We pretrain with sequences of at most T = 512 tokens.”
- beta 2 (pretraining): 0.98 _[verified]_
  > p. 3: “Similarly, we found setting β 2 = 0.98 to improve stability when training with large batch sizes.”
- model size (pretraining): L = 24, H = 1024, A = 16, 355M parameters _[verified]_
  > p. 6: “We begin by training RoBERTa following the BERT LARGE architecture (L = 24, H = 1024, A = 16, 355M parameters).”
- batch size (fine-tuning): {16, 32} _[verified]_
  > p. 7: “We consider a limited hyperparameter sweep for each task, with batch sizes ∈ {16, 32} and learning rates ∈ {1e-5, 2e-5, 3e-5}, with a linear warmup for the first 6% of steps followed by a linear decay to 0.”
- learning rate (fine-tuning): {1e-5, 2e-5, 3e-5} _[verified]_
  > p. 7: “We consider a limited hyperparameter sweep for each task, with batch sizes ∈ {16, 32} and learning rates ∈ {1e-5, 2e-5, 3e-5}, with a linear warmup for the first 6% of steps followed by a linear decay to 0.”
- warmup (fine-tuning): first 6% of steps _[verified]_
  > p. 7: “We consider a limited hyperparameter sweep for each task, with batch sizes ∈ {16, 32} and learning rates ∈ {1e-5, 2e-5, 3e-5}, with a linear warmup for the first 6% of steps followed by a linear decay to 0.”
- epochs (fine-tuning): 10 _[verified]_
  > p. 7: “We finetune for 10 epochs and perform early stopping based on each task's evaluation metric on the dev set.”
- epochs/steps (pretraining): 100K to 300K, and then further to 500K _[verified]_
  > p. 7: “Finally, we pretrain RoBERTa for significantly longer, increasing the number of pretraining steps from 100K to 300K, and then further to 500K.”

## Compute

- DGX-1 machines with 8 x 32GB Nvidia V100 GPUs using mixed precision _[verified]_
  > p. 3: “We train with mixed precision floating point arithmetic on DGX-1 machines, each with 8 × 32GB Nvidia V100 GPUs interconnected by Infiniband (Micikevicius et al., 2018).”
- 1024 V100 GPUs for approximately one day _[verified]_
  > p. 7: “We pretrain our model using 1024 V100 GPUs for approximately one day.”

## Seeds and runs

- Median over five random initializations (seeds) _[verified]_
  > p. 5: “Reported results are medians over five random initializations (seeds).”

## Ablations

- Ablation of input formats comparing SEGMENT-PAIR and SENTENCE-PAIR _[verified]_
  > p. 5: “We first compare the original SEGMENT-PAIR input format from Devlin et al. (2019) to the SENTENCE-PAIR format; both formats retain the NSP loss, but the latter uses single sentences.”
- Ablation comparing training without NSP loss and using text blocks from a single document _[verified]_
  > p. 5: “We next compare training without the NSP loss and training with blocks of text from a single document (DOC-SENTENCES).”
- Ablation comparing DOC-SENTENCES and FULL-SENTENCES sequence restrictions _[verified]_
  > p. 5: “Finally we find that restricting sequences to come from a single document (DOC-SENTENCES) performs slightly better than packing sequences from multiple documents (FULL-SENTENCES).”
- Ablation varying pretraining data size and pretraining duration steps _[verified]_
  > p. 7: “Table 4: Development set results for RoBERTa as we pretrain over more data (16GB → 160GB of text) and pretrain for longer (100K → 300K → 500K steps).”

## Claims

- The best model achieves state-of-the-art results on GLUE, RACE and SQuAD. _[verified]_
  > p. 1: “Our best model achieves state-of-the-art results on GLUE, RACE and SQuAD.”
- The model achieves a score of 88.5 on the public GLUE leaderboard. _[verified]_
  > p. 1: “When trained for longer over additional data, our model achieves a score of 88.5 on the public GLUE leaderboard, matching the 88.4 reported by Yang et al. (2019).”
- The model establishes a new state-of-the-art on 4/9 of the GLUE tasks. _[verified]_
  > p. 1: “Our model establishes a new state-of-the-art on 4/9 of the GLUE tasks: MNLI, QNLI, RTE and STS-B.”

## Future work

- Further exploration of the limits of large batch training _[verified]_
  > p. 6: “We leave further exploration of the limits of large batch training to future work.”
- A more detailed comparison of BPE encodings _[verified]_
  > p. 6: “A more detailed comparison of these encodings is left to future work.”

## Code

- https://github.com/pytorch/fairseq _[verified]_
  > p. 10: “We additionally use a novel dataset, CC-NEWS, and release our models and code for pretraining and finetuning at: https://github.com/pytorch/fairseq.”


## 1910.01108

# DistilBERT, a distilled version of BERT: smaller, faster, cheaper and lighter

Victor Sanh, Lysandre Debut, Julien Chaumond, Thomas Wolf
2020 · arXiv:1910.01108v4[cs.CL]

## Problem

- Operating large pre-trained language models in constrained computational environments remains challenging. _[verified]_
  > p. 1: “As Transfer Learning from large-scale pre-trained models becomes more prevalent in Natural Language Processing (NLP), operating these large models in on-theedge and/or under constrained computational training or inference budgets remains challenging.”
- The growing computational and memory requirements of expanding models hamper their adoption for on-device, real-time applications. _[verified]_
  > p. 1: “Second, while operating these models on-device in real-time has the potential to enable novel and interesting language processing applications, the growing computational and memory requirements of these models may hamper wide adoption.”

## Task

- Natural Language Processing _[verified]_
  > p. 1: “As Transfer Learning from large-scale pre-trained models becomes more prevalent in Natural Language Processing (NLP), operating these large models in on-theedge and/or under constrained computational training or inference budgets remains challenging.”

## Contributions

- We propose DistilBERT, a method to pre-train a smaller general-purpose language representation model using knowledge distillation. _[partial]_
  > p. 1: “In this work, we propose a method to pre-train a smaller general-purpose language representation model, called DistilBERT, which can then be finetuned with good performances on a wide range of tasks like its larger counterparts.”
- We introduce a triple loss combining language modeling, distillation, and cosine-distance losses during pre-training. _[verified]_
  > p. 1: “To leverage the inductive biases learned by larger models during pre-training, we introduce a triple loss combining language modeling, distillation and cosine-distance losses.”
- We release the trained weights and training code in the Transformers library. _[verified]_
  > p. 2: “We have made the trained weights available along with the training code in the Transformersfoot_1 library from HuggingFace [Wolf et al., 2019].”

## Method

- The student model (DistilBERT) shares the general architecture of BERT but reduces the number of layers by half, while removing token-type embeddings and the pooler. _[partial]_
  > p. 2: “In the present work, the student -DistilBERT -has the same general architecture as BERT.”
- The student is trained using a distillation loss over the soft target probabilities of the teacher, along with a masked language modeling loss and a cosine embedding loss. _[partial]_
  > p. 2: “The final training objective is a linear combination of the distillation loss L ce with the supervised training loss, in our case the masked language modeling loss L mlm [Devlin et al., 2018].”
- The student network is initialized by taking every other layer from the teacher model. _[verified]_
  > p. 2: “Taking advantage of the common dimensionality between teacher and student networks, we initialize the student from the teacher by taking one layer out of two.”

## Datasets

- GLUE (development sets) _[verified]_
  > p. 3: “General Language Understanding We assess the language understanding and generalization capabilities of DistilBERT on the General Language Understanding Evaluation (GLUE) benchmark [Wang et al., 2018], a collection of 9 datasets for evaluating natural language understanding systems.”
- IMDb (test) _[verified]_
  > p. 3: “Downstream tasks We further study the performances of DistilBERT on several downstream tasks under efficient inference constraints: a classification task (IMDb sentiment classification - Maas et al. [2011]) and a question answering task (SQuAD v1.1 -Rajpurkar et al. [2016]).”
- SQuAD v1.1 _[verified]_
  > p. 3: “Downstream tasks We further study the performances of DistilBERT on several downstream tasks under efficient inference constraints: a classification task (IMDb sentiment classification - Maas et al. [2011]) and a question answering task (SQuAD v1.1 -Rajpurkar et al. [2016]).”

## Baselines

- ELMo encoder followed by two BiLSTMs _[verified]_
  > p. 3: “We compare the results to the baseline provided by the authors of GLUE: an ELMo (Peters et al. [2018]) encoder followed by two BiLSTMs.”
- BERT / BERT-base _[partial]_
  > p. 3: “DistilBERT also compares surprisingly well to BERT, retaining 97% of the performance with 40% fewer parameters.”

## Metrics

- accuracy _[verified]_
  > p. 3: “Among the 9 tasks, DistilBERT is always on par or improving over the ELMo baseline (up to 19 points of accuracy on STS-B).”
- F1 score _[verified]_
  > p. 4: “In this case, we were able to reach interesting performances given the size of the model: 79.8 F1 and 70.4 EM, i.e. within 3 points of the full model.”
- Exact Match (EM) _[verified]_
  > p. 4: “In this case, we were able to reach interesting performances given the size of the model: 79.8 F1 and 70.4 EM, i.e. within 3 points of the full model.”
- macro-score (average of individual scores on GLUE) _[verified]_
  > p. 4: “We report the macro-score on GLUE.”

## Hyperparameters

- batch size (inference): 1 _[verified]_
  > p. 4: “To further investigate the speed-up/size trade-off of DistilBERT, we compare (in Table 3) the number of parameters of each model along with the inference time needed to do a full pass on the STS-B development set on CPU (Intel Xeon E5-2690 v3 Haswell @2.9GHz) using a batch size of 1.”

## Compute

- CPU (Intel Xeon E5-2690 v3 Haswell @2.9GHz) _[verified]_
  > p. 4: “To further investigate the speed-up/size trade-off of DistilBERT, we compare (in Table 3) the number of parameters of each model along with the inference time needed to do a full pass on the STS-B development set on CPU (Intel Xeon E5-2690 v3 Haswell @2.9GHz) using a batch size of 1.”
- Smartphone (iPhone 7 Plus) _[verified]_
  > p. 4: “We compare the average inference time on a recent smartphone (iPhone 7 Plus) against our previously trained question answering model based on BERT-base.”

## Seeds and runs

- Medians of 5 runs with different seeds _[verified]_
  > p. 3: “BERT and DistilBERT results are the medians of 5 runs with different seeds.”

## Ablations

- Ablation study varying components of the triple loss and the student initialization _[verified]_
  > p. 4: “In this section, we investigate the influence of various components of the triple loss and the student initialization on the performances of the distilled model.”

## Claims

- DistilBERT reduces model size by 40% while retaining 97% of language understanding capabilities and running 60% faster. _[verified]_
  > p. 1: “While most prior work investigated the use of distillation for building task-specific models, we leverage knowledge distillation during the pre-training phase and show that it is possible to reduce the size of a BERT model by 40%, while retaining 97% of its language understanding capabilities and being 60% faster.”
- Smaller language models pre-trained with knowledge distillation can reach similar performance on many downstream tasks while being lighter and faster. _[verified]_
  > p. 2: “In this paper, we show that it is possible to reach similar performances on many downstream-tasks using much smaller language models pre-trained with knowledge distillation, resulting in models that are lighter and faster at inference time, while also requiring a smaller computational training budget.”

## Code

- https://github.com/huggingface/transformers _[verified]_
  > p. 2: “https://github.com/huggingface/transformers”
- https://github.com/huggingface/swift-coreml-transformers _[verified]_
  > p. 4: “https://github.com/huggingface/swift-coreml-transformers”


## 2002.05709

# A Simple Framework for Contrastive Learning of Visual Representations

Ting Chen, Simon Kornblith, Mohammad Norouzi, Geoffrey Hinton

## Problem

- Learning effective visual representations without human supervision is difficult. _[verified]_
  > p. 1: “Learning effective visual representations without human supervision is a long-standing problem.”
- Pixel-level generation methods are computationally expensive and potentially unnecessary for representation learning. _[verified]_
  > p. 1: “However, pixel-level generation is computationally expensive and may not be necessary for representation learning.”
- Heuristic-based pretext tasks can restrict the generality of learned representations. _[verified]_
  > p. 1: “Many such approaches have relied on heuristics to design pretext tasks (Doersch et al., 2015;Zhang et al., 2016;Noroozi & Favaro, 2016;Gidaris et al., 2018), which could limit the generality of the learned representations.”

## Task

- contrastive learning of visual representations _[verified]_
  > p. 1: “This paper presents SimCLR: a simple framework for contrastive learning of visual representations.”

## Contributions

- The introduction of SimCLR, a simple framework for contrastive learning of visual representations. _[verified]_
  > p. 1: “This paper presents SimCLR: a simple framework for contrastive learning of visual representations.”
- A systematic study of the major components of the proposed contrastive learning framework. _[verified]_
  > p. 1: “In order to understand what enables the contrastive prediction tasks to learn useful representations, we systematically study the major components of our framework.”

## Method

- SimCLR uses a stochastic data augmentation module to transform data examples into two correlated views considered as positive pairs. _[verified]_
  > p. 2: “A stochastic data augmentation module that transforms any given data example randomly resulting in two correlated views of the same example, denoted xi and xj , which we consider as a positive pair.”
- A base encoder network, such as ResNet, extracts representation vectors from the augmented data examples. _[verified]_
  > p. 2: “A neural network base encoder f (•) that extracts representation vectors from augmented data examples.”
- A small neural network projection head with a nonlinear MLP maps representations to the latent space where the contrastive loss is applied. _[verified]_
  > p. 2: “A small neural network projection head g(•) that maps representations to the space where contrastive loss is applied.”
- The framework optimizes the model using the normalized temperature-scaled cross entropy loss (NT-Xent). _[verified]_
  > p. 2: “This loss has been used in previous work (Sohn, 2016;Wu et al., 2018;Oord et al., 2018); for convenience, we term it NT-Xent (the normalized temperature-scaled cross entropy loss).”
- The model is trained using large batch sizes and the LARS optimizer, along with global batch normalization across all distributed devices. _[partial]_
  > p. 3: “To stabilize the training, we use the LARS optimizer (You et al., 2017) for all batch sizes.”

## Novelty

- The authors note that most individual components have appeared in previous work, and the improved performance stems from the specific combination of design choices. _[verified]_
  > p. 19: “As we have noted in the main text, most individual components of SimCLR have appeared in previous work, and the improved performance is a result of a combination of these design choices.”

## Datasets

- ImageNet _[partial]_
  > p. 7: “1 The details of sampling and exact subsets can be found in https://www.tensorflow.org/datasets/catalog/imagenet2012_subset.”
- Food-101 _[verified]_
  > p. 16: “We investigated transfer learning performance on the Food-101 dataset (Bossard et al., 2014), CIFAR-10 and CIFAR-100 (Krizhevsky & Hinton, 2009), Birdsnap (Berg et al., 2014), the SUN397 scene dataset (Xiao et al., 2010), Stanford Cars (Krause et al., 2013), FGVC Aircraft (Maji et al., 2013), the PASCAL VOC 2007 classification task (Everingham et al., 2010), the Describable Textures Dataset (DTD) (Cimpoi et al., 2014), Oxford-IIIT Pets (Parkhi et al., 2012), Caltech-101 (Fei-Fei et al., 2004), and Oxford 102 Flowers (Nilsback & Zisserman, 2008).”
- CIFAR-10 _[verified]_
  > p. 16: “We investigated transfer learning performance on the Food-101 dataset (Bossard et al., 2014), CIFAR-10 and CIFAR-100 (Krizhevsky & Hinton, 2009), Birdsnap (Berg et al., 2014), the SUN397 scene dataset (Xiao et al., 2010), Stanford Cars (Krause et al., 2013), FGVC Aircraft (Maji et al., 2013), the PASCAL VOC 2007 classification task (Everingham et al., 2010), the Describable Textures Dataset (DTD) (Cimpoi et al., 2014), Oxford-IIIT Pets (Parkhi et al., 2012), Caltech-101 (Fei-Fei et al., 2004), and Oxford 102 Flowers (Nilsback & Zisserman, 2008).”
- CIFAR-100 _[verified]_
  > p. 16: “We investigated transfer learning performance on the Food-101 dataset (Bossard et al., 2014), CIFAR-10 and CIFAR-100 (Krizhevsky & Hinton, 2009), Birdsnap (Berg et al., 2014), the SUN397 scene dataset (Xiao et al., 2010), Stanford Cars (Krause et al., 2013), FGVC Aircraft (Maji et al., 2013), the PASCAL VOC 2007 classification task (Everingham et al., 2010), the Describable Textures Dataset (DTD) (Cimpoi et al., 2014), Oxford-IIIT Pets (Parkhi et al., 2012), Caltech-101 (Fei-Fei et al., 2004), and Oxford 102 Flowers (Nilsback & Zisserman, 2008).”
- Birdsnap _[verified]_
  > p. 16: “We investigated transfer learning performance on the Food-101 dataset (Bossard et al., 2014), CIFAR-10 and CIFAR-100 (Krizhevsky & Hinton, 2009), Birdsnap (Berg et al., 2014), the SUN397 scene dataset (Xiao et al., 2010), Stanford Cars (Krause et al., 2013), FGVC Aircraft (Maji et al., 2013), the PASCAL VOC 2007 classification task (Everingham et al., 2010), the Describable Textures Dataset (DTD) (Cimpoi et al., 2014), Oxford-IIIT Pets (Parkhi et al., 2012), Caltech-101 (Fei-Fei et al., 2004), and Oxford 102 Flowers (Nilsback & Zisserman, 2008).”
- SUN397 _[verified]_
  > p. 16: “We investigated transfer learning performance on the Food-101 dataset (Bossard et al., 2014), CIFAR-10 and CIFAR-100 (Krizhevsky & Hinton, 2009), Birdsnap (Berg et al., 2014), the SUN397 scene dataset (Xiao et al., 2010), Stanford Cars (Krause et al., 2013), FGVC Aircraft (Maji et al., 2013), the PASCAL VOC 2007 classification task (Everingham et al., 2010), the Describable Textures Dataset (DTD) (Cimpoi et al., 2014), Oxford-IIIT Pets (Parkhi et al., 2012), Caltech-101 (Fei-Fei et al., 2004), and Oxford 102 Flowers (Nilsback & Zisserman, 2008).”
- Stanford Cars _[verified]_
  > p. 16: “We investigated transfer learning performance on the Food-101 dataset (Bossard et al., 2014), CIFAR-10 and CIFAR-100 (Krizhevsky & Hinton, 2009), Birdsnap (Berg et al., 2014), the SUN397 scene dataset (Xiao et al., 2010), Stanford Cars (Krause et al., 2013), FGVC Aircraft (Maji et al., 2013), the PASCAL VOC 2007 classification task (Everingham et al., 2010), the Describable Textures Dataset (DTD) (Cimpoi et al., 2014), Oxford-IIIT Pets (Parkhi et al., 2012), Caltech-101 (Fei-Fei et al., 2004), and Oxford 102 Flowers (Nilsback & Zisserman, 2008).”
- FGVC Aircraft _[verified]_
  > p. 16: “We investigated transfer learning performance on the Food-101 dataset (Bossard et al., 2014), CIFAR-10 and CIFAR-100 (Krizhevsky & Hinton, 2009), Birdsnap (Berg et al., 2014), the SUN397 scene dataset (Xiao et al., 2010), Stanford Cars (Krause et al., 2013), FGVC Aircraft (Maji et al., 2013), the PASCAL VOC 2007 classification task (Everingham et al., 2010), the Describable Textures Dataset (DTD) (Cimpoi et al., 2014), Oxford-IIIT Pets (Parkhi et al., 2012), Caltech-101 (Fei-Fei et al., 2004), and Oxford 102 Flowers (Nilsback & Zisserman, 2008).”
- PASCAL VOC 2007 _[verified]_
  > p. 16: “We investigated transfer learning performance on the Food-101 dataset (Bossard et al., 2014), CIFAR-10 and CIFAR-100 (Krizhevsky & Hinton, 2009), Birdsnap (Berg et al., 2014), the SUN397 scene dataset (Xiao et al., 2010), Stanford Cars (Krause et al., 2013), FGVC Aircraft (Maji et al., 2013), the PASCAL VOC 2007 classification task (Everingham et al., 2010), the Describable Textures Dataset (DTD) (Cimpoi et al., 2014), Oxford-IIIT Pets (Parkhi et al., 2012), Caltech-101 (Fei-Fei et al., 2004), and Oxford 102 Flowers (Nilsback & Zisserman, 2008).”
- Describable Textures Dataset (DTD) _[verified]_
  > p. 16: “We investigated transfer learning performance on the Food-101 dataset (Bossard et al., 2014), CIFAR-10 and CIFAR-100 (Krizhevsky & Hinton, 2009), Birdsnap (Berg et al., 2014), the SUN397 scene dataset (Xiao et al., 2010), Stanford Cars (Krause et al., 2013), FGVC Aircraft (Maji et al., 2013), the PASCAL VOC 2007 classification task (Everingham et al., 2010), the Describable Textures Dataset (DTD) (Cimpoi et al., 2014), Oxford-IIIT Pets (Parkhi et al., 2012), Caltech-101 (Fei-Fei et al., 2004), and Oxford 102 Flowers (Nilsback & Zisserman, 2008).”
- Oxford-IIIT Pets _[verified]_
  > p. 16: “We investigated transfer learning performance on the Food-101 dataset (Bossard et al., 2014), CIFAR-10 and CIFAR-100 (Krizhevsky & Hinton, 2009), Birdsnap (Berg et al., 2014), the SUN397 scene dataset (Xiao et al., 2010), Stanford Cars (Krause et al., 2013), FGVC Aircraft (Maji et al., 2013), the PASCAL VOC 2007 classification task (Everingham et al., 2010), the Describable Textures Dataset (DTD) (Cimpoi et al., 2014), Oxford-IIIT Pets (Parkhi et al., 2012), Caltech-101 (Fei-Fei et al., 2004), and Oxford 102 Flowers (Nilsback & Zisserman, 2008).”
- Caltech-101 _[verified]_
  > p. 16: “We investigated transfer learning performance on the Food-101 dataset (Bossard et al., 2014), CIFAR-10 and CIFAR-100 (Krizhevsky & Hinton, 2009), Birdsnap (Berg et al., 2014), the SUN397 scene dataset (Xiao et al., 2010), Stanford Cars (Krause et al., 2013), FGVC Aircraft (Maji et al., 2013), the PASCAL VOC 2007 classification task (Everingham et al., 2010), the Describable Textures Dataset (DTD) (Cimpoi et al., 2014), Oxford-IIIT Pets (Parkhi et al., 2012), Caltech-101 (Fei-Fei et al., 2004), and Oxford 102 Flowers (Nilsback & Zisserman, 2008).”
- Oxford 102 Flowers _[unsupported]_
  > p. 16: “We investigated transfer learning performance on the Food-101 dataset (Bossard et al., 2014), CIFAR-10 and CIFAR-100 (Krizhevsky & Hinton, 2009), Birdsnap (Berg et al., 2014), the SUN397 scene dataset (Xiao et al., 2010), Stanford Cars (Krause et al., 2013), FGVC Aircraft (Maji et al., 2013), the PASCAL VOC 2007 classification task (Everingham et al., 2010), the Describable Textures Dataset (DTD) (Cimpoi et al., 2014), Oxford-IIIT Pets (Parkhi et al., 2012), Caltech-101 (Fei-Fei et al., 2004), and Oxford 102 Flowers (Nilsback & Zisserman, 2008).”

## Baselines

- Supervised baseline _[verified]_
  > p. 7: “Supervised baseline | ResNet-50 | 48.4 | 80.4”
- Local Aggregation _[verified]_
  > p. 7: “Local Agg. | ResNet-50 |  | 24 | 60.2 | -”
- MoCo _[verified]_
  > p. 7: “MoCo | ResNet-50 |  | 24 | 60.6 | -”
- PIRL _[verified]_
  > p. 7: “PIRL | ResNet-50 |  | 24 | 63.6 | -”
- CPC v2 _[verified]_
  > p. 7: “CPC v2 | ResNet-50 |  | 24 | 63.8 | 85.3”
- Rotation _[verified]_
  > p. 7: “Rotation | RevNet-50 (4×) |  | 86 | 55.4 | -”
- BigBiGAN _[verified]_
  > p. 7: “BigBiGAN | RevNet-50 (4×) |  | 86 | 61.3 | 81.9”
- AMDIM _[verified]_
  > p. 7: “AMDIM | Custom-ResNet |  | 626 | 68.1 | -”
- CMC _[verified]_
  > p. 7: “CMC | ResNet-50 (2×) |  | 188 | 68.4 | 88.2”
- Pseudo-label _[verified]_
  > p. 7: “Pseudo-label | ResNet-50 | 51.6 | 82.4”
- VAT+Entropy Min. _[verified]_
  > p. 7: “VAT+Entropy Min. | ResNet-50 | 47.0 | 83.4”
- UDA (w. RandAug) _[verified]_
  > p. 7: “UDA (w. RandAug) | ResNet-50 | - | 88.5”
- FixMatch (w. RandAug) _[verified]_
  > p. 7: “FixMatch (w. RandAug) | ResNet-50 | - | 89.1”
- S4L (Rot+VAT+En. M.) _[verified]_
  > p. 7: “S4L (Rot+VAT+En. M.) | ResNet-50 (4×) | - | 91.2”
- InstDisc _[verified]_
  > p. 7: “InstDisc | ResNet-50 | 39.2 | 77.4”

## Metrics

- Top-1 accuracy _[verified]_
  > p. 4: “Figure 5. Linear evaluation (ImageNet top-1 accuracy) under individual or composition of data augmentations, applied only to one branch.”
  > p. 7: “Method | Architecture |  | Param (M) | Top 1 | Top 5”
- Top 5 accuracy _[verified]_
  > p. 7: “Method | Architecture |  | Param (M) | Top 1 | Top 5”
- mean per-class accuracy _[verified]_
  > p. 16: “We follow the evaluation protocols in the papers introducing these datasets, i.e., we report top-1 accuracy for Food-101, CIFAR-10, CIFAR-100, Birdsnap, SUN397, Stanford Cars, and DTD; mean per-class accuracy for FGVC Aircraft, Oxford-IIIT Pets, Caltech-101, and Oxford 102 Flowers; and the 11-point mAP metric as defined in Everingham et al. (2010) for PASCAL VOC 2007.”
- 11-point mAP _[verified]_
  > p. 16: “We follow the evaluation protocols in the papers introducing these datasets, i.e., we report top-1 accuracy for Food-101, CIFAR-10, CIFAR-100, Birdsnap, SUN397, Stanford Cars, and DTD; mean per-class accuracy for FGVC Aircraft, Oxford-IIIT Pets, Caltech-101, and Oxford 102 Flowers; and the 11-point mAP metric as defined in Everingham et al. (2010) for PASCAL VOC 2007.”

## Hyperparameters

- batch size (pre-training): 256 to 8192 _[verified]_
  > p. 3: “Instead, we vary the training batch size N from 256 to 8192.”
- optimizer (pre-training): LARS _[verified]_
  > p. 3: “To stabilize the training, we use the LARS optimizer (You et al., 2017) for all batch sizes.”
- learning rate (pre-training): 4.8 _[verified]_
  > p. 3: “As the loss, we use NT-Xent, optimized using LARS with learning rate of 4.8 (= 0.3 × BatchSize/256) and weight decay of 10 -6 .”
- weight decay (pre-training): 10 -6 _[verified]_
  > p. 3: “As the loss, we use NT-Xent, optimized using LARS with learning rate of 4.8 (= 0.3 × BatchSize/256) and weight decay of 10 -6 .”
- batch size (pre-training): 4096 _[verified]_
  > p. 3: “We train at batch size 4096 for 100 epochs. 3”
- epochs (pre-training): 100 _[verified]_
  > p. 3: “We train at batch size 4096 for 100 epochs. 3”
- warmup (pre-training): first 10 epochs _[verified]_
  > p. 3: “Furthermore, we use linear warmup for the first 10 epochs, and decay the learning rate with the cosine decay schedule without restarts (Loshchilov & Hutter, 2016).”
- batch size (fine-tuning): 4096 _[verified]_
  > p. 15: “Fine-tuning Procedure We fine-tune using the Nesterov momentum optimizer with a batch size of 4096, momentum of 0.9, and a learning rate of 0.8 (following LearningRate = 0.05 × BatchSize/256) without warmup.”
- optimizer (fine-tuning): Nesterov momentum _[verified]_
  > p. 15: “Fine-tuning Procedure We fine-tune using the Nesterov momentum optimizer with a batch size of 4096, momentum of 0.9, and a learning rate of 0.8 (following LearningRate = 0.05 × BatchSize/256) without warmup.”
- momentum (fine-tuning): 0.9 _[verified]_
  > p. 15: “Fine-tuning Procedure We fine-tune using the Nesterov momentum optimizer with a batch size of 4096, momentum of 0.9, and a learning rate of 0.8 (following LearningRate = 0.05 × BatchSize/256) without warmup.”
- learning rate (fine-tuning): 0.8 _[verified]_
  > p. 15: “Fine-tuning Procedure We fine-tune using the Nesterov momentum optimizer with a batch size of 4096, momentum of 0.9, and a learning rate of 0.8 (following LearningRate = 0.05 × BatchSize/256) without warmup.”
- epochs (fine-tuning): 60 _[verified]_
  > p. 15: “For 1% labeled data we fine-tune for 60 epochs, and for 10% labeled data we fine-tune for 30 epochs.”
- epochs (fine-tuning): 30 _[verified]_
  > p. 15: “For 1% labeled data we fine-tune for 60 epochs, and for 10% labeled data we fine-tune for 30 epochs.”

## Compute

- Cloud TPUs using 32 to 128 cores _[verified]_
  > p. 3: “We train our model with Cloud TPUs, using 32 to 128 cores depending on the batch size.”
- Training time of approximately 1.5 hours using 128 TPU v3 cores _[verified]_
  > p. 3: “2 With 128 TPU v3 cores, it takes ∼1.5 hours to train our ResNet-50 with a batch size of 4096 for 100 epochs.”

## Claims

- A linear classifier trained on self-supervised representations learned by SimCLR achieves 76.5% top-1 accuracy on ImageNet. _[partial]_
  > p. 1: “A linear classifier trained on self-supervised representations learned by Sim-CLR achieves 76.5% top-1 accuracy, which is a 7% relative improvement over previous state-ofthe-art, matching the performance of a supervised ResNet-50.”
- Fine-tuning on only 1% of the labels achieves 85.8% top-5 accuracy. _[verified]_
  > p. 1: “When fine-tuned on only 1% of the labels, we achieve 85.8% top-5 accuracy, outperforming AlexNet with 100× fewer labels.”
- SimCLR outperforms previous work while remaining simpler without specialized architectures or a memory bank. _[verified]_
  > p. 1: “Not only does SimCLR outperform previous work (Figure 1), but it is also simpler, requiring neither specialized architectures (Bachman et al., 2019;Hénaff et al., 2019) nor a memory bank (Wu et al., 2018;Tian et al., 2019;He et al., 2019;Misra & van der Maaten, 2019).”

## Code

- https://github.com/google-research/simclr _[verified]_
  > p. 1: “1 Code available at https://github.com/google-research/simclr.”


## 2010.11929

# AN IMAGE IS WORTH 16X16 WORDS: TRANSFORMERS FOR IMAGE RECOGNITION AT SCALE

Alexey Dosovitskiy, Lucas Beyer, Alexander Kolesnikov, Dirk Weissenborn, Xiaohua Zhai, Thomas Unterthiner, Mostafa Dehghani, Matthias Minderer, Georg Heigold, Sylvain Gelly, Jakob Uszkoreit, Neil Houlsby
2021 · arXiv:2010.11929v2[cs.CV]

## Problem

- Applications of the Transformer architecture to computer vision remain limited and rely heavily on convolutional networks. _[verified]_
  > p. 1: “While the Transformer architecture has become the de-facto standard for natural language processing tasks, its applications to computer vision remain limited.”
- Alternative models that replace convolutions entirely have not yet been scaled effectively on modern hardware accelerators. _[verified]_
  > p. 1: “The latter models, while theoretically efficient, have not yet been scaled effectively on modern hardware accelerators due to the use of specialized attention patterns.”

## Task

- image classification _[verified]_
  > p. 1: “We show that this reliance on CNNs is not necessary and a pure transformer applied directly to sequences of image patches can perform very well on image classification tasks.”

## Method

- The model follows the original Transformer design closely and uses standard learnable 1D position embeddings added to patch embeddings. _[verified]_
  > p. 3: “We use standard learnable 1D position embeddings, since we have not observed significant performance gains from using more advanced 2D-aware position embeddings (Appendix D.4).”
- To process 2D images, the input image is reshaped into a sequence of flattened 2D patches and mapped to a constant latent dimension using a trainable linear projection. _[verified]_
  > p. 3: “To handle 2D images, we reshape the image x ∈ R H×W ×C into a sequence of flattened 2D patches x p ∈ R N ×(P 2 •C) , where (H, W ) is the resolution of the original image, C is the number of channels, (P, P ) is the resolution of each image patch, and N = HW/P 2 is the resulting number of patches, which also serves as the effective input sequence length for the Transformer.”
- A learnable classification embedding is prepended to the sequence of patches, and a classification head is attached to its output state during both pre-training and fine-tuning. _[verified]_
  > p. 3: “Both during pre-training and fine-tuning, a classification head is attached to z 0 L .”
- The Transformer encoder consists of alternating layers of multiheaded self-attention and MLP blocks, with layernorm applied before every block and residual connections after every block. _[verified]_
  > p. 3: “The Transformer encoder (Vaswani et al., 2017) consists of alternating layers of multiheaded selfattention (MSA, see Appendix A) and MLP blocks (Eq. 2, 3).”
- The model is typically pre-trained on large datasets and then fine-tuned on smaller downstream tasks by replacing the prediction head with a zero-initialized feedforward layer. _[verified]_
  > p. 4: “Typically, we pre-train ViT on large datasets, and fine-tune to (smaller) downstream tasks.”

## Datasets

- ILSVRC-2012 ImageNet (1.3M images) _[verified]_
  > p. 4: “To explore model scalability, we use the ILSVRC-2012 ImageNet dataset with 1k classes and 1.3M images (we refer to it as ImageNet in what follows), its superset ImageNet-21k with 21k classes and 14M images (Deng et al., 2009), and JFT (Sun et al., 2017) with 18k classes and 303M high-resolution images.”
- ImageNet-21k (14M images) _[verified]_
  > p. 4: “To explore model scalability, we use the ILSVRC-2012 ImageNet dataset with 1k classes and 1.3M images (we refer to it as ImageNet in what follows), its superset ImageNet-21k with 21k classes and 14M images (Deng et al., 2009), and JFT (Sun et al., 2017) with 18k classes and 303M high-resolution images.”
- JFT (303M high-resolution images) _[verified]_
  > p. 4: “To explore model scalability, we use the ILSVRC-2012 ImageNet dataset with 1k classes and 1.3M images (we refer to it as ImageNet in what follows), its superset ImageNet-21k with 21k classes and 14M images (Deng et al., 2009), and JFT (Sun et al., 2017) with 18k classes and 303M high-resolution images.”
- CIFAR-10/100 _[verified]_
  > p. 4: “We transfer the models trained on these dataset to several benchmark tasks: ImageNet on the original validation labels and the cleaned-up ReaL labels (Beyer et al., 2020), CIFAR-10/100 (Krizhevsky, 2009), Oxford-IIIT Pets (Parkhi et al., 2012), and Oxford Flowers-102 (Nilsback & Zisserman, 2008).”
- Oxford-IIIT Pets _[verified]_
  > p. 4: “We transfer the models trained on these dataset to several benchmark tasks: ImageNet on the original validation labels and the cleaned-up ReaL labels (Beyer et al., 2020), CIFAR-10/100 (Krizhevsky, 2009), Oxford-IIIT Pets (Parkhi et al., 2012), and Oxford Flowers-102 (Nilsback & Zisserman, 2008).”
- Oxford Flowers-102 _[verified]_
  > p. 4: “We transfer the models trained on these dataset to several benchmark tasks: ImageNet on the original validation labels and the cleaned-up ReaL labels (Beyer et al., 2020), CIFAR-10/100 (Krizhevsky, 2009), Oxford-IIIT Pets (Parkhi et al., 2012), and Oxford Flowers-102 (Nilsback & Zisserman, 2008).”
- VTAB (19 tasks) _[verified]_
  > p. 5: “We also evaluate on the 19-task VTAB classification suite (Zhai et al., 2019b).”

## Baselines

- Big Transfer (BiT) _[verified]_
  > p. 5: “The first comparison point is Big Transfer (BiT) (Kolesnikov et al., 2020), which performs supervised transfer learning with large ResNets.”
- Noisy Student _[verified]_
  > p. 5: “The second is Noisy Student (Xie et al., 2020), which is a large EfficientNet trained using semi-supervised learning on ImageNet and JFT-300M with the labels removed.”
- VIVI _[verified]_
  > p. 6: “Figure 2 decomposes the VTAB tasks into their respective groups, and compares to previous SOTA methods on this benchmark: BiT, VIVI -a ResNet co-trained on ImageNet and Youtube (Tschannen et al., 2020), and S4L -supervised plus semi-supervised learning on ImageNet (Zhai et al., 2019a).”
- S4L _[verified]_
  > p. 6: “Figure 2 decomposes the VTAB tasks into their respective groups, and compares to previous SOTA methods on this benchmark: BiT, VIVI -a ResNet co-trained on ImageNet and Youtube (Tschannen et al., 2020), and S4L -supervised plus semi-supervised learning on ImageNet (Zhai et al., 2019a).”

## Metrics

- Few-shot or fine-tuning accuracy _[verified]_
  > p. 5: “We report results on downstream datasets either through few-shot or fine-tuning accuracy.”
- Top-5 and top-1 accuracy _[verified]_
  > p. 20: “We also evaluate our flagship ViT-H/14 model on the ObjectNet benchmark following the evaluation setup in Kolesnikov et al. (2020), resulting in 82.1% top-5 accuracy and 61.7% top-1 accuracy.”

## Hyperparameters

- optimizer (pre-training): Adam _[verified]_
  > p. 5: “We train all models, including ResNets, using Adam (Kingma & Ba, 2015) with β 1 = 0.9, β 2 = 0.999, a batch size of 4096 and apply a high weight decay of 0.1, which we found to be useful for transfer of all models (Appendix D.1 shows that, in contrast to common practices, Adam works slightly better than SGD for ResNets in our setting).”
- beta_1 (pre-training): 0.9 _[verified]_
  > p. 5: “We train all models, including ResNets, using Adam (Kingma & Ba, 2015) with β 1 = 0.9, β 2 = 0.999, a batch size of 4096 and apply a high weight decay of 0.1, which we found to be useful for transfer of all models (Appendix D.1 shows that, in contrast to common practices, Adam works slightly better than SGD for ResNets in our setting).”
- beta_2 (pre-training): 0.999 _[verified]_
  > p. 5: “We train all models, including ResNets, using Adam (Kingma & Ba, 2015) with β 1 = 0.9, β 2 = 0.999, a batch size of 4096 and apply a high weight decay of 0.1, which we found to be useful for transfer of all models (Appendix D.1 shows that, in contrast to common practices, Adam works slightly better than SGD for ResNets in our setting).”
- batch size (pre-training): 4096 _[verified]_
  > p. 5: “We train all models, including ResNets, using Adam (Kingma & Ba, 2015) with β 1 = 0.9, β 2 = 0.999, a batch size of 4096 and apply a high weight decay of 0.1, which we found to be useful for transfer of all models (Appendix D.1 shows that, in contrast to common practices, Adam works slightly better than SGD for ResNets in our setting).”
- weight decay (pre-training): 0.1 _[verified]_
  > p. 5: “We train all models, including ResNets, using Adam (Kingma & Ba, 2015) with β 1 = 0.9, β 2 = 0.999, a batch size of 4096 and apply a high weight decay of 0.1, which we found to be useful for transfer of all models (Appendix D.1 shows that, in contrast to common practices, Adam works slightly better than SGD for ResNets in our setting).”
- optimizer (fine-tuning): SGD with momentum _[verified]_
  > p. 5: “For fine-tuning we use SGD with momentum, batch size 512, for all models, see Appendix B.1.1.”
- batch size (fine-tuning): 512 _[verified]_
  > p. 5: “For fine-tuning we use SGD with momentum, batch size 512, for all models, see Appendix B.1.1.”
- Polyak averaging factor (fine-tuning): 0.9999 _[verified]_
  > p. 5: “For ImageNet results in Table 2, we fine-tuned at higher resolution: 512 for ViT-L/16 and 518 for ViT-H/14, and also used Polyak & Juditsky (1992) averaging with a factor of 0.9999 (Ramachandran et al., 2019;Wang et al., 2020b).”
- momentum (fine-tuning): 0.9 _[verified]_
  > p. 13: “We fine-tune all ViT models using SGD with a momentum of 0.9.”

## Compute

- Models were trained on TPUv3 hardware, and compute reported in TPUv3-core-days _[verified]_
  > p. 5: “All models were trained on TPUv3 hardware, and we report the number of TPUv3-core-days taken to pre-train each of them, that is, the number of TPU v3 cores (2 per chip) used for training multiplied by the training time in days.”
- ViT-L/16 model pre-trained on ImageNet-21k could be trained using standard cloud TPUv3 with 8 cores in approximately 30 days _[verified]_
  > p. 6: “Finally, the ViT-L/16 model pre-trained on the public ImageNet-21k dataset performs well on most datasets too, while taking fewer resources to pre-train: it could be trained using a standard cloud TPUv3 with 8 cores in approximately 30 days.”

## Seeds and runs

- Mean and standard deviation of accuracies averaged over three fine-tuning runs _[verified]_
  > p. 6: “We report mean and standard deviation of the accuracies, averaged over three fine-tuning runs.”

## Ablations

- Ablation study on positional embedding presence and encoding method using ViT-B/16 model _[verified]_
  > p. 18: “Table 8 summarizes the results from this ablation study on a ViT-B/16 model.”

## Claims

- Vision Transformer attains excellent results compared to state-of-the-art convolutional networks while requiring fewer computational resources. _[verified]_
  > p. 1: “When pre-trained on large amounts of data and transferred to multiple mid-sized or small image recognition benchmarks (ImageNet, CIFAR-100, VTAB, etc.), Vision Transformer (ViT) attains excellent results compared to state-of-the-art convolutional networks while requiring substantially fewer computational resources to train.”
- The best model reaches specific high accuracy percentages on ImageNet, ImageNet-ReaL, CIFAR-100, and the VTAB suite. _[verified]_
  > p. 2: “In particular, the best model reaches the accuracy of 88.55% on ImageNet, 90.72% on ImageNet-ReaL, 94.55% on CIFAR-100, and 77.63% on the VTAB suite of 19 tasks.”

## Limitations

- Gap between self-supervised and large-scale supervised pre-training performance _[verified]_
  > p. 9: “Our initial experiments show improvement from self-supervised pre-training, but there is still large gap between self-supervised and large-scale supervised pretraining.”

## Future work

- Apply Vision Transformer to other computer vision tasks like detection and segmentation _[verified]_
  > p. 9: “One is to apply ViT to other computer vision tasks, such as detection and segmentation.”
- Continue exploring self-supervised pre-training methods _[verified]_
  > p. 9: “Another challenge is to continue exploring selfsupervised pre-training methods.”
- Further scale Vision Transformer models to improve performance _[verified]_
  > p. 9: “Finally, further scaling of ViT would likely lead to improved performance.”

## Code

- https://github.com/google-research/vision_transformer _[verified]_
  > p. 1: “Fine-tuning code and pre-trained models are available at https://github.com/ google-research/vision_transformer”
- https://github.com/csrhddlam/axial-deeplab _[verified]_
  > p. 19: “Our implementation is based on the open-sourced PyTorch implementation in https://github.com/ csrhddlam/axial-deeplab.In our experiments, we reproduced the scores reported in(Wang et al., 2020b) in terms of accuracy, however, our implementation, similar to the open-source implementation, is very slow on TPUs.Therefore, we were not able to use it for extensive large-scale experiments.These may be unlocked by a carefully optimized implementation.”


## 2106.09685

# LORA: LOW-RANK ADAPTATION OF LARGE LAN-GUAGE MODELS

Edward Hu, Yelong Shen, Phillip Wallis, Zeyuan Allen-Zhu, Yuanzhi Li, Shean Wang, Lu Wang, Weizhu Chen
2021 · arXiv:2106.09685v2[cs.CL]

## Problem

- Full fine-tuning of large pre-trained language models like GPT-3 175B becomes prohibitively expensive and logistically difficult. _[verified]_
  > p. 1: “Using GPT-3 175B as an example -deploying independent instances of fine-tuned models, each with 175B parameters, is prohibitively expensive.”
- Existing parameter-efficient adaptation methods often introduce inference latency or reduce the usable sequence length. _[verified]_
  > p. 1: “However, existing techniques often introduce inference latency (Houlsby et al., 2019;Rebuffi et al., 2017) by extending model depth or reduce the model's usable sequence length (Li & Liang, 2021;Lester et al., 2021;Hambardzumyan et al., 2020;Liu et al., 2021) (Section 3).”
- Prior efficient adaptation methods often fail to match full fine-tuning baselines. _[verified]_
  > p. 2: “More importantly, these method often fail to match the fine-tuning baselines, posing a trade-off between efficiency and model quality.”

## Task

- Adaptation of large-scale pre-trained language models to downstream tasks. _[verified]_
  > p. 1: “An important paradigm of natural language processing consists of large-scale pretraining on general domain data and adaptation to particular tasks or domains.”

## Contributions

- Proposing Low-Rank Adaptation (LoRA), which freezes pretrained model weights and injects trainable rank decomposition matrices into Transformer layers. _[verified]_
  > p. 1: “We propose Low-Rank Adaptation, or LoRA, which freezes the pretrained model weights and injects trainable rank decomposition matrices into each layer of the Transformer architecture, greatly reducing the number of trainable parameters for downstream tasks.”
- Providing an empirical investigation into rank-deficiency in language model adaptation. _[verified]_
  > p. 1: “We also provide an empirical investigation into rank-deficiency in language model adaptation, which sheds light on the efficacy of LoRA.”
- Releasing a software package to integrate LoRA with PyTorch models along with implementations and checkpoints. _[verified]_
  > p. 1: “We release a package that facilitates the integration of LoRA with PyTorch models and provide our implementations and model checkpoints for RoBERTa, DeBERTa, and GPT-2 at https://github.com/microsoft/LoRA.”

## Method

- The proposed method uses a low-rank decomposition to represent weight updates, constraining the weight matrix update as W 0 + BA where A and B are trainable low-rank matrices and the original pre-trained weight W 0 is frozen. _[verified]_
  > p. 4: “For a pre-trained weight matrix W 0 ∈ R d×k , we constrain its update by representing the latter with a low-rank decomposition W 0 + ∆W = W 0 + BA, where B ∈ R d×r , A ∈ R r×k , and the rank r min(d, k).”
- The method applies a random Gaussian initialization for matrix A and zero for matrix B so that the update term starts at zero, and scales the product by a constant alpha divided by r. _[partial]_
  > p. 4: “We use a random Gaussian initialization for A and zero for B, so ∆W = BA is zero at the beginning of training.”
- The authors focus on applying LoRA specifically to the attention weights within Transformer language models while freezing the MLP modules. _[verified]_
  > p. 5: “We limit our study to only adapting the attention weights for downstream tasks and freeze the MLP modules (so they are not trained in downstream tasks) both for simplicity and parameter-efficiency.”

## Novelty

- Unlike full fine-tuning which learns a full-dimension parameter update for each task, the proposed approach is parameter-efficient and uses a low-rank representation to encode weight updates. _[partial]_
  > p. 3: “In this paper, we adopt a more parameter-efficient approach, where the task-specific parameter”
- LoRA does not require accumulated gradient updates to have full rank during adaptation, recovering the expressiveness of full fine-tuning as the rank increases without introducing additional inference latency. _[verified]_
  > p. 4: “LoRA takes a step further and does not require the accumulated gradient update to weight matrices to have full-rank during adaptation.”

## Datasets

- GLUE _[verified]_
  > p. 5: “Specifically, we evaluate on the GLUE (Wang et al., 2019) benchmark for RoBERTa and DeBERTa.”
- WikiSQL _[verified]_
  > p. 5: “We follow the setup of Li & Liang (2021) on GPT-2 for a direct comparison and add WikiSQL (Zhong et al., 2017) (NL to SQL queries) and SAMSum (Gliwa et al., 2019) (conversation summarization) for large-scale experiments on GPT-3.”
- SAMSum _[verified]_
  > p. 5: “We follow the setup of Li & Liang (2021) on GPT-2 for a direct comparison and add WikiSQL (Zhong et al., 2017) (NL to SQL queries) and SAMSum (Gliwa et al., 2019) (conversation summarization) for large-scale experiments on GPT-3.”
- E2E NLG Challenge _[verified]_
  > p. 7: “Due to space constraint, we only present our result on E2E NLG Challenge (Table 3) in this section.”
- WebNLG _[verified]_
  > p. 7: “See Section F.1 for results on WebNLG (Gardent et al., 2017) and DART (Nan et al., 2020).”
- DART _[verified]_
  > p. 7: “See Section F.1 for results on WebNLG (Gardent et al., 2017) and DART (Nan et al., 2020).”

## Baselines

- Fine-Tuning (FT) _[verified]_
  > p. 5: “Fine-Tuning (FT) is a common approach for adaptation.”
- FT Top2 _[verified]_
  > p. 5: “We include one such baseline reported in prior work (Li & Liang, 2021) on GPT-2, which adapts just the last two layers (FT Top2 ).”
- Bias-only or BitFit _[verified]_
  > p. 6: “Bias-only or BitFit is a baseline where we only train the bias vectors while freezing everything else.”
- Prefix-embedding tuning (PreEmbed) _[verified]_
  > p. 6: “Prefix-embedding tuning (PreEmbed) inserts special tokens among the input tokens.”
- Prefix-layer tuning (PreLayer) _[verified]_
  > p. 6: “Prefix-layer tuning (PreLayer) is an extension to prefix-embedding tuning.”
- Adapter H _[verified]_
  > p. 6: “We call this original design Adapter H .”
- Adapter L _[verified]_
  > p. 6: “Recently, Lin et al. (2020) proposed a more efficient design with the adapter layer applied only after the MLP module and after a LayerNorm.”
- Adapter P _[verified]_
  > p. 6: “This is very similar to another deign proposed in Pfeiffer et al. (2021), which we call Adapter P .”
- AdapterDrop (Adapter D ) _[verified]_
  > p. 6: “We also include another baseline call AdapterDrop (Rücklé et al., 2020) which drops some adapter layers for greater efficiency (Adapter D ).”

## Metrics

- BLEU score _[partial]_
  > p. 7: “For all metrics, higher is better.”
- NIST score _[partial]_
  > p. 7: “For all metrics, higher is better.”
- MET score _[partial]_
  > p. 7: “For all metrics, higher is better.”
- ROUGE-L score _[partial]_
  > p. 7: “For all metrics, higher is better.”
- CIDEr score _[partial]_
  > p. 7: “For all metrics, higher is better.”
- Logical form validation accuracy on WikiSQL _[verified]_
  > p. 8: “We report the logical form validation accuracy on WikiSQL, validation accuracy on MultiNLI-matched, and Rouge-1/2/L on SAMSum.”
- Validation accuracy on MultiNLI-matched _[verified]_
  > p. 8: “We report the logical form validation accuracy on WikiSQL, validation accuracy on MultiNLI-matched, and Rouge-1/2/L on SAMSum.”
- Rouge-1/2/L on SAMSum _[verified]_
  > p. 8: “We report the logical form validation accuracy on WikiSQL, validation accuracy on MultiNLI-matched, and Rouge-1/2/L on SAMSum.”

## Hyperparameters

- sequence length: 128 _[verified]_
  > p. 7: “First, we use the same batch size for all tasks and use a sequence length of 128 to match the adapter baselines.”
- r: 4 _[verified]_
  > p. 5: “With r = 4 and only the query and value projection matrices being adapted, the checkpoint size is reduced by roughly 10,000× (from 350GB to 35MB)foot_2 .”

## Compute

- NVIDIA Quadro RTX8000 GPU _[verified]_
  > p. 4: “We use an NVIDIA Quadro RTX8000.”
- NVIDIA Tesla V100 GPU _[verified]_
  > p. 5: “We use NVIDIA Tesla V100 for all experiments.”

## Seeds and runs

- Averaged over 100 trials _[partial]_
  > p. 4: “Table 1: Infernece latency of a single forward pass in GPT-2 medium measured in milliseconds, averaged over 100 trials.”

## Ablations

- Ablation on different rank r values _[verified]_
  > p. 10: “Table 6: Validation accuracy on WikiSQL and MultiNLI with different rank r.”

## Claims

- LoRA can drastically reduce the number of trainable parameters and GPU memory requirements compared to fine-tuned GPT-3 175B. _[verified]_
  > p. 1: “Compared to GPT-3 175B fine-tuned with Adam, LoRA can reduce the number of trainable parameters by 10,000 times and the GPU memory requirement by 3 times.”
- LoRA performs on-par or better than fine-tuning while offering higher training throughput and no inference latency. _[verified]_
  > p. 1: “LoRA performs on-par or better than finetuning in model quality on RoBERTa, DeBERTa, GPT-2, and GPT-3, despite having fewer trainable parameters, a higher training throughput, and, unlike adapters, no additional inference latency.”

## Limitations

- A small rank may not be effective for every task or dataset, such as when a downstream task uses a different language than pre-training. _[partial]_
  > p. 10: “However, we do not expect a small r to work for every task or dataset.”

## Future work

- Combine LoRA with other efficient adaptation methods to potentially provide orthogonal improvements. _[verified]_
  > p. 12: “1) LoRA can be combined with other efficient adaptation methods, potentially providing orthogonal improvement.”
- Investigate the underlying mechanism of how features learned during pre-training are transformed for downstream tasks. _[verified]_
  > p. 12: “2) The mechanism behind fine-tuning or LoRA is far from clear -how are features learned during pre-training transformed to do well on downstream tasks?”
- Find more principled ways to select which weight matrices to apply LoRA to, rather than relying on heuristics. _[verified]_
  > p. 13: “3) We mostly depend on heuristics to select the weight matrices to apply LoRA to.”
- Explore whether the rank-deficiency of the adaptation matrix implies that pre-trained model weights could be rank-deficient as well. _[verified]_
  > p. 13: “4) Finally, the rank-deficiency of ∆W suggests that W could be rank-deficient as well, which can also be a source of inspiration for future works.”

## Code

- https://github.com/microsoft/LoRA _[verified]_
  > p. 1: “We release a package that facilitates the integration of LoRA with PyTorch models and provide our implementations and model checkpoints for RoBERTa, DeBERTa, and GPT-2 at https://github.com/microsoft/LoRA. * Equal contribution. 0”


## 1910.10683

# Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer

Colin Raffel, Noam Shazeer, Adam Roberts, Sharan Narang, Michael Matena, Wei Li, Peter J Liu, Colin ©2020, Noam Raffel, Adam Shazeer, Katherine Roberts, Sharan Lee, Michael Narang, Yanqi Matena, Wei Zhou, Peter J Li, Liu
2023 · arXiv:1910.10683v4[cs.LG]

## Problem

- The rapid progress and diversity of transfer learning techniques in NLP make it difficult to compare different algorithms and understand existing methods. _[verified]_
  > p. 2: “The rapid rate of progress and diversity of techniques in this burgeoning field can make it difficult to compare different algorithms, tease apart the effects of new contributions, and understand the space of existing methods for transfer learning.”

## Task

- summarization _[verified]_
  > p. 1: “By combining the insights from our exploration with scale and our new "Colossal Clean Crawled Corpus", we achieve state-of-the-art results on many benchmarks covering summarization, question answering, text classification, and more.”
- question answering _[verified]_
  > p. 1: “By combining the insights from our exploration with scale and our new "Colossal Clean Crawled Corpus", we achieve state-of-the-art results on many benchmarks covering summarization, question answering, text classification, and more.”
- text classification _[verified]_
  > p. 1: “By combining the insights from our exploration with scale and our new "Colossal Clean Crawled Corpus", we achieve state-of-the-art results on many benchmarks covering summarization, question answering, text classification, and more.”

## Contributions

- Introducing a unified framework that converts all text-based language problems into a text-to-text format. _[verified]_
  > p. 1: “In this paper, we explore the landscape of transfer learning techniques for NLP by introducing a unified framework that converts all text-based language problems into a text-to-text format.”
- Conducting a systematic study comparing pre-training objectives, architectures, unlabeled data sets, and transfer approaches. _[verified]_
  > p. 1: “Our systematic study compares pre-training objectives, architectures, unlabeled data sets, transfer approaches, and other factors on dozens of language understanding tasks.”
- Releasing the Colossal Clean Crawled Corpus data set, pre-trained models, and code. _[partial]_
  > p. 1: “By combining the insights from our exploration with scale and our new "Colossal Clean Crawled Corpus", we achieve state-of-the-art results on many benchmarks covering summarization, question answering, text classification, and more.”

## Datasets

- Colossal Clean Crawled Corpus (about 750 GB) _[verified]_
  > p. 7: “We dub this data set the "Colossal Clean Crawled Corpus" (or C4 for short) and release it as part of TensorFlow Datasets.”
- GLUE _[verified]_
  > p. 7: “Specifically, we measure performance on the GLUE and SuperGLUE text classification meta-benchmarks; CNN/Daily Mail abstractive summarization; SQuAD question answering; and WMT English to German, French, and Romanian translation.”
- SuperGLUE _[verified]_
  > p. 7: “Specifically, we measure performance on the GLUE and SuperGLUE text classification meta-benchmarks; CNN/Daily Mail abstractive summarization; SQuAD question answering; and WMT English to German, French, and Romanian translation.”
- CNN/Daily Mail _[verified]_
  > p. 7: “Specifically, we measure performance on the GLUE and SuperGLUE text classification meta-benchmarks; CNN/Daily Mail abstractive summarization; SQuAD question answering; and WMT English to German, French, and Romanian translation.”
- SQuAD _[verified]_
  > p. 7: “Specifically, we measure performance on the GLUE and SuperGLUE text classification meta-benchmarks; CNN/Daily Mail abstractive summarization; SQuAD question answering; and WMT English to German, French, and Romanian translation.”
- WMT English to German _[verified]_
  > p. 7: “Specifically, we measure performance on the GLUE and SuperGLUE text classification meta-benchmarks; CNN/Daily Mail abstractive summarization; SQuAD question answering; and WMT English to German, French, and Romanian translation.”
- CoLA _[verified]_
  > p. 7: “Sentence acceptability judgment (CoLA (Warstadt et al., 2018))”
- SST-2 _[verified]_
  > p. 7: “Sentiment analysis (SST-2 (Socher et al., 2013))”
- MRPC _[verified]_
  > p. 7: “Paraphrasing/sentence similarity (MRPC (Dolan and Brockett, 2005), STS-B (Cer et al., 2017), QQP (Iyer et al., 2017))”
- STS-B _[verified]_
  > p. 7: “Paraphrasing/sentence similarity (MRPC (Dolan and Brockett, 2005), STS-B (Cer et al., 2017), QQP (Iyer et al., 2017))”
- QQP _[verified]_
  > p. 7: “Paraphrasing/sentence similarity (MRPC (Dolan and Brockett, 2005), STS-B (Cer et al., 2017), QQP (Iyer et al., 2017))”
- MNLI _[verified]_
  > p. 7: “Natural language inference (MNLI (Williams et al., 2017), QNLI (Rajpurkar et al., 2016), RTE (Dagan et al., 2005), CB (De Marneff et al., 2019))”
- QNLI _[verified]_
  > p. 7: “Natural language inference (MNLI (Williams et al., 2017), QNLI (Rajpurkar et al., 2016), RTE (Dagan et al., 2005), CB (De Marneff et al., 2019))”
- RTE _[verified]_
  > p. 7: “Natural language inference (MNLI (Williams et al., 2017), QNLI (Rajpurkar et al., 2016), RTE (Dagan et al., 2005), CB (De Marneff et al., 2019))”
- CB _[verified]_
  > p. 7: “Natural language inference (MNLI (Williams et al., 2017), QNLI (Rajpurkar et al., 2016), RTE (Dagan et al., 2005), CB (De Marneff et al., 2019))”
- WNLI _[verified]_
  > p. 7: “Coreference resolution (WNLI and WSC (Levesque et al., 2012))”
- WSC _[verified]_
  > p. 7: “Coreference resolution (WNLI and WSC (Levesque et al., 2012))”
- COPA _[verified]_
  > p. 7: “Sentence completion (COPA (Roemmele et al., 2011))”
- WIC _[verified]_
  > p. 7: “Word sense disambiguation (WIC (Pilehvar and Camacho-Collados, 2018))”
- MultiRC _[verified]_
  > p. 7: “Question answering (MultiRC (Khashabi et al., 2018), ReCoRD (Zhang et al., 2018), BoolQ (Clark et al., 2019))”
- ReCoRD _[verified]_
  > p. 7: “Question answering (MultiRC (Khashabi et al., 2018), ReCoRD (Zhang et al., 2018), BoolQ (Clark et al., 2019))”
- BoolQ _[verified]_
  > p. 7: “Question answering (MultiRC (Khashabi et al., 2018), ReCoRD (Zhang et al., 2018), BoolQ (Clark et al., 2019))”
- Definite Pronoun Resolution _[verified]_
  > p. 8: “As suggested by Kocijan et al. (2019) we also include the Definite Pronoun Resolution (DPR) data set (Rahman and Ng, 2012) in the combined SuperGLUE task.”

## Metrics

- BLEU score for machine translation _[verified]_
  > p. 14: “For all translation tasks, we report the BLEU score (Papineni et al., 2002) as provided by SacreBLEU v1.3.0 (Post, 2018) with "exp" smoothing and "intl" tokenization.”
- ROUGE-2-F score for text summarization _[unsupported]_
  > p. 14: “Similarly, for SQuAD we find the performance of the "exact match" and "F1" scores to be highly correlated so we report the "exact match" score alone.”
- Exact match score for question answering _[verified]_
  > p. 14: “Similarly, for SQuAD we find the performance of the "exact match" and "F1" scores to be highly correlated so we report the "exact match" score alone.”

## Hyperparameters

- dropout: 0.1 _[verified]_
  > p. 11: “For regularization, we use a dropout probability of 0.1 everywhere dropout is applied in the model.”
- pre-training steps (pre-training): 2 19 = 524,288 _[verified]_
  > p. 11: “We pre-train each model for 2 19 = 524,288 steps on C4 before fine-tuning.”
- maximum sequence length: 512 _[verified]_
  > p. 11: “We use a maximum sequence length of 512 and a batch size of 128 sequences.”
- batch size: 128 sequences _[verified]_
  > p. 11: “We use a maximum sequence length of 512 and a batch size of 128 sequences.”
- warm-up steps (pre-training): 10 4 _[verified]_
  > p. 12: “During pre-training, we use an "inverse square root" learning rate schedule: 1 max(n, k) where n is the current training iteration and k is the number of warm-up steps (set to 10 4 in all of our experiments).”
- learning rate (pre-training): 0.01 _[verified]_
  > p. 12: “This sets a constant learning rate of 0.01 for the first 10 4 steps, then exponentially decays the learning rate until pre-training is over.”
- fine-tuning steps (fine-tuning): 2 18 = 262,144 _[verified]_
  > p. 12: “Our models are fine-tuned for 2 18 = 262,144 steps on all tasks.”
- learning rate (fine-tuning): 0.001 _[verified]_
  > p. 12: “We use a constant learning rate of 0.001 when fine-tuning.”
- vocabulary size: 32,000 _[verified]_
  > p. 12: “For all experiments, we use a vocabulary of 32,000 wordpieces.”
- token dropout percentage (pre-training): 15% _[verified]_
  > p. 13: “Inspired by BERT's "masked language modeling" objective and the "word dropout" regularization technique (Bowman et al., 2015), we design an objective that randomly samples and then drops out 15% of tokens in the input sequence.”

## Compute

- Cloud TPU Pods containing TPU v3 chips and Mesh TensorFlow library _[partial]_
  > p. 5: “As a result, we use a combination of model and data parallelism and train models on "slices" of Cloud TPU Pods.”

## Seeds and runs

- Trained baseline model 10 times from scratch with different random initializations and data set shuffling _[verified]_
  > p. 14: “As a cheaper alternative, we train our baseline model 10 times from scratch (i.e. with different random initializations and data set shuffling) and assume that the variance over these runs of the base model also applies to each experimental variant.”

## Claims

- Achieved state-of-the-art results on many benchmarks covering summarization, question answering, text classification, and others. _[verified]_
  > p. 1: “By combining the insights from our exploration with scale and our new "Colossal Clean Crawled Corpus", we achieve state-of-the-art results on many benchmarks covering summarization, question answering, text classification, and more.”
- Trained models up to 11 billion parameters. _[unsupported]_
  > p. 3: “As such, our work primarily comprises a survey, exploration, and empirical comparison of existing techniques.”

## Limitations

- English-only pre-training failed to achieve state-of-the-art results on translation tasks. _[verified]_
  > p. 43: “We were disappointed to find that English-only pre-training did not achieve state-of-the-art results on the translation tasks we studied.”

## Future work

- Explore entirely different ways of leveraging unlabeled data instead of minor variations in objectives. _[verified]_
  > p. 24: “Instead, it may be fortuitous to explore entirely different ways of leveraging unlabeled data.”
- Research methods to achieve stronger performance with cheaper models for transfer learning. _[verified]_
  > p. 43: “As a result, we advocate for research on methods that achieve stronger performance with cheaper models so that transfer learning can be applied where it will have the most impact.”
- Investigate more efficient ways to provide general-purpose knowledge without requiring 1 trillion tokens of text. _[verified]_
  > p. 43: “More concretely, it would be useful to be able to attain good fine-tuning performance without needing to train our models on 1 trillion tokens of text first.”
- Formulate a more rigorous notion of task similarity between pre-training and downstream tasks. _[verified]_
  > p. 43: “It would be useful to formulate a more rigorous notion of the "similarity" between the pre-training and downstream tasks, so that we could make more principled choices about what source of unlabeled data to use.”
- Further investigate language-agnostic models to handle NLP tasks regardless of the language. _[verified]_
  > p. 43: “To address these issues, we are interested in further investigating language-agnostic models, i.e. models that can perform a given NLP task with good performance regardless of the text's language.”

## Code

- https://github.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words _[verified]_
  > p. 6: “Our heuristics are inspired by past work on using Common 6. https://github.com/LDNOOBW/List-of-Dirty-Naughty-Obscene-and-Otherwise-Bad-Words”
- https://github.com/jcpeterson/openwebtext13 _[verified]_
  > p. 27: “Table 8: 12. https://github.com/jcpeterson/openwebtext13. https://www.tensorflow.org/datasets/catalog/wikipediaPerformance resulting from pre-training on different data sets.The first four variants are based on our new C4 data set.produced a SuperGLUE score of 73.24, beating our baseline's score (using C4) of 71.36.This is almost entirely attributable to a boost in performance from 25.78 (baseline, C4) to 50.93 (Wikipedia + TBC) on the Exact Match score for MultiRC (see Table 16).MultiRC is a reading comprehension data set whose largest source of data comes from fiction books, which is exactly the domain covered by TBC.Similarly, using the RealNews-like data set for pre-training conferred an increase from 68.16 to 73.72 on the Exact Match score for ReCoRD, a data set that measures reading comprehension on news articles.As a final example, using data from Wikipedia produced significant (but less dramatic) gains on SQuAD, which is a question-answering data set with passages sourced from Wikipedia.”
- https://github.com/google-research/bert/blob/master/multilingual.md _[verified]_
  > p. 31: “https://github.com/google-research/bert/blob/master/multilingual.md”


## 2003.10555

# ELECTRA: PRE-TRAINING TEXT ENCODERS AS DISCRIMINATORS RATHER THAN GENERATORS

Kevin Clark, Minh-Thang Luong, Quoc V Le, Christopher D Manning
2020 · arXiv:2003.10555v1[cs.CL]

## Problem

- Masked language modeling methods generally require large amounts of compute to be effective. _[verified]_
  > p. 1: “While they produce good results when transferred to downstream NLP tasks, they generally require large amounts of compute to be effective.”
- Current pre-training methods incur a substantial compute cost because the network only learns from 15% of the tokens per example. _[verified]_
  > p. 1: “While more effective than conventional language-model pre-training due to learning bidirectional representations, these masked language modeling (MLM) approaches incur a substantial compute cost because the network only learns from 15% of the tokens per example.”
- Current pre-training methods raise concerns about their cost and accessibility due to large compute requirements. _[verified]_
  > p. 2: “Most current pre-training methods require large amounts of compute to be effective, raising concerns about their cost and accessibility.”

## Task

- language representation learning and downstream NLP tasks _[verified]_
  > p. 1: “While they produce good results when transferred to downstream NLP tasks, they generally require large amounts of compute to be effective.”

## Contributions

- We propose a more sample-efficient pre-training task called replaced token detection. _[verified]_
  > p. 1: “As an alternative, we propose a more sample-efficient pre-training task called replaced token detection.”
- We call our approach ELECTRA for Efficiently Learning an Encoder that Classifies Token Replacements Accurately. _[partial]_
  > p. 2: “We call our approach ELECTRAfoot_0 for "Efficiently Learning an Encoder that Classifies Token Replacements Accurately."”

## Method

- The approach trains a generator G and a discriminator D jointly, where the generator produces a distribution over tokens using a masked language model. _[verified]_
  > p. 3: “The generator can be any model that produces an output distribution over tokens, but we usually use a small masked language model that is trained jointly with the discriminator.”
- The generator is trained with maximum likelihood to perform masked language modeling by predicting original identities of masked-out tokens. _[partial]_
  > p. 3: “The generator is trained to perform masked language modeling (MLM).”
- The discriminator is trained to distinguish whether tokens in a corrupted example match the original input data or were replaced by generator samples. _[verified]_
  > p. 3: “The discriminator is trained to distinguish tokens in the data from tokens that have been replaced by generator samples.”
- The combined loss function of MLM loss and discriminator loss is minimized over a large corpus of raw text, and the generator is discarded after pre-training. _[partial]_
  > p. 3: “After pre-training, we throw out the generator and only fine-tune the discriminator (the ELECTRA model) on downstream tasks.”

## Datasets

- General Language Understanding Evaluation (GLUE) _[verified]_
  > p. 4: “We evaluate on the General Language Understanding Evaluation (GLUE) benchmark (Wang et al., 2019) and Stanford Question Answering (SQuAD) dataset (Rajpurkar et al., 2016).”
- Stanford Question Answering (SQuAD) (1.1, 2.0) _[verified]_
  > p. 4: “We evaluate on the General Language Understanding Evaluation (GLUE) benchmark (Wang et al., 2019) and Stanford Question Answering (SQuAD) dataset (Rajpurkar et al., 2016).”
- Wikipedia and BooksCorpus (3.3 Billion tokens) _[verified]_
  > p. 4: “For most experiments we pre-train on the same data as BERT, which consists of 3.3 Billion tokens from Wikipedia and BooksCorpus (Zhu et al., 2015).”
- XLNet pre-training data (33B tokens) _[verified]_
  > p. 4: “However, for our Large model we pre-trained on the data used for XLNet (Yang et al., 2019), which extends the BERT dataset to 33B tokens by including data from ClueWeb (Callan et al., 2009), CommonCrawl, and Gigaword (Parker et al., 2011).”

## Baselines

- BERT _[verified]_
  > p. 6: “In addition to BERT, we compare against two less resource-intensive pre-training methods based on language modeling: ELMo (Peters et al., 2018) and GPT (Radford et al., 2018).”
- ELMo _[verified]_
  > p. 6: “In addition to BERT, we compare against two less resource-intensive pre-training methods based on language modeling: ELMo (Peters et al., 2018) and GPT (Radford et al., 2018).”
- GPT _[verified]_
  > p. 6: “In addition to BERT, we compare against two less resource-intensive pre-training methods based on language modeling: ELMo (Peters et al., 2018) and GPT (Radford et al., 2018).”
- RoBERTa _[unsupported]_
  > p. 7: “Our ELECTRA-Large models are the same size as BERT-Large but are trained for much longer.”
- XLNet _[unsupported]_
  > p. 7: “We use a batch size 2048 and the XLNet pre-training data.”
- SpanBERT _[verified]_
  > p. 8: “SpanBERT | 7.1e20 (1x) | 335M | 88.8 | 94.6 | 85.7 | 88.7 | 85.7 | 88.7”
- ALBERT _[verified]_
  > p. 7: “ALBERT | 3.1e22 (10x) | 69.1 | 97.1 | 91.2 | 92.0 | 90.5 | 91.3 | – | 89.2 | 91.8 | 89.0 | –”

## Metrics

- Spearman correlation _[verified]_
  > p. 4: “Our evaluation metrics are Spearman correlation for STS, Matthews correlation for CoLA, and accuracy for the other GLUE tasks; we generally report the average score over all tasks.”
- Matthews correlation _[verified]_
  > p. 4: “Our evaluation metrics are Spearman correlation for STS, Matthews correlation for CoLA, and accuracy for the other GLUE tasks; we generally report the average score over all tasks.”
- accuracy _[verified]_
  > p. 4: “Our evaluation metrics are Spearman correlation for STS, Matthews correlation for CoLA, and accuracy for the other GLUE tasks; we generally report the average score over all tasks.”
- Exact-Match (EM) _[verified]_
  > p. 4: “We use the standard evaluation metrics of Exact-Match (EM) and F1 scores.”
- F1 score _[verified]_
  > p. 4: “We use the standard evaluation metrics of Exact-Match (EM) and F1 scores.”

## Hyperparameters

- sequence length (pre-training): 128 _[verified]_
  > p. 6: “Starting with the BERT-Base hyperparameters, we shortened the sequence length (from 512 to 128), reduced the batch size (from 256 to 128), reduced the model's hidden dimension size (from 768 to 256), and used smaller token embeddings (from 768 to 128).”
- batch size (pre-training): 128 _[verified]_
  > p. 6: “Starting with the BERT-Base hyperparameters, we shortened the sequence length (from 512 to 128), reduced the batch size (from 256 to 128), reduced the model's hidden dimension size (from 768 to 256), and used smaller token embeddings (from 768 to 128).”
- hidden dimension size (pre-training): 256 _[verified]_
  > p. 6: “Starting with the BERT-Base hyperparameters, we shortened the sequence length (from 512 to 128), reduced the batch size (from 256 to 128), reduced the model's hidden dimension size (from 768 to 256), and used smaller token embeddings (from 768 to 128).”
- token embeddings (pre-training): 128 _[verified]_
  > p. 6: “Starting with the BERT-Base hyperparameters, we shortened the sequence length (from 512 to 128), reduced the batch size (from 256 to 128), reduced the model's hidden dimension size (from 768 to 256), and used smaller token embeddings (from 768 to 128).”
- training steps (pre-training): 1.5M _[verified]_
  > p. 6: “We train BERT-Small for 1.5M steps, so it uses the same training FLOPs as ELECTRA-Small, which was trained for 1M steps. 5”
- training steps (pre-training): 1M _[verified]_
  > p. 6: “We train BERT-Small for 1.5M steps, so it uses the same training FLOPs as ELECTRA-Small, which was trained for 1M steps. 5”
- training steps (pre-training): 400k _[verified]_
  > p. 7: “In particular, we train a model for 400k steps (ELECTRA-400K; roughly 1/4 the pre-training compute of RoBERTa) and one for 1.75M steps (ELECTRA-1.75M; similar compute to RoBERTa).”
- training steps (pre-training): 1.75M _[verified]_
  > p. 7: “In particular, we train a model for 400k steps (ELECTRA-400K; roughly 1/4 the pre-training compute of RoBERTa) and one for 1.75M steps (ELECTRA-1.75M; similar compute to RoBERTa).”
- batch size (pre-training): 2048 _[verified]_
  > p. 7: “We use a batch size 2048 and the XLNet pre-training data.”
- masked token percentage (pre-training): 15% _[verified]_
  > p. 3: “Typically k = 0.15n , i.e., 15% of the tokens are masked out.”
- training steps (pre-training): 500k _[verified]_
  > p. 4: “We train these models for 500k steps.”
- training steps (pre-training): 4e6 _[verified]_
  > p. 15: “Furthermore, we push the limits of base-sized and small-sized models by training them on the XLNet data instead of wikibooks and for much longer (4e6 train steps); these models are called ELECTRA-Base++ and ELECTRA-Small++ in the table.”

## Compute

- single GPU for small model training _[verified]_
  > p. 6: “As a goal of this work is to improve the efficiency of pre-training, we develop a small model that can be quickly trained on a single GPU.”
- training time for ELMo _[verified]_
  > p. 6: “ELMo | 3.3e18 / 2.6e10 | 19x / 1.2x | 96M | 14d on 3 GTX 1080 GPUs | 71.2”
- training time for GPT _[verified]_
  > p. 6: “GPT | 4.0e19 / 3.0e10 | 1.6x / 0.97x | 117M | 25d on 8 P6000 GPUs | 78.8”
- training time for BERT-Small _[verified]_
  > p. 6: “BERT-Small | 1.4e18 / 3.7e9 | 45x / 8x | 14M | 4d on 1 V100 GPU | 75.1”
- training time for BERT-Base _[verified]_
  > p. 6: “BERT-Base | 6.4e19 / 2.9e10 | 1x / 1x | 110M | 4d on 16 TPUv3s | 82.2”
- training time for ELECTRA-Small _[verified]_
  > p. 6: “ELECTRA-Small | 1.4e18 / 3.7e9 | 45x / 8x | 14M | 4d on 1 V100 GPU | 79.9”
- training time for ELECTRA-Base _[verified]_
  > p. 6: “ELECTRA-Base | 6.4e19 / 2.9e10 | 1x / 1x | 110M | 4d on 16 TPUv3s | 85.1”

## Seeds and runs

- 10 fine-tuning runs from the same pre-training checkpoint _[verified]_
  > p. 4: “We therefore report the median of 10 fine-tuning runs from the same pre-trained checkpoint for each result.”
- ensemble the best 10 of 30 models fine-tuned with different random seeds _[verified]_
  > p. 14: “• For each task we ensemble the best 10 of 30 models fine-tuned with different random seeds but initialized from the same pre-trained checkpoint.”

## Ablations

- Weight Sharing strategies between generator and discriminator _[verified]_
  > p. 4: “We compare the weight tying strategies when the generator is the same size as the discriminator.”
- Different generator and discriminator sizes _[verified]_
  > p. 5: “GLUE scores for differently-sized generators and discriminators are shown in the left of Figure 3.”
- Training Algorithms including joint training, two-stage training, and adversarial training _[verified]_
  > p. 5: “Lastly, we explore other training algorithms for ELECTRA, although these did not end up improving results.”

## Claims

- ELECTRA-Small outperforms a comparably small BERT model by 5 points on GLUE and outperforms GPT. _[verified]_
  > p. 2: “2 ELECTRA-Small outperforms a comparably small BERT model by 5 points on GLUE, and even outperforms the much larger GPT model (Radford et al., 2018).”
- ELECTRA-Large performs comparably to RoBERTa and XLNet while using 1/4 of the compute. _[verified]_
  > p. 2: “Our approach also works well at large scale, where we train an ELECTRA-Large model that performs comparably to RoBERTa (Liu et al., 2019) and XLNet (Yang et al., 2019), despite having fewer parameters and using 1/4 of the compute for training.”
- ELECTRA-Large outperforms ALBERT on GLUE and sets a new state-of-the-art for SQuAD 2.0. _[verified]_
  > p. 2: “Training ELECTRA-Large further results in an even stronger model that outperforms ALBERT (Lan et al., 2019) on GLUE and sets a new state-of-the-art for SQuAD 2.0.”

## Limitations

- More analysis is required to fully explain the parameter efficiency of ELECTRA. _[verified]_
  > p. 9: “We speculate that ELECTRA is more parameter-efficient than BERT because it does not have to model the full distribution of possible tokens at each position, but we believe more analysis is needed to completely explain ELECTRA's parameter efficiency.”

## Future work

- Future NLP pre-training research should consider efficiency alongside absolute performance and report compute usage and parameter counts. _[verified]_
  > p. 10: “We also hope more future work on NLP pre-training will consider efficiency as well as absolute performance, and follow our effort in reporting compute usage and parameter counts along with evaluation metrics.”
- Comparing MLM predictions of BERT and ELECTRA could be an interesting way to understand the differences between their encoders in future research. _[verified]_
  > p. 18: “We think comparisons of BERT's and ELECTRA's MLM predictions might be an interesting way to uncover more about the differences between ELECTRA and BERT encoders in future work.”

## Code

- https://github.com/google-research/ _[verified]_
  > p. 2: “Code and pre-trained weights will be released at https://github.com/google-research/ electra”


## 2104.08821

# SimCSE: Simple Contrastive Learning of Sentence Embeddings

Tianyu Gao, Xingcheng Yao, Danqi Chen

## Problem

- Pre-trained word embeddings suffer from anisotropy issues. _[verified]_
  > p. 2: “We also draw a connection to the recent findings that pre-trained word embeddings suffer from anisotropy (Ethayarajh, 2019;Li et al., 2020) and prove that-through a spectrum perspective-the contrastive learning objective "flattens" the singular value distribution of the sentence embedding space, hence improving uniformity.”

## Task

- Learning universal sentence embeddings and evaluating on semantic textual similarity tasks. _[partial]_
  > p. 1: “Learning universal sentence embeddings is a fundamental problem in natural language processing and has been studied extensively in the literature (Kiros et al., 2015;Hill et al., 2016;Conneau et al., 2017;Logeswaran and Lee, 2018;Cer et al., 2018;Reimers and Gurevych, 2019, inter alia).”

## Contributions

- We present SimCSE, a simple contrastive learning framework that advances state-of-the-art sentence embeddings. _[verified]_
  > p. 1: “This paper presents SimCSE, a simple contrastive learning framework that greatly advances state-of-the-art sentence embeddings.”
- We describe an unsupervised approach using standard dropout as noise. _[verified]_
  > p. 1: “We first describe an unsupervised approach, which takes an input sentence and predicts itself in a contrastive objective, with only standard dropout used as noise.”
- We propose a supervised approach incorporating natural language inference datasets into contrastive learning. _[verified]_
  > p. 1: “Then, we propose a supervised approach, which incorporates annotated pairs from natural language inference datasets into our contrastive learning framework by using "entailment" pairs as positives and "contradiction" pairs as hard negatives.”

## Method

- Sentences are encoded using a pre-trained language model such as BERT or RoBERTa. _[verified]_
  > p. 2: “In this work, we encode input sentences using a pre-trained language model such as BERT (Devlin et al., 2019) or RoBERTa (Liu et al., 2019): h = f θ (x), and then fine-tune all the parameters using the contrastive learning objective (Eq. 1).”
- Unsupervised SimCSE uses identical sentences as positive pairs, relying on independently sampled standard dropout masks in Transformers as noise. _[partial]_
  > p. 3: “The idea of unsupervised SimCSE is extremely simple: we take a collection of sentences {x i } m i=1 and use x + i = x i .”
- Supervised SimCSE leverages entailment pairs from NLI datasets as positive examples and incorporates contradiction pairs as hard negatives. _[verified]_
  > p. 5: “Formally, we extend (x i , x + i ) to (x i , x + i , x - i ) , where x i is the premise, x + i and x - i are entailment and contradiction hypotheses.”

## Novelty

- Using standard dropout on intermediate representations outperforms discrete data augmentation operators in NLP contrastive learning. _[verified]_
  > p. 2: “As we will see in §3, simply using standard dropout on intermediate representations outperforms these discrete operators.”

## Datasets

- STS tasks (STS 2012-2016, STS Benchmark, SICK-Relatedness) _[verified]_
  > p. 6: “We evaluate on 7 STS tasks: STS 2012-2016 (Agirre et al., 2012(Agirre et al., , 2013(Agirre et al., , 2014(Agirre et al., , 2015(Agirre et al., , 2016)), STS Benchmark (Cer et al., 2017) and SICK-Relatedness (Marelli et al., 2014).”
- English Wikipedia (10 6) _[verified]_
  > p. 6: “We train unsupervised SimCSE on 10 6 randomly sampled sentences from English Wikipedia, and train supervised SimCSE on the combination of MNLI and SNLI datasets (314k).”
- MNLI and SNLI datasets (314k) _[verified]_
  > p. 6: “We train unsupervised SimCSE on 10 6 randomly sampled sentences from English Wikipedia, and train supervised SimCSE on the combination of MNLI and SNLI datasets (314k).”
- QQP (134k) _[partial]_
  > p. 5: “QQP (134k) | 81.8 | 81.8”
- Flickr30k (318k) _[partial]_
  > p. 5: “Flickr30k (318k) | 81.5 | 81.4”
- ParaNMT (5m) _[partial]_
  > p. 5: “ParaNMT (5m) | 79.7 | 78.7”
- ANLI (52k) _[partial]_
  > p. 5: “+ ANLI (52k) | - | 85.0”

## Baselines

- Average GloVe embeddings _[verified]_
  > p. 7: “Unsupervised baselines include average GloVe embeddings (Pennington et al., 2014), average BERT or RoBERTa embeddings 10 , and post-processing methods such as BERT-flow (Li et al., 2020) and BERTwhitening (Su et al., 2021).”
- Average BERT or RoBERTa embeddings _[verified]_
  > p. 7: “Unsupervised baselines include average GloVe embeddings (Pennington et al., 2014), average BERT or RoBERTa embeddings 10 , and post-processing methods such as BERT-flow (Li et al., 2020) and BERTwhitening (Su et al., 2021).”
- BERT-flow _[verified]_
  > p. 7: “Unsupervised baselines include average GloVe embeddings (Pennington et al., 2014), average BERT or RoBERTa embeddings 10 , and post-processing methods such as BERT-flow (Li et al., 2020) and BERTwhitening (Su et al., 2021).”
- BERTwhitening _[verified]_
  > p. 7: “Unsupervised baselines include average GloVe embeddings (Pennington et al., 2014), average BERT or RoBERTa embeddings 10 , and post-processing methods such as BERT-flow (Li et al., 2020) and BERTwhitening (Su et al., 2021).”
- IS-BERT _[verified]_
  > p. 7: “We also compare to several recent methods using a contrastive objective, including 1) IS-BERT (Zhang et al., 2020), which maximizes the agreement between global and local features; 2) DeCLUTR (Giorgi et al., 2021), which takes different spans from the same document as positive pairs; 3) CT (Carlsson et al., 2021), which aligns embeddings of the same sentence from two different encoders.”
- DeCLUTR _[verified]_
  > p. 7: “We also compare to several recent methods using a contrastive objective, including 1) IS-BERT (Zhang et al., 2020), which maximizes the agreement between global and local features; 2) DeCLUTR (Giorgi et al., 2021), which takes different spans from the same document as positive pairs; 3) CT (Carlsson et al., 2021), which aligns embeddings of the same sentence from two different encoders.”
- CT _[verified]_
  > p. 7: “We also compare to several recent methods using a contrastive objective, including 1) IS-BERT (Zhang et al., 2020), which maximizes the agreement between global and local features; 2) DeCLUTR (Giorgi et al., 2021), which takes different spans from the same document as positive pairs; 3) CT (Carlsson et al., 2021), which aligns embeddings of the same sentence from two different encoders.”
- InferSent _[verified]_
  > p. 7: “Other supervised 10 Following Su et al. (2021), we take the average of the first and the last layers, which is better than only taking the last. 11 We do not compare to CLEAR (Wu et al., 2020), because they use their own version of pre-trained models, and the numbers appear to be much lower. Also note that CT is a concurrent work to ours. methods include InferSent (Conneau et al., 2017), Universal Sentence Encoder (Cer et al., 2018), and SBERT/SRoBERTa (Reimers and Gurevych, 2019) with post-processing methods (BERT-flow, whitening, and CT).”
- Universal Sentence Encoder _[verified]_
  > p. 7: “Other supervised 10 Following Su et al. (2021), we take the average of the first and the last layers, which is better than only taking the last. 11 We do not compare to CLEAR (Wu et al., 2020), because they use their own version of pre-trained models, and the numbers appear to be much lower. Also note that CT is a concurrent work to ours. methods include InferSent (Conneau et al., 2017), Universal Sentence Encoder (Cer et al., 2018), and SBERT/SRoBERTa (Reimers and Gurevych, 2019) with post-processing methods (BERT-flow, whitening, and CT).”
- SBERT/SRoBERTa _[verified]_
  > p. 7: “Other supervised 10 Following Su et al. (2021), we take the average of the first and the last layers, which is better than only taking the last. 11 We do not compare to CLEAR (Wu et al., 2020), because they use their own version of pre-trained models, and the numbers appear to be much lower. Also note that CT is a concurrent work to ours. methods include InferSent (Conneau et al., 2017), Universal Sentence Encoder (Cer et al., 2018), and SBERT/SRoBERTa (Reimers and Gurevych, 2019) with post-processing methods (BERT-flow, whitening, and CT).”

## Metrics

- Spearman's correlation _[verified]_
  > p. 13: “For all of our experiments, we report Spearman's rank correlation.”

## Hyperparameters

- epochs (supervised Sim-CSE): 3 _[verified]_
  > p. 13: “For supervised Sim-CSE, we train our models for 3 epochs, evaluate the model every 250 training steps on the development set of STS-B and keep the best checkpoint for the final evaluation on test sets.”
- epochs (unsupervised SimCSE): one _[verified]_
  > p. 13: “We do the same for the unsupervised SimCSE, except that we train the model for one epoch.”
- batch size: {64, 128, 256, 512} _[verified]_
  > p. 13: “We carry out grid-search of batch size ∈ {64, 128, 256, 512} and learning rate ∈ {1e-5, 3e-5, 5e-5} on STS-B development set and adopt the hyperparameter settings in Table A.1.”
- learning rate: {1e-5, 3e-5, 5e-5} _[verified]_
  > p. 13: “We carry out grid-search of batch size ∈ {64, 128, 256, 512} and learning rate ∈ {1e-5, 3e-5, 5e-5} on STS-B development set and adopt the hyperparameter settings in Table A.1.”
- temperature: 0.05 _[verified]_
  > p. 15: “As shown in Table D.1, with a carefully tuned temperature τ = 0.05, cosine similarity is better than dot product.”

## Ablations

- Impact of different pooling methods and hard negatives _[verified]_
  > p. 8: “We investigate the impact of different pooling methods and hard negatives.”
- Ablation studies of normalization, temperature, and MLM objectives _[verified]_
  > p. 8: “We provide more ablation studies (normalization, temperature, and MLM objectives) in Appendix D.”

## Claims

- Unsupervised and supervised BERT base models achieve high average Spearman's correlation on STS tasks representing improvements over previous best results. _[verified]_
  > p. 1: “We evaluate SimCSE on standard semantic textual similarity (STS) tasks, and our unsupervised and supervised models using BERT base achieve an average of 76.3% and 81.6% Spearman's correlation respectively, a 4.2% and 2.2% improvement compared to the previous best results.”

## Future work

- Call for unifying evaluation settings for sentence embeddings in future research _[verified]_
  > p. 14: “We call for unifying the setting in evaluating sentence embeddings for future research.”

## Code

- https://github.com/princeton-nlp/SimCSE _[verified]_
  > p. 1: “* The first two authors contributed equally (listed in alphabetical order).This work was done when Xingcheng visited the Princeton NLP group remotely.1Our code and pre-trained models are publicly available at https://github.com/princeton-nlp/SimCSE.”
- https://github.com/huggingface/ _[verified]_
  > p. 14: “https://github.com/huggingface/ transformers”
- https://github.com/facebookresearch/ _[verified]_
  > p. 15: “https://github.com/facebookresearch/ SentEval”


## 2005.11401

# Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks

Patrick Lewis, Ethan Perez, Aleksandra Piktus, Fabio Petroni, Vladimir Karpukhin, Naman Goyal, Heinrich Küttler, Mike Lewis, Wen-Tau Yih, Tim Rocktäschel, Sebastian Riedel, Douwe Kiela
2021 · arXiv:2005.11401v4[cs.CL]

## Problem

- Large language models struggle with precise knowledge access and manipulation on knowledge-intensive tasks. _[verified]_
  > p. 1: “However, their ability to access and precisely manipulate knowledge is still limited, and hence on knowledge-intensive tasks, their performance lags behind task-specific architectures.”
- Pretrained models cannot easily revise memory, provide provenance, or avoid hallucinations. _[verified]_
  > p. 1: “They cannot easily expand or revise their memory, can't straightforwardly provide insight into their predictions, and may produce "hallucinations" [38].”

## Task

- knowledge-intensive NLP tasks _[verified]_
  > p. 1: “We fine-tune and evaluate our models on a wide range of knowledgeintensive NLP tasks and set the state of the art on three open domain QA tasks, outperforming parametric seq2seq models and task-specific retrieve-and-extract architectures.”
- open-domain extractive question answering _[partial]_
  > p. 1: “REALM [20] and ORQA [31], two recently introduced models that combine masked language models [8] with a differentiable retriever, have shown promising results, Figure 1: Overview of our approach. We combine a pre-trained retriever (Query Encoder + Document Index) with a pre-trained seq2seq model (Generator) and fine-tune end-to-end. For query x, we use Maximum Inner Product Search (MIPS) to find the top-K documents z i . For final prediction y, we treat z as a latent variable and marginalize over seq2seq predictions given different documents. but have only explored open-domain extractive question answering.”

## Contributions

- Introduction of retrieval-augmented generation (RAG) models combining parametric and non-parametric memory. _[verified]_
  > p. 1: “We introduce RAG models where the parametric memory is a pre-trained seq2seq model and the non-parametric memory is a dense vector index of Wikipedia, accessed with a pre-trained neural retriever.”
- Proposal of two RAG formulations conditioning on retrieved passages per-sequence or per-token. _[verified]_
  > p. 1: “We compare two RAG formulations, one which conditions on the same retrieved passages across the whole generated sequence, and another which can use different passages per token.”

## Datasets

- Wikipedia (21M documents) _[partial]_
  > p. 4: “For all experiments, we use a single Wikipedia dump for our non-parametric knowledge source.”
- Natural Questions (NQ) _[verified]_
  > p. 4: “We consider four popular open-domain QA datasets: Natural Questions (NQ) [29], TriviaQA (TQA) [24].”
- TriviaQA (TQA) _[verified]_
  > p. 4: “We consider four popular open-domain QA datasets: Natural Questions (NQ) [29], TriviaQA (TQA) [24].”
- WebQuestions (WQ) _[verified]_
  > p. 4: “WebQuestions (WQ) [3] and CuratedTrec (CT) [2].”
- CuratedTrec (CT) _[verified]_
  > p. 4: “WebQuestions (WQ) [3] and CuratedTrec (CT) [2].”
- MSMARCO NLG task v2.1 _[verified]_
  > p. 4: “To test RAG's natural language generation (NLG) in a knowledge-intensive setting, we use the MSMARCO NLG task v2.1 [43].”
- SearchQA (100K train, 14K dev, and 27K test, 100K train, 14K dev, and 27K test examples) _[verified]_
  > p. 5: “We use the splits from SearchQA [10], with 100K train, 14K dev, and 27K test examples.”
- FEVER _[partial]_
  > p. 5: “FEVER [56] requires classifying whether a natural language claim is supported or refuted by Wikipedia, or whether there is not enough information to decide.”

## Baselines

- Extractive QA paradigm _[verified]_
  > p. 4: “We compare RAG to the popular extractive QA paradigm [5,7,31,26], where answers are extracted spans from retrieved documents, relying primarily on non-parametric knowledge.”
- Closed-Book QA approaches _[verified]_
  > p. 4: “We also compare to "Closed-Book QA" approaches [52], which, like RAG, generate answers, but which do not exploit retrieval, instead relying purely on parametric knowledge.”
- BART model for comparison on Jeopardy _[verified]_
  > p. 5: “As this is a new task, we train a BART model for comparison.”
- DPR QA system _[verified]_
  > p. 5: “RAG compares favourably to the DPR QA system, which uses a BERT-based "crossencoder" to re-rank documents, along with an extractive reader.”
- Thorne and Vlachos 2-way FEVER model _[verified]_
  > p. 7: “For 2-way classification, we compare against Thorne and Vlachos [57], who train RoBERTa [35] to classify the claim as true or false given the gold evidence sentence.”
- BART-large model _[verified]_
  > p. 17: “For Open-MSMarco and Jeopardy question generation, we report test numbers using ten retrieved documents for both RAG-Token and RAG-Sequence, and we also train a BART-large model as a baseline.”

## Metrics

- Exact Match (EM) _[verified]_
  > p. 4: “We use the same train/dev/test splits as prior work [31,26] and report Exact Match (EM) scores.”
- SQuAD-tuned Q-BLEU-1 _[verified]_
  > p. 5: “Following [67], we evaluate using the SQuAD-tuned Q-BLEU-1 metric [42].”
- Label accuracy for FEVER _[verified]_
  > p. 5: “In both cases we report label accuracy.”
- Rouge-L _[verified]_
  > p. 6: “RAG-Sequence outperforms BART on Open MS-MARCO NLG by 2.6 Bleu points and 2.6 Rouge-L points.”
- Ratio of distinct ngrams to total ngrams _[verified]_
  > p. 7: “Following recent work on diversity-promoting decoding [33,59,39], we also investigate generation diversity by calculating the ratio of distinct ngrams to total ngrams generated by different models.”

## Hyperparameters

- k (retrieved documents) (training): {5, 10} _[verified]_
  > p. 4: “We consider k ∈ {5, 10} for training and set k for test time using dev data.”
- retrieved documents (test time): 15 _[verified]_
  > p. 17: “For Open-domain QA we report test numbers using 15 retrieved documents for RAG-Token models.”
  > p. 17: “For Open-MSMarco and Jeopardy question generation, we report test numbers using ten retrieved documents for both RAG-Token and RAG-Sequence, and we also train a BART-large model as a baseline.”
- retrieved documents (test time): 50 _[verified]_
  > p. 17: “For RAG-Sequence models, we report test results using 50 retrieved documents, and we use the Thorough Decoding approach since answers are generally short.”
- beam size: four _[verified]_
  > p. 17: “We use a beam size of four, and use the Fast Decoding approach for RAG-Sequence models, as Thorough Decoding did not improve performance.”

## Compute

- Hardware and precision setup using 8 NVIDIA V100 GPUs _[verified]_
  > p. 17: “We train with mixed precision floating point arithmetic [40], distributing training across 8, 32GB NVIDIA V100 GPUs, though training and inference can be run on one GPU.”
- CPU memory required for FAISS index _[verified]_
  > p. 17: “We find that doing Maximum Inner Product Search with FAISS is sufficiently fast on CPU, so we store document index vectors on CPU, requiring ∼ 100 GB of CPU memory for all of Wikipedia.”

## Ablations

- Freezing the retriever during training _[verified]_
  > p. 7: “To assess the effectiveness of the retrieval mechanism, we run ablations where we freeze the retriever during training.”
- Replacing dense retriever with BM25 word-overlap retriever _[verified]_
  > p. 7: “Here, we replace RAG's retriever with a fixed BM25 system, and use BM25 retrieval scores as logits when calculating p(z|x).”

## Claims

- RAG models set state-of-the-art results on three open domain QA tasks. _[verified]_
  > p. 1: “We fine-tune and evaluate our models on a wide range of knowledgeintensive NLP tasks and set the state of the art on three open domain QA tasks, outperforming parametric seq2seq models and task-specific retrieve-and-extract architectures.”
- Fact verification results are achieved within 4.3% of the state-of-the-art pipeline models. _[verified]_
  > p. 2: “For FEVER [56] fact verification, we achieve results within 4.3% of state-of-the-art pipeline models which use strong retrieval supervision.”

## Limitations

- External knowledge sources like Wikipedia may contain biases and are not entirely factual _[verified]_
  > p. 10: “With these advantages also come potential downsides: Wikipedia, or any potential external knowledge source, will probably never be entirely factual and completely devoid of bias.”

## Future work

- Investigate jointly pre-training the components from scratch using a denoising objective or similar approach _[verified]_
  > p. 9: “In future work, it may be fruitful to investigate if the two components can be jointly pre-trained from scratch, either with a denoising objective similar to BART or some another objective.”

## Ethics

- The model provides societal benefits by hallucinating less and offering more factual grounding, control, and interpretability _[verified]_
  > p. 10: “This work offers several positive societal benefits over previous work: the fact that it is more strongly grounded in real factual knowledge (in this case Wikipedia) makes it "hallucinate" less with generations that are more factual, and offers more control and interpretability.”
- Potential risks include generating abusive, faked, misleading content, impersonating others, or automating spam and job automation _[verified]_
  > p. 10: “Since RAG can be employed as a language model, similar concerns as for GPT-2 [50] are valid here, although arguably to a lesser extent, including that it might be used to generate abuse, faked or misleading content in the news or on social media; to impersonate others; or to automate the production of spam/phishing content [54].”

## Code

- https://github.com/huggingface/transformers/blob/master/examples/rag/ _[verified]_
  > p. 2: “Code to run experiments with RAG has been open-sourced as part of the HuggingFace Transformers Library[66] and can be found at https://github.com/huggingface/transformers/blob/master/ examples/rag/.An interactive demo of RAG models can be found at https://huggingface.co/rag/”
- https://huggingface.co/rag/ _[verified]_
  > p. 2: “Code to run experiments with RAG has been open-sourced as part of the HuggingFace Transformers Library[66] and can be found at https://github.com/huggingface/transformers/blob/master/ examples/rag/.An interactive demo of RAG models can be found at https://huggingface.co/rag/”
- https://github.com/pytorch/fairseq _[verified]_
  > p. 17: “https://github.com/pytorch/fairseq”
- https://github.com/huggingface/transformers _[verified]_
  > p. 17: “https://github.com/huggingface/transformers”


## 2201.11903

# Chain-of-Thought Prompting Elicits Reasoning in Large Language Models

Jason Wei, Xuezhi Wang, Dale Schuurmans, Maarten Bosma, Brian Ichter, Fei Xia, Ed H Chi Quoc, V Le, Denny Zhou
2023 · arXiv:2201.11903v6[cs.CL]

## Problem

- Large language models struggle with complex reasoning tasks. _[verified]_
  > p. 1: “We explore how generating a chain of thought-a series of intermediate reasoning steps-significantly improves the ability of large language models to perform complex reasoning.”

## Task

- Arithmetic, commonsense, and symbolic reasoning tasks. _[verified]_
  > p. 1: “Experiments on three large language models show that chain-of-thought prompting improves performance on a range of arithmetic, commonsense, and symbolic reasoning tasks.”

## Contributions

- Introducing chain-of-thought prompting to improve reasoning capabilities in large language models. _[verified]_
  > p. 1: “In particular, we show how such reasoning abilities emerge naturally in sufficiently large language models via a simple method called chain-ofthought prompting, where a few chain of thought demonstrations are provided as exemplars in prompting.”

## Datasets

- GSM8K _[verified]_
  > p. 3: “We consider the following five math word problem benchmarks: (1) the GSM8K benchmark of math word problems (Cobbe et al., 2021), (2) the SVAMP dataset of math word problems with varying structures (Patel et al., 2021), (3) the ASDiv dataset of diverse math word problems (Miao et al., 2020), (4) the AQuA dataset of algebraic word problems, and (5) the MAWPS benchmark (Koncel-Kedziorski et al., 2016).”
- SVAMP _[verified]_
  > p. 3: “We consider the following five math word problem benchmarks: (1) the GSM8K benchmark of math word problems (Cobbe et al., 2021), (2) the SVAMP dataset of math word problems with varying structures (Patel et al., 2021), (3) the ASDiv dataset of diverse math word problems (Miao et al., 2020), (4) the AQuA dataset of algebraic word problems, and (5) the MAWPS benchmark (Koncel-Kedziorski et al., 2016).”
- ASDiv _[verified]_
  > p. 3: “We consider the following five math word problem benchmarks: (1) the GSM8K benchmark of math word problems (Cobbe et al., 2021), (2) the SVAMP dataset of math word problems with varying structures (Patel et al., 2021), (3) the ASDiv dataset of diverse math word problems (Miao et al., 2020), (4) the AQuA dataset of algebraic word problems, and (5) the MAWPS benchmark (Koncel-Kedziorski et al., 2016).”
- AQuA _[verified]_
  > p. 3: “We consider the following five math word problem benchmarks: (1) the GSM8K benchmark of math word problems (Cobbe et al., 2021), (2) the SVAMP dataset of math word problems with varying structures (Patel et al., 2021), (3) the ASDiv dataset of diverse math word problems (Miao et al., 2020), (4) the AQuA dataset of algebraic word problems, and (5) the MAWPS benchmark (Koncel-Kedziorski et al., 2016).”
- MAWPS _[verified]_
  > p. 3: “We consider the following five math word problem benchmarks: (1) the GSM8K benchmark of math word problems (Cobbe et al., 2021), (2) the SVAMP dataset of math word problems with varying structures (Patel et al., 2021), (3) the ASDiv dataset of diverse math word problems (Miao et al., 2020), (4) the AQuA dataset of algebraic word problems, and (5) the MAWPS benchmark (Koncel-Kedziorski et al., 2016).”
- CSQA _[verified]_
  > p. 7: “The popular CSQA (Talmor et al., 2019) asks commonsense questions about the world involving complex semantics that often require prior knowledge.”
- StrategyQA _[verified]_
  > p. 7: “StrategyQA (Geva et al., 2021) requires models to infer a multi-hop strategy to answer questions.”
- Date Understanding _[verified]_
  > p. 7: “We choose two specialized evaluation sets from the BIG-bench effort (BIG-bench collaboration, 2021): Date Understanding, which involves inferring a date from a given context, and Sports Understanding, which involves determining whether a sentence relating to sports is plausible or implausible.”
- Sports Understanding _[verified]_
  > p. 7: “We choose two specialized evaluation sets from the BIG-bench effort (BIG-bench collaboration, 2021): Date Understanding, which involves inferring a date from a given context, and Sports Understanding, which involves determining whether a sentence relating to sports is plausible or implausible.”
- SayCan _[verified]_
  > p. 7: “Finally, the SayCan dataset (Ahn et al., 2022) involves mapping a natural language instruction to a sequence of robot actions from a discrete set.”

## Baselines

- Standard few-shot prompting _[verified]_
  > p. 3: “For the baseline, we consider standard few-shot prompting, popularized by Brown et al. (2020), in which a language model is given in-context exemplars of input-output pairs before outputting a prediction for a test-time example.”

## Seeds and runs

- Averaged results over five random seeds for LaMDA _[verified]_
  > p. 4: “For LaMDA, we report averaged results over five random seeds, where each seed had a different randomly shuffled order of exemplars.”
- Single exemplar order for all other models _[verified]_
  > p. 4: “As LaMDA experiments did not show large variance among different seeds, to save compute we report results for a single exemplar order for all other models.”

## Ablations

- Equation only prompting variation _[verified]_
  > p. 5: “One reason for why chain-of-thought prompting might help is that it produces the mathematical equation to be evaluated, and so we test a variation where the model is prompted to output only a mathematical equation before giving the answer.”
- Variable compute only variation using a sequence of dots _[verified]_
  > p. 6: “To isolate the effect of variable computation from chain-of-thought reasoning, we test a configuration where the model is prompted to output a only sequence of dots (. . .) equal to the number of characters in the equation needed to solve the problem.”
- Chain of thought after answer variation _[verified]_
  > p. 6: “Therefore, we test an alternative configuration where the chain of thought prompt is only given after the answer, isolating whether the model actually depends on the produced chain of thought to give the final answer.”

## Claims

- Prompting PaLM 540B with eight chain-of-thought exemplars achieves state-of-the-art accuracy on GSM8K. _[verified]_
  > p. 1: “For instance, prompting a PaLM 540B with just eight chain-of-thought exemplars achieves state-of-the-art accuracy on the GSM8K benchmark of math word problems, surpassing even finetuned GPT-3 with a verifier.”

## Limitations

- Emulating human thought processes does not prove that neural networks are actually reasoning. _[verified]_
  > p. 9: “As for limitations, we first qualify that although chain of thought emulates the thought processes of human reasoners, this does not answer whether the neural network is actually "reasoning," which we leave as an open question.”
- Manual annotation costs could become prohibitive when attempting to use chain of thought for finetuning. _[verified]_
  > p. 9: “Second, although the cost of manually augmenting exemplars with chains of thought is minimal in the few-shot setting, such annotation costs could be prohibitive for finetuning (though this could potentially be surmounted with synthetic data generation, or zero-shot generalization).”
- There is no absolute guarantee of correct reasoning paths, which can cause both correct and incorrect answers. _[verified]_
  > p. 9: “Third, there is no guarantee of correct reasoning paths, which can lead to both correct and incorrect answers; improving factual generations of language models is an open direction for future work (Rashkin et al., 2021;Ye and Durrett, 2022;Wiegreffe et al., 2022, inter alia).”
- Emergence of chain-of-thought reasoning only at large model scales makes real-world deployment costly. _[verified]_
  > p. 9: “Finally, the emergence of chain-of-thought reasoning only at large model scales makes it costly to serve in real-world applications; further research could explore how to induce reasoning in smaller models.”
- Performance gains from chain of thought did not transfer perfectly across all models. _[verified]_
  > p. 18: “The fact that gains from chain of thought did not transfer perfectly among models is a limitation; further work could investigate why how different pre-training datasets and model architectures affect the performance gain from chain-of-thought prompting.”
- Reasoning processes generated by large language models lack guarantees of factual correctness or coherence. _[verified]_
  > p. 28: “Overall, there are no guarantees that the reasoning processes generated by large language models are coherent or factually correct, as underscored by the recent work evaluating the factuality of language model generations and explanations (Maynez et al., 2020;Rashkin et al., 2021;Ye and Durrett, 2022;Marasović et al., 2022;Wiegreffe et al., 2022).”

## Future work

- Improve factual generations of language models. _[verified]_
  > p. 9: “Third, there is no guarantee of correct reasoning paths, which can lead to both correct and incorrect answers; improving factual generations of language models is an open direction for future work (Rashkin et al., 2021;Ye and Durrett, 2022;Wiegreffe et al., 2022, inter alia).”
- Explore how to induce reasoning in smaller models. _[verified]_
  > p. 9: “Finally, the emergence of chain-of-thought reasoning only at large model scales makes it costly to serve in real-world applications; further research could explore how to induce reasoning in smaller models.”
- Investigate how pre-training datasets and architectures affect chain-of-thought performance gains. _[verified]_
  > p. 18: “The fact that gains from chain of thought did not transfer perfectly among models is a limitation; further work could investigate why how different pre-training datasets and model architectures affect the performance gain from chain-of-thought prompting.”
- Examine how to generate chain of thought annotations robustly. _[verified]_
  > p. 18: “How to generate chain of thought annotations in a robust fashion could be an interesting direction for future work.”
- Evaluate chain-of-thought prompting empirically on diverse tasks where humans use chains of thought. _[verified]_
  > p. 19: “We leave the empirical evaluation of chain-of-thought prompting on such diverse tasks (e.g., machine translation, etc.) to future work.”
- Conduct an analysis of the factuality of generated chains of thought. _[verified]_
  > p. 26: “This is a limitation, and future work should perform an analysis of the factuality of such chains of thought.”

## Code

- https://github.com/google/BIG-bench/tree/main/bigbench/benchmark_tasks/strategyqa _[verified]_
  > p. 30: “Geva et al., 2021): we use the open-domain setting (question-only set) from BIG-bench collaboration (2021): https://github.com/google/BIG-bench/ tree/main/bigbench/benchmark_tasks/strategyqa.The original dataset is from https://github.com/eladsegal/strategyqa,MIT license: https://github.com/ eladsegal/strategyqa/blob/main/LICENSE.”
- https://github.com/eladsegal/strategyqa _[verified]_
  > p. 30: “Geva et al., 2021): we use the open-domain setting (question-only set) from BIG-bench collaboration (2021): https://github.com/google/BIG-bench/ tree/main/bigbench/benchmark_tasks/strategyqa.The original dataset is from https://github.com/eladsegal/strategyqa,MIT license: https://github.com/ eladsegal/strategyqa/blob/main/LICENSE.”
- https://github.com/eladsegal/strategyqa/blob/main/LICENSE _[verified]_
  > p. 30: “Geva et al., 2021): we use the open-domain setting (question-only set) from BIG-bench collaboration (2021): https://github.com/google/BIG-bench/ tree/main/bigbench/benchmark_tasks/strategyqa.The original dataset is from https://github.com/eladsegal/strategyqa,MIT license: https://github.com/ eladsegal/strategyqa/blob/main/LICENSE.”


## 2210.03629

# REAC T : SYNERGIZING REASONING AND ACTING IN LANGUAGE MODELS

Shunyu Yao, Jeffrey Zhao, Dian Yu, Nan Du, Izhak Shafran, Karthik Narasimhan, Yuan Cao
2023 · arXiv:2210.03629v3[cs.CL]

## Problem

- Reasoning and acting in large language models have primarily been studied separately. _[verified]_
  > p. 1: “While large language models (LLMs) have demonstrated impressive performance across tasks in language understanding and interactive decision making, their abilities for reasoning (e.g. chain-of-thought prompting) and acting (e.g. action plan generation) have primarily been studied as separate topics.”
- Chain-of-thought reasoning is a static black box ungrounded in the external world. _[verified]_
  > p. 2: “However, this "chain-of-thought" reasoning is a static black box, in that the model uses its own internal representations to generate thoughts and is not grounded in the external world, which limits its ability to reason reactively or update its knowledge.”
- Prior action-prediction approaches do not employ language models to perform abstract reasoning or maintain a working memory. _[verified]_
  > p. 2: “However, they do not employ language models to reason abstractly about high-level goals or maintain a working memory to support acting, barring Huang et al. (2022b) who perform a limited form of verbal reasoning to reiterate spatial facts about the current state.”

## Task

- question answering _[verified]_
  > p. 1: “Concretely, on question answering (HotpotQA) and fact verification (Fever), ReAct overcomes prevalent issues of hallucination and error propagation in chain-of-thought reasoning by interacting with a simple Wikipedia API, and generating human-like task-solving trajectories that are more interpretable than baselines without reasoning traces.”
- fact verification _[verified]_
  > p. 1: “Concretely, on question answering (HotpotQA) and fact verification (Fever), ReAct overcomes prevalent issues of hallucination and error propagation in chain-of-thought reasoning by interacting with a simple Wikipedia API, and generating human-like task-solving trajectories that are more interpretable than baselines without reasoning traces.”
- interactive decision making _[verified]_
  > p. 1: “Furthermore, on two interactive decision making benchmarks (ALFWorld and WebShop), ReAct outperforms imitation and reinforcement learning methods by an absolute success rate of 34% and 10% respectively, while being prompted with only one or two in-context examples.”

## Contributions

- Introduction of ReAct, a prompt-based paradigm combining reasoning and acting in language models. _[verified]_
  > p. 3: “(1) we introduce ReAct, a novel promptbased paradigm to synergize reasoning and acting in language models for general task solving;”
- Extensive experiments demonstrating ReAct's few-shot learning advantages over isolated reasoning or action generation. _[verified]_
  > p. 3: “(2) we perform extensive experiments across diverse benchmarks to showcase the advantage of ReAct in a few-shot learning setup over prior approaches that perform either reasoning or action generation in isolation;”
- Systematic ablations and analysis on the importance of acting in reasoning tasks and reasoning in interactive tasks. _[verified]_
  > p. 3: “(3) we present systematic ablations and analysis to understand the importance of acting in reasoning tasks, and reasoning in interactive tasks;”

## Datasets

- Hot-PotQA _[verified]_
  > p. 4: “(1) Hot-PotQA (Yang et al., 2018), a multi-hop question answering benchmark that requires reasoning over two or more Wikipedia passages, and”
- FEVER _[verified]_
  > p. 4: “(2) FEVER (Thorne et al., 2018), a fact verification benchmark where each claim is annotated SUPPORTS, REFUTES, or NOT ENOUGH INFO, based on if there exists a Wikipedia passage to verify the claim.”
- ALFWorld (unseen evaluation games, 134) _[verified]_
  > p. 7: “ALFWorld (Shridhar et al., 2020b) (Figure 1(2)) is a synthetic text-based game designed to align with the embodied ALFRED benchmark (Shridhar et al., 2020a).”
- WebShop (test, 500 test instructions) _[verified]_
  > p. 7: “We investigate WebShop (Yao et al., 2022), a recently proposed online shopping website environment with 1.18M real-world products and 12k human instructions.”

## Baselines

- Standard prompting _[verified]_
  > p. 5: “(a) Standard prompting (Standard), which removes all thoughts, actions, observations in ReAct trajectories.”
- Chain-of-thought prompting _[verified]_
  > p. 5: “(b) Chain-of-thought prompting (CoT) (Wei et al., 2022), which removes actions and observations and serve as a reasoning-only baseline.”
- Self-consistency baseline _[verified]_
  > p. 5: “We also build a self-consistency baseline (CoT-SC) (Wang et al., 2022a;b) by sampling 21 CoT trajectories with decoding temperature 0.7 during inference and adopting the majority answer, which is found to consistently boost performance over CoT.”
- Acting-only prompt _[verified]_
  > p. 5: “(c) Acting-only prompt (Act), which removes thoughts in ReAct trajectories, loosely resembling how WebGPT (Nakano et al., 2021) interacts with the Internet to answer questions, though it operates on a different task and action space, and uses imitation and reinforcement learning instead of prompting.”
- BUTLER imitation learning agent _[verified]_
  > p. 7: “For baselines, we use BUTLER (Shridhar et al., 2020b), an imitation learning agent trained on 10 expert trajectories for each task type 5 .”

## Metrics

- Exact match _[partial]_
  > p. 14: “HotpotQA (exact match) 29.4 30.8”
- Success rate percentage _[partial]_
  > p. 14: “ALFWorld (success rate %) 70.9 78.4”
- Average score _[verified]_
  > p. 7: “This task is evaluated by average score (percentage of desired attributes covered by the chosen product averaged across all episodes) and success rate (percentage of episodes where the chosen product satisfies all requirements) on 500 test instructions.”

## Hyperparameters

- decoding temperature (inference): 0.7 _[verified]_
  > p. 5: “We also build a self-consistency baseline (CoT-SC) (Wang et al., 2022a;b) by sampling 21 CoT trajectories with decoding temperature 0.7 during inference and adopting the majority answer, which is found to consistently boost performance over CoT.”
- steps (HotpotQA): 7 _[partial]_
  > p. 5: “We set 7 and 5 steps for HotpotQA and FEVER respectively as we find more steps will not improve ReAct performancefoot_3 .”
- steps (FEVER): 5 _[partial]_
  > p. 5: “We set 7 and 5 steps for HotpotQA and FEVER respectively as we find more steps will not improve ReAct performancefoot_3 .”

## Ablations

- Ablation of ReAct trajectories into standard prompting, chain-of-thought prompting, self-consistency, and acting-only prompt. _[partial]_
  > p. 5: “Baselines We systematically ablate ReAct trajectories to build prompts for multiple baselines (with formats as Figure 1(1a-1c)): (a) Standard prompting (Standard), which removes all thoughts, actions, observations in ReAct trajectories.”
- Ablation experiment using a thought pattern composed of IM-like dense external feedback. _[verified]_
  > p. 8: “To demonstrate the differences between ReAct and IM, and to highlight the importance of internal reasoning vs. simple reactions to external feedback, we ran an ablation experiment using a thought pattern composed of IM-like dense external feedback.”

## Claims

- ReAct outperforms imitation and reinforcement learning methods by absolute success rates of 34% and 10% on two interactive decision making benchmarks. _[verified]_
  > p. 1: “Furthermore, on two interactive decision making benchmarks (ALFWorld and WebShop), ReAct outperforms imitation and reinforcement learning methods by an absolute success rate of 34% and 10% respectively, while being prompted with only one or two in-context examples.”
- ReAct demonstrates effectiveness over baselines as well as improved human interpretability and trustworthiness. _[verified]_
  > p. 1: “We apply our approach, named ReAct, to a diverse set of language and decision making tasks and demonstrate its effectiveness over state-of-the-art baselines in addition to improved human interpretability and trustworthiness.”
- On ALFWorld and WebShop, ReAct prompting outperforms methods trained with 10^3 to 10^5 task instances with an absolute improvement of 34% and 10% in success rates. _[verified]_
  > p. 3: “On ALFWorld and WebShop, two or even one-shot ReAct prompting is able to outperform imitation or reinforcement learning methods trained with 10 3 ∼ 10 5 task instances, with an absolute improvement of 34% and 10% in success rates respectively.”

## Limitations

- Complex tasks with large action spaces require excessive demonstrations that can exceed the input length limit. _[verified]_
  > p. 9: “Despite the simplicity of our method, complex tasks with large action spaces require more demonstrations to learn well, which unfortunately can easily go beyond the input length limit of in-context learning.”

## Future work

- Utilize more high-quality human annotations to improve performance. _[verified]_
  > p. 9: “We explore the fine-tuning approach on HotpotQA with initial promising results, but learning from more high-quality human annotations will be the desiderata to further improve the performance.”
- Scale up ReAct using multi-task training and reinforcement learning. _[verified]_
  > p. 10: “Scaling up ReAct with multi-task training and combining it with complementary paradigms like reinforcement learning could result in stronger agents that further unlock the potential of LLMs for more applications.”

## Ethics

- Interacting with external environments carries potential dangers such as accessing private information or taking harmful actions. _[verified]_
  > p. 10: “However, hooking up a large language model with an action space to interact with external environments (e.g. the web, physical environments) has potential dangers, e.g. looking up inappropriate or private information, or taking harmful actions in an environment.”


## 2302.13971

# LLaMA: Open and Efficient Foundation Language Models

Hugo Touvron, Thibaut Lavril, Gautier Izacard, Xavier Martinet, Marie-Anne Lachaux, Timothee Lacroix, Baptiste Rozière, Naman Goyal, Eric Hambro, Faisal Azhar, Aurelien Rodriguez, Joulin Edouard Grave, Guillaume Lample, Meta Ai, Sandhini Askell, Ariel Agarwal, Gretchen Herbert-Voss, Tom Krueger, Rewon Henighan, Aditya Child, Daniel M Ramesh, Jeffrey Ziegler, Clemens Wu, Christopher Winter, Mark Hesse, Eric Chen, Mateusz Sigler, Scott Litwin, Benjamin Gray, Jack Chess, Christopher Clark, Sam Berner, Alec Mc- Candlish, Ilya Radford, Dario Sutskever, 2020 Amodei, Mark Chen, Jerry Tworek, Heewoo Jun, Qiming Yuan, Henrique Ponde, Oliveira Pinto, Jared Ka- Plan, Harri Edwards, Yuri Burda, Nicholas Joseph, Greg Brockman, Alex Ray, Raul Puri, Gretchen Krueger, Michael Petrov, Heidy Khlaaf, Girish Sas- Try, Pamela Mishkin, Brooke Chan, Scott Gray, Nick Ryder, Mikhail Pavlov, Alethea Power, Lukasz Kaiser, Mohammad Bavarian, Clemens Winter, Philippe Tillet, Felipe Petroski Such, Dave Cum- Mings, Matthias Plappert, Fotios Chantzis, Eliza- Beth Barnes, Ariel Herbert-Voss, William Hebgen Guss, Alex Nichol, Alex Paino, Nikolas Tezak, Jie Tang, Igor Babuschkin, Suchir Balaji, Shantanu Jain, William Saunders, Christopher Hesse, Andrew N Carr, Jan Leike, Josh Achiam, Vedant Misra, Evan Morikawa, Alec Radford, Matthew Knight, Miles Brundage, Mira Murati, Peter Katie Mayer, Bob Mcgrew, Dario Amodei, Sam Mccandlish, Ilya Sutskever, Wojciech 2021 Zaremba, Eval, Aakanksha Chowdhery, Sharan Narang, Jacob Devlin, Maarten Bosma, Gaurav Mishra, Adam Roberts, Hyung Paul Barham, Won Chung, Charles Sutton, Sebastian Gehrmann, Parker Schuh, Kensen Shi, Sasha Tsvyashchenko, Joshua Maynez, Abhishek Rao, Parker Barnes, Yi Tay, Noam Shazeer, Vin- Odkumar Prabhakaran, Emily Reif, Nan Du, Ben Hutchinson, Reiner Pope, James Bradbury, Jacob Austin, Michael Isard, Guy Gur-Ari, Pengcheng Yin, Toju Duke, Anselm Levskaya, Sanjay Ghe- Mawat, Sunipa Dev, Henryk Michalewski, Xavier Garcia, Kevin Robinson, Liam Fe- Dus, Denny Zhou, Daphne Ippolito, David Luan, Hyeontaek Lim, Barret Zoph, Alexander Spiridonov, Ryan Sepassi, David Dohan, Shivani Agrawal, Mark Omernick, Andrew M Dai, Thanumalayan Sankara- Narayana Pillai, Marie Pellat, Aitor Lewkowycz, Erica Moreira, Rewon Child, Oleksandr Polozov, Katherine Lee, Zongwei Zhou, Xuezhi Wang, Bren- Nan Saeta, Mark Diaz, Orhan Firat, Michele Catasta, Jason Wei, Kathy Meier-Hellstern, Douglas Eck, Hyung Won Chung, Le Hou, S Longpre, William Fedus, Eric Li, Mostafa Dehghani, Siddhartha Brahma, Al- Bert Webson, Shane Shixiang, Zhuyun Gu, Mirac Dai, Xinyun Suzgun, Aakanksha Chen, Dasha Chowdh- Ery, Sharan Valter, Gaurav Narang, Adams Wei Mishra, Vincent Yu, Yanping Zhao, An- Drew M Huang, Hongkun Dai, Slav Yu, Ed Petrov, Jeff Huai Hsin Chi, Jacob Dean, Adam Devlin, Denny Roberts, Quoc Zhou, Jason Wei Le, Scal, Kenton Lee, Ming-Wei Chang, Tom Kwiatkowski, Michael Collins, Kristina 2019 Toutanova, Boolq, Peter Clark, Isaac Cowhey, Oren Etzioni, Tushar Khot, Ashish Sabharwal, Carissa Schoenick, Oyvind 2018 Tafjord, Karl Cobbe, Vineet Kosaraju, Jacob Hilton, Reiichiro Nakano, Daniel Fried, Armen Aghajanyan, Jessy Lin, Sida Wang, Eric Wallace, Freda Shi, Ruiqi Zhong, Wen- Tau Yih, Luke Zettlemoyer, Mike 2022 Lewis, Leo Gao, Stella Biderman, Sid Black, Laurence Gold, Travis Hoppe, Charles Foster, Jason Phang, Horace He, Anish Thite, Noa Nabeshima, Shawn Presser, Connor 2020 Leahy, Jonathan Tow, Jordan Hoffmann, Sebastian Borgeaud, Arthur Mensch, Elena Buchatskaya, Trevor Cai, Eliza Rutherford, Diego De, Las Casas, Lisa Anne Hendricks, Johannes Welbl, Aidan Clark, Tom Hennigan, Eric Noland, Katie Millican, George Van Den Driessche, Bogdan Damoc, Aurelia Guy, Simon Osindero, Karen Si- Monyan, Erich Elsen, Jack W Rae
2023 · arXiv:2302.13971v1[cs.CL]

## Problem

- Existing scaling laws prioritize training compute budgets over inference efficiency budgets. _[verified]_
  > p. 1: “The objective of the scaling laws from Hoffmann et al. ( 2022) is to determine how to best scale the dataset and model sizes for a particular training compute budget.”
- Most high-performing language models rely on proprietary or undocumented training data. _[verified]_
  > p. 1: “Unlike Chinchilla, PaLM, or GPT-3, we only use publicly available data, making our work compatible with open-sourcing, while most existing models rely on data which is either not publicly available or undocumented (e.g. "Books -2TB" or "Social media conversations").”

## Task

- Training large language models on massive text corpora for generative tasks. _[verified]_
  > p. 1: “Large Languages Models (LLMs) trained on massive corpora of texts have shown their ability to perform new tasks from textual instructions or from a few examples (Brown et al., 2020).”

## Contributions

- Introduction of LLaMA, a collection of foundation language models ranging from 7B to 65B parameters trained exclusively on publicly available data. _[verified]_
  > p. 1: “We introduce LLaMA, a collection of foundation language models ranging from 7B to 65B parameters.”

## Datasets

- CommonCrawl (3.3 TB) _[verified]_
  > p. 2: “CommonCrawl | 67.0% | 1.10 | 3.3 TB”
- C4 (783 GB) _[verified]_
  > p. 2: “C4 | 15.0% | 1.06 | 783 GB”
- Github (328 GB) _[verified]_
  > p. 2: “Github | 4.5% | 0.64 | 328 GB”
- Wikipedia (83 GB) _[verified]_
  > p. 2: “Wikipedia | 4.5% | 2.45 | 83 GB”
- Books (85 GB) _[verified]_
  > p. 2: “Books | 4.5% | 2.23 | 85 GB”
- ArXiv (92 GB) _[verified]_
  > p. 2: “ArXiv | 2.5% | 1.06 | 92 GB”
- StackExchange (78 GB) _[verified]_
  > p. 2: “StackExchange | 2.0% | 1.03 | 78 GB”
- BoolQ _[verified]_
  > p. 4: “We consider eight standard common sense reasoning benchmarks: BoolQ (Clark et al., 2019), PIQA (Bisk et al., 2020), SIQA (Sap et al., 2019), HellaSwag (Zellers et al., 2019), WinoGrande (Sakaguchi et al., 2021), ARC easy and challenge (Clark et al., 2018) and OpenBookQA (Mihaylov et al., 2018).”
- PIQA _[verified]_
  > p. 4: “We consider eight standard common sense reasoning benchmarks: BoolQ (Clark et al., 2019), PIQA (Bisk et al., 2020), SIQA (Sap et al., 2019), HellaSwag (Zellers et al., 2019), WinoGrande (Sakaguchi et al., 2021), ARC easy and challenge (Clark et al., 2018) and OpenBookQA (Mihaylov et al., 2018).”
- SIQA _[verified]_
  > p. 4: “We consider eight standard common sense reasoning benchmarks: BoolQ (Clark et al., 2019), PIQA (Bisk et al., 2020), SIQA (Sap et al., 2019), HellaSwag (Zellers et al., 2019), WinoGrande (Sakaguchi et al., 2021), ARC easy and challenge (Clark et al., 2018) and OpenBookQA (Mihaylov et al., 2018).”
- HellaSwag _[verified]_
  > p. 4: “We consider eight standard common sense reasoning benchmarks: BoolQ (Clark et al., 2019), PIQA (Bisk et al., 2020), SIQA (Sap et al., 2019), HellaSwag (Zellers et al., 2019), WinoGrande (Sakaguchi et al., 2021), ARC easy and challenge (Clark et al., 2018) and OpenBookQA (Mihaylov et al., 2018).”
- WinoGrande _[verified]_
  > p. 4: “We consider eight standard common sense reasoning benchmarks: BoolQ (Clark et al., 2019), PIQA (Bisk et al., 2020), SIQA (Sap et al., 2019), HellaSwag (Zellers et al., 2019), WinoGrande (Sakaguchi et al., 2021), ARC easy and challenge (Clark et al., 2018) and OpenBookQA (Mihaylov et al., 2018).”
- ARC-e _[verified]_
  > p. 4: “We consider eight standard common sense reasoning benchmarks: BoolQ (Clark et al., 2019), PIQA (Bisk et al., 2020), SIQA (Sap et al., 2019), HellaSwag (Zellers et al., 2019), WinoGrande (Sakaguchi et al., 2021), ARC easy and challenge (Clark et al., 2018) and OpenBookQA (Mihaylov et al., 2018).”
- ARC-c _[verified]_
  > p. 4: “We consider eight standard common sense reasoning benchmarks: BoolQ (Clark et al., 2019), PIQA (Bisk et al., 2020), SIQA (Sap et al., 2019), HellaSwag (Zellers et al., 2019), WinoGrande (Sakaguchi et al., 2021), ARC easy and challenge (Clark et al., 2018) and OpenBookQA (Mihaylov et al., 2018).”
- OBQA _[verified]_
  > p. 4: “We consider eight standard common sense reasoning benchmarks: BoolQ (Clark et al., 2019), PIQA (Bisk et al., 2020), SIQA (Sap et al., 2019), HellaSwag (Zellers et al., 2019), WinoGrande (Sakaguchi et al., 2021), ARC easy and challenge (Clark et al., 2018) and OpenBookQA (Mihaylov et al., 2018).”
- Natural Questions _[verified]_
  > p. 5: “We compare LLaMA to existing large language models on two closed-book question answering benchmarks: Natural Questions (Kwiatkowski et al., 2019) andTriviaQA (Joshi et al., 2017).”
- TriviaQA (filtered dev set) _[verified]_
  > p. 5: “We compare LLaMA to existing large language models on two closed-book question answering benchmarks: Natural Questions (Kwiatkowski et al., 2019) andTriviaQA (Joshi et al., 2017).”
- RACE _[verified]_
  > p. 5: “We evaluate our models on the RACE reading comprehension benchmark (Lai et al., 2017).”
- MATH (12K) _[verified]_
  > p. 5: “MATH is a dataset of 12K middle school and high school mathematics problems written in LaTeX.”
- GSM8k _[verified]_
  > p. 5: “GSM8k is a set of middle school mathematical problems.”
- HumanEval _[verified]_
  > p. 5: “We evaluate the ability of our models to write code from a natural language description on two benchmarks: HumanEval (Chen et al., 2021) and MBPP (Austin et al., 2021).”
- MBPP _[verified]_
  > p. 5: “We evaluate the ability of our models to write code from a natural language description on two benchmarks: HumanEval (Chen et al., 2021) and MBPP (Austin et al., 2021).”
- MMLU _[verified]_
  > p. 6: “The massive multitask language understanding benchmark, or MMLU, introduced by Hendrycks et al. ( 2020) consists of multiple choice questions covering various domains of knowledge, including humanities, STEM and social sciences.”

## Baselines

- GPT-3 _[verified]_
  > p. 4: “We compare LLaMA with other foundation models, namely the non-publicly available language models GPT-3 (Brown et al., 2020), Gopher (Rae et al., 2021), Chinchilla (Hoffmann et al., 2022) and PaLM (Chowdhery et al., 2022), as well as the open-sourced OPT models (Zhang et al., 2022), GPT-J (Wang and Komatsuzaki, 2021), and GPT-Neo (Black et al., 2022).”
- Gopher _[verified]_
  > p. 4: “We compare LLaMA with other foundation models, namely the non-publicly available language models GPT-3 (Brown et al., 2020), Gopher (Rae et al., 2021), Chinchilla (Hoffmann et al., 2022) and PaLM (Chowdhery et al., 2022), as well as the open-sourced OPT models (Zhang et al., 2022), GPT-J (Wang and Komatsuzaki, 2021), and GPT-Neo (Black et al., 2022).”
- Chinchilla _[verified]_
  > p. 4: “We compare LLaMA with other foundation models, namely the non-publicly available language models GPT-3 (Brown et al., 2020), Gopher (Rae et al., 2021), Chinchilla (Hoffmann et al., 2022) and PaLM (Chowdhery et al., 2022), as well as the open-sourced OPT models (Zhang et al., 2022), GPT-J (Wang and Komatsuzaki, 2021), and GPT-Neo (Black et al., 2022).”
- PaLM _[verified]_
  > p. 4: “We compare LLaMA with other foundation models, namely the non-publicly available language models GPT-3 (Brown et al., 2020), Gopher (Rae et al., 2021), Chinchilla (Hoffmann et al., 2022) and PaLM (Chowdhery et al., 2022), as well as the open-sourced OPT models (Zhang et al., 2022), GPT-J (Wang and Komatsuzaki, 2021), and GPT-Neo (Black et al., 2022).”
- OPT _[verified]_
  > p. 4: “We compare LLaMA with other foundation models, namely the non-publicly available language models GPT-3 (Brown et al., 2020), Gopher (Rae et al., 2021), Chinchilla (Hoffmann et al., 2022) and PaLM (Chowdhery et al., 2022), as well as the open-sourced OPT models (Zhang et al., 2022), GPT-J (Wang and Komatsuzaki, 2021), and GPT-Neo (Black et al., 2022).”
  > p. 4: “In Section 4, we also briefly compare LLaMA with instruction-tuned models such as OPT-IML (Iyer et al., 2022) and Flan-PaLM (Chung et al., 2022).”
- GPT-J _[verified]_
  > p. 4: “We compare LLaMA with other foundation models, namely the non-publicly available language models GPT-3 (Brown et al., 2020), Gopher (Rae et al., 2021), Chinchilla (Hoffmann et al., 2022) and PaLM (Chowdhery et al., 2022), as well as the open-sourced OPT models (Zhang et al., 2022), GPT-J (Wang and Komatsuzaki, 2021), and GPT-Neo (Black et al., 2022).”
- GPT-Neo _[verified]_
  > p. 4: “We compare LLaMA with other foundation models, namely the non-publicly available language models GPT-3 (Brown et al., 2020), Gopher (Rae et al., 2021), Chinchilla (Hoffmann et al., 2022) and PaLM (Chowdhery et al., 2022), as well as the open-sourced OPT models (Zhang et al., 2022), GPT-J (Wang and Komatsuzaki, 2021), and GPT-Neo (Black et al., 2022).”
- Flan-PaLM _[verified]_
  > p. 4: “In Section 4, we also briefly compare LLaMA with instruction-tuned models such as OPT-IML (Iyer et al., 2022) and Flan-PaLM (Chung et al., 2022).”
- Minerva _[verified]_
  > p. 5: “In Table 7, we compare with PaLM and Minerva (Lewkowycz et al., 2022).”
- LaMDA _[verified]_
  > p. 6: “In Table 8, we compare the pass@1 scores of our models with existing language models that have not been finetuned on code, namely PaLM and LaMDA (Thoppilan et al., 2022).”

## Metrics

- Exact match performance _[verified]_
  > p. 5: “For both benchmarks, we report exact match performance in a closed book setting, i.e., where the models do not have access to documents that contain evidence to answer the question.”
- Zero-shot accuracy _[verified]_
  > p. 5: “Table 6: Reading Comprehension.Zero-shot accuracy.”
- pass@1 _[verified]_
  > p. 6: “In Table 8, we compare the pass@1 scores of our models with existing language models that have not been finetuned on code, namely PaLM and LaMDA (Thoppilan et al., 2022).”
- pass@100 and pass@80 _[verified]_
  > p. 6: “The pass@100 and pass@80 metrics were obtained with temperature 0.8.”
- Five-shot accuracy _[verified]_
  > p. 7: “Table 9: Massive Multitask Language Understanding (MMLU).Five-shot accuracy.”

## Hyperparameters

- learning rate: 3.0e^−^4 _[verified]_
  > p. 3: “6.7B | 4096 | 32 | 32 | 3.0e^−^4 | 4M | 1.0T”
- batch size: 4M _[verified]_
  > p. 3: “6.7B | 4096 | 32 | 32 | 3.0e^−^4 | 4M | 1.0T”
- tokens: 1.0T _[verified]_
  > p. 3: “6.7B | 4096 | 32 | 32 | 3.0e^−^4 | 4M | 1.0T”
- learning rate: 1.5e^−^4 _[verified]_
  > p. 3: “32.5B | 6656 | 52 | 60 | 1.5e^−^4 | 4M | 1.4T”
- temperature (inference): 0.1 _[verified]_
  > p. 6: “The pass@1 results reported in this table were obtained by sampling with temperature 0.1.”
- temperature (inference): 0.8 _[verified]_
  > p. 6: “The pass@100 and pass@80 metrics were obtained with temperature 0.8.”

## Compute

- Single V100 GPU during inference _[verified]_
  > p. 5: “This model runs on a single V100 GPU during inference.”
- A100-80GB GPU power consumption for LLaMA-7B _[verified]_
  > p. 11: “LLaMA-7B | A100-80GB | 400W | 82,432 | 36 MWh | 14”
- A100-80GB GPU power consumption for LLaMA-13B _[verified]_
  > p. 11: “LLaMA-13B | A100-80GB | 400W | 135,168 | 59 MWh | 23”
- A100-80GB GPU power consumption for LLaMA-33B _[verified]_
  > p. 11: “LLaMA-33B | A100-80GB | 400W | 530,432 | 233 MWh | 90”
- A100-80GB GPU power consumption for LLaMA-65B _[verified]_
  > p. 11: “LLaMA-65B | A100-80GB | 400W | 1,022,362 | 449 MWh | 173”

## Claims

- LLaMA-13B outperforms GPT-3 on most benchmarks despite being much smaller. _[verified]_
  > p. 1: “In particular, LLaMA-13B outperforms GPT-3 (175B) on most benchmarks, and LLaMA-65B is competitive with the best models, Chinchilla-70B and PaLM-540B.”
- LLaMA-65B is competitive with top large language models like Chinchilla and PaLM. _[verified]_
  > p. 1: “At the higher-end of the scale, our 65B-parameter model is also competitive with the best large language models such as Chinchilla or PaLM-540B.”

## Limitations

- Evaluation methods used are insufficient to fully understand model risks. _[verified]_
  > p. 7: “While we have selected some of the standard benchmarks that are used by the language model community to indicate some of the issues with these models, these evaluations are not sufficient to fully understand the risks associated with these models.”
- Lack of control over the third-party PerspectiveAPI pipeline makes comparison difficult. _[verified]_
  > p. 8: “We do not have control over the pipeline used by the third-party PerspectiveAPI, making comparison with previous models difficult.”

## Future work

- Investigate instruction finetuning further. _[verified]_
  > p. 11: “Additionally, we observed like Chung et al. (2022) that finetuning these models on instructions lead to promising results, and we plan to further investigate this in future work.”
- Release larger models trained on larger pretraining corpora. _[verified]_
  > p. 11: “Finally, we plan to release larger models trained on larger pretraining corpora in the future, since we have seen a constant improvement in performance as we were scaling.”

## Ethics

- Training models consumes significant energy and causes carbon emissions. _[verified]_
  > p. 10: “The training of our models have consumed a massive quantity of energy, responsible for the emission of carbon dioxide.”

## Code

- https://github.com/facebookresearch/llama _[verified]_
  > p. 1: “In this context, given a target level of performance, the preferred model is not the fastest to train but the fastest at inference, and although it may be cheaper to train a large model to reach a certain level of 1 https://github.com/facebookresearch/llama”
- https://github.com/facebookresearch/xformers _[verified]_
  > p. 3: “https://github.com/facebookresearch/xformers”
- https://github.com/facebookresearch/metaseq/tree/main/projects/OPT/chronicles _[verified]_
  > p. 10: “https://github.com/facebookresearch/metaseq/ tree/main/projects/OPT/chronicles”


## 2305.18290

# Direct Preference Optimization: Your Language Model is Secretly a Reward Model

Rafael Rafailov, Archit Sharma, Eric Mitchell, Stefano Ermon, Christopher D Manning, Chelsea Finn
2024 · arXiv:2305.18290v3[cs.LG]

## Problem

- Achieving precise control over the behavior of large-scale unsupervised language models is difficult. _[verified]_
  > p. 1: “While large-scale unsupervised language models (LMs) learn broad world knowledge and some reasoning skills, achieving precise control of their behavior is difficult due to the completely unsupervised nature of their training.”
- Traditional reinforcement learning from human feedback is a complex and often unstable procedure. _[verified]_
  > p. 1: “However, RLHF is a complex and often unstable procedure, first fitting a reward model that reflects the human preferences, and then fine-tuning the large unsupervised LM using reinforcement learning to maximize this estimated reward without drifting too far from the original model.”

## Task

- Sentiment modulation in language models _[verified]_
  > p. 1: “Notably, fine-tuning with DPO exceeds PPO-based RLHF in ability to control sentiment of generations, and matches or improves response quality in summarization and single-turn dialogue while being substantially simpler to implement and train.”
- Text summarization _[verified]_
  > p. 1: “Notably, fine-tuning with DPO exceeds PPO-based RLHF in ability to control sentiment of generations, and matches or improves response quality in summarization and single-turn dialogue while being substantially simpler to implement and train.”
- Single-turn dialogue generation _[verified]_
  > p. 1: “Notably, fine-tuning with DPO exceeds PPO-based RLHF in ability to control sentiment of generations, and matches or improves response quality in summarization and single-turn dialogue while being substantially simpler to implement and train.”

## Contributions

- Introduction of Direct Preference Optimization (DPO), a simple algorithm to solve the standard RLHF problem with a classification loss. _[verified]_
  > p. 1: “In this paper we introduce a new parameterization of the reward model in RLHF that enables extraction of the corresponding optimal policy in closed form, allowing us to solve the standard RLHF problem with only a simple classification loss.”
- DPO eliminates the need for sampling from the language model or significant hyperparameter tuning during fine-tuning. _[verified]_
  > p. 1: “The resulting algorithm, which we call Direct Preference Optimization (DPO), is stable, performant, and computationally lightweight, eliminating the need for sampling from the LM during fine-tuning or performing significant hyperparameter tuning.”

## Method

- The standard RLHF pipeline begins with supervised fine-tuning (SFT) of a pre-trained language model on task-specific data. _[verified]_
  > p. 3: “SFT: RLHF typically begins by fine-tuning a pre-trained LM with supervised learning on high-quality data for the downstream task(s) of interest (dialogue, summarization, etc.), to obtain a model π SFT .”
- In the reward modeling phase, human preferences for model completions are collected and parameterized via models like the Bradley-Terry model to estimate a reward function using maximum likelihood. _[verified]_
  > p. 3: “Assuming access to a static dataset of comparisons D = x (i) , y w , y (i) l N i=1 sampled from p * , we can parametrize a reward model r ϕ (x, y) and estimate the parameters via maximum likelihood.”
- The RL optimization phase uses the learned reward function to update the language model policy by maximizing a reward objective with a KL-divergence penalty, typically optimized using PPO. _[verified]_
  > p. 3: “The standard approach [51,40,1,28] has been to construct the reward function r(x, y) = r ϕ (x, y) -β(log π θ (y | x) -log π ref (y | x)), and maximize using PPO [39].”
- The proposed DPO method reformulates the RLHF objective by using an analytical mapping from reward functions to optimal policies, transforming a loss function over rewards into a loss function over policies. _[verified]_
  > p. 4: “As we will describe next in detail, our key insight is to leverage an analytical mapping from reward functions to optimal policies, which enables us to transform a loss function over reward functions into a loss function over policies.”
- Direct Preference Optimization (DPO) directly optimizes the language model policy on a preference dataset by minimizing a maximum likelihood objective that implicitly represents the reward through the policy itself. _[verified]_
  > p. 3: “Analogous to the reward modeling approach (i.e. Eq. 2), our policy objective becomes: L DPO (π θ ; π ref ) = -E (x,yw,y l )∼D log σ β log π θ (y w | x) π ref (y w | x) -β log π θ (y l | x) π ref (y l | x) .”

## Novelty

- Unlike traditional RLHF methods that explicitly learn a standalone reward model and optimize it via reinforcement learning, the proposed approach derives a simple policy optimization method using preferences directly without an RL training loop. _[verified]_
  > p. 4: “Unlike prior RLHF methods, which learn a reward and then optimize it via RL, our approach leverages a particular choice of reward model parameterization that enables extraction of its optimal policy in closed form, without an RL training loop.”
- The method avoids fitting an explicit, standalone reward model by using a change-of-variables approach based on an analytical mapping from reward functions to optimal policies. _[verified]_
  > p. 4: “This change-of-variables approach avoids fitting an explicit, standalone reward model, while still optimizing under existing models of human preferences, such as the Bradley-Terry model.”

## Datasets

- IMDb (train) _[verified]_
  > p. 7: “In controlled sentiment generation, x is a prefix of a movie review from the IMDb dataset [24], and the policy must generate y with positive sentiment.”
- Reddit TL;DR summarization _[verified]_
  > p. 7: “Following prior work, we use the Reddit TL;DR summarization dataset [43] along with human preferences gathered by Stiennon et al..”
- Anthropic Helpful and Harmless dialogue (170k dialogues) _[verified]_
  > p. 7: “we use the Anthropic Helpful and Harmless dialogue dataset [1], containing 170k dialogues between a human and an automated assistant.”
- CNN/DailyMail (test) _[unsupported]_
  > p. 9: “news articles in the test split of the CNN/DailyMail dataset [26], using the best sampling temperatures from TL;DR (0 and 0.25).”

## Baselines

- DPO _[unsupported]_
  > p. 7: “DPO provides the highest expected reward for all KL values, demonstrating the quality of the optimization.”
- PPO _[verified]_
  > p. 7: “DPO exceeds PPO's best-case performance on summarization, while being more robust to changes in the sampling temperature.”
  > p. 8: “We also consider PPO [39] using a reward function learned from the preference data and PPO-GT, which is an oracle that learns from the ground truth reward function available in the controlled sentiment setting.”
- Preferred-FT _[verified]_
  > p. 8: “In addition, we evaluate the SFT model as well as Preferred-FT, which is a model fine-tuned with supervised learning on the chosen completion y w from either the SFT model (in controlled sentiment and summarization) or a generic LM (in single-turn dialogue).”
- SFT _[verified]_
  > p. 8: “In addition, we evaluate the SFT model as well as Preferred-FT, which is a model fine-tuned with supervised learning on the chosen completion y w from either the SFT model (in controlled sentiment and summarization) or a generic LM (in single-turn dialogue).”
- GPT-J Best of 128 _[verified]_
  > p. 7: “GPT-JBestof 128”
- Unlikelihood _[verified]_
  > p. 8: “Another pseudo-supervised method is Unlikelihood [46], which simply optimizes the policy to maximize the probability assigned to y w and minimize the probability assigned to y l ; we use an optional coefficient α ∈ [0, 1] on the 'unlikelihood' term.”
- Best of N _[verified]_
  > p. 8: “Finally, we consider the Best of N baseline, sampling N responses from the SFT model (or Preferred-FT in dialogue) and returning the highest-scoring response according to a reward function learned from the preference dataset.”
- Zero-shot prompting with GPT-J _[verified]_
  > p. 8: “Most simply, we explore zero-shot prompting with GPT-J [45] in the summarization task and 2-shot prompting with Pythia-2.8B [3] in the dialogue task.”
- 2-shot prompting with Pythia-2.8B _[verified]_
  > p. 8: “Most simply, we explore zero-shot prompting with GPT-J [45] in the summarization task and 2-shot prompting with Pythia-2.8B [3] in the dialogue task.”

## Metrics

- Expected reward vs KL to the reference policy _[verified]_
  > p. 7: “Left.The frontier of expected reward vs KL to the reference policy.”
- TL;DR summarization win rates vs human-written summaries using GPT-4 as evaluator _[verified]_
  > p. 7: “Right.TL;DR summarization win rates vs. human-written summaries, using GPT-4 as evaluator.”
- Win rate against a baseline policy using GPT-4 as a proxy for human evaluation _[verified]_
  > p. 7: “therefore, we evaluate algorithms with their win rate against a baseline policy, using GPT-4 as a proxy for human evaluation of summary quality and response helpfulness in the summarization and single-turn dialogue settings, respectively.”
- Average sequence-level KL with the reference policy _[verified]_
  > p. 8: “computing the average reward under the true reward function as well as the average sequence-level KL 3 with the reference policy KL (π || π ref ).”

## Hyperparameters

- target KL: {3, 6, 9, 12} _[verified]_
  > p. 8: “We execute multiple training runs for each algorithm, using a different hyperparameter for policy conservativeness in each run (target KL ∈ {3, 6, 9, 12} for PPO, β ∈ {0.05, 0.1, 1, 5}, α ∈ {0.05, 0.1, 0.5, 1} for unlikelihood, random seeds for preferred-FT).”
- β: {0.05, 0.1, 1, 5} _[verified]_
  > p. 8: “We execute multiple training runs for each algorithm, using a different hyperparameter for policy conservativeness in each run (target KL ∈ {3, 6, 9, 12} for PPO, β ∈ {0.05, 0.1, 1, 5}, α ∈ {0.05, 0.1, 0.5, 1} for unlikelihood, random seeds for preferred-FT).”
- α: {0.05, 0.1, 0.5, 1} _[verified]_
  > p. 8: “We execute multiple training runs for each algorithm, using a different hyperparameter for policy conservativeness in each run (target KL ∈ {3, 6, 9, 12} for PPO, β ∈ {0.05, 0.1, 1, 5}, α ∈ {0.05, 0.1, 0.5, 1} for unlikelihood, random seeds for preferred-FT).”
- sampling temperature: 0.0 to 1.0 _[verified]_
  > p. 9: “The completions for all methods are sampled at temperatures varying from 0.0 to 1.0, and the win rates are shown in Figure 2 (right).”

## Seeds and runs

- Multiple training runs using different hyperparameters for policy conservativeness and random seeds, totaling 22 runs _[verified]_
  > p. 8: “We execute multiple training runs for each algorithm, using a different hyperparameter for policy conservativeness in each run (target KL ∈ {3, 6, 9, 12} for PPO, β ∈ {0.05, 0.1, 1, 5}, α ∈ {0.05, 0.1, 0.5, 1} for unlikelihood, random seeds for preferred-FT). This sweep includes 22 runs in total.”

## Claims

- DPO fine-tunes language models to align with human preferences as well as or better than existing methods. _[verified]_
  > p. 1: “Our experiments show that DPO can fine-tune LMs to align with human preferences as well as or better than existing methods.”
- DPO works with language models having up to 6B parameters. _[verified]_
  > p. 2: “Our experiments show that DPO is at least as effective as existing methods, including PPO-based RLHF, for learning from preferences in tasks such as sentiment modulation, summarization, and dialogue, using language models with up to 6B parameters.”

## Future work

- Investigate how the DPO policy generalizes out of distribution compared to learning from an explicit reward function. _[verified]_
  > p. 10: “How does the DPO policy generalize out of distribution, compared with learning from an explicit reward function?”
- Explore whether training with self-labeling from the DPO policy can make effective use of unlabeled prompts. _[verified]_
  > p. 10: “For example, can training with self-labeling from the DPO policy similarly make effective use of unlabeled prompts?”
- Study how reward over-optimization manifests in the direct preference optimization setting. _[verified]_
  > p. 10: “On another front, how does reward over-optimization manifest in the direct preference optimization setting, and is the slight decrease in performance in Figure 3-right an instance of it?”
- Scale DPO to state-of-the-art models orders of magnitude larger than 6B parameters. _[verified]_
  > p. 10: “Additionally, while we evaluate models up to 6B parameters, exploration of scaling DPO to state-of-the-art models orders of magnitude larger is an exciting direction for future work.”
- Determine the best way to elicit high-quality judgments from automated systems like GPT-4. _[verified]_
  > p. 10: “Regarding evaluations, we find that the win rates computed by GPT-4 are impacted by the prompt; future work may study the best way to elicit high-quality judgments from automated systems.”
- Apply DPO to generative models in modalities other than language model preference training. _[verified]_
  > p. 10: “Finally, many possible applications of DPO exist beyond training language models from human preferences, including training generative models in other modalities.”

## Code

- https://huggingface.co/CarperAI/openai_summarize_tldr_sft _[verified]_
  > p. 7: “https://huggingface.co/CarperAI/openai_summarize_tldr_sft”
- https://huggingface.co/reciprocate/ppo_hh_pythia-6B _[verified]_
  > p. 9: “https://huggingface.co/reciprocate/ppo_hh_pythia-6B”
- https://github.com/CarperAI/trlx/tree/main/examples/hh _[verified]_
  > p. 9: “https://github.com/CarperAI/trlx/tree/main/examples/hh”


## 2305.14314

# QLORA: Efficient Finetuning of Quantized LLMs

Tim Dettmers, Artidoro Pagnoni, Ari Holtzman, Luke Zettlemoyer
2023 · arXiv:2305.14314v1[cs.LG]

## Problem

- Finetuning very large language models is prohibitively expensive in terms of GPU memory. _[verified]_
  > p. 1: “However, finetuning very large models is prohibitively expensive; regular 16-bit finetuning of a LLaMA 65B parameter model [57] requires more than 780 GB of GPU memory.”
- Existing quantization methods only work for inference and fail during training. _[verified]_
  > p. 1: “While recent quantization methods can reduce the memory footprint of LLMs [14,13,18,66], such techniques only work for inference and break down during training [65].”

## Task

- instruction following and chatbot performance evaluation _[verified]_
  > p. 1: “We use QLORA to finetune more than 1,000 models, providing a detailed analysis of instruction following and chatbot performance across 8 instruction datasets, multiple model types (LLaMA, T5), and model scales that would be infeasible to run with regular finetuning (e.g. 33B and 65B parameter models).”

## Contributions

- Introduction of 4-bit NormalFloat (NF4), an information-theoretically optimal data type for normally distributed weights. _[verified]_
  > p. 1: “QLORA introduces a number of innovations to save memory without sacrificing performance: (a) 4-bit NormalFloat (NF4), a new data type that is information theoretically optimal for normally distributed weights”
- Double Quantization to reduce the average memory footprint by quantizing the quantization constants. _[verified]_
  > p. 1: “(b) Double Quantization to reduce the average memory footprint by quantizing the quantization constants, and (c) Paged Optimizers to manage memory spikes.”
- Paged Optimizers to manage memory spikes. _[verified]_
  > p. 1: “(b) Double Quantization to reduce the average memory footprint by quantizing the quantization constants, and (c) Paged Optimizers to manage memory spikes.”

## Method

- QLORA utilizes a 4-bit NormalFloat (NF4) storage data type for base model weights and a BFloat16 data type for computations, dequantizing weights to 16-bit for matrix multiplication during forward and backward passes. _[partial]_
  > p. 4: “QLORA has one low-precision storage data type, in our case usually 4-bit, and one computation data type that is usually BFloat16.”
- Double Quantization is applied to the quantization constants to further reduce their memory footprint by treating them as inputs to a second quantization step. _[verified]_
  > p. 5: “More specifically, Double Quantization treats quantization constants c 2 FP32 of the first quantization as inputs to a second quantization.”
- Paged Optimizers are employed using NVIDIA unified memory to automatically page optimizer states between GPU and CPU RAM, preventing out-of-memory errors during gradient checkpointing spikes. _[verified]_
  > p. 5: “Paged Optimizers use the NVIDIA unified memoryfoot_0 feature wich does automatic page-to-page transfers between the CPU and GPU for error-free GPU processing in the scenario where the GPU occasionally runs out-of-memory.”
- The approach integrates Low-rank Adapters (LoRA) where only the adapter parameters receive weight gradients while the base model weights remain fixed and quantized. _[partial]_
  > p. 5: “To summarize, QLORA has one storage data type (usually 4-bit NormalFloat) and a computation data type .”

## Novelty

- The introduction of the 4-bit NormalFloat (NF4) data type, which is information-theoretically optimal for zero-centered normally distributed weights. _[partial]_
  > p. 4: “QLORA achieves high-fidelity 4-bit finetuning via two techniques we propose-4-bit NormalFloat (NF4) quantization and Double Quantization.”
- The use of Double Quantization to reduce the memory overhead introduced by quantization constants. _[unsupported]_
  > p. 4: “Additionally, we introduce Paged Optimizers, to prevent memory spikes during gradient checkpointing from causing out-of-memory errors that have traditionally made finetuning on a single machine difficult for large models.”
- The employment of Paged Optimizers to manage memory spikes and prevent out-of-memory errors during single-machine large model finetuning. _[verified]_
  > p. 4: “Additionally, we introduce Paged Optimizers, to prevent memory spikes during gradient checkpointing from causing out-of-memory errors that have traditionally made finetuning on a single machine difficult for large models.”

## Datasets

- GLUE _[verified]_
  > p. 6: “Our evaluations include GLUE [58] with RoBERTa-large [38], Super-NaturalInstructions (TKInstruct) [61] with T5 [49], and 5-shot MMLU [24] after finetuning LLaMA on Flan v2 [39] and Alpaca [55].”
- Super-NaturalInstructions _[verified]_
  > p. 6: “Our evaluations include GLUE [58] with RoBERTa-large [38], Super-NaturalInstructions (TKInstruct) [61] with T5 [49], and 5-shot MMLU [24] after finetuning LLaMA on Flan v2 [39] and Alpaca [55].”
- MMLU _[verified]_
  > p. 6: “Our evaluations include GLUE [58] with RoBERTa-large [38], Super-NaturalInstructions (TKInstruct) [61] with T5 [49], and 5-shot MMLU [24] after finetuning LLaMA on Flan v2 [39] and Alpaca [55].”
- OPT (125m -13B) _[verified]_
  > p. 6: “To additionally study the advantages of NF4 over other 4-bit data types, we use the setup of Dettmers and Zettlemoyer [13] and measure post-quantization zero-shot accuracy and perplexity across different models (OPT [72], LLaMA [57], BLOOM [52], Pythia [7]) for model sizes 125m -13B.”
- LLaMA (125m -13B) _[verified]_
  > p. 6: “To additionally study the advantages of NF4 over other 4-bit data types, we use the setup of Dettmers and Zettlemoyer [13] and measure post-quantization zero-shot accuracy and perplexity across different models (OPT [72], LLaMA [57], BLOOM [52], Pythia [7]) for model sizes 125m -13B.”
- BLOOM (125m -13B) _[verified]_
  > p. 6: “To additionally study the advantages of NF4 over other 4-bit data types, we use the setup of Dettmers and Zettlemoyer [13] and measure post-quantization zero-shot accuracy and perplexity across different models (OPT [72], LLaMA [57], BLOOM [52], Pythia [7]) for model sizes 125m -13B.”
- Pythia (125m -13B) _[verified]_
  > p. 6: “To additionally study the advantages of NF4 over other 4-bit data types, we use the setup of Dettmers and Zettlemoyer [13] and measure post-quantization zero-shot accuracy and perplexity across different models (OPT [72], LLaMA [57], BLOOM [52], Pythia [7]) for model sizes 125m -13B.”
- Alpaca _[verified]_
  > p. 7: “To this end, we finetune LLaMA 7B through 65B on two instruction following datasets, Alpaca and FLAN v2, and evaluate on the MMLU benchmark via 5-shot accuracy.”
- FLAN v2 _[verified]_
  > p. 7: “To this end, we finetune LLaMA 7B through 65B on two instruction following datasets, Alpaca and FLAN v2, and evaluate on the MMLU benchmark via 5-shot accuracy.”
- OASST1 _[verified]_
  > p. 8: “We include datasets obtained through crowd-sourcing (OASST1 [31], HH-RLHF [4]), distillation from instruction-tuned models (Alpaca [55], self-instruct [59], unnaturalinstructions [26]), corpora aggregations (FLAN v2 [12]), as well as hybrids (Chip2 [32], Longform [30]).”
- HH-RLHF _[verified]_
  > p. 8: “We include datasets obtained through crowd-sourcing (OASST1 [31], HH-RLHF [4]), distillation from instruction-tuned models (Alpaca [55], self-instruct [59], unnaturalinstructions [26]), corpora aggregations (FLAN v2 [12]), as well as hybrids (Chip2 [32], Longform [30]).”
- self-instruct _[verified]_
  > p. 8: “We include datasets obtained through crowd-sourcing (OASST1 [31], HH-RLHF [4]), distillation from instruction-tuned models (Alpaca [55], self-instruct [59], unnaturalinstructions [26]), corpora aggregations (FLAN v2 [12]), as well as hybrids (Chip2 [32], Longform [30]).”
- unnaturalinstructions _[verified]_
  > p. 8: “We include datasets obtained through crowd-sourcing (OASST1 [31], HH-RLHF [4]), distillation from instruction-tuned models (Alpaca [55], self-instruct [59], unnaturalinstructions [26]), corpora aggregations (FLAN v2 [12]), as well as hybrids (Chip2 [32], Longform [30]).”
- Chip2 _[verified]_
  > p. 8: “We include datasets obtained through crowd-sourcing (OASST1 [31], HH-RLHF [4]), distillation from instruction-tuned models (Alpaca [55], self-instruct [59], unnaturalinstructions [26]), corpora aggregations (FLAN v2 [12]), as well as hybrids (Chip2 [32], Longform [30]).”
- Longform _[verified]_
  > p. 8: “We include datasets obtained through crowd-sourcing (OASST1 [31], HH-RLHF [4]), distillation from instruction-tuned models (Alpaca [55], self-instruct [59], unnaturalinstructions [26]), corpora aggregations (FLAN v2 [12]), as well as hybrids (Chip2 [32], Longform [30]).”
- Vicuna prompts (80 prompts) _[unsupported]_
  > p. 9: “The OASST1 dataset is a multilingual collection of crowd-sourced multiturn dialogs between a user and an assistant.”
- OASST1 validation dataset (validation, 953 unique user queries) _[verified]_
  > p. 9: “We select all user messages in the validation dataset as queries and include previous turns in the prompt.”
- Pile Common Crawl _[verified]_
  > p. 7: “Table 2: Pile Common Crawl mean perplexity for different data types for 125M to 13B OPT, BLOOM, LLaMA, and Pythia models.”
- CrowS dataset _[verified]_
  > p. 15: “Table 8: Evaluation of biases on the CrowS dataset.”

## Baselines

- Vicuna chatbot system _[verified]_
  > p. 8: “We compare our models to both research (Vicuna [10] and Open Assistant [31]) and commercial (GPT-4 [42], GPT-3.5-turbo and Bard) chatbot systems.”
- Open Assistant chatbot system _[verified]_
  > p. 8: “We compare our models to both research (Vicuna [10] and Open Assistant [31]) and commercial (GPT-4 [42], GPT-3.5-turbo and Bard) chatbot systems.”
- GPT-4 commercial chatbot system _[verified]_
  > p. 8: “We compare our models to both research (Vicuna [10] and Open Assistant [31]) and commercial (GPT-4 [42], GPT-3.5-turbo and Bard) chatbot systems.”
- GPT-3.5-turbo commercial chatbot system _[verified]_
  > p. 8: “We compare our models to both research (Vicuna [10] and Open Assistant [31]) and commercial (GPT-4 [42], GPT-3.5-turbo and Bard) chatbot systems.”
- Bard commercial chatbot system _[verified]_
  > p. 8: “We compare our models to both research (Vicuna [10] and Open Assistant [31]) and commercial (GPT-4 [42], GPT-3.5-turbo and Bard) chatbot systems.”

## Metrics

- Perplexity _[verified]_
  > p. 6: “To additionally study the advantages of NF4 over other 4-bit data types, we use the setup of Dettmers and Zettlemoyer [13] and measure post-quantization zero-shot accuracy and perplexity across different models (OPT [72], LLaMA [57], BLOOM [52], Pythia [7]) for model sizes 125m -13B.”
- Zero-shot accuracy _[verified]_
  > p. 6: “To additionally study the advantages of NF4 over other 4-bit data types, we use the setup of Dettmers and Zettlemoyer [13] and measure post-quantization zero-shot accuracy and perplexity across different models (OPT [72], LLaMA [57], BLOOM [52], Pythia [7]) for model sizes 125m -13B.”
- 5-shot MMLU test accuracy _[verified]_
  > p. 7: “To this end, we finetune LLaMA 7B through 65B on two instruction following datasets, Alpaca and FLAN v2, and evaluate on the MMLU benchmark via 5-shot accuracy.”
- Score out of ten assigned by GPT-4 relative to ChatGPT _[verified]_
  > p. 9: “Given a query along with ChatGPT's and a model's responses, GPT-4 is prompted to assign a score out of ten to both responses and provide an explanation.”
- Elo rating _[verified]_
  > p. 9: “With both human and automated pairwise comparisons, we create a tournament-style competition where models compete against each other.”
- GLUE accuracy _[verified]_
  > p. 7: “Dataset | GLUE (Acc.) |  |  | Super-NaturalInstructions | (RougeL) |”
- Super-NaturalInstructions RougeL _[verified]_
  > p. 7: “Dataset | GLUE (Acc.) |  |  | Super-NaturalInstructions | (RougeL) |”

## Hyperparameters

- learning rate (baseline fine-tuning): 1e-6 to 5e-5 _[verified]_
  > p. 6: “We do a hyperparameter search over learning rates 1e-6 to 5e-5 and batch sizes 8 to 128 to find robust baselines.”
- batch size (baseline fine-tuning): 8 to 128 _[verified]_
  > p. 6: “We do a hyperparameter search over learning rates 1e-6 to 5e-5 and batch sizes 8 to 128 to find robust baselines.”
- nucleus sampling p (inference): 0.9 _[verified]_
  > p. 8: “We describe below our proposed setup, using nucleus sampling with p = 0.9 and temperature 0.7 in all cases.”
- temperature (inference): 0.7 _[verified]_
  > p. 8: “We describe below our proposed setup, using nucleus sampling with p = 0.9 and temperature 0.7 in all cases.”
- K (Elo rating): 32 _[verified]_
  > p. 9: “We start with a score of 1,000 and use K = 32.”
- LoRA dropout (QLoRA): { 0.0, 0.05, 0.1} _[verified]_
  > p. 22: “A.1 Hyperparameters for QLORA We do a hyperparameter search for LoRA over the following variables: LoRA dropout { 0.0, 0.05, 0.1}, LoRA r { 8, 16, 32, 64, 128, 256}, LoRA layers {key+query, all attention layers, all FFN layers, all layers, attention + FFN output layers}.”
- LoRA r (QLoRA): { 8, 16, 32, 64, 128, 256} _[verified]_
  > p. 22: “A.1 Hyperparameters for QLORA We do a hyperparameter search for LoRA over the following variables: LoRA dropout { 0.0, 0.05, 0.1}, LoRA r { 8, 16, 32, 64, 128, 256}, LoRA layers {key+query, all attention layers, all FFN layers, all layers, attention + FFN output layers}.”
- LoRA layers (QLoRA): {key+query, all attention layers, all FFN layers, all layers, attention + FFN output layers} _[verified]_
  > p. 22: “A.1 Hyperparameters for QLORA We do a hyperparameter search for LoRA over the following variables: LoRA dropout { 0.0, 0.05, 0.1}, LoRA r { 8, 16, 32, 64, 128, 256}, LoRA layers {key+query, all attention layers, all FFN layers, all layers, attention + FFN output layers}.”
- LoRA r (QLoRA): 64 _[verified]_
  > p. 23: “We set LoRA r = 64, α = 16, and add LoRA modules on all linear layers of the base model.”
- LoRA alpha (QLoRA): 16 _[verified]_
  > p. 23: “We set LoRA r = 64, α = 16, and add LoRA modules on all linear layers of the base model.”
- Adam beta2 (QLoRA): 0.999 _[verified]_
  > p. 23: “We also use Adam beta2 of 0.999, max grad norm of 0.3 and LoRA dropout of 0.1 for models up to 13B and 0.05 for 33B and 65B models.”
- max grad norm (QLoRA): 0.3 _[verified]_
  > p. 23: “We also use Adam beta2 of 0.999, max grad norm of 0.3 and LoRA dropout of 0.1 for models up to 13B and 0.05 for 33B and 65B models.”
- LoRA dropout (QLoRA (models up to 13B)): 0.1 _[verified]_
  > p. 23: “We also use Adam beta2 of 0.999, max grad norm of 0.3 and LoRA dropout of 0.1 for models up to 13B and 0.05 for 33B and 65B models.”
- LoRA dropout (QLoRA (33B and 65B models)): 0.05 _[verified]_
  > p. 23: “We also use Adam beta2 of 0.999, max grad norm of 0.3 and LoRA dropout of 0.1 for models up to 13B and 0.05 for 33B and 65B models.”

## Compute

- Training of 33B Guanaco on 24 GB consumer GPUs in less than 12 hours _[verified]_
  > p. 10: “Furthermore, our 33B Guanaco can be trained on 24 GB consumer GPUs in less than 12 hours.”

## Seeds and runs

- Repeated tournament procedure 10,000 times with different random seeds _[verified]_
  > p. 9: “Similar to Chiang et al. [10], we repeat this procedure 10,000 times with different random seeds to control for ordering effects, e.g., the effect of which model pairs compete with each other first.”

## Ablations

- Ablation studying whether to finetune only on the response vs on instruction and response _[verified]_
  > p. 8: “For datasets that have a clear distinction between instruction and response, we finetune only on the response (see ablations in Appendix B).”
- Ablation subsampling large datasets into sizes of 50,000, 100,000 and 150,000 to examine quality vs size _[verified]_
  > p. 24: “To understand the effects of dataset quality vs. dataset size, we experiment with subsampling large datasets with at least 150,000 samples (Chip2, FLAN v2, Unnatural Instructions), into datasets of size 50,000, 100,000 and 150,000 and examine the resulting trends, as shown in Table 11.”

## Claims

- The best model family, Guanaco, reaches 99.3% of ChatGPT's performance level on the Vicuna benchmark with 24 hours of finetuning. _[verified]_
  > p. 1: “Our best model family, which we name Guanaco, outperforms all previous openly released models on the Vicuna benchmark, reaching 99.3% of the performance level of ChatGPT while only requiring 24 hours of finetuning on a single GPU.”
- QLORA reduces average memory requirements for finetuning a 65B model from over 780 GB to under 48 GB. _[verified]_
  > p. 2: “QLORA reduces the average memory requirements of finetuning a 65B parameter model from >780GB of GPU memory to <48GB without degrading the runtime or predictive performance compared to a 16bit fully finetuned baseline.”

## Limitations

- Inability to establish that QLORA matches full 16-bit finetuning at 33B and 65B scales due to resource costs. _[verified]_
  > p. 15: “Despite this evidence, we did not establish that QLORA can match full 16-bit finetuning performance at 33B and 65B scales.”
- Lack of evaluation on other benchmarks such as BigBench, RAFT, and HELM. _[verified]_
  > p. 15: “While we provide evaluations on MMLU, the Vicuna benchmark, and the OA benchmark, we did not evaluate on other benchmarks such as BigBench, RAFT, and HELM, and it is not ensured that our evaluations generalize to these benchmarks.”
- Only a limited responsible AI evaluation of Guanaco was conducted. _[verified]_
  > p. 15: “While we provide a detailed evaluation for general chatbot performance, another limitation is that we only do a limited responsible AI evaluation of Guanaco.”
- Failure to evaluate different bit-precisions like 3-bit base models or different adapter methods. _[verified]_
  > p. 16: “An additional limitation is that we did not evaluate different bit-precisions, such as using 3-bit base models, or different adapter methods.”

## Future work

- Future work should use HC and Psychology to address subjective preferences in chatbot evaluation. _[verified]_
  > p. 14: “Future work should investigate approaches to mitigate these problems drawing from disciplines that developed mechanisms to deal with subjective preferences, such as Human-Computer Interaction and Psychology.”
- Future work should examine potential biases in automated evaluation systems and mitigation strategies. _[verified]_
  > p. 14: “Future work should examine the presence of potential biases in automated evaluation systems as well as possible mitigation strategies.”
- Investigate how multilingual training improves performance in languages other than English. _[verified]_
  > p. 14: “We leave it to future work to investigate the degree to which such multilingual training improves performance on instructions in languages other than English and whether this explains the larger gap between Vicuna-13B model (only trained on English data) and Guanaco 33B and 65B on the OA benchmark.”
- Further study the performance matching at 33B and 65B scales compared to full 16-bit finetuning. _[verified]_
  > p. 15: “Due to the immense resource costs, we leave this study to future work.”
- Further evaluation of analyzing biases in Guanaco and similar chatbots. _[verified]_
  > p. 15: “We leave further evaluation of analyzing biases in Guanaco and similar chatbots to future work.”

## Ethics

- Finetuning is a dual-use technology that can be abused to cause harm. _[verified]_
  > p. 16: “However, finetuning is a dual-use technology that can be abused to cause harm.”
- Equalizing access to LLM technology allows for better and more independent analysis. _[verified]_
  > p. 16: “Widespread use of LLMs has known dangers [8,6], but we believe that equalizing access to a technology that is quickly becoming ubiquitous will allow for better more independent analysis than keeping the power of LLMs in the hands of large corporations that do not release models or source code for auditing.”
- QLORA may enable privacy-preserving usage of LLMs on devices like mobile phones. _[verified]_
  > p. 16: “QLORA can help enable privacy-preserving usage of LLMs, where users can own and manage their own data and models, while simultaneously making LLMs easier to deploy.”


## 2402.03300

# DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models

Zhihong Shao, Peiyi Wang, Qihao Zhu, Runxin Xu, Junxiao Song, Xiao Bi, Haowei Zhang, Mingchuan Zhang, Y K Li, Y Wu, Daya Guo
2024 · arXiv:2402.03300v3[cs.CL]

## Problem

- Mathematical reasoning presents a major challenge for language models due to its structured and complex nature. _[verified]_
  > p. 1: “Mathematical reasoning poses a significant challenge for language models due to its complex and structured nature.”
- Top models like GPT-4 and Gemini-Ultra are closed-source, while accessible open-source models trail significantly in performance. _[verified]_
  > p. 2: “However, cutting-edge models such as GPT-4 (OpenAI, 2023) and Gemini-Ultra (Anil et al., 2023) are not publicly available, and the currently accessible open-source models considerably trail behind in performance.”

## Task

- mathematical reasoning _[partial]_
  > p. 1: “Mathematical reasoning poses a significant challenge for language models due to its complex and structured nature.”

## Contributions

- The authors introduce DeepSeekMath 7B, trained on a large math-related corpus using code pretraining and a data selection pipeline. _[verified]_
  > p. 1: “In this paper, we introduce DeepSeekMath 7B, which continues pretraining DeepSeek-Coder-Base-v1.5 7B with 120B math-related tokens sourced from Common Crawl, together with natural language and code data.”
- The authors propose Group Relative Policy Optimization (GRPO), a memory-efficient variant of PPO for reinforcement learning. _[verified]_
  > p. 1: “Second, we introduce Group Relative Policy Optimization (GRPO), a variant of Proximal Policy Optimization (PPO), that enhances mathematical reasoning abilities while concurrently optimizing the memory usage of PPO.”
- The research contribution includes scalable math pre-training and the exploration and analysis of reinforcement learning. _[verified]_
  > p. 3: “Our contribution includes scalable math pre-training, along with the exploration and analysis of reinforcement learning.”

## Method

- An iterative pipeline is used to build the DeepSeekMath Corpus from Common Crawl, starting with a seed corpus and training a fastText model to gather math web pages over four iterations. _[verified]_
  > p. 4: “As depicted in Figure 2, we present an iterative pipeline that demonstrates how to systematically gather a large-scale mathematical corpus from Common Crawl, starting with a seed corpus (e.g., a small but high-quality collection of math-related dataset).”
- To prevent benchmark contamination, web pages containing 10-gram strings (or 3-to-9-gram exact matches) matching evaluation benchmarks are filtered out from the math training corpus. _[verified]_
  > p. 5: “The filtering criteria are as follows: any text segment containing a 10-gram string that matches exactly with any sub-string from the evaluation benchmarks is removed from our math training corpus.”
- DeepSeekMath-Base 7B is initialized with DeepSeek-Coder-Base-v1.5 7B and trained for 500B tokens on a mix of DeepSeekMath Corpus, AlgebraicStack, arXiv, GitHub code, and natural language data. _[partial]_
  > p. 7: “Our model is initialized with DeepSeek-Coder-Base-v1.5 7B (Guo et al., 2024) and trained for 500B tokens.”
- Mathematical instruction-tuning is performed on DeepSeekMath-Base using a dataset of 776K examples covering chain-of-thought, program-of-thought, and tool-integrated reasoning formats. _[partial]_
  > p. 10: “In this section, we introduce DeepSeekMath-Instruct 7B which undergoes mathematical instruction tuning based on DeepSeekMath-Base.”
- Group Relative Policy Optimization (GRPO) is proposed as a reinforcement learning algorithm that eliminates the need for a separate value function by using the average reward of multiple sampled outputs as the baseline. _[verified]_
  > p. 13: “To address this, as shown in Figure 4, we propose Group Relative Policy Optimization (GRPO), which obviates the need for additional value function approximation as in PPO, and instead uses the average reward of multiple sampled outputs, produced in response to the same question, as the baseline.”

## Novelty

- GRPO avoids the memory and computational burden of approximating a separate value function in PPO by using the average reward of multiple sampled outputs for the same question as the baseline. _[verified]_
  > p. 13: “To address this, as shown in Figure 4, we propose Group Relative Policy Optimization (GRPO), which obviates the need for additional value function approximation as in PPO, and instead uses the average reward of multiple sampled outputs, produced in response to the same question, as the baseline.”

## Datasets

- OpenWebMath (13.6B) _[verified]_
  > p. 4: “First, we choose OpenWebMath (Paster et al., 2023), a collection of high-quality mathematical web texts, as our initial seed corpus.”
- Common Crawl (40B HTML pages) _[verified]_
  > p. 4: “Specifically, we randomly select 500,000 data points from the seed corpus as positive training examples and another 500,000 web pages from Common Crawl as negative ones.”
- DeepSeekMath Corpus (120.2B) _[partial]_
  > p. 5: “After four iterations of data collection, we end up with 35.5M mathematical web pages, totaling 120B tokens.”
- AlgebraicStack _[verified]_
  > p. 8: “The distribution of the data is as follows: 56% is from the DeepSeekMath Corpus, 4% from AlgebraicStack, 10% from arXiv, 20% is Github code, and the remaining 10% is natural language data from Common Crawl in both English and Chinese.”
- arXiv _[verified]_
  > p. 8: “The distribution of the data is as follows: 56% is from the DeepSeekMath Corpus, 4% from AlgebraicStack, 10% from arXiv, 20% is Github code, and the remaining 10% is natural language data from Common Crawl in both English and Chinese.”
- Github _[verified]_
  > p. 8: “The distribution of the data is as follows: 56% is from the DeepSeekMath Corpus, 4% from AlgebraicStack, 10% from arXiv, 20% is Github code, and the remaining 10% is natural language data from Common Crawl in both English and Chinese.”
- MathPile (8.9B) _[verified]_
  > p. 6: “MathPile | 8.9B | 2.7% | 3.3% | 2.2% | 12.5% | 15.7% | 1.2% | 0.0% | 2.8%”
- Proof-Pile-2 (51.9B) _[verified]_
  > p. 6: “Proof-Pile-2 | 51.9B | 14.3% | 11.2% | 3.7% | 43.8% | 29.2% | 19.9% | 5.1% | 11.7%”
- ArXiv-RedPajama _[verified]_
  > p. 17: “ArXiv-RedPajama | 3.3% | 3.4% | 4.0% | 9.4% | 9.0% | 7.4% | 0.8% | 2.3%”

## Baselines

- Minerva _[verified]_
  > p. 8: “Minerva | 7B | 16.2% | 14.1% | 7.7% | - | 35.6% | - | - | -”
- Mistral _[verified]_
  > p. 8: “Mistral | 7B | 40.3% | 14.3% | 9.2% | 71.9% | 51.1% | 44.9% | 5.1% | 23.4%”
- Llemma _[verified]_
  > p. 8: “Llemma | 7B | 37.4% | 18.1% | 6.3% | 59.4% | 43.1% | 43.4% | 11.9% | 23.6%”
- CodeLlama _[verified]_
  > p. 9: “CodeLlama | 7B | 27.1% | 17.2% | 16.3% | 17.6%”
- InternLM2-Math _[verified]_
  > p. 12: “InternLM2-Math | 20B | 82.6% | 37.7% | - | -”
- Qwen _[verified]_
  > p. 12: “Qwen | 72B | 78.9% | 35.2% | - | -”
- WizardMath-v1.1 _[verified]_
  > p. 12: “WizardMath-v1.1 | 7B | 83.2% | 33.0% | - | -”
- MetaMath _[verified]_
  > p. 12: “MetaMath | 70B | 82.3% | 26.6% | 66.4% | 70.9%”

## Metrics

- Pass@1 _[verified]_
  > p. 9: “HumanEval (Pass@1)”

## Hyperparameters

- vector dimension: 256 _[verified]_
  > p. 4: “We employ an open-source libraryfoot_0 for training, configuring the vector dimension to 256, learning rate to 0.1, the maximum length”
- learning rate: 0.1 _[verified]_
  > p. 4: “We employ an open-source libraryfoot_0 for training, configuring the vector dimension to 256, learning rate to 0.1, the maximum length”
- model size (pre-training): 1.3B _[verified]_
  > p. 6: “We apply math training to a general pre-trained language model with 1.3B parameters, which shares the same framework as the DeepSeek LLMs (DeepSeek-AI, 2024), denoted as DeepSeek-LLM 1.3B.”
- training tokens (pre-training): 150B _[verified]_
  > p. 6: “We separately train a model on each mathematical corpus for 150B tokens.”
- optimizer (pre-training): AdamW _[verified]_
  > p. 6: “Following the training practice of DeepSeek LLMs, we use the AdamW optimizer (Loshchilov and Hutter, 2017) with 1 = 0.9, 2 = 0.95, and weight_decay = 0.1, along with a multi-step learning rate schedule where the learning rate reaches the peak after 2,000 warmup steps, decreases to its 31.6% after 80% of the training process, and further decreases to 10.0% of the peak after 90% of the training process.”
- weight decay (pre-training): 0.1 _[verified]_
  > p. 6: “Following the training practice of DeepSeek LLMs, we use the AdamW optimizer (Loshchilov and Hutter, 2017) with 1 = 0.9, 2 = 0.95, and weight_decay = 0.1, along with a multi-step learning rate schedule where the learning rate reaches the peak after 2,000 warmup steps, decreases to its 31.6% after 80% of the training process, and further decreases to 10.0% of the peak after 90% of the training process.”
- warmup steps (pre-training): 2,000 _[verified]_
  > p. 6: “Following the training practice of DeepSeek LLMs, we use the AdamW optimizer (Loshchilov and Hutter, 2017) with 1 = 0.9, 2 = 0.95, and weight_decay = 0.1, along with a multi-step learning rate schedule where the learning rate reaches the peak after 2,000 warmup steps, decreases to its 31.6% after 80% of the training process, and further decreases to 10.0% of the peak after 90% of the training process.”
- learning rate (pre-training): 5.3e-4 _[verified]_
  > p. 6: “We set the maximum value of learning rate to 5.3e-4, and use a batch size of 4M tokens with a 4K context length.”
- batch size (pre-training): 4M tokens _[verified]_
  > p. 6: “We set the maximum value of learning rate to 5.3e-4, and use a batch size of 4M tokens with a 4K context length.”
- context length (pre-training): 4K _[verified]_
  > p. 6: “We set the maximum value of learning rate to 5.3e-4, and use a batch size of 4M tokens with a 4K context length.”
- training tokens (pre-training): 500B _[verified]_
  > p. 7: “Our model is initialized with DeepSeek-Coder-Base-v1.5 7B (Guo et al., 2024) and trained for 500B tokens.”
- learning rate (pre-training): 4.2e-4 _[verified]_
  > p. 8: “We mainly adopt the training setting specified in Section 2.2.1, except that we set the maximum value of the learning rate to 4.2e-4 and use a batch size of 10M tokens.”
- batch size (pre-training): 10M tokens _[verified]_
  > p. 8: “We mainly adopt the training setting specified in Section 2.2.1, except that we set the maximum value of the learning rate to 4.2e-4 and use a batch size of 10M tokens.”
- context length (instruction tuning): 4K tokens _[verified]_
  > p. 10: “Training examples are randomly concatenated until reaching a maximum context length of 4K tokens.”
- epochs/steps (instruction tuning): 500 steps _[verified]_
  > p. 10: “We train the model for 500 steps with a batch size of 256 and a constant learning rate of 5e-5.”
- batch size (instruction tuning): 256 _[verified]_
  > p. 10: “We train the model for 500 steps with a batch size of 256 and a constant learning rate of 5e-5.”
- learning rate (instruction tuning): 5e-5 _[verified]_
  > p. 10: “We train the model for 500 steps with a batch size of 256 and a constant learning rate of 5e-5.”
- learning rate (reward model training): 2e-5 _[verified]_
  > p. 15: “We train our initial reward model based on the DeepSeekMath-Base 7B with a learning rate of 2e-5.”
- learning rate (RL): 1e-6 _[verified]_
  > p. 15: “For GRPO, we set the learning rate of the policy model as 1e-6.”
- KL coefficient (RL): 0.04 _[verified]_
  > p. 15: “The KL coefficient is 0.04.”
- outputs per question (RL): 64 _[verified]_
  > p. 15: “For each question, we sample 64 outputs.”
- max length (RL): 1024 _[verified]_
  > p. 15: “The max length is set to 1024, and the training batch size is 1024.”
- batch size (RL): 1024 _[verified]_
  > p. 15: “The max length is set to 1024, and the training batch size is 1024.”

## Ablations

- Investigation of how code affects mathematical reasoning under different training settings _[verified]_
  > p. 16: “Table 6: Investigation of how code affects mathematical reasoning under different training settings.We experiment with DeepSeek-LLM 1.3B, and evaluate its mathematical reasoning performance without and with tool use via few-shot chain-of-thought prompting and few-shot program-of-thought prompting, respectively.”
- Investigation of how different settings of code and math training affect model performance of language understanding, reasoning, and coding _[verified]_
  > p. 17: “Table 7: Investigation of how different settings of code and math training affect model performance of language understanding, reasoning, and coding.We experiment with DeepSeek-LLM 1.3B.We evaluate the models on MMLU and BBH using few-shot chain-of-thought prompting.On HumanEval and MBPP, we conduct zero-shot and few-shot evaluations, respectively.”
- Effect of math training on different arXiv datasets _[verified]_
  > p. 17: “Table 8: Effect of math training on different arXiv datasets.Model performance is evaluated with few-shot chain-of-thought prompting.”

## Claims

- DeepSeekMath 7B scores 51.7% on the competition-level MATH benchmark without external toolkits. _[verified]_
  > p. 1: “DeepSeekMath 7B has achieved an impressive score of 51.7% on the competition-level MATH benchmark without relying on external toolkits and voting techniques, approaching the performance level of Gemini-Ultra and GPT-4.”
- Self-consistency over 64 samples achieves 60.9% on the MATH benchmark. _[verified]_
  > p. 1: “Self-consistency over 64 samples from DeepSeekMath 7B achieves 60.9% on MATH.”
- DeepSeekMath-Base 7B achieves 64.2% on GSM8K and 36.2% on the MATH dataset, outperforming Minerva 540B. _[verified]_
  > p. 2: “The evaluation results indicate that the large-scale corpus is of high quality, as our base model DeepSeekMath-Base 7B achieves 64.2% on GSM8K (Cobbe et al., 2021) and 36.2% on the competition-level MATH dataset (Hendrycks et al., 2021), outperforming Minerva 540B (Lewkowycz et al., 2022a).”
- GRPO provides improvements on in-domain and out-of-domain mathematical tasks. _[verified]_
  > p. 2: “By solely using a subset of English instruction tuning data, GRPO obtains a substantial improvement over the strong DeepSeekMath-Instruct, including both in-domain (GSM8K: 82.9% → 88.2%, MATH: 46.8% → 51.7%) and out-of-domain mathematical tasks (e.g., CMATH: 84.6% → 88.8%) during the reinforcement learning phase.”

## Limitations

- The conclusion regarding arXiv papers being ineffective has certain limitations and unstudied aspects. _[verified]_
  > p. 18: “However, this conclusion has its limitations and should be taken with a grain of salt.”
- The model has weaker performance on geometry and theorem-proof compared to closed-source models. _[verified]_
  > p. 22: “Although DeepSeekMath achieves impressive scores on quantitative reasoning benchmarks, its capability on geometry and theorem-proof are relatively weaker than closed models.”
- DeepSeekMath shows similar performance in zero-shot and few-shot evaluation due to model scale limitations. _[partial]_
  > p. 22: “In addition, restricted by the model scale, DeepSeekMath is worse than GPT-4 on few-shot capability.”

## Future work

- Further exploration is required regarding the impact of arXiv tokens. _[verified]_
  > p. 18: “Thus, further exploration is required, which we leave for future studies.”
- Explore the reinforcement learning pipeline on out-of-distribution question prompts using advanced sampling strategies. _[verified]_
  > p. 21: “In the future, we will explore our RL pipeline on out-of-distribution question prompts, in conjunction with advanced sampling (decoding) strategies, like those based on tree-search methods (Yao et al., 2023).”
- Explore reinforcement learning algorithms that are robust against noisy reward signals. _[verified]_
  > p. 22: “To this end, we will explore the reinforcement learning algorithm that is robust against noisy reward signals.”
- Improve the engineered data selection pipeline to construct higher quality pre-trained corpora and explore potential directions for effective RL. _[verified]_
  > p. 22: “In the future, we will further improve our engineered data selection pipeline to construct more high-quality pre-trained corpus.”

## Code

- https://github.com/InternLM/InternLM-Math _[verified]_
  > p. 11: “https://github.com/InternLM/InternLM-Math”
- https://github.com/openai/prm800k/issues/12 _[verified]_
  > p. 22: “https://github.com/openai/prm800k/issues/12#issuecomment-1728491852”


## 1506.01497

# Faster R-CNN: Towards Real-Time Object Detection with Region Proposal Networks

Shaoqing Ren, Kaiming He, Ross Girshick, Jian Sun, • R Girshick
2016 · arXiv:1506.01497v3[cs.CV]

## Problem

- Region proposal computation has become a computational bottleneck in state-of-the-art object detection networks. _[verified]_
  > p. 1: “Advances like SPPnet [1] and Fast R-CNN [2] have reduced the running time of these detection networks, exposing region proposal computation as a bottleneck.”

## Task

- Object detection _[verified]_
  > p. 1: “For the very deep VGG-16 model [3], our detection system has a frame rate of 5fps (including all steps) on a GPU, while achieving state-of-the-art object detection accuracy on PASCAL VOC 2007, 2012, and MS COCO datasets with only 300 proposals per image.”

## Contributions

- Introduction of a Region Proposal Network (RPN) that shares full-image convolutional features with the detection network for nearly cost-free region proposals. _[verified]_
  > p. 1: “In this work, we introduce a Region Proposal Network (RPN) that shares full-image convolutional features with the detection network, thus enabling nearly cost-free region proposals.”
- Merging RPN and Fast R-CNN into a single network that shares convolutional features. _[partial]_
  > p. 1: “We further merge RPN and Fast R-CNN into a single network by sharing their convolutional features-using the recently popular terminology of neural networks with "attention" mechanisms, the RPN component tells the unified network where to look.”
- Introduction of novel anchor boxes as references at multiple scales and aspect ratios to efficiently predict region proposals. _[verified]_
  > p. 1: “In contrast to prevalent methods [8], [9], [1], [2] that use pyramids of images (Figure 1, a) or pyramids of filters (Figure 1, b), we introduce novel "anchor" boxes that serve as references at multiple scales and aspect ratios.”

## Method

- The object detection system consists of a Region Proposal Network (RPN) that proposes regions and a Fast R-CNN detector that uses these proposals, forming a single unified network. _[partial]_
  > p. 3: “Our object detection system, called Faster R-CNN, is composed of two modules.”
- The RPN slides a small network over convolutional feature maps and maps each window to lower-dimensional features fed into box-regression and box-classification layers. _[partial]_
  > p. 3: “To generate region proposals, we slide a small network over the convolutional feature map output by the last shared convolutional layer.”
- Anchor boxes of multiple scales and aspect ratios are used at each sliding-window position to simultaneously predict region proposals and handle multiple scales efficiently. _[partial]_
  > p. 4: “An anchor is centered at the sliding window in question, and is associated with a scale and aspect ratio (Figure 3, left).”
- The training objective minimizes a multi-task loss function combining classification log loss and smooth L1 bounding box regression loss. _[verified]_
  > p. 5: “With these definitions, we minimize an objective function following the multi-task loss in Fast R-CNN [2].”
- Shared features between RPN and Fast R-CNN are learned using a pragmatic 4-step alternating optimization training algorithm. _[verified]_
  > p. 6: “In this paper, we adopt a pragmatic 4-step training algorithm to learn shared features via alternating optimization.”

## Novelty

- Unlike non-translation-invariant methods such as MultiBox, the proposed approach is fully translation invariant in both anchors and proposal computation functions. _[verified]_
  > p. 4: “An important property of our approach is that it is translation invariant, both in terms of the anchors and the functions that compute proposals relative to the anchors.”
- The anchor-based multi-scale design uses a pyramid of anchors instead of traditional image/feature pyramids or filter pyramids, which is more cost-efficient. _[verified]_
  > p. 4: “As a comparison, our anchor-based method is built on a pyramid of anchors, which is more cost-efficient.”

## Datasets

- PASCAL VOC 2007 (trainval and test, about 5k trainval images and 5k test images over 20 object categories) _[verified]_
  > p. 7: “We comprehensively evaluate our method on the PASCAL VOC 2007 detection benchmark [11].”
- PASCAL VOC 2012 _[verified]_
  > p. 7: “We also provide results on the PASCAL VOC 2012 benchmark for a few models.”
- Microsoft COCO (training set, validation set, and test-dev set, 80k images on the training set, 40k images on the validation set, and 20k images on the test-dev set) _[verified]_
  > p. 10: “We present more results on the Microsoft COCO object detection dataset [12].”

## Baselines

- Selective Search _[verified]_
  > p. 7: “For Selective Search (SS) [4], we generate about 2000 proposals by the "fast" mode.”
- EdgeBoxes _[verified]_
  > p. 7: “For EdgeBoxes (EB) [6], we generate the proposals by the default EB setting tuned for 0.7 7. www.robots.ox.ac.uk/ ∼ vgg/research/very deep/ IoU.”
- OverFeat _[verified]_
  > p. 10: “The OverFeat paper [9] proposes a detection method that uses regressors and classifiers on sliding windows over convolutional feature maps.”

## Metrics

- detection mean Average Precision _[verified]_
  > p. 7: “We primarily evaluate detection mean Average Precision (mAP), because this is the actual metric for object detection (rather than focusing on object proposal proxy metrics).”
- Recall-to-IoU _[unsupported]_
  > p. 9: “It is more appropriate to use this metric to diagnose the proposal method than to evaluate it.”
- mAP averaged for IoU in [0.5 : 0.05 : 0.95] and mAP@0.5 _[verified]_
  > p. 10: “We evaluate the mAP averaged for IoU ∈ [0.5 : 0.05 : 0.95] (COCO's standard metric, simply denoted as mAP@[.5, .95]) and mAP@0.5 (PASCAL VOC's metric).”

## Hyperparameters

- lambda: 10 _[verified]_
  > p. 5: “By default we set λ = 10, and thus both cls and reg terms are roughly equally weighted.”
- learning rate: 0.001 for 60k mini-batches, and 0.0001 for the next 20k mini-batches _[verified]_
  > p. 5: “We use a learning rate of 0.001 for 60k mini-batches, and 0.0001 for the next 20k mini-batches on the PASCAL VOC dataset.”
- momentum: 0.9 _[verified]_
  > p. 5: “We use a momentum of 0.9 and a weight decay of 0.0005 [37].”
- weight decay: 0.0005 _[verified]_
  > p. 5: “We use a momentum of 0.9 and a weight decay of 0.0005 [37].”
- learning rate: 0.003 for 240k iterations and then 0.0003 for 80k iterations _[verified]_
  > p. 10: “The RPN step and Fast R-CNN step are both trained for 240k iterations with a learning rate of 0.003 and then for 80k iterations with 0.0003.”

## Compute

- 8-GPU implementation _[verified]_
  > p. 10: “We train our models on an 8-GPU implementation, and the effective mini-batch size becomes 8 for RPN (1 per GPU) and 16 for Fast R-CNN (2 per GPU).”

## Ablations

- Sharing convolutional layers between the RPN and Fast R-CNN detection network _[verified]_
  > p. 7: “First, we show the effect of sharing convolutional layers between the RPN and Fast R-CNN detection network.”
- Disentangling the RPN's influence on training the Fast R-CNN detection network by changing proposal regions used at test-time _[verified]_
  > p. 7: “Next, we disentangle the RPN's influence on training the Fast R-CNN detection network.”
- Investigating the roles of RPN's cls and reg outputs by turning off either of them at test-time _[verified]_
  > p. 8: “Next, we separately investigate the roles of RPN's cls and reg outputs by turning off either of them at test-time.”
- Evaluating the effects of more powerful networks on the proposal quality of RPN alone using VGG-16 _[partial]_
  > p. 8: “We also evaluate the effects of more powerful networks on the proposal quality of RPN alone.”
- Investigating settings of anchors with different scales and aspect ratios _[verified]_
  > p. 9: “In Table 8 we investigate the settings of anchors.”
- Comparing different values of lambda in Equation 1 _[verified]_
  > p. 9: “In Table 9 we compare different values of λ in Equation (1).”
- Comparing one-stage and two-stage detection systems _[verified]_
  > p. 10: “To compare the one-stage and two-stage systems, we emulate the OverFeat system (and thus also circumvent other differences of implementation details) by one-stage Fast R-CNN.”

## Claims

- The detection system achieves a frame rate of 5fps on a GPU while achieving state-of-the-art accuracy. _[verified]_
  > p. 1: “For the very deep VGG-16 model [3], our detection system has a frame rate of 5fps (including all steps) on a GPU, while achieving state-of-the-art object detection accuracy on PASCAL VOC 2007, 2012, and MS COCO datasets with only 300 proposals per image.”
- Faster R-CNN and RPN formed the foundation of several 1st-place winning entries in ILSVRC and COCO 2015 competitions. _[verified]_
  > p. 1: “In ILSVRC and COCO 2015 competitions, Faster R-CNN and RPN are the foundations of the 1st-place winning entries in several tracks.”
- The marginal cost for computing proposals is small, such as 10ms per image. _[verified]_
  > p. 1: “By sharing convolutions at test-time, the marginal cost for computing proposals is small (e.g., 10ms per image).”

## Code

- https://github.com/shaoqingren/faster_ _[verified]_
  > p. 2: “Code has been made publicly available at https://github.com/shaoqingren/faster_ rcnn (in MATLAB) and https://github.com/ rbgirshick/py-faster-rcnn (in Python).”
- https://github.com/rbgirshick/py-faster-rcnn _[verified]_
  > p. 2: “Code has been made publicly available at https://github.com/shaoqingren/faster_ rcnn (in MATLAB) and https://github.com/ rbgirshick/py-faster-rcnn (in Python).”


## 1505.04597

# U-Net: Convolutional Networks for Biomedical Image Segmentation

Olaf Ronneberger, Philipp Fischer, Thomas Brox
2015 · arXiv:1505.04597v1[cs.CV]

## Problem

- Successful training of deep networks typically requires thousands of annotated training samples, which are usually beyond reach in biomedical tasks. _[partial]_
  > p. 1: “Hence, thousands of training images are usually beyond reach in biomedical tasks.”
- Sliding-window convolutional networks are slow and face a trade-off between localization accuracy and context use. _[partial]_
  > p. 2: “First, it is quite slow because the network must be run separately for each patch, and there is a lot of redundancy due to overlapping patches.”

## Task

- biomedical image segmentation _[verified]_
  > p. 1: “However, in many visual tasks, especially in biomedical image processing, the desired output should include localization, i.e., a class label is supposed to be assigned to each pixel.”
- cell tracking _[verified]_
  > p. 1: “Using the same network trained on transmitted light microscopy images (phase contrast and DIC) we won the ISBI cell tracking challenge 2015 in these categories by a large margin.”

## Contributions

- We present a network and training strategy relying on strong data augmentation to efficiently use available annotated samples. _[verified]_
  > p. 1: “In this paper, we present a network and training strategy that relies on the strong use of data augmentation to use the available annotated samples more efficiently.”
- We modify and extend the fully convolutional network architecture to work with very few training images and yield more precise segmentations. _[verified]_
  > p. 2: “We modify and extend this architecture such that it works with very few training images and yields more precise segmentations; see Figure 1.”
- We propose a weighted loss function to separate touching objects of the same class. _[verified]_
  > p. 3: “To this end, we propose the use of a weighted loss, where the separating background labels between touching cells obtain a large weight in the loss function.”

## Method

- The network architecture consists of a contracting path for context and an expansive path for precise localization. _[verified]_
  > p. 4: “It consists of a contracting path (left side) and an expansive path (right side).”
- The network is trained using stochastic gradient descent with a high momentum of 0.99 and a batch size of a single image. _[partial]_
  > p. 4: “The input images and their corresponding segmentation maps are used to train the network with the stochastic gradient descent implementation of Caffe [6].”
- The objective function combines a pixel-wise soft-max over the final feature map with a cross entropy loss function. _[verified]_
  > p. 4: “The energy function is computed by a pixel-wise soft-max over the final feature map combined with the cross entropy loss function.”
- Weights are initialized from a Gaussian distribution with a standard deviation of square root of two over N to ensure unit variance per feature map. _[verified]_
  > p. 5: “For a network with our architecture (alternating convolution and ReLU layers) this can be achieved by drawing the initial weights from a Gaussian distribution with a standard deviation of 2/N , where N denotes the number of incoming nodes of one neuron [5].”
- Data augmentation is performed using random elastic deformations, shift and rotation invariance, and drop-out layers. _[partial]_
  > p. 6: “Especially random elastic deformations of the training samples seem to be the key concept to train a segmentation network with very few annotated images.”

## Datasets

- EM segmentation challenge (training, test, 30 images (512x512 pixels)) _[partial]_
  > p. 6: “The data set is provided by the EM segmentation challenge [14] that was started at ISBI 2012 and is still open for new contributions.”
- PhC-U373 (training, 35 partially annotated training images) _[partial]_
  > p. 7: “The first data set "PhC-U373" 2 contains Glioblastoma-astrocytoma U373 cells on a polyacrylimide substrate recorded by phase contrast microscopy (see Figure 4a,b and Supp. Material).”
- DIC-HeLa (training, 20 partially annotated training images) _[partial]_
  > p. 7: “The second data set "DIC-HeLa" 3 are HeLa cells on a flat glass recorded by differential interference contrast (DIC) microscopy (see Figure 3, Figure 4c,d and Supp. Material).”

## Baselines

- Sliding-window convolutional network by Ciresan et al. _[verified]_
  > p. 6: “This is significantly better than the sliding-window convolutional network result by Ciresan et al. [1], whose best submission had a warping error of 0.000420 and a rand error of 0.0504.”
- DIVE-SCI _[verified]_
  > p. 6: “2. | DIVE-SCI | 0.000355 | 0.0305 | 0.0584”
  > p. 6: “4. | DIVE | 0.000430 | 0.0545 | 0.0582”
- IDSIA _[verified]_
  > p. 6: “3. | IDSIA [1] | 0.000420 | 0.0504 | 0.0613”
  > p. 6: “10. | IDSIA-SCI | 0.000653 | 0.0189 | 0.1027”
- IMCB-SG (2014) _[verified]_
  > p. 7: “IMCB-SG (2014) |  | 0.2669 | 0.2935”
- KTH-SE (2014) _[verified]_
  > p. 7: “KTH-SE (2014) |  | 0.7953 | 0.4607”
- HOUS-US (2014) _[verified]_
  > p. 7: “HOUS-US (2014) |  | 0.5323 | -”
- second-best algorithm (2015) on PhC-U373 _[verified]_
  > p. 7: “Here we achieve an average IOU ("intersection over union") of 92%, which is significantly better than the second best algorithm with 83% (see Table 2).”

## Metrics

- Warping error _[verified]_
  > p. 6: “The evaluation is done by thresholding the map at 10 different levels and computation of the "warping error", the "Rand error" and the "pixel error" [14].”
- Rand error _[verified]_
  > p. 6: “The evaluation is done by thresholding the map at 10 different levels and computation of the "warping error", the "Rand error" and the "pixel error" [14].”
- Pixel error _[verified]_
  > p. 6: “The evaluation is done by thresholding the map at 10 different levels and computation of the "warping error", the "Rand error" and the "pixel error" [14].”
- IOU (Intersection over Union) _[verified]_
  > p. 7: “Here we achieve an average IOU ("intersection over union") of 92%, which is significantly better than the second best algorithm with 83% (see Table 2).”

## Hyperparameters

- batch size: a single image _[verified]_
  > p. 4: “To minimize the overhead and make maximum use of the GPU memory, we favor large input tiles over a large batch size and hence reduce the batch to a single image.”
- momentum: 0.99 _[verified]_
  > p. 4: “Accordingly we use a high momentum (0.99) such that a large number of the previously seen training samples determine the update in the current optimization step.”

## Compute

- GPU memory utilization optimized via large input tiles and a batch size of a single image. _[verified]_
  > p. 4: “To minimize the overhead and make maximum use of the GPU memory, we favor large input tiles over a large batch size and hence reduce the batch to a single image.”

## Seeds and runs

- Results averaged over 7 rotated versions of the input data. _[verified]_
  > p. 6: “The u-net (averaged over 7 rotated versions of the input data) achieves without any further pre-or postprocessing a warping error of 0.0003529 (the new best score, see Table 1) and a rand-error of 0.0382.”

## Claims

- Segmentation of a 512x512 image takes less than a second on a recent GPU. _[verified]_
  > p. 1: “Segmentation of a 512x512 image takes less than a second on a recent GPU.”
- The network outperforms the prior best sliding-window convolutional network on the ISBI challenge for segmentation of neuronal structures. _[verified]_
  > p. 1: “We show that such a network can be trained end-to-end from very few images and outperforms the prior best method (a sliding-window convolutional network) on the ISBI challenge for segmentation of neuronal structures in electron microscopic stacks.”
- The network won the ISBI cell tracking challenge 2015 by a large margin. _[verified]_
  > p. 1: “Using the same network trained on transmitted light microscopy images (phase contrast and DIC) we won the ISBI cell tracking challenge 2015 in these categories by a large margin.”

## Future work

- Apply the u-net architecture to many more tasks easily _[verified]_
  > p. 8: “We are sure that the u-net architecture can be applied easily to many more tasks.”


## 2103.14030

# Swin Transformer: Hierarchical Vision Transformer using Shifted Windows

Ze Liu, Yutong Lin, Yue Cao, Han Hu, Yixuan Wei, Zheng Zhang, Stephen Lin, Baining Guo
2021 · arXiv:2103.14030v2[cs.CV]

## Problem

- Large variations in the scale of visual entities and high pixel resolution in images pose challenges for adapting Transformers from language to vision. _[verified]_
  > p. 1: “Challenges in adapting Transformer from language to vision arise from differences between the two domains, such as large variations in the scale of visual entities and the high resolution of pixels in images compared to words in text.”

## Task

- image classification _[verified]_
  > p. 1: “These qualities of Swin Transformer make it compatible with a broad range of vision tasks, including image classification (87.3 top-1 accuracy on ImageNet-1K) and dense prediction tasks such as object detection (58.7 box AP and 51.1 mask AP on COCO testdev) and semantic segmentation (53.5 mIoU on ADE20K val).”
- object detection _[verified]_
  > p. 1: “These qualities of Swin Transformer make it compatible with a broad range of vision tasks, including image classification (87.3 top-1 accuracy on ImageNet-1K) and dense prediction tasks such as object detection (58.7 box AP and 51.1 mask AP on COCO testdev) and semantic segmentation (53.5 mIoU on ADE20K val).”
- semantic segmentation _[verified]_
  > p. 1: “These qualities of Swin Transformer make it compatible with a broad range of vision tasks, including image classification (87.3 top-1 accuracy on ImageNet-1K) and dense prediction tasks such as object detection (58.7 box AP and 51.1 mask AP on COCO testdev) and semantic segmentation (53.5 mIoU on ADE20K val).”

## Contributions

- We propose a hierarchical Transformer called Swin Transformer whose representation is computed with Shifted windows. _[verified]_
  > p. 1: “To address these differences, we propose a hierarchical Transformer whose representation is computed with Shifted windows.”

## Method

- An input RGB image is split into non-overlapping patches by a patch splitting module, and a linear embedding layer projects these raw features to an arbitrary dimension C. _[partial]_
  > p. 3: “It first splits an input RGB image into non-overlapping patches by a patch splitting module, like ViT.”
- Hierarchical representations are produced by reducing the number of tokens using patch merging layers as the network gets deeper through four stages. _[verified]_
  > p. 3: “To produce a hierarchical representation, the number of tokens is reduced by patch merging layers as the network gets deeper.”
- Swin Transformer blocks replace standard multi-head self-attention with a module based on shifted windows, followed by a 2-layer MLP with GELU nonlinearity. _[verified]_
  > p. 4: “As illustrated in Figure 3(b), a Swin Transformer block consists of a shifted window based MSA module, followed by a 2-layer MLP with GELU nonlinearity in between.”
- Self-attention is computed efficiently within local non-overlapping windows to achieve linear computational complexity relative to the image patch number. _[verified]_
  > p. 4: “For efficient modeling, we propose to compute self-attention within local windows.”
- A shifted window partitioning approach alternates between regular and shifted window configurations in consecutive blocks to introduce cross-window connections. _[verified]_
  > p. 4: “To introduce cross-window connections while maintaining the efficient computation of non-overlapping windows, we propose a shifted window partitioning approach which alternates between two partitioning configurations in consecutive Swin Transformer blocks.”
- A batch computation approach using cyclic-shifting toward the top-left direction handles shifted windows efficiently while maintaining the number of batched windows. _[verified]_
  > p. 5: “Here, we propose a more efficient batch computation approach by cyclic-shifting toward the top-left direction, as illustrated in Figure 4.”

## Novelty

- Computing self-attention within local windows reduces computational complexity from quadratic to linear compared to global self-attention. _[partial]_
  > p. 4: “Global self-attention computation is generally unaffordable for a large hw, while the window based self-attention is scalable.”
- The shifted window partitioning approach introduces cross-window connections while maintaining the efficiency of non-overlapping windows. _[verified]_
  > p. 4: “To introduce cross-window connections while maintaining the efficient computation of non-overlapping windows, we propose a shifted window partitioning approach which alternates between two partitioning configurations in consecutive Swin Transformer blocks.”

## Datasets

- ImageNet-1K (1.28M training images and 50K validation images) _[verified]_
  > p. 5: “For image classification, we benchmark the proposed Swin Transformer on ImageNet-1K [19], which contains 1.28M training images and 50K validation images from 1,000 classes.”
- COCO 2017 (training, validation, test-dev, 118K training, 5K validation and 20K test-dev images) _[verified]_
  > p. 6: “Settings Object detection and instance segmentation experiments are conducted on COCO 2017, which contains 118K training, 5K validation and 20K test-dev images.”
- ADE20K (training, validation, testing, 25K images in total) _[partial]_
  > p. 7: “ADE20K [83] is a widely-used semantic segmentation dataset, covering a broad range of 150 semantic 4. Ablation study on the shifted windows approach and different position embedding methods on three benchmarks, using the Swin-T architecture.”
- ImageNet-22K (14.2 million images and 22K classes) _[verified]_
  > p. 6: “We also pre-train on the larger ImageNet-22K dataset, which contains 14.2 million images and 22K classes.”

## Baselines

- RegNet and EfficientNet state-of-the-art ConvNets _[verified]_
  > p. 6: “Compared with the state-of-the-art ConvNets, i.e. Reg-Net [48] and EfficientNet [58], the Swin Transformer achieves a slightly better speed-accuracy trade-off.”
- Cascade Mask R-CNN, ATSS, RepPoints v2, and Sparse RCNN object detection frameworks _[verified]_
  > p. 6: “For the ablation study, we consider four typical object detection frameworks: Cascade Mask R-CNN [29,6], ATSS [79], RepPoints v2 [12], and Sparse RCNN [56] in mmdetection [10].”
- Improved HTC (denoted as HTC++) _[verified]_
  > p. 6: “For system-level comparison, we adopt an improved HTC [9] (denoted as HTC++) with instaboost [22], stronger multi-scale training [7], 6x schedule (72 epochs), soft-NMS [5], and ImageNet-22K pre-trained model as initialization.”
- ResNe(X)t and DeiT _[verified]_
  > p. 6: “We compare our Swin Transformer to standard Con- vNets, i.e. ResNe(X)t, and previous Transformer networks, e.g. DeiT.”
- ResNeXt101-64x4d _[verified]_
  > p. 7: “Swin Transformer achieves a high detection accuracy of 51.9 box AP and 45.0 mask AP, which are significant gains of +3.6 box AP and +3.3 mask AP over ResNeXt101-64x4d, which has similar model size, FLOPs and latency.”
- DeiT-S _[verified]_
  > p. 7: “The results of Swin-T are +2.5 box AP and +2.3 mask AP higher than DeiT-S with similar model size (86M vs. 80M) and significantly higher inference speed (15.3 FPS vs. 10.4 FPS).”
- ResNet-101 and ResNeSt-101 _[partial]_
  > p. 8: “It is also +4.4 mIoU higher than ResNet-101, and +2.4 mIoU higher than ResNeSt-101 [78].”
- SETR _[verified]_
  > p. 8: “Our Swin-L model with ImageNet-22K pre-training achieves 53.5 mIoU on the val set, surpassing the previous best model by +3.2 mIoU (50.3 mIoU by SETR [81] which has a larger model size).”
- Performer _[verified]_
  > p. 8: “Compared to Performer [14], which is one of the fastest Transformer architectures (see [60]), the proposed shifted window based self-attention computation and the overall Swin Transformer architectures are slightly faster (see Table 5), while achieving +2.3% top-1 accuracy compared to Performer on ImageNet-1K using Swin-T (see Table 6).”

## Metrics

- Top-1 accuracy on a single crop for image classification _[verified]_
  > p. 5: “The top-1 accuracy on a single crop is reported.”
- Box AP and mask AP for object detection and instance segmentation _[verified]_
  > p. 7: “Swin Transformer achieves a high detection accuracy of 51.9 box AP and 45.0 mask AP, which are significant gains of +3.6 box AP and +3.3 mask AP over ResNeXt101-64x4d, which has similar model size, FLOPs and latency.”
- mIoU for semantic segmentation _[unsupported]_
  > p. 8: “From these results, it can be seen that Swin-S is +5.3 mIoU higher (49.3 vs. 44.0) than DeiT-S with similar computation cost.”

## Hyperparameters

- optimizer (Regular ImageNet-1K training): AdamW _[verified]_
  > p. 5: “We employ an AdamW [37] optimizer for 300 epochs using a cosine decay learning rate scheduler and 20 epochs of linear warm-up.”
- epochs (Regular ImageNet-1K training): 300 _[verified]_
  > p. 5: “We employ an AdamW [37] optimizer for 300 epochs using a cosine decay learning rate scheduler and 20 epochs of linear warm-up.”
- warmup (Regular ImageNet-1K training): 20 _[verified]_
  > p. 5: “We employ an AdamW [37] optimizer for 300 epochs using a cosine decay learning rate scheduler and 20 epochs of linear warm-up.”
- batch size (Regular ImageNet-1K training): 1024 _[verified]_
  > p. 5: “A batch size of 1024, an initial learning rate of 0.001, and a weight decay of 0.05 are used.”
- learning rate (Regular ImageNet-1K training): 0.001 _[verified]_
  > p. 5: “A batch size of 1024, an initial learning rate of 0.001, and a weight decay of 0.05 are used.”
- weight decay (Regular ImageNet-1K training): 0.05 _[verified]_
  > p. 5: “A batch size of 1024, an initial learning rate of 0.001, and a weight decay of 0.05 are used.”
- optimizer (Object detection and instance segmentation): AdamW _[verified]_
  > p. 6: “For these four frameworks, we utilize the same settings: multi-scale training [8,56] (resizing the input such that the shorter side is between 480 and 800 while the longer side is at most 1333), AdamW [44] optimizer (initial learning rate of 0.0001, weight decay of 0.05, and batch size of 16), and 3x schedule (36 epochs).”
- learning rate (Object detection and instance segmentation): 0.0001 _[verified]_
  > p. 6: “For these four frameworks, we utilize the same settings: multi-scale training [8,56] (resizing the input such that the shorter side is between 480 and 800 while the longer side is at most 1333), AdamW [44] optimizer (initial learning rate of 0.0001, weight decay of 0.05, and batch size of 16), and 3x schedule (36 epochs).”
- weight decay (Object detection and instance segmentation): 0.05 _[verified]_
  > p. 6: “For these four frameworks, we utilize the same settings: multi-scale training [8,56] (resizing the input such that the shorter side is between 480 and 800 while the longer side is at most 1333), AdamW [44] optimizer (initial learning rate of 0.0001, weight decay of 0.05, and batch size of 16), and 3x schedule (36 epochs).”
- batch size (Object detection and instance segmentation): 16 _[verified]_
  > p. 6: “For these four frameworks, we utilize the same settings: multi-scale training [8,56] (resizing the input such that the shorter side is between 480 and 800 while the longer side is at most 1333), AdamW [44] optimizer (initial learning rate of 0.0001, weight decay of 0.05, and batch size of 16), and 3x schedule (36 epochs).”
- epochs (Object detection and instance segmentation): 36 _[verified]_
  > p. 6: “For these four frameworks, we utilize the same settings: multi-scale training [8,56] (resizing the input such that the shorter side is between 480 and 800 while the longer side is at most 1333), AdamW [44] optimizer (initial learning rate of 0.0001, weight decay of 0.05, and batch size of 16), and 3x schedule (36 epochs).”
- optimizer (Pre-training on ImageNet-22K): AdamW _[verified]_
  > p. 6: “We employ an AdamW optimizer for 90 epochs using a linear decay learning rate scheduler with a 5-epoch linear warm-up.”
- epochs (Pre-training on ImageNet-22K): 90 _[verified]_
  > p. 6: “We employ an AdamW optimizer for 90 epochs using a linear decay learning rate scheduler with a 5-epoch linear warm-up.”
- warmup (Pre-training on ImageNet-22K): 5 _[verified]_
  > p. 6: “We employ an AdamW optimizer for 90 epochs using a linear decay learning rate scheduler with a 5-epoch linear warm-up.”
- batch size (Pre-training on ImageNet-22K): 4096 _[verified]_
  > p. 6: “A batch size of 4096, an initial learning rate of 0.001, and a weight decay of 0.01 are used.”
- learning rate (Pre-training on ImageNet-22K): 0.001 _[verified]_
  > p. 6: “A batch size of 4096, an initial learning rate of 0.001, and a weight decay of 0.01 are used.”
- weight decay (Pre-training on ImageNet-22K): 0.01 _[verified]_
  > p. 6: “A batch size of 4096, an initial learning rate of 0.001, and a weight decay of 0.01 are used.”
- epochs (ImageNet-1K fine-tuning): 30 _[verified]_
  > p. 6: “In ImageNet-1K fine-tuning, we train the models for 30 epochs with a batch size of 1024, a constant learning rate of 10 -5 , and a weight decay of 10 -8 .”
- batch size (ImageNet-1K fine-tuning): 1024 _[verified]_
  > p. 6: “In ImageNet-1K fine-tuning, we train the models for 30 epochs with a batch size of 1024, a constant learning rate of 10 -5 , and a weight decay of 10 -8 .”
- learning rate (ImageNet-1K fine-tuning): 10 -5 _[verified]_
  > p. 6: “In ImageNet-1K fine-tuning, we train the models for 30 epochs with a batch size of 1024, a constant learning rate of 10 -5 , and a weight decay of 10 -8 .”
- weight decay (ImageNet-1K fine-tuning): 10 -8 _[verified]_
  > p. 6: “In ImageNet-1K fine-tuning, we train the models for 30 epochs with a batch size of 1024, a constant learning rate of 10 -5 , and a weight decay of 10 -8 .”

## Compute

- Throughput measured using a V100 GPU _[verified]_
  > p. 6: “Throughput is measured using the GitHub repository of [68] and a V100 GPU, following [63].”

## Ablations

- Ablation study on the shifted windows approach and different position embedding methods _[verified]_
  > p. 7: “4. Ablation study on the shifted windows approach and different position embedding methods on three benchmarks, using the Swin-T architecture.”
- Ablations of the shifted window approach on the three tasks _[verified]_
  > p. 8: “Ablations of the shifted window approach on the three tasks are reported in Table 4.”

## Claims

- Swin Transformer achieves 87.3 top-1 accuracy on ImageNet-1K. _[verified]_
  > p. 1: “These qualities of Swin Transformer make it compatible with a broad range of vision tasks, including image classification (87.3 top-1 accuracy on ImageNet-1K) and dense prediction tasks such as object detection (58.7 box AP and 51.1 mask AP on COCO testdev) and semantic segmentation (53.5 mIoU on ADE20K val).”
- Swin Transformer achieves 58.7 box AP and 51.1 mask AP on COCO testdev. _[verified]_
  > p. 1: “These qualities of Swin Transformer make it compatible with a broad range of vision tasks, including image classification (87.3 top-1 accuracy on ImageNet-1K) and dense prediction tasks such as object detection (58.7 box AP and 51.1 mask AP on COCO testdev) and semantic segmentation (53.5 mIoU on ADE20K val).”
- Swin Transformer achieves 53.5 mIoU on ADE20K val. _[verified]_
  > p. 1: “These qualities of Swin Transformer make it compatible with a broad range of vision tasks, including image classification (87.3 top-1 accuracy on ImageNet-1K) and dense prediction tasks such as object detection (58.7 box AP and 51.1 mask AP on COCO testdev) and semantic segmentation (53.5 mIoU on ADE20K val).”
- Swin Transformer performance surpasses the previous state-of-the-art by large margins on COCO and ADE20K. _[verified]_
  > p. 1: “Its performance surpasses the previous state-of-the-art by a large margin of +2.7 box AP and +2.6 mask AP on COCO, and +3.2 mIoU on ADE20K, demonstrating the potential of Transformer-based models as vision backbones.”

## Future work

- Investigate applying the shifted window based self-attention to natural language processing _[verified]_
  > p. 9: “As a key element of Swin Transformer, the shifted window based self-attention is shown to be effective and efficient on vision problems, and we look forward to investigating its use in natural language processing as well.”

## Code

- https://github.com/microsoft/Swin-Transformer _[verified]_
  > p. 1: “This paper presents a new vision Transformer, called Swin Transformer, that capably serves as a general-purpose backbone for computer vision. Challenges in adapting Transformer from language to vision arise from differences between the two domains, such as large variations in the scale of visual entities and the high resolution of pixels in images compared to words in text. To address these differences, we propose a hierarchical Transformer whose representation is computed with Shifted windows. The shifted windowing scheme brings greater efficiency by limiting self-attention computation to non-overlapping local windows while also allowing for cross-window connection. This hierarchical architecture has the flexibility to model at various scales and has linear computational complexity with respect to image size. These qualities of Swin Transformer make it compatible with a broad range of vision tasks, including image classification (87.3 top-1 accuracy on ImageNet-1K) and dense prediction tasks such as object detection (58.7 box AP and 51.1 mask AP on COCO testdev) and semantic segmentation (53.5 mIoU on ADE20K val). Its performance surpasses the previous state-of-theart by a large margin of +2.7 box AP and +2.6 mask AP on COCO, and +3.2 mIoU on ADE20K, demonstrating the potential of Transformer-based models as vision backbones. The hierarchical design and the shifted window approach also prove beneficial for all-MLP architectures. The code and models are publicly available at https://github. com/microsoft/Swin-Transformer.”


## 2111.06377

# Masked Autoencoders Are Scalable Vision Learners

Kaiming He, Xinlei Chen, Saining Xie, Yanghao Li, Piotr Dollár, Ross Girshick
2021 · arXiv:2111.06377v3[cs.CV]

## Problem

- Progress of autoencoding methods in computer vision lags behind natural language processing. _[verified]_
  > p. 1: “However, despite significant interest in this idea following the success of BERT, progress of autoencoding methods in vision lags behind NLP.”

## Task

- computer vision _[verified]_
  > p. 1: “This paper shows that masked autoencoders (MAE) are scalable self-supervised learners for computer vision.”

## Contributions

- We develop an asymmetric encoder-decoder architecture where the encoder operates only on visible patches and a lightweight decoder reconstructs the image. _[verified]_
  > p. 1: “First, we develop an asymmetric encoder-decoder architecture, with an encoder that operates only on the visible subset of patches (without mask tokens), along with a lightweight decoder that reconstructs the original image from the latent representation and mask tokens.”
- We find that masking a high proportion of the input image, such as 75%, yields a meaningful self-supervisory task. _[verified]_
  > p. 1: “Second, we find that masking a high proportion of the input image, e.g., 75%, yields a nontrivial and meaningful self-supervisory task.”

## Method

- An asymmetric autoencoder design consisting of an encoder that operates only on unmasked patches and a lightweight decoder that processes both encoded patches and mask tokens. _[verified]_
  > p. 3: “Unlike classical autoencoders, we adopt an asymmetric design that allows the encoder to operate only on the partial, observed signal (without mask tokens) and a lightweight decoder that reconstructs the full signal from the latent representation and mask tokens.”
- Images are divided into patches and sampled using a uniform random distribution with a high masking ratio. _[verified]_
  > p. 3: “Our sampling strategy is straightforward: we sample random patches without replacement, following a uniform distribution.”
- The encoder is a Vision Transformer applied solely to visible, unmasked patches without using mask tokens. _[partial]_
  > p. 3: “However, our encoder only operates on a small subset (e.g., 25%) of the full set.”
- The decoder is a separate series of Transformer blocks taking the full set of encoded patches and shared mask tokens with added positional embeddings. _[verified]_
  > p. 3: “The input to the MAE decoder is the full set of tokens consisting of (i) encoded visible patches, and (ii) mask tokens.”
- The model is trained to reconstruct the original image by minimizing the mean squared error on masked patches in the pixel space. _[verified]_
  > p. 4: “Our loss function computes the mean squared error (MSE) between the reconstructed and original images in the pixel space.”

## Novelty

- The use of an asymmetric encoder-decoder architecture where the encoder processes only a small subset of unmasked patches and a lightweight decoder reconstructs the full signal. _[verified]_
  > p. 3: “Unlike classical autoencoders, we adopt an asymmetric design that allows the encoder to operate only on the partial, observed signal (without mask tokens) and a lightweight decoder that reconstructs the full signal from the latent representation and mask tokens.”

## Datasets

- ImageNet-1K (IN1K) (training set) _[verified]_
  > p. 4: “We do self-supervised pre-training on the ImageNet-1K (IN1K) [13] training set.”
- COCO _[verified]_
  > p. 8: “We fine-tune Mask R-CNN [24] end-to-end on COCO [37].”
- ADE20K _[verified]_
  > p. 8: “We experiment on ADE20K [72] using UperNet [63] (see A.4).”
- iNaturalists _[verified]_
  > p. 8: “Table 6 studies transfer learning on the iNaturalists [56] and Places [71] tasks (see A.5).”
- Places _[verified]_
  > p. 8: “Table 6 studies transfer learning on the iNaturalists [56] and Places [71] tasks (see A.5).”

## Baselines

- ViT-Large backbone used in ablation studies _[verified]_
  > p. 4: “We use ViT-Large (ViT-L/16) [16] as the backbone in our ablation study.”
- MoCo v3 contrastive learning method _[verified]_
  > p. 6: “MoCo v3 [9] saturates at 300 epochs for ViT-L.”
- BEiT masked image modeling method _[verified]_
  > p. 7: “Comparing with BEiT [2], our MAE is more accurate while being simpler and faster.”
- DINO self-supervised method _[partial]_
  > p. 7: “DINO [5] | IN1K | 82.8 | - | - | -”
- Supervised training baseline _[partial]_
  > p. 8: “supervised | IN1K w/ labels | 47.4 | 49.9”

## Metrics

- Top-1 validation accuracy of a single crop _[verified]_
  > p. 4: “We report top-1 validation accuracy of a single 224×224 crop.”
- Fine-tuning (ft) and linear probing (lin) accuracy in percentage _[verified]_
  > p. 5: “We report fine-tuning (ft) and linear probing (lin) accuracy (%).”
- Box AP for object detection and mask AP for instance segmentation _[verified]_
  > p. 8: “We report box AP for object detection and mask AP for instance segmentation.”
- Mean Intersection over Union (mIoU) for semantic segmentation _[verified]_
  > p. 8: “Table 5: ADE20K semantic segmentation (mIoU) using Uper-Net.”

## Hyperparameters

- decoder depth (pre-training): 8 _[verified]_
  > p. 5: “the decoder has depth 8 and width 512, the reconstruction target is unnormalized pixels, the data augmentation is random resized cropping, the masking ratio is 75%, and the pre-training length is 800 epochs.”
- decoder width (pre-training): 512 _[verified]_
  > p. 5: “the decoder has depth 8 and width 512, the reconstruction target is unnormalized pixels, the data augmentation is random resized cropping, the masking ratio is 75%, and the pre-training length is 800 epochs.”
- masking ratio (pre-training): 75% _[verified]_
  > p. 5: “the decoder has depth 8 and width 512, the reconstruction target is unnormalized pixels, the data augmentation is random resized cropping, the masking ratio is 75%, and the pre-training length is 800 epochs.”
- pre-training length (pre-training): 800 epochs _[verified]_
  > p. 5: “the decoder has depth 8 and width 512, the reconstruction target is unnormalized pixels, the data augmentation is random resized cropping, the masking ratio is 75%, and the pre-training length is 800 epochs.”
- fine-tuning epochs (fine-tuning): 50 _[verified]_
  > p. 4: “Here fine-tuning is only for 50 epochs (vs. 200 from scratch), implying that the fine-tuning accuracy heavily depends on pre-training.”
- pre-training length (pre-training): 1600 epochs _[verified]_
  > p. 7: “The MAE models in Table 3 are pre-trained for 1600 epochs for better accuracy (Figure 7).”
- batch size (fine-tuning): 16 _[verified]_
  > p. 12: “We fine-tune end-to-end for 100 epochs with a batch size of 16.”
- fine-tuning epochs (fine-tuning): 100 _[partial]_
  > p. 12: “We fine-tune end-to-end for 100 epochs with a batch size of 16.”

## Compute

- Benchmarked using 128 TPU-v3 cores with TensorFlow _[verified]_
  > p. 5: “Table 2: Wall-clock time of our MAE training (800 epochs), benchmarked in 128 TPU-v3 cores with TensorFlow.”
- Training time of 31 hours for 1600 epochs on ViT-L using 128 TPU-v3 cores _[verified]_
  > p. 7: “For example, training ViT-L on 128 TPU-v3 cores, our MAE's training time is 31 hours for 1600 epochs and MoCo v3's is 36 hours for 300 epochs [9].”

## Ablations

- Ablation study on reconstruction targets _[verified]_
  > p. 6: “Reconstruction target. We compare different reconstruction targets in Table 1d.”
- Ablation study on data augmentation _[partial]_
  > p. 5: “(e) Data augmentation. Our MAE works with”
- Ablation study on mask sampling strategies _[verified]_
  > p. 6: “In Table 1f we compare different mask sampling strategies, illustrated in Figure 6.”
- Ablation study on decoder depth and width _[verified]_
  > p. 5: “Decoder design. Our MAE decoder can be flexibly designed, as studied in Table 1a and 1b.”

## Claims

- The approach accelerates training by 3x or more and improves accuracy. _[verified]_
  > p. 1: “Coupling these two designs enables us to train large models efficiently and effectively: we accelerate training (by 3× or more) and improve accuracy.”
- A vanilla ViT-Huge model achieves an accuracy of 87.8% using only ImageNet-1K data. _[verified]_
  > p. 1: “Our scalable approach allows for learning high-capacity models that generalize well: e.g., a vanilla ViT-Huge model achieves the best accuracy (87.8%) among methods that use only ImageNet-1K data.”

## Limitations

- Images and languages are fundamentally different signals and this distinction must be carefully handled. _[verified]_
  > p. 8: “On the other hand, we note that images and languages are signals of a different nature and this difference must be addressed carefully.”

## Future work

- The authors hope that the provided perspective will inspire future research. _[verified]_
  > p. 8: “We hope this perspective will inspire future work.”

## Ethics

- The model's predictions reflect dataset biases that can lead to negative societal impacts, and it may generate non-existent content. _[verified]_
  > p. 9: “The proposed method predicts content based on learned statistics of the training dataset and as such will reflect biases in those data, including ones with negative societal impacts.”


## 2201.03545

# A ConvNet for the 2020s

Zhuang Liu, Hanzi Mao, Chao-Yuan Wu, Christoph Feichtenhofer, Trevor Darrell, Saining Xie
2022 · arXiv:2201.03545v2[cs.CV]

## Problem

- Vanilla Vision Transformers face difficulties when applied to general computer vision tasks such as object detection and semantic segmentation. _[verified]_
  > p. 1: “A vanilla ViT, on the other hand, faces difficulties when applied to general computer vision tasks such as object detection and semantic segmentation.”
- The effectiveness of hybrid hierarchical Transformer approaches is credited to Transformers rather than convolution inductive biases. _[verified]_
  > p. 1: “However, the effectiveness of such hybrid approaches is still largely credited to the intrinsic superiority of Transformers, rather than the inherent inductive biases of convolutions.”

## Task

- image classification _[partial]_
  > p. 1: “A vanilla ViT, on the other hand, faces difficulties when applied to general computer vision tasks such as object detection and semantic segmentation.”
- object detection _[verified]_
  > p. 1: “A vanilla ViT, on the other hand, faces difficulties when applied to general computer vision tasks such as object detection and semantic segmentation.”
- semantic segmentation _[verified]_
  > p. 1: “A vanilla ViT, on the other hand, faces difficulties when applied to general computer vision tasks such as object detection and semantic segmentation.”

## Contributions

- We gradually modernize a standard ResNet toward the design of a vision Transformer and discover key performance components. _[verified]_
  > p. 1: “We gradually "modernize" a standard ResNet toward the design of a vision Transformer, and discover several key components that contribute to the performance difference along the way.”
- We propose a family of pure ConvNet models dubbed ConvNeXt that compete favorably with Transformers in accuracy and scalability. _[verified]_
  > p. 1: “The outcome of this exploration is a family of pure ConvNet models dubbed Con-vNeXt.”

## Method

- Starting from a ResNet-50 baseline, the authors progressively modernize the architecture by adopting various design choices inspired by Swin Transformers, such as macro design adjustments, inverted bottlenecks, and large kernel sizes. _[partial]_
  > p. 3: “Our starting point is a ResNet-50 model.”
- The network is trained using an enhanced training recipe close to DeiT and Swin Transformer, utilizing the AdamW optimizer, extensive data augmentations, and regularization techniques over 300 epochs. _[verified]_
  > p. 3: “In our study, we use a training recipe that is close to DeiT's [73] and Swin Transformer's [45].”
- Macro design modifications include changing the stage compute ratio to 1:1:9:1 or equivalent, and replacing the standard ResNet stem with a patchify layer using a non-overlapping convolution. _[verified]_
  > p. 4: “We replace the ResNet-style stem cell with a patchify layer implemented using a 4×4, stride 4 convolutional layer.”
- Micro-level designs are updated to match Transformer properties, including the use of depthwise convolutions for ResNeXt-style grouped convolutions, inverted bottlenecks, 7x7 large kernels, a single GELU activation per block, and Layer Normalization instead of BatchNorm. _[verified]_
  > p. 5: “From now on, we will use one LayerNorm as our choice of normalization in each residual block.”

## Novelty

- The paper demonstrates that design choices from vision Transformers can be systematically mapped and adapted to standard ConvNets to create a modernized architecture called ConvNeXt. _[verified]_
  > p. 5: “Intriguingly, a significant portion of the design choices taken in a vision Transformer may be mapped to ConvNet instantiations.”
- The authors show that while individual architectural components were previously researched separately in the past decade, combining them collectively yields a pure ConvNet that can outperform the Swin Transformer without specialized modules like shifted window attention. _[partial]_
  > p. 6: “It is worth noting that all design choices discussed so far are adapted from vision Transformers.”

## Datasets

- ImageNet-1K _[verified]_
  > p. 6: “Training on ImageNet-1K.”
- ImageNet-22K _[verified]_
  > p. 6: “Pre-training on ImageNet-22K.”
- COCO _[verified]_
  > p. 8: “We finetune Mask R-CNN [27] and Cascade Mask R-CNN [9] on the COCO dataset with ConvNeXt backbones.”
- ADE20K _[verified]_
  > p. 8: “We also evaluate ConvNeXt backbones on the ADE20K semantic segmentation task with UperNet [85].”

## Baselines

- ResNet-50/200 _[verified]_
  > p. 3: “Thus, the first step of our exploration is to train a baseline model with the vision Transformer training procedure, in this case, ResNet-50/200.”
- DeiT _[verified]_
  > p. 6: “Table 1 (upper) shows the result comparison with two recent Transformer variants, DeiT [73] and Swin Transformers [45], as well as two ConvNets from architecture search -RegNets [54], EfficientNets [71] and EfficientNetsV2 [72].”
- Swin Transformers _[verified]_
  > p. 6: “Table 1 (upper) shows the result comparison with two recent Transformer variants, DeiT [73] and Swin Transformers [45], as well as two ConvNets from architecture search -RegNets [54], EfficientNets [71] and EfficientNetsV2 [72].”
- RegNets _[verified]_
  > p. 6: “Table 1 (upper) shows the result comparison with two recent Transformer variants, DeiT [73] and Swin Transformers [45], as well as two ConvNets from architecture search -RegNets [54], EfficientNets [71] and EfficientNetsV2 [72].”
- EfficientNets _[verified]_
  > p. 6: “Table 1 (upper) shows the result comparison with two recent Transformer variants, DeiT [73] and Swin Transformers [45], as well as two ConvNets from architecture search -RegNets [54], EfficientNets [71] and EfficientNetsV2 [72].”

## Metrics

- Top-1 Accuracy _[verified]_
  > p. 10: “The ImageNet-1K top-1 accuracies and FLOPs for each step are shown in Table 10 and 11.”
- AP _[verified]_
  > p. 8: “AP numbers of the ResNet-50 and X101 models are from [45].”
- mIoU _[unlocated]_
  > p. 8: “In Appendix B, we report validation mIoU with multi-scale testing.”

## Hyperparameters

- optimizer (Training on ImageNet-1K): AdamW _[verified]_
  > p. 6: “We train ConvNeXts for 300 epochs using AdamW [46] with a learning rate of 4e-3.”
- learning rate (Training on ImageNet-1K): 4e-3 _[verified]_
  > p. 6: “We train ConvNeXts for 300 epochs using AdamW [46] with a learning rate of 4e-3.”
- warmup epochs (Training on ImageNet-1K): 20 _[verified]_
  > p. 6: “There is a 20-epoch linear warmup and a cosine decaying schedule afterward.”
- batch size (Training on ImageNet-1K): 4096 _[verified]_
  > p. 6: “We use a batch size of 4096 and a weight decay of 0.05.”
- weight decay (Training on ImageNet-1K): 0.05 _[verified]_
  > p. 6: “We use a batch size of 4096 and a weight decay of 0.05.”
- epochs (Training on ImageNet-1K): 300 _[verified]_
  > p. 6: “We train ConvNeXts for 300 epochs using AdamW [46] with a learning rate of 4e-3.”
- epochs (Pre-training on ImageNet-22K): 90 _[verified]_
  > p. 6: “We pre-train ConvNeXts on ImageNet-22K for 90 epochs with a warmup of 5 epochs.”
- warmup epochs (Pre-training on ImageNet-22K): 5 _[verified]_
  > p. 6: “We pre-train ConvNeXts on ImageNet-22K for 90 epochs with a warmup of 5 epochs.”
- epochs (Fine-tuning on ImageNet-1K): 30 _[verified]_
  > p. 6: “We fine-tune ImageNet-22K pre-trained models on ImageNet-1K for 30 epochs.”
- optimizer (Fine-tuning on ImageNet-1K): AdamW _[verified]_
  > p. 6: “We use AdamW, a learning rate of 5e-5, cosine learning rate schedule, layer-wise learning rate decay [6,12], no warmup, a batch size of 512, and weight decay of 1e-8.”
- learning rate (Fine-tuning on ImageNet-1K): 5e-5 _[verified]_
  > p. 6: “We use AdamW, a learning rate of 5e-5, cosine learning rate schedule, layer-wise learning rate decay [6,12], no warmup, a batch size of 512, and weight decay of 1e-8.”
- batch size (Fine-tuning on ImageNet-1K): 512 _[verified]_
  > p. 6: “We use AdamW, a learning rate of 5e-5, cosine learning rate schedule, layer-wise learning rate decay [6,12], no warmup, a batch size of 512, and weight decay of 1e-8.”
- weight decay (Fine-tuning on ImageNet-1K): 1e-8 _[verified]_
  > p. 6: “We use AdamW, a learning rate of 5e-5, cosine learning rate schedule, layer-wise learning rate decay [6,12], no warmup, a batch size of 512, and weight decay of 1e-8.”
- iterations (Semantic segmentation on ADE20K): 160K _[verified]_
  > p. 8: “All model variants are trained for 160K iterations with a batch size of 16.”
- batch size (Semantic segmentation on ADE20K): 16 _[verified]_
  > p. 8: “All model variants are trained for 160K iterations with a batch size of 16.”

## Compute

- A100 GPU throughput benchmarking _[verified]_
  > p. 8: “We measure FPS on an A100 GPU.”

## Seeds and runs

- Three random seeds averaged for ResNet-50 regime _[verified]_
  > p. 3: “Each reported accuracy on the ResNet-50 regime is an average obtained from training with three different random seeds.”

## Ablations

- Modernization steps on ResNet-50 and ResNet-200 architectures and training procedures _[verified]_
  > p. 10: “Here we provide detailed tabulated results for the modernization experiments, at both ResNet-50 / Swin-T and ResNet-200 / Swin-B regimes.”

## Claims

- ConvNeXt achieves 87.8% ImageNet top-1 accuracy and outperforms Swin Transformers on COCO and ADE20K. _[verified]_
  > p. 1: “Constructed entirely from standard ConvNet modules, ConvNeXts compete favorably with Transformers in terms of accuracy and scalability, achieving 87.8% ImageNet top-1 accuracy and outperforming Swin Transformers on COCO detection and ADE20K segmentation, while maintaining the simplicity and efficiency of standard ConvNets.”

## Limitations

- ConvNeXts might not be suitable for all computer vision applications, such as multi-modal learning or tasks requiring discretized, sparse, or structured outputs. _[partial]_
  > p. 12: “ConvNeXt may be more suited for certain tasks, while Transformers may be more flexible for others.”

## Future work

- Further investigation into the robustness behavior comparing ConvNeXt and Transformers. _[verified]_
  > p. 12: “Further investigation on the robustness behavior of ConvNeXt vs. Transformer will be an interesting research direction.”

## Ethics

- Investigating large model designs leads to increased carbon emissions. _[verified]_
  > p. 12: “Investigating those model designs inevitably results in an increase in carbon emissions.”
- Large models and datasets raise concerns regarding model robustness and fairness. _[verified]_
  > p. 12: “Additionally, large models and datasets present issues in terms of model robustness and fairness.”
- A careful approach to data selection is needed to prevent data biases. _[verified]_
  > p. 12: “A more circumspect and responsible approach to data selection is required to avoid potential concerns with data biases.”


## 2304.07193

# DINOv2: Learning Robust Visual Features without Supervision

Maxime Oquab, Timothée Darcet, Théo Moutakanni, Huy V Vo, Marc Szafraniec, Vasil Khalidov, Pierre Fernandez, Daniel Haziza, Francisco Massa, Alaaeldin El-Nouby, Mahmoud Assran, Nicolas Ballas, Wojciech Galuba, Russell Howes, Po-Yao Huang, Shang-Wen Li, Ishan Misra, Michael Rabbat, Vasu Sharma, Gabriel Synnaeve, Hu Xu, Hervé Jegou, Julien Mairal, Patrick Labatut, Armand Joulin, Piotr Bojanowski
2024 · arXiv:2304.07193v2[cs.CV]

## Problem

- Text-guided pretraining limits the information retained about images because captions only approximate rich visual content. _[verified]_
  > p. 2: “This form of text-guided pretraining limits the information that can be retained about the image since captions only approximate the rich information in images, and complex pixel-level information may not surface with this supervision.”
- Scaling self-supervised learning on uncurated datasets typically leads to a significant drop in feature quality due to a lack of data control. _[verified]_
  > p. 2: “Some efforts on scaling these approaches beyond ImageNet-1k have been attempted (Caron et al., 2019;Goyal et al., 2021;2022a), but they focused on uncurated datasets, which typically lead to a significant drop in the quality of the features.”

## Task

- image classification _[verified]_
  > p. 1: “These models should generate visual features that work out of the box on any task, both at the image level, e.g., image classification, and pixel level, e.g., segmentation.”
- segmentation _[verified]_
  > p. 1: “These models should generate visual features that work out of the box on any task, both at the image level, e.g., image classification, and pixel level, e.g., segmentation.”

## Contributions

- An automatic pipeline to build a dedicated, diverse, and curated image dataset from uncurated sources. _[verified]_
  > p. 1: “In terms of data, we propose an automatic pipeline to build a dedicated, diverse, and curated image dataset instead of uncurated data, as typically done in the self-supervised literature.”
- Training a 1B parameter ViT model and distilling it into smaller models that surpass existing general-purpose features on most benchmarks. _[verified]_
  > p. 1: “In terms of models, we train a ViT model (Dosovitskiy et al., 2021) with 1B parameters and distill it into a series of smaller models that surpass the best available general-purpose features, OpenCLIP (Ilharco et al., 2021) on most of the benchmarks at image and pixel levels.”
- Technical improvements that accelerate and stabilize training at scale, making the approach faster and more memory efficient. _[verified]_
  > p. 1: “Most of the technical contributions aim at accelerating and stabilizing the training at scale.”

## Method

- An image-level cross-entropy loss objective between student and teacher network class tokens extracted from different crops. _[partial]_
  > p. 5: “We consider the cross-entropy loss between the features extracted from a student and a teacher network.”
- A patch-level objective utilizing masked input patches for the student network and visible patches for the teacher network. _[verified]_
  > p. 5: “We randomly mask some of the input patches given to the student, but not to the teacher.”
- Sinkhorn-Knopp centering is used for the teacher network instead of standard softmax-centering. _[verified]_
  > p. 6: “Ruan et al. (2023) recommend to replace the teacher softmax-centering step of DINO and iBot by the Sinkhorn-Knopp (SK) batch normalization of SwAV (Caron et al., 2020).”
- The KoLeo regularizer is applied to encourage a uniform span of the features within a batch. _[verified]_
  > p. 6: “The KoLeo regularizer derives from the Kozachenko-Leonenko differential entropy estimator (see Beirlant et al. (1997); Delattre & Fournier (2017)) and encourages a uniform span of the features within a batch.”
- The image resolution is increased during a short period at the end of pretraining. _[verified]_
  > p. 6: “However, training at high resolution is time and memory demanding, and instead, we increase the resolution of images to 518 × 518 during a short period at the end of pretraining.”

## Novelty

- Unlike prior work that shares parameters between DINO and iBOT projection heads, separate heads are used at scale. _[verified]_
  > p. 6: “At scale, we observed that the opposite is true, and we therefore use two separate heads in all our experiments.”

## Datasets

- ImageNet-22k _[verified]_
  > p. 4: “Our selection of curated datasets is detailed in the appendix (Table 15) and contains ImageNet-22k, the train split of ImageNet-1k, Google Landmarks and several fine-grained datasets.”
- ImageNet-1k (train) _[verified]_
  > p. 4: “Our selection of curated datasets is detailed in the appendix (Table 15) and contains ImageNet-22k, the train split of ImageNet-1k, Google Landmarks and several fine-grained datasets.”
  > p. 7: “We report the Top-1 accuracy on the validation set of ImageNet-1k with a k-NN 1.”
  > p. 11: “As a first evaluation, we probe the quality of the holistic image representation produced by the model on the ImageNet-1k classification dataset.”
- Google Landmarks _[verified]_
  > p. 4: “Our selection of curated datasets is detailed in the appendix (Table 15) and contains ImageNet-22k, the train split of ImageNet-1k, Google Landmarks and several fine-grained datasets.”
- uncurated web data (1.2B unique images) _[verified]_
  > p. 4: “For the uncurated data source, we collect a raw unfiltered dataset of images from a publicly available repository of crawled web data.”
- LVD-142M _[verified]_
  > p. 4: “We assemble our curated LVD-142M dataset by retrieving, from a large pool of uncurated data, images that are close to those in several curated datasets.”
- uncurated dataset (142 million images) _[verified]_
  > p. 8: “For the uncurated dataset, we randomly sample 142 million images from the same data source as LVD-142M.”
- INet-22k \ INet-1k _[verified]_
  > p. 8: “We also include a variant of ImageNet-22k obtained by removing the synsets of ImageNet-1k (INet-22k \ INet-1k) for completeness.”
- Oxford-M _[unsupported]_
  > p. 9: “Table 3a shows the impact of using the KoLeo loss.”
- ADE-20k _[unsupported]_
  > p. 9: “Table 3a shows the impact of using the KoLeo loss.”
- ImageNet-ReaL _[verified]_
  > p. 11: “Because most SSL methods were developped using ImageNet-1k validation performance as a debugging signal, we also report the top-1 accuracy on ImageNet-ReaL and ImageNet-V2.”
- ImageNet-V2 _[verified]_
  > p. 11: “Because most SSL methods were developped using ImageNet-1k validation performance as a debugging signal, we also report the top-1 accuracy on ImageNet-ReaL and ImageNet-V2.”
- iNaturalist 2018 _[verified]_
  > p. 13: “For iNaturalist 2018, iNaturalist 2021, and Places205, we train a linear classifier with data augmentations as in Sec. 7.1”
- iNaturalist 2021 _[verified]_
  > p. 13: “For iNaturalist 2018, iNaturalist 2021, and Places205, we train a linear classifier with data augmentations as in Sec. 7.1”
- Places205 _[verified]_
  > p. 13: “For iNaturalist 2018, iNaturalist 2021, and Places205, we train a linear classifier with data augmentations as in Sec. 7.1”
- UCF-101 _[verified]_
  > p. 13: “We evaluated features on three datasets, namely UCF-101 (Soomro et al., 2012), Kinetics-400 (Kay et al., 2017) and Something-Something v2 (Goyal et al., 2017).”
- Kinetics-400 _[verified]_
  > p. 13: “We evaluated features on three datasets, namely UCF-101 (Soomro et al., 2012), Kinetics-400 (Kay et al., 2017) and Something-Something v2 (Goyal et al., 2017).”
- Something-Something v2 _[verified]_
  > p. 13: “We evaluated features on three datasets, namely UCF-101 (Soomro et al., 2012), Kinetics-400 (Kay et al., 2017) and Something-Something v2 (Goyal et al., 2017).”
- NYUd _[unsupported]_
  > p. 15: “We consider three different setups for this evaluation.”
- KITTI _[unsupported]_
  > p. 15: “We consider three different setups for this evaluation.”
- SUN3d _[partial]_
  > p. 15: “We probe the quality of patch-level features extracted from our network on several dense downstream tasks: semantic image segmentation and monocular depth estimation in several settings and we conduct evaluations on multiple datasets for each.”

## Baselines

- MAE _[verified]_
  > p. 11: “First, we run our evaluations for MAE (He et al., 2022), DINO (Caron et al., 2021), SEERv2 (Goyal et al., 2022a), MSN (Assran et al., 2022), EsViT (Li et al., 2022a), Mugs (Zhou et al., 2022b) and iBOT (Zhou et al., 2022a).”
- DINO _[verified]_
  > p. 11: “First, we run our evaluations for MAE (He et al., 2022), DINO (Caron et al., 2021), SEERv2 (Goyal et al., 2022a), MSN (Assran et al., 2022), EsViT (Li et al., 2022a), Mugs (Zhou et al., 2022b) and iBOT (Zhou et al., 2022a).”
- SEERv2 _[verified]_
  > p. 11: “First, we run our evaluations for MAE (He et al., 2022), DINO (Caron et al., 2021), SEERv2 (Goyal et al., 2022a), MSN (Assran et al., 2022), EsViT (Li et al., 2022a), Mugs (Zhou et al., 2022b) and iBOT (Zhou et al., 2022a).”
- MSN _[verified]_
  > p. 11: “First, we run our evaluations for MAE (He et al., 2022), DINO (Caron et al., 2021), SEERv2 (Goyal et al., 2022a), MSN (Assran et al., 2022), EsViT (Li et al., 2022a), Mugs (Zhou et al., 2022b) and iBOT (Zhou et al., 2022a).”
- EsViT _[verified]_
  > p. 11: “First, we run our evaluations for MAE (He et al., 2022), DINO (Caron et al., 2021), SEERv2 (Goyal et al., 2022a), MSN (Assran et al., 2022), EsViT (Li et al., 2022a), Mugs (Zhou et al., 2022b) and iBOT (Zhou et al., 2022a).”
- Mugs _[verified]_
  > p. 11: “First, we run our evaluations for MAE (He et al., 2022), DINO (Caron et al., 2021), SEERv2 (Goyal et al., 2022a), MSN (Assran et al., 2022), EsViT (Li et al., 2022a), Mugs (Zhou et al., 2022b) and iBOT (Zhou et al., 2022a).”
- iBOT _[verified]_
  > p. 11: “First, we run our evaluations for MAE (He et al., 2022), DINO (Caron et al., 2021), SEERv2 (Goyal et al., 2022a), MSN (Assran et al., 2022), EsViT (Li et al., 2022a), Mugs (Zhou et al., 2022b) and iBOT (Zhou et al., 2022a).”
- CLIP _[verified]_
  > p. 11: “Second, we report performance of open-source weakly-supervised models such as CLIP (Radford et al., 2021), OpenCLIP (Ilharco et al., 2021;Cherti et al., 2023), and SWAG (Singh et al., 2022).”
- OpenCLIP _[verified]_
  > p. 11: “Second, we report performance of open-source weakly-supervised models such as CLIP (Radford et al., 2021), OpenCLIP (Ilharco et al., 2021;Cherti et al., 2023), and SWAG (Singh et al., 2022).”
- SWAG _[verified]_
  > p. 11: “Second, we report performance of open-source weakly-supervised models such as CLIP (Radford et al., 2021), OpenCLIP (Ilharco et al., 2021;Cherti et al., 2023), and SWAG (Singh et al., 2022).”

## Metrics

- Top-1 accuracy on ImageNet-1k _[verified]_
  > p. 7: “We report the Top-1 accuracy on the validation set of ImageNet-1k with a k-NN 1.”
- mIoU _[verified]_
  > p. 10: “We train linear classifiers on top of frozen features at different resolutions and report Top-1 accuracy on ImageNet and mIoU on ADE-20k.”
- RMSE _[unsupported]_
  > p. 16: “We report the RMSE metric on the 3 datasets.”

## Hyperparameters

- drop rate: 40% _[verified]_
  > p. 7: “With high drop rates (d = 40% in this work), this allows a drastic improvement in compute efficiency and memory usage.”
- KoLeo regularizer weight: 0.1 _[verified]_
  > p. 29: “We apply the KoLeo regularizer with a weight of 0.1 between the class tokens of the first global crop, for all samples within a GPU without cross-communication for this step.”
- learning rate: 1e-3 _[verified]_
  > p. 31: “Drop-rate LR Batch size DINOv2-S (distilled) ViT-S/14 0 1e-3 2048 DINOv2-B (distilled)”
- batch size: 2048 _[verified]_
  > p. 31: “Drop-rate LR Batch size DINOv2-S (distilled) ViT-S/14 0 1e-3 2048 DINOv2-B (distilled)”
- iterations (pre-training): 625k _[verified]_
  > p. 31: “All models run for 625k iterations with optimizer AdamW, an initial LayerScale value of 1e-5, a weight decay cosine schedule from 0.04 to 0.2, a learning rate warmup of 100k iterations, a teacher momentum cosine schedule from 0.994 to 1, and we train in float16 precision in all cases (except for the”
- optimizer (pre-training): AdamW _[verified]_
  > p. 31: “All models run for 625k iterations with optimizer AdamW, an initial LayerScale value of 1e-5, a weight decay cosine schedule from 0.04 to 0.2, a learning rate warmup of 100k iterations, a teacher momentum cosine schedule from 0.994 to 1, and we train in float16 precision in all cases (except for the”
- initial LayerScale value: 1e-5 _[verified]_
  > p. 31: “All models run for 625k iterations with optimizer AdamW, an initial LayerScale value of 1e-5, a weight decay cosine schedule from 0.04 to 0.2, a learning rate warmup of 100k iterations, a teacher momentum cosine schedule from 0.994 to 1, and we train in float16 precision in all cases (except for the”
- weight decay: 0.04 to 0.2 _[verified]_
  > p. 31: “All models run for 625k iterations with optimizer AdamW, an initial LayerScale value of 1e-5, a weight decay cosine schedule from 0.04 to 0.2, a learning rate warmup of 100k iterations, a teacher momentum cosine schedule from 0.994 to 1, and we train in float16 precision in all cases (except for the”
- warmup: 100k _[verified]_
  > p. 31: “All models run for 625k iterations with optimizer AdamW, an initial LayerScale value of 1e-5, a weight decay cosine schedule from 0.04 to 0.2, a learning rate warmup of 100k iterations, a teacher momentum cosine schedule from 0.994 to 1, and we train in float16 precision in all cases (except for the”
- teacher momentum: 0.994 to 1 _[verified]_
  > p. 31: “All models run for 625k iterations with optimizer AdamW, an initial LayerScale value of 1e-5, a weight decay cosine schedule from 0.04 to 0.2, a learning rate warmup of 100k iterations, a teacher momentum cosine schedule from 0.994 to 1, and we train in float16 precision in all cases (except for the”

## Compute

- Compute cluster for LVD-142M dataset creation _[verified]_
  > p. 5: “The whole processing is distributed on a compute cluster of 20 nodes equipped with 8 V100-32GB GPUs and takes less than two days to produce the LVD-142M dataset.”
- Hardware used for model training _[verified]_
  > p. 6: “We train models on A100 GPUs using PyTorch 2.0.”
- Segmentation training compute time and hardware _[verified]_
  > p. 15: “Although our setup for this experiment doesn't makes use of the optimisations described in Sec. 5, the segmentation training in this experiment took 28 hours on 16 V100 GPUs.”
- GPU-hours and carbon emission for ViT-g pre-training _[verified]_
  > p. 21: “For example, a single pre-training of a ViT-g model (22k GPU-hours) emits 3.7 tons of CO 2 eq, while a finetuning on ImageNet-1k (1k GPU-hours) emits 0.2 tons.”

## Ablations

- Ablation of pretraining data sources comparing LVD-142M, ImageNet-22k, and uncurated data _[verified]_
  > p. 8: “In this experiment, we probe the impact of LVD-142M compared to ImageNet-22k, a commonly used pretraining dataset, or using directly raw and uncurated data.”
- Ablation of loss terms including KoLeo loss and masked image modeling _[partial]_
  > p. 9: “This section analyzes the performance hit observed if we ablate specific loss terms, starting from our best-performing model.”
- Ablation of changing image resolution during pretraining _[verified]_
  > p. 10: “We measure the impact of changing the resolution during the pretraining on the performance of image and patch-level features.”

## Claims

- The proposed technical improvements make the approach roughly 2 times faster and require 3 times less memory than similar discriminative self-supervised methods. _[verified]_
  > p. 2: “These improvements make our approach around 2× faster and require 3× less memory than similar discriminative self-supervised methods, allowing us to leverage longer training with larger batch sizes.”
- Self-supervised pretraining alone is a viable approach for learning transferable frozen features comparable to top openly available weakly-supervised models. _[verified]_
  > p. 3: “We conclude that selfsupervised pretraining alone is a good candidate for learning transferable frozen features that are competitive with the best openly available weakly-supervised models.”

## Limitations

- The model remains biased toward Western countries, particularly showing a performance drop in Africa. _[verified]_
  > p. 18: “This shows that our model is still biased toward Western countries.”
- The model performs significantly better on high-income households than low-income ones. _[unsupported]_
  > p. 18: “Similarly, our model performs Figure 10: Matching across images.”
- A more thorough evaluation of biases may reveal additional flaws. _[verified]_
  > p. 20: “While this is encouraging, we also acknowledge that a more thorough evaluation of biases may reveal flaws in our model.”

## Future work

- Continue scaling models and data along the same axes. _[verified]_
  > p. 21: “We expect that more of these properties will emerge at larger scales of models and data, akin to instruction emergence in large language models, and plan to continue scaling along these axes.”
- Leverage linear layer compatibility to train a language-enabled AI system that processes visual features. _[verified]_
  > p. 21: “In future work, we plan to leverage this ability to train a a language-enabled AI system that can process visual features as if they were word tokens, and extract the required information to ground the system.”

## Ethics

- The carbon footprint and potential carbon emissions of reproducing DINOv2 are reported. _[verified]_
  > p. 20: “We report the potential carbon emission of reproducing DINOv2-g when assuming a power consumption for the A100-40GB of 400W, a PUE of 1.1 and carbon intensity factor of 0.385 kg CO 2 e per KWh.”

## Code

- https://github.com/facebookresearch/dinov2 _[verified]_
  > p. 6: “https://github.com/facebookresearch/dinov2”
- https://github.com/facebookresearch/xformers _[verified]_
  > p. 7: “https://github.com/facebookresearch/xformers”


## 2304.02643

# Segment Anything

Alexander Kirillov, Eric Mintun, Nikhila Ravi, Hanzi Mao, Chloe Rolland, Laura Gustafson, Tete Xiao, Spencer Whitehead, Alexander C Berg, Wan-Yen Lo, Piotr Dollár, Ross Girshick
2023 · arXiv:2304.02643v1[cs.CV]

## Problem

- Computer vision lacks a foundation model for image segmentation that can generalize via prompt engineering. _[partial]_
  > p. 1: “In this work, our goal is to build a foundation model for image segmentation.”
- Abundant training data does not exist for many computer vision problems beyond vision and language encoders. _[verified]_
  > p. 1: “While much progress has been made on vision and language encoders, computer vision includes a wide range of problems beyond this scope, and for many of these, abundant training data does not exist.”

## Task

- promptable segmentation _[verified]_
  > p. 2: “Inspired by this line of work, we propose the promptable segmentation task, where the goal is to return a valid segmentation mask given any segmentation prompt (see Fig. 1a).”

## Contributions

- Proposed the promptable segmentation task as a pre-training objective and zero-shot transfer mechanism. _[verified]_
  > p. 2: “We use the promptable segmentation task as both a pre-training objective and to solve general downstream segmentation tasks via prompt engineering.”
- Developed the Segment Anything Model (SAM) with a lightweight mask decoder for real-time promptable segmentation. _[partial]_
  > p. 2: “We refer to this model as the Segment Anything Model, or SAM (see Fig. 1b).”
- Built a data engine using model-in-the-loop annotation to collect a massive dataset. _[verified]_
  > p. 2: “Our solution is to build a "data engine", i.e., we co-develop our model with model-in-the-loop dataset annotation (see Fig. 1c).”
- Created the SA-1B dataset containing over 1 billion masks from 11 million images. _[verified]_
  > p. 2: “Our final dataset, SA-1B, includes more than 1B masks from 11M licensed and privacy-preserving images (see Fig. 2).”

## Method

- SAM consists of three core components: an image encoder, a flexible prompt encoder, and a fast mask decoder. _[verified]_
  > p. 5: “SAM has three components, illustrated in Fig. 4: an image encoder, a flexible prompt encoder, and a fast mask decoder.”
- The image encoder uses a Vision Transformer pre-trained with MAE, minimally adapted for high-resolution inputs, running once per image. _[verified]_
  > p. 5: “Motivated by scalability and powerful pretraining methods, we use an MAE [47] pre-trained Vision Transformer (ViT) [33] minimally adapted to process high resolution inputs [62].”
- The prompt encoder handles sparse prompts like points, boxes, and text using positional and learned embeddings, and dense prompts like masks using convolutions. _[partial]_
  > p. 5: “We consider two sets of prompts: sparse (points, boxes, text) and dense (masks).”
- The mask decoder combines image and prompt embeddings via a modified Transformer decoder block and outputs dynamic mask predictions. _[verified]_
  > p. 5: “This design, inspired by [14,20], employs a modification of a Transformer decoder block [103] followed by a dynamic mask prediction head.”
- To resolve ambiguity, the model predicts multiple masks simultaneously using separate output tokens and backpropagates only the minimum loss. _[partial]_
  > p. 5: “To address this, we modify the model to predict multiple output masks for a single prompt (see Fig. 3).”
- The model is supervised using a linear combination of focal loss and dice loss, trained by simulating interactive prompt sequences across multiple iterations. _[verified]_
  > p. 5: “We supervise mask prediction with the linear combination of focal loss [65] and dice loss [73] used in [14].”

## Datasets

- SA-1B (1.1B masks and 11M images) _[verified]_
  > p. 5: “As segmentation masks are not abundant on the internet, we built a data engine to enable the collection of our 1.1B mask dataset, SA-1B.”
- COCO _[partial]_
  > p. 6: “Average annotation time per mask decreased from 34 to 14 seconds as the model improved. We note that 14 seconds is 6.5× faster than mask annotation for COCO [66] and only 2× slower than bounding-box labeling with extreme points [76,71].”
- LVIS v1 _[partial]_
  > p. 7: “We observe that SA-1B has greater coverage of image corners compared to LVIS v1 [44] and ADE20K [117], the two most similarly distributed datasets, while COCO [66] and Open Images V5 [60] have a more prominent center bias.”
- ADE20K _[verified]_
  > p. 7: “We observe that SA-1B has greater coverage of image corners compared to LVIS v1 [44] and ADE20K [117], the two most similarly distributed datasets, while COCO [66] and Open Images V5 [60] have a more prominent center bias.”
- Open Images V5 _[verified]_
  > p. 7: “We observe that SA-1B has greater coverage of image corners compared to LVIS v1 [44] and ADE20K [117], the two most similarly distributed datasets, while COCO [66] and Open Images V5 [60] have a more prominent center bias.”
- ADE20K [117] BBBC038v1 [12] Cityscapes [25] DOORS [80] DRAM [24] EgoHOS [113] GTEA [34,63] Hypersim [86] IBD [17] iShape [111] LVIS [44] NDD20 [100] NDISPark [22,23] OVIS [81] PPDLS [74] Plittersdorf [46] STREETS [91] TimberSeg [38] TrashCan [52] VISOR [28,27] WoodScape [112] PIDRay [104] ZeroWaste-f [6] _[partial]_
  > p. 8: “We use a newly compiled suite of 23 datasets with diverse image distributions.”
- BSDS500 _[verified]_
  > p. 10: “We evaluate SAM on the classic low-level task of edge detection using BSDS500 [72,3].”

## Baselines

- RITM interactive segmentation model _[verified]_
  > p. 8: “We compare mainly to RITM [92], a strong interactive segmenter that performs best on our benchmark compared to other strong baselines [67,18].”
- SimpleClick interactive segmentation model _[verified]_
  > p. 9: “Fig. 9c shows additional baselines, SimpleClick [67] and FocalClick [18], which obtain lower single point performance than RITM and SAM.”
- FocalClick interactive segmentation model _[verified]_
  > p. 9: “Fig. 9c shows additional baselines, SimpleClick [67] and FocalClick [18], which obtain lower single point performance than RITM and SAM.”
- ViTDet-H detector acting as proposal generator _[verified]_
  > p. 10: “We compare to a strong baseline implemented as a ViTDet [62] detector (with cascade Mask R-CNN [48,11] ViT-H).”
- HED deep learning edge detection method _[verified]_
  > p. 10: “Nevertheless, SAM performs well compared to pioneering deep learning methods such as HED [108] (also trained on BSDS500) and significantly better than prior, though admittedly outdated, zero-shot transfer methods.”

## Metrics

- mIoU (mean intersection-over-union) _[verified]_
  > p. 8: “We therefore supplement the standard mIoU metric (i.e., the mean of all IoUs between predicted and ground truth masks) with a human study in which annotators rate mask quality from 1 (nonsense) to 10 (pixel-perfect).”
- Human evaluation score from 1 to 10 _[verified]_
  > p. 8: “We therefore supplement the standard mIoU metric (i.e., the mean of all IoUs between predicted and ground truth masks) with a human study in which annotators rate mask quality from 1 (nonsense) to 10 (pixel-perfect).”
- Recall at 50% precision (R50) _[verified]_
  > p. 10: “This bias is reflected quantitatively in Table 3: recall at 50% precision (R50) is high, at the cost of precision.”
- Average recall (AR) metric _[verified]_
  > p. 10: “We compute the standard average recall (AR) metric on LVIS v1 [44].”
- Mask average precision (AP) metric _[verified]_
  > p. 10: “Looking at the mask AP metric we observe gaps on both datasets, where SAM is reasonably close, though certainly behind ViTDet.”

## Hyperparameters

- optimizer: AdamW (β 1 = 0.9, β 2 = 0.999) _[verified]_
  > p. 17: “We use the AdamW [68] optimizer (β 1 = 0.9, β 2 = 0.999) and a linear learning rate warmup [42] for 250 iterations and a step-wise learning rate decay schedule.”
- warmup: 250 iterations _[verified]_
  > p. 17: “We use the AdamW [68] optimizer (β 1 = 0.9, β 2 = 0.999) and a linear learning rate warmup [42] for 250 iterations and a step-wise learning rate decay schedule.”
- learning rate: 8e -4 _[verified]_
  > p. 17: “The initial learning rate (lr), after warmup, is 8e -4 .”
- epochs/steps: 90k iterations _[verified]_
  > p. 17: “We train for 90k iterations (∼2 SA-1B epochs) and decrease the lr by a factor of 10 at 60k iterations and again at 86666 iterations.”
- batch size: 256 _[verified]_
  > p. 17: “The batch size is 256 images.”
- weight decay: 0.1 _[verified]_
  > p. 17: “To regularize SAM, we set weight decay (wd) to 0.1 and apply drop path [53] (dp) with a rate of 0.4.”
  > p. 18: “wd = 0.1, and dp = 0.6/0.4 for ViT-B/L, respectively.”
- drop path: 0.4 _[verified]_
  > p. 17: “To regularize SAM, we set weight decay (wd) to 0.1 and apply drop path [53] (dp) with a rate of 0.4.”
- layer-wise learning rate decay: 0.8 _[verified]_
  > p. 17: “We use a layer-wise learning rate decay [5] (ld) of 0.8.”
- model size: ViT-H _[verified]_
  > p. 17: “We initialize SAM from an MAE [47] pre-trained ViT-H.”
- epochs/steps: 180k iterations _[verified]_
  > p. 18: “To train ViT-B and ViT-L, we use 180k iterations with batch size 128 distributed across 128 GPUs.”
- batch size: 128 _[verified]_
  > p. 18: “To train ViT-B and ViT-L, we use 180k iterations with batch size 128 distributed across 128 GPUs.”
  > p. 22: “We train this model with largescale jitter [40] for 120k iterations with batch size 128.”
- learning rate: 8e -4 /4e -4 _[verified]_
  > p. 18: “We set lr = 8e -4 /4e -4 , ld = 0.6/0.8,”
- layer-wise learning rate decay: 0.6/0.8 _[verified]_
  > p. 18: “We set lr = 8e -4 /4e -4 , ld = 0.6/0.8,”
- drop path: 0.6/0.4 _[verified]_
  > p. 18: “wd = 0.1, and dp = 0.6/0.4 for ViT-B/L, respectively.”
- data augmentation: largescale jitter _[partial]_
  > p. 22: “We train this model with largescale jitter [40] for 120k iterations with batch size 128.”
- epochs/steps: 120k iterations _[verified]_
  > p. 22: “We train this model with largescale jitter [40] for 120k iterations with batch size 128.”

## Compute

- Training distributed across 256 GPUs _[verified]_
  > p. 17: “We distribute training across 256 GPUs, due to the large image encoder and 1024×1024 input size.”
- Training with up to 64 randomly sampled masks per GPU _[verified]_
  > p. 17: “To limit GPU mem-ory usage, we train with up to 64 randomly sampled masks per GPU.”
- Training ViT-B and ViT-L distributed across 128 GPUs _[partial]_
  > p. 18: “To train ViT-B and ViT-L, we use 180k iterations with batch size 128 distributed across 128 GPUs.”

## Ablations

- Ablation on training with cumulative data from data engine stages versus automatically generated masks only _[verified]_
  > p. 11: “Fig. 13 (left) plots SAM's performance when trained on cumulative data from the data engine stages.”
- Ablation on data volume using 11M, 1M, and 0.1M images _[partial]_
  > p. 11: “In Fig. 13 (middle) we look at the impact of data volume.”
- Ablation on image encoder scaling using ViT-B, ViT-L, and ViT-H _[partial]_
  > p. 12: “(Right) Scaling SAM's image encoder shows meaningful, yet saturating gains.”

## Claims

- SAM produces high-quality masks from a single foreground point across 23 diverse segmentation datasets. _[verified]_
  > p. 2: “First, using a diverse new suite of 23 segmentation datasets, we find that SAM produces high-quality masks from a single foreground point, often only slightly below that of the manually annotated ground truth.”
- SA-1B has 400 times more masks than any existing segmentation dataset. _[verified]_
  > p. 2: “SA-1B, collected fully automatically using the final stage of our data engine, has 400× more masks than any existing segmentation dataset [66,44,117,60], and as we verify extensively, the masks are of high quality and diversity.”
- The prompt encoder and mask decoder can predict a mask from a prompt in about 50 milliseconds. _[verified]_
  > p. 2: “Given an image embedding, the prompt encoder and mask decoder predict a mask from a prompt in ∼50ms in a web browser.”
- SAM demonstrates consistently strong quantitative and qualitative results on various downstream tasks under a zero-shot transfer protocol. _[verified]_
  > p. 2: “Second, we find consistently strong quantitative and qualitative results on a variety of downstream tasks under a zero-shot transfer protocol using prompt engineering, including edge detection, object proposal generation, instance segmentation, and a preliminary exploration of text-to-mask prediction.”

## Limitations

- SAM is not perfect and can miss fine structures or hallucinate small components. _[partial]_
  > p. 12: “While SAM performs well in general, it is not perfect.”
- SAM's overall performance is not real-time when using a heavy image encoder. _[verified]_
  > p. 12: “Moreover, SAM can process prompts in real-time, but nevertheless SAM's overall performance is not real-time when using a heavy image encoder.”
- The text-to-mask task is exploratory and not entirely robust. _[verified]_
  > p. 12: “Our foray into the text-to-mask task is exploratory and not entirely robust, although we believe it can be improved with more effort.”
- Some geographic regions and economic groups are underrepresented in SA-1B. _[verified]_
  > p. 28: “While SA-1B is more geographically diverse than many of its predecessors, we acknowledge that some geographic regions and economic groups are underrepresented.”

## Ethics

- Biases may arise when SAM is used as a component in larger systems. _[verified]_
  > p. 8: “We believe our findings stem from the nature of the task, and acknowledge biases may arise when SAM is used as a component in larger systems.”
- Images were filtered for objectionable content by the provider, but false negatives are possible. _[verified]_
  > p. 28: “The images were filtered for objectionable content by the provider, but we acknowledge the possibility of false negatives.”
- Training large models incurs environmental impact and cost. _[verified]_
  > p. 28: “We acknowledge the environmental impact and cost of training large scale models.”
- Users should run their own fairness evaluations for specific downstream use cases. _[verified]_
  > p. 28: “As such we recommend users run their own fairness evaluation when using SAM for their specific use case.”

## Code

- https://github.com/serengil/retinaface _[verified]_
  > p. 26: “We used the RetinaFace [88,89] model (https://github.com/serengil/retinaface) to detect faces.”
- https://github.com/facebookresearch/segment-anything _[verified]_
  > p. 28: “The license for SAM can be found at https://github.com/facebookresearch/segment-anything.”


## 2309.16588

# Untitled paper

Timothée Darcet, Maxime Oquab, Julien Mairal, Piotr Bojanowski
2024 · arXiv:2309.16588v2[cs.CV]

## Problem

- Vision Transformers exhibit artifacts in feature maps characterized by high-norm tokens in low-informative background areas. _[partial]_
  > p. 1: “In this paper, we identify and characterize artifacts in feature maps of both supervised and self-supervised ViT networks.”
- DINOv2 is surprisingly incompatible with unsupervised object discovery methods like LOST. _[partial]_
  > p. 2: “When used to extract features, it delivers disappointing performance, only on par with supervised alternative backbones in this scenario.”

## Task

- learning visual representations with Vision Transformers _[verified]_
  > p. 1: “Transformers have recently emerged as a powerful tool for learning visual representations.”

## Contributions

- Proposing a simple solution based on providing additional tokens to the input sequence to fill the role of outlier tokens. _[verified]_
  > p. 1: “We propose a simple yet effective solution based on providing additional tokens to the input sequence of the Vision Transformer to fill that role.”

## Method

- Adding learnable register tokens to the vision transformer sequence after the patch embedding layer to act as memory slots. _[partial]_
  > p. 5: “We therefore propose a simple fix to this issue: we explicitly add new tokens to the sequence, that the model can learn to use as registers.”
- Evaluating the approach across three distinct training paradigms: supervised (DeiT-III), text-supervised (OpenCLIP), and self-supervised (DINOv2). _[verified]_
  > p. 6: “We try it on three different state-of-the-art training methods for supervised, text-supervised, and unsupervised learning, shortly described below.”
- Discarding the register tokens at the end of the transformer while retaining the patch and class tokens for final image representation. _[verified]_
  > p. 5: “At the end of the vision transformer, these tokens are discarded, and the [CLS] token and patch tokens are used as image representations, as usual.”

## Novelty

- Identifying that attention map artifacts in vision transformers are actually high-norm outlier tokens that store global information. _[partial]_
  > p. 3: “Artifacts are high-norm outlier tokens.”
- Adapting the memory transformer mechanism of extra tokens to vision transformers to resolve interpretability and local feature degradation issues. _[partial]_
  > p. 5: “Interestingly, we show here that this mechanism admits a natural justification for vision transformers, fixing an interpretability and performance issue that was present otherwise.”

## Datasets

- Aircraft _[verified]_
  > p. 15: “4: Linear probing of models with and without registers on the Aircraft dataset, using various tokens as representation.”
- ImageNet-22k (random subset) _[verified]_
  > p. 15: “We produce these plots by running the model on a random subset of ImageNet-22k, and averaging the attention maps for the corresponding tokens at the last layer.”
  > p. 6: “| ImageNet ADE20k NYUd |  |”
- ADE20k _[verified]_
  > p. 6: “| ImageNet ADE20k NYUd |  |”
- NYUd _[verified]_
  > p. 6: “| ImageNet ADE20k NYUd |  |”
- VOC 2007 _[partial]_
  > p. 8: “We run object discovery on PASCAL Unsupervised Object Discovery using LOST”
- VOC 2012 _[partial]_
  > p. 8: “We run object discovery on PASCAL Unsupervised Object Discovery using LOST”
- COCO 20k (20k) _[partial]_
  > p. 8: “We run object discovery on PASCAL Unsupervised Object Discovery using LOST”

## Metrics

- Top-1 accuracy _[verified]_
  > p. 15: “position prediction reconstruction #registers patches considered top-1 acc L2 error ↓”
- L2 error _[verified]_
  > p. 15: “position prediction reconstruction #registers patches considered top-1 acc L2 error ↓”
- Top-1 _[verified]_
  > p. 6: “| Top-1 | mIoU | rmse ↓”
- mIoU _[verified]_
  > p. 6: “| Top-1 | mIoU | rmse ↓”
- rmse _[verified]_
  > p. 6: “| Top-1 | mIoU | rmse ↓”

## Claims

- The proposed solution fixes the outlier problem entirely for both supervised and self-supervised models. _[verified]_
  > p. 1: “We show that this solution fixes that problem entirely for both supervised and self-supervised models, sets a new state of the art for self-supervised visual models on dense visual prediction tasks, enables object discovery methods with larger models, and most importantly leads to smoother feature maps and attention maps for downstream visual processing.”
- Outlier tokens have roughly 10x higher norm at the output and correspond to around 2% of the total sequence. _[verified]_
  > p. 2: “We observe that they are tokens with roughly 10x higher norm at the output and correspond to a small fraction of the total sequence (around 2%).”
- The proportion of tokens with norm larger than 150 is measured at 2.37% for DINOv2. _[partial]_
  > p. 3: “We measure the proportion of tokens with norm larger than 150 at 2.37%.”

## Limitations

- The random choice of token used in the evaluation introduces a significant source of variance. _[partial]_
  > p. 16: “The results presented in table 1 are obtained by taking a random patch token, either normal or outlier.”

## Code

- https://github.com/facebookresearch/deit _[verified]_
  > p. 6: “https://github.com/facebookresearch/deit”
  > p. 6: “https://github.com/facebookresearch/dinov2”
- https://github.com/mlfoundations/open_clip _[verified]_
  > p. 6: “https://github.com/mlfoundations/open_clip”


## 2303.15343

# Sigmoid Loss for Language Image Pre-Training

Xiaohua Zhai, Basil Mustafa, Alexander Kolesnikov, Lucas Beyer, Google Deepmind

## Problem

- Standard contrastive learning with softmax normalization requires a global view of pairwise similarities, leading to numerical instability and memory bottlenecks. _[verified]_
  > p. 1: “Unlike standard contrastive learning with softmax normalization, the sigmoid loss operates solely on image-text pairs and does not require a global view of the pairwise similarities for normalization.”

## Task

- Language-Image Pre-training _[verified]_
  > p. 1: “We propose a simple pairwise Sigmoid loss for Language-Image Pre-training (SigLIP).”

## Contributions

- Proposing a simple pairwise sigmoid loss for Language-Image Pre-training (SigLIP) that operates solely on image-text pairs. _[verified]_
  > p. 1: “We propose a simple pairwise Sigmoid loss for Language-Image Pre-training (SigLIP).”
- Demonstrating that the sigmoid loss improves performance at smaller batch sizes and allows extreme batch size scaling up to one million. _[partial]_
  > p. 1: “Finally, we push the batch size to the extreme, up to one million, and find that the benefits of growing batch size quickly diminish, with a more reasonable batch size of 32 k being sufficient.”

## Method

- The model architecture adopts a vision transformer for processing images and a transformer architecture for processing texts. _[verified]_
  > p. 3: “In this paper, we adopt the vision transformer architecture [17] for images and the transformer architecture [47] for texts.”
- Instead of a softmax-based contrastive loss, a pairwise sigmoid loss is proposed that processes every image-text pair independently as binary classification. _[partial]_
  > p. 3: “Instead of the softmax-based contrastive loss, we propose a simpler alternative that does not require computing global normalization factors.”
- An additional learnable bias term b is introduced alongside the temperature t to alleviate the heavy imbalance from numerous negative pairs. _[verified]_
  > p. 3: “To alleviate this, we introduce an additional learnable bias term b similar to the temperature t.”
- The training procedure utilizes a memory-efficient distributed implementation where representations are permuted across devices to avoid expensive all-gathers and reduce memory cost. _[unsupported]_
  > p. 3: “Denoting the perdevice batch size as b = |B| D , the loss is reformulated as:”

## Novelty

- The proposed sigmoid-based loss operates independently on image-text pairs without requiring global normalization factors, unlike traditional softmax-based contrastive loss. _[verified]_
  > p. 3: “Instead of the softmax-based contrastive loss, we propose a simpler alternative that does not require computing global normalization factors.”

## Datasets

- ImageNet _[verified]_
  > p. 4: “To validate our models, we report zero-shot transfer results on the ImageNet dataset [14] and zero-shot retrieval results across 36 languages on the XM3600 dataset [44].”
- XM3600 _[verified]_
  > p. 4: “To validate our models, we report zero-shot transfer results on the ImageNet dataset [14] and zero-shot retrieval results across 36 languages on the XM3600 dataset [44].”
- LiT image-text dataset _[verified]_
  > p. 4: “Following [59], we use the same precomputed embeddings for the images using a ViT-g vision model, and train a base size text tower from scratch with the same hyperparameters using the LiT image-text dataset [59].”
- WebLI _[verified]_
  > p. 5: “We pre-train SigLIP models on the WebLI dataset [13], using only English image and text pairs.”
- C4 _[verified]_
  > p. 5: “The text is tokenized by a 32 k vocabulary sentencepiece tokenizer [27] trained on the English C4 dataset [37], and a maximum of 16 text tokens are kept.”
- Oxford-iiit pet _[verified]_
  > p. 9: “Zero-shot transfer results are reported on ImageNet [14], Oxford-iiit pet [34] and Ci-far100 [26].”
- Cifar100 _[verified]_
  > p. 9: “Zero-shot transfer results are reported on ImageNet [14], Oxford-iiit pet [34] and Ci-far100 [26].”

## Baselines

- Softmax loss baseline _[partial]_
  > p. 4: “Sigmoid loss outperforms the softmax loss significantly with small batch sizes, and performs similarly at larger batch sizes.”
- CLIP baseline pre-trained on WebLI with standard softmax loss _[verified]_
  > p. 5: “We use CLIP (We-bLI) to denote the CLIP baseline pre-trained on WebLI with the standard softmax loss.”
- Open-CLIP and CLIP models _[verified]_
  > p. 8: “Our SigLIP models outperform all prior models, e.g. Open-CLIP [22] and CLIP [36], by a significant margin on both zero-shot classification and retrieval tasks.”
- EVA-CLIP and CLIPA-v2 models _[verified]_
  > p. 8: “Compared to the concurrent EVA-CLIP [43] and CLIPA-v2 [29], our SigLIP-L performs across the board, in both the low and high resolution cases.”

## Metrics

- Zero-shot transfer accuracy on ImageNet _[verified]_
  > p. 4: “To validate our models, we report zero-shot transfer results on the ImageNet dataset [14] and zero-shot retrieval results across 36 languages on the XM3600 dataset [44].”
- Zero-shot retrieval results across 36 languages _[verified]_
  > p. 4: “To validate our models, we report zero-shot transfer results on the ImageNet dataset [14] and zero-shot retrieval results across 36 languages on the XM3600 dataset [44].”
- Image retrieval recall@1 _[verified]_
  > p. 7: “The scaled-up mSigLIP ViT-B model achieves the state-of-theart 42.6% image retrieval recall@1 and 54.1% text retrieval recall@1 for a Base model.”
- Text retrieval recall@1 _[verified]_
  > p. 7: “The scaled-up mSigLIP ViT-B model achieves the state-of-theart 42.6% image retrieval recall@1 and 54.1% text retrieval recall@1 for a Base model.”

## Hyperparameters

- optimizer: ScalingViT-Adafactor _[verified]_
  > p. 4: “We use the ScalingViT-Adafactor optimizer [58] by default for all our experiments.”
- optimizer: LION _[verified]_
  > p. 6: “It is trained using the LION [12] optimizer with decoupled weight decay 1 × 10 -7 , linearly warm-up of learning rate over 6.5k steps up to a peak of 1 × 10 -4 , followed by a cosine decay to 0.”
- weight decay: 1 × 10 -7 _[verified]_
  > p. 6: “It is trained using the LION [12] optimizer with decoupled weight decay 1 × 10 -7 , linearly warm-up of learning rate over 6.5k steps up to a peak of 1 × 10 -4 , followed by a cosine decay to 0.”
- warmup: 6.5k steps _[verified]_
  > p. 6: “It is trained using the LION [12] optimizer with decoupled weight decay 1 × 10 -7 , linearly warm-up of learning rate over 6.5k steps up to a peak of 1 × 10 -4 , followed by a cosine decay to 0.”
- learning rate: 1 × 10 -4 _[verified]_
  > p. 6: “It is trained using the LION [12] optimizer with decoupled weight decay 1 × 10 -7 , linearly warm-up of learning rate over 6.5k steps up to a peak of 1 × 10 -4 , followed by a cosine decay to 0.”
- epochs/steps: 65 000 steps _[verified]_
  > p. 6: “We train for a total of 65 000 steps with a batch size of 32k -this leads to just under one day of training.”
- batch size: 32k _[partial]_
  > p. 6: “We train for a total of 65 000 steps with a batch size of 32k -this leads to just under one day of training.”
- batch size: 20 k _[verified]_
  > p. 6: “With a ViT-g/14 [58] model as the vision tower and a Large text tower, we can train at 20 k batch size on four chips for 107 k steps in under two days.”
- epochs/steps: 107 k steps _[verified]_
  > p. 6: “With a ViT-g/14 [58] model as the vision tower and a Large text tower, we can train at 20 k batch size on four chips for 107 k steps in under two days.”
- learning rate (fine-tuning): 0.1 _[verified]_
  > p. 7: “In all the experiments, we apply a 0.1 learning rate multiplier to the pre-trained image tower to make it suitable for fine-tuning.”
- batch size (fine-tuning): 16 k _[partial]_
  > p. 7: “We used 16 TPU-v4 chips and train at 16 k batch size for 2.4 B examples seen.”
- epochs/steps (fine-tuning): 2.4 B examples _[verified]_
  > p. 7: “We used 16 TPU-v4 chips and train at 16 k batch size for 2.4 B examples seen.”
- learning rate (resolution adaptation): 100x smaller _[verified]_
  > p. 7: “To get SigLIP models for different resolutions, we train for 5 billion more examples at the target resolution, with a 100x smaller learning rate and no weight decay.”
- optimizer: β 2 = 0.95 _[verified]_
  > p. 8: “We opt for setting β 2 = 0.95 for all our experiments.”
- optimizer: ScalingViT-Adafactor with β 1 = 0.9 and β 2 = 0.95 _[verified]_
  > p. 14: “We train a standard base size text tower, using the ScalingViT-Adafactor optimizer [58] with β 1 = 0.9 and β 2 = 0.95.”
- learning rate: 0.001 _[verified]_
  > p. 14: “We use 0.001 learning rate with a linear warmup schedule for the first 200 M examples seen, and then the learning rate is decayed to zero with a cosine learning rate schedule.”
- weight decay: 0.0001 _[verified]_
  > p. 14: “Weight decay is set to 0.0001 for all the experiments.”
- batch size: 16384 _[verified]_
  > p. 9: “In order to study this for SigLIP, we train M/16 image models alongside an M text model at batch size 16384 for 3.6 billion seen examples.”

## Compute

- Four TPU-v4 chips used for memory efficient sigmoid loss exploration _[verified]_
  > p. 6: “We explore the usage of SigLiT models in this section with only four TPU-v4 chips, as the memory efficient sigmoid loss is suitable for this application scenario.”
- 16 TPU-v4 chips used for fine-tuning experiment _[verified]_
  > p. 7: “We used 16 TPU-v4 chips and train at 16 k batch size for 2.4 B examples seen.”
- 32 TPU-v4 chips for two days for from-scratch SigLIP _[verified]_
  > p. 7: “We also present from-scratch results in the bottom rows of Table 1: with 32 TPUv4 chips for only two days, SigLIP achieves 72.1% 0-shot accuracy.”
- Comparison training cost of approximately 2500 TPUv3-days reported in [30] _[verified]_
  > p. 7: “This presents a significant training cost reduction e.g. compared to CLIP (approx. 2500 TPUv3-days for 72.6%) reported in [30].”
- Google Cloud TPUs used for training models developed in big vision codebase _[verified]_
  > p. 17: “• Hardware & Software: The models are developed in the big vision codebase [5,4] and trained on Google Cloud TPUs.”

## Seeds and runs

- Repeating SigLIP training five times with recommended 32k batch size _[verified]_
  > p. 14: “We repeat SigLIP training five times, using the recommended 32k batch size and 3B seen examples.”

## Ablations

- Ablation on mini-batch composition and distribution of negative examples by masking out negative examples _[verified]_
  > p. 8: “We run experiments in the SigLiT setup at batch-size 16 k for 900 M steps and vary the composition of the batch by masking out (i.e.”
- Ablation on bias term in the loss function using Base architecture _[verified]_
  > p. 9: “We ablate the bias term in the loss function, using the Base architecture with an 8 k batch size, trained for 900M examples with the SigLIP setup.”

## Claims

- A SigLiT model achieves 84.5% ImageNet zero-shot accuracy in two days using only four TPUv4 chips. _[verified]_
  > p. 1: “Combined with Locked-image Tuning, with only four TPUv4 chips, we train a SigLiT model that achieves 84.5% ImageNet zero-shot accuracy in two days.”
- Sigmoid loss performs significantly better than the softmax loss when the batch size is smaller than 16 k. _[verified]_
  > p. 2: “We find that the sigmoid loss performs significantly better than the softmax loss when the batch size is smaller than 16 k.”

## Code

- https://github.com/google-research/big_vision _[verified]_
  > p. 1: “We propose a simple pairwise Sigmoid loss for Language-Image Pre-training (SigLIP). Unlike standard contrastive learning with softmax normalization, the sigmoid loss operates solely on image-text pairs and does not require a global view of the pairwise similarities for normalization. The sigmoid loss simultaneously allows further scaling up the batch size, while also performing better at smaller batch sizes. Combined with Locked-image Tuning, with only four TPUv4 chips, we train a SigLiT model that achieves 84.5% ImageNet zero-shot accuracy in two days. The disentanglement of the batch size from the loss further allows us to study the impact of examples vs pairs and negative to positive ratio. Finally, we push the batch size to the extreme, up to one million, and find that the benefits of growing batch size quickly diminish, with a more reasonable batch size of 32 k being sufficient. We release our models at https://github. com/google-research/big_vision and hope our research motivates further explorations in improving the quality and efficiency of language-image pre-training.”


## 2112.10752

# High-Resolution Image Synthesis with Latent Diffusion Models

Robin Rombach, Andreas Blattmann, Dominik Lorenz, Patrick Esser, Björn Ommer
2022 · arXiv:2112.10752v2[cs.CV]

## Problem

- Diffusion models typically operate directly in pixel space, making optimization consume hundreds of GPU days and inference expensive. _[verified]_
  > p. 1: “However, since these models typically operate directly in pixel space, optimization of powerful DMs often consumes hundreds of GPU days and inference is expensive due to sequential evaluations.”
- High-resolution synthesis of complex scenes is computationally demanding and requires massive resources only available to a small fraction of the field. _[verified]_
  > p. 1: “Especially high-resolution synthesis of complex, natural scenes is presently dominated by scaling up likelihood-based models, potentially containing billions of parameters in autoregressive (AR) transformers [66,67].”

## Task

- image inpainting _[verified]_
  > p. 1: “Our latent diffusion models (LDMs) achieve new state-of-the-art scores for image inpainting and class-conditional image synthesis and highly competitive performance on various tasks, including text-to-image synthesis, unconditional image generation and super-resolution, while significantly reducing computational requirements compared to pixel-based DMs.”
- class-conditional image synthesis _[verified]_
  > p. 1: “Our latent diffusion models (LDMs) achieve new state-of-the-art scores for image inpainting and class-conditional image synthesis and highly competitive performance on various tasks, including text-to-image synthesis, unconditional image generation and super-resolution, while significantly reducing computational requirements compared to pixel-based DMs.”
- text-to-image synthesis _[verified]_
  > p. 1: “Our latent diffusion models (LDMs) achieve new state-of-the-art scores for image inpainting and class-conditional image synthesis and highly competitive performance on various tasks, including text-to-image synthesis, unconditional image generation and super-resolution, while significantly reducing computational requirements compared to pixel-based DMs.”
- unconditional image generation _[verified]_
  > p. 1: “Our latent diffusion models (LDMs) achieve new state-of-the-art scores for image inpainting and class-conditional image synthesis and highly competitive performance on various tasks, including text-to-image synthesis, unconditional image generation and super-resolution, while significantly reducing computational requirements compared to pixel-based DMs.”
- super-resolution _[verified]_
  > p. 1: “Our latent diffusion models (LDMs) achieve new state-of-the-art scores for image inpainting and class-conditional image synthesis and highly competitive performance on various tasks, including text-to-image synthesis, unconditional image generation and super-resolution, while significantly reducing computational requirements compared to pixel-based DMs.”

## Contributions

- Our method scales more gracefully to higher dimensional data and can be efficiently applied to high-resolution synthesis of megapixel images. _[verified]_
  > p. 2: “(i) In contrast to purely transformer-based approaches [23,66], our method scales more graceful to higher dimensional data and can thus (a) work on a compression level which provides more faithful and detailed reconstructions than previous work (see Fig. 1) and (b) can be efficiently Figure 2. Illustrating perceptual and semantic compression: Most bits of a digital image correspond to imperceptible details.”
- We achieve competitive performance on multiple tasks while significantly lowering computational and inference costs. _[verified]_
  > p. 2: “(ii) We achieve competitive performance on multiple tasks (unconditional image synthesis, inpainting, stochastic super-resolution) and datasets while significantly lowering computational costs.”
- Our approach does not require a delicate weighting of reconstruction and generative abilities, ensuring faithful reconstructions and little regularization. _[verified]_
  > p. 2: “(iii) We show that, in contrast to previous work [93] which learns both an encoder/decoder architecture and a score-based prior simultaneously, our approach does not require a delicate weighting of reconstruction and generative abilities.”
- Our model can be applied in a convolutional fashion for densely conditioned tasks to render large, consistent images. _[verified]_
  > p. 2: “(iv) We find that for densely conditioned tasks such as super-resolution, inpainting and semantic synthesis, our model can be applied in a convolutional fashion and render large, consistent images of ∼ 1024 2 px.”
- We design a general-purpose conditioning mechanism based on cross-attention, enabling multi-modal training. _[verified]_
  > p. 2: “(v) Moreover, we design a general-purpose conditioning mechanism based on cross-attention, enabling multi-modal training.”
- We release pretrained latent diffusion and autoencoding models that might be reusable for various tasks. _[verified]_
  > p. 2: “(vi) Finally, we release pretrained latent diffusion and autoencoding models at https : / / github . com/CompVis/latent-diffusion which might be reusable for a various tasks besides training of DMs [81].”

## Method

- An autoencoder is used to compress images into a low-dimensional latent space using a perceptual loss and a patch-based adversarial objective. _[verified]_
  > p. 3: “Our perceptual compression model is based on previous work [23] and consists of an autoencoder trained by combination of a perceptual loss [106] and a patch-based [33] adversarial objective [20,23,103].”
- The latent space is regularized using either a KL-penalty or a vector quantization layer to avoid arbitrarily high-variance latent spaces. _[verified]_
  > p. 4: “In order to order to avoid arbitrarily high-variance latent spaces, we experiment with two different kinds of regularizations.”
- A diffusion model is trained in the learned latent space using a reweighted variant of the variational lower bound to predict a denoised variant. _[partial]_
  > p. 4: “For image synthesis, the most successful models [15,30,72] rely on a reweighted variant of the variational lower bound on p(x), which mirrors denoising score-matching [85].”
- The neural backbone of the model is a time-conditional UNet that uses cross-attention mechanisms to incorporate conditioning inputs from various modalities. _[partial]_
  > p. 4: “The neural backbone θ (•, t) of our model is realized as a time-conditional UNet [71].”

## Novelty

- The approach explicitly separates the compressive learning phase from the generative learning phase. _[verified]_
  > p. 3: “We propose to circumvent this drawback by introducing an explicit separation of the compressive from the generative learning phase (see Fig. 2).”
- Unlike previous works that used an arbitrary 1D ordering, this method preserves the 2D spatial structure of the learned latent space using mild compression rates. _[verified]_
  > p. 4: “This is in contrast to previous works [23,66], which relied on an arbitrary 1D ordering of the learned space z to model its distribution autoregressively and thereby ignored much of the inherent structure of z.”
- Unlike previous work relying on autoregressive transformers in a discrete latent space, this approach exploits image-specific inductive biases via a UNet. _[verified]_
  > p. 4: “Unlike previous work that relied on autoregressive, attention-based transformer models in a highly compressed, discrete latent space [23,66,103], we can take advantage of image-specific inductive biases that our model offers.”

## Datasets

- ImageNet _[verified]_
  > p. 5: “Fig. 6 shows sample quality as a function of training progress for 2M steps of class-conditional models on the ImageNet [12] dataset.”
- CelebA-HQ _[verified]_
  > p. 5: “We train unconditional models of 256 2 images on CelebA-HQ [39], FFHQ [41], LSUN-Churches and -Bedrooms [102] and evaluate the i) sample quality and ii) their coverage of the data manifold using ii) FID [29] and ii) Precision-and-Recall [50].”
- FFHQ _[verified]_
  > p. 5: “We train unconditional models of 256 2 images on CelebA-HQ [39], FFHQ [41], LSUN-Churches and -Bedrooms [102] and evaluate the i) sample quality and ii) their coverage of the data manifold using ii) FID [29] and ii) Precision-and-Recall [50].”
- LSUN-Churches _[verified]_
  > p. 5: “We train unconditional models of 256 2 images on CelebA-HQ [39], FFHQ [41], LSUN-Churches and -Bedrooms [102] and evaluate the i) sample quality and ii) their coverage of the data manifold using ii) FID [29] and ii) Precision-and-Recall [50].”
- LSUN-Bedrooms _[verified]_
  > p. 5: “We train unconditional models of 256 2 images on CelebA-HQ [39], FFHQ [41], LSUN-Churches and -Bedrooms [102] and evaluate the i) sample quality and ii) their coverage of the data manifold using ii) FID [29] and ii) Precision-and-Recall [50].”
- LAION _[unsupported]_
  > p. 6: “Samples generated with 200 DDIM steps and η = 1.0. We use unconditional guidance [32] with s = 10.0. and avoid the difficulty of weighing reconstruction quality against learning the prior over the latent space, see Fig. 12.”
- LAION-400M _[verified]_
  > p. 7: “For textto-image image modeling, we train a 1.45B parameter KL-regularized LDM conditioned on language prompts on LAION-400M [78].”
- MS-COCO (validation) _[verified]_
  > p. 7: “For quantitative analysis, we follow prior work and evaluate text-to-image generation on the MS-COCO [51] validation set, where our model improves upon powerful AR [17,66] and GAN-based [109] methods, cf . Tab. 2.”
  > p. 7: “To further analyze the flexibility of the cross-attention based conditioning mechanism we also train models to synthesize images based on semantic layouts on OpenImages [49], and finetune on COCO [4], see c.f.g [32], s = 1.5”
- OpenImages _[verified]_
  > p. 7: “To further analyze the flexibility of the cross-attention based conditioning mechanism we also train models to synthesize images based on semantic layouts on OpenImages [49], and finetune on COCO [4], see c.f.g [32], s = 1.5”
- Places _[verified]_
  > p. 8: “The exact training & evaluation protocol on Places [108] is described in Sec. E.2.2.”

## Baselines

- DC-VAE _[verified]_
  > p. 6: “DC-VAE [63] | 15.8 | - | - |  | ImageBART [21] | 9.57 | - | -”
- VQGAN+T. _[verified]_
  > p. 6: “VQGAN+T. [23] (k=400) | 10.2 | - | - |  | U-Net GAN (+aug) [77] | 10.9 (7.6) | - | -”
- PGGAN _[verified]_
  > p. 6: “PGGAN [39] | 8.0 | - | - |  | UDM [43] | 5.54 | - | -”
- LSGM _[verified]_
  > p. 6: “LSGM [93] | 7.22 | - | - |  | StyleGAN [41] | 4.16 | 0.71 | 0.46”
- UDM _[verified]_
  > p. 6: “UDM [43] | 7.16 | - | - |  | ProjectedGAN [76] | 3.08 | 0.65 | 0.46”
- ImageBART _[verified]_
  > p. 6: “ImageBART [21] | 9.57 | - | -”
- U-Net GAN (+aug) _[verified]_
  > p. 6: “U-Net GAN (+aug) [77] | 10.9 (7.6) | - | -”
- StyleGAN _[verified]_
  > p. 6: “StyleGAN [41] | 4.16 | 0.71 | 0.46”
  > p. 6: “StyleGAN2 [42] | 3.86 | - |  | - | StyleGAN [41] | 2.35 | 0.59 | 0.48”
- ProjectedGAN _[verified]_
  > p. 6: “ProjectedGAN [76] | 3.08 | 0.65 | 0.46”
- DDPM _[verified]_
  > p. 6: “DDPM [30] | 7.89 | - |  | - | ImageBART [21] | 5.51 | - | -”
- ADM _[verified]_
  > p. 6: “ADM [15] | 1.90 | 0.66 | 0.51”
- CogView _[verified]_
  > p. 6: “CogView^† [17] | 27.10 | 18.20 | 4B | self-ranking, rejection rate 0.017”
- LAFITE _[verified]_
  > p. 6: “LAFITE^† [109] | 26.94 | 26.02 | 75M |”
- GLIDE _[verified]_
  > p. 6: “GLIDE^∗ [59] | 12.24 | - | 6B | 277 DDIM steps, c.f.g. [32] s = 3”
- Make-A-Scene _[verified]_
  > p. 6: “Make-A-Scene^∗ [26] | 11.84 | - | 4B | c.f.g for AR models [98] s = 5”
- Image Regression _[verified]_
  > p. 8: “Image Regression [72] | 15.2 | 121.1 | 27.9 | 0.801 | 625M | N/A”
- SR3 _[verified]_
  > p. 8: “SR3 [72] | 5.2 | 180.1 | 26.4 | 0.762 | 625M | N/A”
- LaMa _[verified]_
  > p. 9: “LaMa [88]^† | 12.31 | 0.243± | 0.038 | 2.23 | 0.134± | 0.080”
- CoModGAN _[verified]_
  > p. 9: “CoModGAN [107] | 10.4 | 0.26 |  | 1.82 | 0.15 |”
- RegionWise _[verified]_
  > p. 9: “RegionWise [52] | 21.3 | 0.27 |  | 4.75 | 0.15 |”
- DeepFill v2 _[verified]_
  > p. 9: “DeepFill v2 [104] | 22.1 | 0.28 |  | 5.20 | 0.16 |”
- EdgeConnect _[verified]_
  > p. 9: “EdgeConnect [58] | 30.5 | 0.28 |  | 8.37 | 0.16 |”

## Metrics

- Fréchet Inception Distance _[verified]_
  > p. 5: “We train unconditional models of 256 2 images on CelebA-HQ [39], FFHQ [41], LSUN-Churches and -Bedrooms [102] and evaluate the i) sample quality and ii) their coverage of the data manifold using ii) FID [29] and ii) Precision-and-Recall [50].”
- Precision _[verified]_
  > p. 5: “We train unconditional models of 256 2 images on CelebA-HQ [39], FFHQ [41], LSUN-Churches and -Bedrooms [102] and evaluate the i) sample quality and ii) their coverage of the data manifold using ii) FID [29] and ii) Precision-and-Recall [50].”
- Recall _[verified]_
  > p. 5: “We train unconditional models of 256 2 images on CelebA-HQ [39], FFHQ [41], LSUN-Churches and -Bedrooms [102] and evaluate the i) sample quality and ii) their coverage of the data manifold using ii) FID [29] and ii) Precision-and-Recall [50].”
- Inception Score _[unsupported]_
  > p. 6: “CogView^† [17] | 27.10 | 18.20 | 4B | self-ranking, rejection rate 0.017”
- Peak Signal-to-Noise Ratio _[verified]_
  > p. 8: “Method | FID ↓ | IS ↑ | PSNR ↑ | SSIM ↑ | Nparams | [ sampless ](∗ )”
- Structural Similarity Index _[verified]_
  > p. 8: “Method | FID ↓ | IS ↑ | PSNR ↑ | SSIM ↑ | Nparams | [ sampless ](∗ )”
- Learned Perceptual Image Patch Similarity _[verified]_
  > p. 9: “Method | FID ↓ | LPIPS | ↓ | FID ↓ | LPIPS | ↓”

## Hyperparameters

- parameters: 1.45B _[verified]_
  > p. 7: “For textto-image image modeling, we train a 1.45B parameter KL-regularized LDM conditioned on language prompts on LAION-400M [78].”
- parameters: 387M _[verified]_
  > p. 8: “Following [15], the UNet of this diffusion model uses attention layers on three levels of its feature hierarchy, the BigGAN [3] residual block for up-and downsampling and has 387M parameters”

## Compute

- Single NVIDIA A100 GPU used for experiments _[verified]_
  > p. 5: “To obtain a comparable test-field, we fix the computational resources to a single NVIDIA A100 for all experiments in this section and train all models for the same number of steps and with the same number of parameters.”

## Ablations

- Ablation on downsampling factor f for LDM _[verified]_
  > p. 5: “This section analyzes the behavior of our LDMs with different downsampling factors f ∈ {1, 2, 4, 8, 16, 32} (abbreviated as LDM-f , where LDM-1 corresponds to pixel-based DMs).”
- Ablation on first stage regularization schemes (KL vs VQ) and attention mechanisms _[verified]_
  > p. 8: “In particular, we compare the inpainting efficiency of LDM-1 (i.e. a pixel-based conditional DM) with LDM-4, for both KL and VQ regularizations, as well as VQ-LDM-4 without any attention in the first stage (see Tab. 8), where the latter reduces GPU memory for decoding at high resolutions.”

## Claims

- Our latent diffusion models achieve new state-of-the-art scores for image inpainting and class-conditional image synthesis. _[verified]_
  > p. 1: “Our latent diffusion models (LDMs) achieve new state-of-the-art scores for image inpainting and class-conditional image synthesis and highly competitive performance on various tasks, including text-to-image synthesis, unconditional image generation and super-resolution, while significantly reducing computational requirements compared to pixel-based DMs.”

## Limitations

- Sequential sampling is slower than GANs. _[verified]_
  > p. 9: “While LDMs significantly reduce computational requirements compared to pixel-based approaches, their sequential sampling process is still slower than that of GANs.”
- Reconstruction capability can bottleneck tasks requiring fine pixel-space accuracy. _[verified]_
  > p. 9: “Moreover, the use of LDMs can be questionable when high precision is required: although the loss of image quality is very small in our f = 4 autoencoding models (see Fig. 1), their reconstruction capability can become a bottleneck for tasks that require fine-grained accuracy in pixel space.”

## Future work

- Perform a more detailed analysis of modifying the UNet architecture by conditioning on the time step. _[verified]_
  > p. 26: “We leave a more detailed analysis of this modification to future work.”

## Ethics

- Generative models can facilitate the creation of manipulated data or spam. _[verified]_
  > p. 9: “On the other hand, it also means that it becomes easier to create and disseminate manipulated data or spread misinformation and spam.”
- Deep fakes disproportionately affect women. _[verified]_
  > p. 9: “In particular, the deliberate manipulation of images ("deep fakes") is a common problem in this context, and women in particular are disproportionately affected by it [13,24].”
- Generative models can reveal sensitive training data collected without consent. _[verified]_
  > p. 9: “Generative models can also reveal their training data [5,90], which is of great concern when the data contain sensitive or personal information and were collected without explicit consent.”
- Deep learning modules tend to reproduce or exacerbate existing data biases. _[verified]_
  > p. 9: “Finally, deep learning modules tend to reproduce or exacerbate biases that are already present in the data [22,38,91].”

## Code

- https://github.com/lucidrains/x-transformers _[verified]_
  > p. 24: “adapted from https://github.com/lucidrains/x-transformers”
- https://huggingface.co/transformers/model_doc/bert.html _[verified]_
  > p. 26: “https://huggingface.co/transformers/model_doc/bert.html#berttokenizerfast”


## 2212.09748

# Scalable Diffusion Models with Transformers

William Peebles, Saining Xie
2023 · arXiv:2212.09748v2[cs.CV]

## Problem

- Transformers have been widely adopted in autoregressive models but remain underutilized in other generative frameworks like diffusion models, which traditionally rely on convolutional U-Net architectures. _[verified]_
  > p. 1: “Many classes of image-level generative models remain holdouts to the trend, though-while transformers see widespread use in autoregressive models [3,6,43,47], they have seen less adoption in other generative modeling frameworks.”

## Task

- image-level generative modeling _[verified]_
  > p. 1: “Many classes of image-level generative models remain holdouts to the trend, though-while transformers see widespread use in autoregressive models [3,6,43,47], they have seen less adoption in other generative modeling frameworks.”

## Contributions

- Demystify architectural choices in diffusion models and provide empirical baselines using standard transformer designs. _[verified]_
  > p. 2: “With this work, we aim to demystify the significance of architectural choices in diffusion models and offer empirical baselines for future generative modeling research.”
- Introduce Diffusion Transformers (DiTs), a new class of diffusion models based on Vision Transformers. _[verified]_
  > p. 2: “In this paper, we focus on a new class of diffusion models based on transformers.”
- Study the scaling behavior of transformers regarding network complexity versus sample quality under the Latent Diffusion Models framework. _[verified]_
  > p. 2: “More specifically, we study the scaling behavior of transformers with respect to network complexity vs. sample quality.”

## Method

- The approach applies Diffusion Transformers (DiTs) to latent space by combining off-the-shelf convolutional VAEs with transformer-based DDPMs. _[verified]_
  > p. 4: “In this paper, we apply DiTs to latent space, although they could be applied to pixel space without modification as well.”
- The model uses a patchify first layer to convert spatial representations into a sequence of tokens, combined with frequency-based positional embeddings. _[verified]_
  > p. 4: “The first layer of DiT is "patchify," which converts the spatial input into a sequence of T tokens, each of dimension d, by linearly embedding each patch in the input.”
- The architecture processes conditional inputs such as timesteps and class labels using four explored variants of transformer blocks (in-context conditioning, cross-attention, adaLN, and adaLN-Zero). _[verified]_
  > p. 4: “We explore four variants of transformer blocks that process conditional inputs differently.”
- Model scaling is handled via standard transformer configs (DiT-S, DiT-B, DiT-L, and DiT-XL) that jointly scale depth, hidden dimension, and attention heads. _[verified]_
  > p. 5: “Following ViT, we use standard transformer configs that jointly scale N , d and attention heads [10,63].”
- A standard linear decoder is used after the final DiT block to map the output sequence back into noise and covariance predictions matching the original spatial shape. _[verified]_
  > p. 5: “We use a standard linear decoder to do this; we apply the final layer norm (adaptive if using adaLN) and linearly decode each token into a p×p×2C tensor, where C is the number of channels in the spatial input to DiT.”

## Novelty

- The authors introduce Diffusion Transformers (DiTs) as a new architecture for diffusion models that stays faithful to the standard vision transformer (ViT) architecture to retain scaling properties. _[partial]_
  > p. 4: “We introduce Diffusion Transformers (DiTs), a new architecture for diffusion models.”

## Datasets

- ImageNet _[verified]_
  > p. 5: “We train class-conditional latent DiT models at 256 × 256 and 512 × 512 image resolution on the Ima-geNet dataset [31], a highly-competitive generative modeling benchmark.”

## Baselines

- BigGAN-deep _[verified]_
  > p. 9: “BigGAN-deep [2] | 6.95 | 7.36 | 171.4 | 0.87 | 0.28”
- StyleGAN-XL _[verified]_
  > p. 9: “StyleGAN-XL [53] | 2.30 | 4.02 | 265.12 | 0.78 | 0.53”
- ADM _[verified]_
  > p. 9: “ADM [9] | 10.94 | 6.02 | 100.98 | 0.69 | 0.63”
  > p. 9: “ADM-U | 7.49 | 5.13 | 127.49 | 0.72 | 0.63”
  > p. 9: “ADM-G | 4.59 | 5.25 | 186.70 | 0.82 | 0.52”
  > p. 9: “ADM-G, ADM-U | 3.94 | 6.14 | 215.84 | 0.83 | 0.53”
- CDM _[verified]_
  > p. 9: “CDM [20] | 4.88 | - | 158.71 | - | -”
- LDM-8 _[verified]_
  > p. 9: “LDM-8 [48] | 15.51 | - | 79.03 | 0.65 | 0.63”
  > p. 9: “LDM-8-G | 7.76 | - | 209.52 | 0.84 | 0.35”
- LDM-4 _[verified]_
  > p. 9: “LDM-4 | 10.56 | - | 103.49 | 0.71 | 0.62”
  > p. 9: “LDM-4-G (cfg=1.25) | 3.95 | - | 178.22 | 0.81 | 0.55”

## Metrics

- Fréchet Inception Distance (FID) _[verified]_
  > p. 6: “We measure scaling performance with Fréchet Inception Distance (FID) [18], the standard metric for evaluating generative models of images.”
- Inception Score _[verified]_
  > p. 6: “We additionally report Inception Score [51], sFID [34] and Precision/Recall [32] as secondary metrics.”
- sFID _[verified]_
  > p. 6: “We additionally report Inception Score [51], sFID [34] and Precision/Recall [32] as secondary metrics.”
- Precision _[verified]_
  > p. 6: “We additionally report Inception Score [51], sFID [34] and Precision/Recall [32] as secondary metrics.”
- Recall _[verified]_
  > p. 6: “We additionally report Inception Score [51], sFID [34] and Precision/Recall [32] as secondary metrics.”

## Hyperparameters

- optimizer: AdamW _[verified]_
  > p. 5: “We train all models with AdamW [29,33].”
- learning rate: 1 × 10 -4 _[verified]_
  > p. 6: “We use a constant learning rate of 1 × 10 -4 , no weight decay and a batch size of 256.”
- weight decay: no weight decay _[verified]_
  > p. 6: “We use a constant learning rate of 1 × 10 -4 , no weight decay and a batch size of 256.”
- batch size: 256 _[verified]_
  > p. 6: “We use a constant learning rate of 1 × 10 -4 , no weight decay and a batch size of 256.”
- EMA decay: 0.9999 _[verified]_
  > p. 6: “Following common practice in the generative modeling literature, we maintain an exponential moving average (EMA) of DiT weights over training with a decay of 0.9999.”

## Compute

- TPU-v3 pods _[verified]_
  > p. 6: “We implement all models in JAX [1] and train them using TPU-v3 pods.”

## Ablations

- Ablation of block designs: in-context, cross-attention, adaptive layer norm (adaLN), and adaLN-zero _[verified]_
  > p. 6: “We train four of our highest Gflop DiT-XL/2 models, each using a different block designin-context (119.4 Gflops), cross-attention (137.6 Gflops), adaptive layer norm (adaLN, 118.6 Gflops) or adaLN-zero (118.6 Gflops).”
- Ablation of model configs (S, B, L, XL) and patch sizes (8, 4, 2) _[verified]_
  > p. 8: “We train 12 DiT models, sweeping over model configs (S, B, L, XL) and patch sizes (8,4,2).”
- Ablation of three VAE decoders (original LDM decoder and two fine-tuned decoders used by Stable Diffusion) _[verified]_
  > p. 13: “In this section, we ablate three different choices of the VAE decoder; the original one used by LDM and the two fine-tuned decoders used by Stable Diffusion.”

## Claims

- The U-Net inductive bias is not crucial to diffusion model performance and can be replaced with transformers. _[verified]_
  > p. 2: “We show that the U-Net inductive bias is not crucial to the performance of diffusion models, and they can be readily replaced with standard designs such as transformers.”
- There is a strong correlation between DiT network complexity (measured in Gflops) and sample quality (measured by FID). _[verified]_
  > p. 2: “We further show that DiTs are scalable architectures for diffusion models: there is a strong correlation between the network complexity (measured by Gflops) vs. sample quality (measured by FID).”
- Scaling up DiT with a high-capacity backbone (118.6 Gflops) achieves a state-of-the-art result of 2.27 FID on class-conditional 256x256 ImageNet generation. _[verified]_
  > p. 2: “By simply scaling-up DiT and training an LDM with a high-capacity backbone (118.6 Gflops), we are able to achieve a state-of-the-art result of 2.27 FID on the classconditional 256 × 256 ImageNet generation benchmark.”

## Future work

- Continue scaling Diffusion Transformers to larger model sizes and token counts _[verified]_
  > p. 9: “Given the promising scaling results in this paper, future work should continue to scale DiTs to larger models and token counts.”
- Explore DiT as a drop-in backbone for text-to-image models like DALL•E 2 and Stable Diffusion _[verified]_
  > p. 9: “DiT could also be explored as a drop-in backbone for textto-image models like DALL•E 2 and Stable Diffusion.”
- Explore further why applying classifier-free guidance to a subset of elements yields good performance _[verified]_
  > p. 12: “It is somewhat interesting that applying guidance to a subset of elements can still yield good performance, and we leave it to future work to explore this phenomenon further.”


## 2210.02747

# FLOW MATCHING FOR GENERATIVE MODELING

Yaron Lipman, Ricky T Q Chen, Heli Ben-Hamu, Maximilian Nickel, Matt Le, FAIR Meta Ai
2023 · arXiv:2210.02747v2[cs.LG]

## Problem

- Existing methods for training Continuous Normalizing Flows lack scalability due to expensive simulations, intractable integrals, or biased gradients. _[verified]_
  > p. 1: “Indeed, maximum likelihood training (e.g., Grathwohl et al. (2018)) require expensive numerical ODE simulations, while existing simulation-free methods either involve intractable integrals (Rozen et al., 2021) or biased gradients (Ben-Hamu et al., 2022).”
- Diffusion-based models are restricted to simple diffusion processes, leading to confined sampling paths and long training times. _[verified]_
  > p. 1: “However, the restriction to simple diffusion processes leads to a rather confined space of sampling probability paths, resulting in very long training times and the need to adopt specialized methods (e.g., Song et al. (2020a); Zhang & Chen (2022)) for efficient sampling.”

## Task

- generative modeling _[verified]_
  > p. 1: “We introduce a new paradigm for generative modeling built on Continuous Normalizing Flows (CNFs), allowing us to train CNFs at unprecedented scale.”

## Contributions

- We introduce Flow Matching (FM), a simulation-free approach for training Continuous Normalizing Flows. _[verified]_
  > p. 1: “Specifically, we present the notion of Flow Matching (FM), a simulation-free approach for training CNFs based on regressing vector fields of fixed conditional probability paths.”
- We propose the Conditional Flow Matching (CFM) training objective which provides equivalent gradients without requiring knowledge of the target vector field. _[verified]_
  > p. 2: “Then, inspired by denoising score matching, we show that a per-example training objective, termed Conditional Flow Matching (CFM), provides equivalent gradients and does not require explicit knowledge of the intractable target vector field.”
- We introduce the use of Optimal Transport displacement interpolation to define conditional probability paths for faster training and sampling. _[verified]_
  > p. 1: “An instance of particular interest is using Optimal Transport (OT) displacement interpolation to define the conditional probability paths.”

## Method

- The Flow Matching objective is designed to match a target probability path by regressing the vector field u_t with a neural network v_t parameterized by learnable parameters theta. _[verified]_
  > p. 2: “The Flow Matching objective is then designed to match this target probability path, which will allow us to flow from p 0 to p 1 .”
- The Conditional Flow Matching (CFM) objective allows for tractable training by conditioning on individual data samples, sharing identical gradients with the original Flow Matching objective. _[verified]_
  > p. 4: “Specifically, we consider the Conditional Flow Matching (CFM) objective,”
- Gaussian conditional probability paths and corresponding unique vector fields are constructed using time-dependent mean and standard deviation functions. _[verified]_
  > p. 4: “Namely, we consider conditional probability paths of the form p t (x|x 1 ) = N (x | µ t (x 1 ), σ t (x 1 ) 2 I), (10) where µ : [0, 1] × R d → R d is the time-dependent mean of the Gaussian distribution, while σ : [0, 1] × R → R >0 describes a time-dependent scalar standard deviation (std).”

## Novelty

- Conditional Flow Matching generalizes vector field matching compared to existing diffusion models and score matching approaches. _[verified]_
  > p. 7: “Conditional Flow Matching draws inspiration from this result, but generalizes to matching vector fields directly.”
- Unlike previous works that rely on restricted settings of Gaussian conditional paths defined by simple diffusion processes, the proposed formulation accommodates broader paths such as the conditional Optimal Transport path. _[verified]_
  > p. 7: “in particular -it does not include our conditional OT path.”

## Datasets

- CIFAR-10 _[verified]_
  > p. 7: “We explore the empirical benefits of using Flow Matching on the image datasets of CIFAR-10 ( Krizhevsky et al., 2009) and ImageNet at resolutions 32, 64, and 128 (Chrabaszcz et al., 2017;Deng et al., 2009).”
- ImageNet _[verified]_
  > p. 7: “We explore the empirical benefits of using Flow Matching on the image datasets of CIFAR-10 ( Krizhevsky et al., 2009) and ImageNet at resolutions 32, 64, and 128 (Chrabaszcz et al., 2017;Deng et al., 2009).”
- ImageNet validation set (validation) _[verified]_
  > p. 9: “Lastly, we experimented with Flow Matching for conditional image generation. In particular, upsampling images procedure in (Saharia et al., 2022) and compute the FID of the upsampled validation images; baselines include reference (FID of original validation set), and regression.”

## Baselines

- DDPM _[verified]_
  > p. 8: “DDPM | 3.12 | 7.48 | 274 | 3.54 | 6.99 | 262 | 3.32 | 17.36 | 264 | PacGAN2 (Lin et al., 2018) | – | 57.5”
- Score Matching _[verified]_
  > p. 8: “Score Matching | 3.16 | 19.94 | 242 | 3.56 | 5.68 | 178 | 3.40 | 19.74 | 441 | Logo-GAN-AE (Sage et al., 2018) | – | 50.9”
- ScoreFlow _[verified]_
  > p. 8: “ScoreFlow | 3.09 | 20.78 | 428 | 3.55 | 14.14 | 195 | 3.36 | 24.95 | 601 | Self-cond. GAN (Luˇci´c et al., 2019) | – | 41.7”
- MGAN _[verified]_
  > p. 8: “MGAN (Hoang et al., 2018) | – | 58.9”
- PacGAN2 _[verified]_
  > p. 8: “PacGAN2 (Lin et al., 2018) | – | 57.5”
- Logo-GAN-AE _[verified]_
  > p. 8: “Logo-GAN-AE (Sage et al., 2018) | – | 50.9”
- Self-cond. GAN _[verified]_
  > p. 8: “Self-cond. GAN (Luˇci´c et al., 2019) | – | 41.7”
- Uncond. BigGAN _[verified]_
  > p. 8: “Uncond. BigGAN (Luˇci´c et al., 2019) | – | 25.3”
- PGMGAN _[verified]_
  > p. 8: “PGMGAN (Armandpour et al., 2021) | – | 21.7”
- SR3 _[verified]_
  > p. 9: “SR3Regression(Sahariaet al., 2022) | 15.25.2 | 121.1180.1 | 26.427.9 | 0.8010.762”
- Regression _[verified]_
  > p. 9: “SR3Regression(Sahariaet al., 2022) | 15.25.2 | 121.1180.1 | 26.427.9 | 0.8010.762”

## Metrics

- Likelihood (BPD / NLL) _[verified]_
  > p. 8: “Table 1: Likelihood (BPD), quality of generated samples (FID), and evaluation time (NFE) for the same model trained with different methods.”
- FID _[verified]_
  > p. 8: “Table 1: Likelihood (BPD), quality of generated samples (FID), and evaluation time (NFE) for the same model trained with different methods.”
- NFE _[verified]_
  > p. 8: “Table 1: Likelihood (BPD), quality of generated samples (FID), and evaluation time (NFE) for the same model trained with different methods.”
- PSNR _[verified]_
  > p. 9: “FM-OT achieves similar PSNR and SSIM values to (Saharia et al., 2022) while considerably improving on FID and IS, which as argued by (Saharia et al., 2022) is a better indication of generation quality.”
- SSIM _[verified]_
  > p. 9: “FM-OT achieves similar PSNR and SSIM values to (Saharia et al., 2022) while considerably improving on FID and IS, which as argued by (Saharia et al., 2022) is a better indication of generation quality.”
- IS _[verified]_
  > p. 9: “FM-OT achieves similar PSNR and SSIM values to (Saharia et al., 2022) while considerably improving on FID and IS, which as argued by (Saharia et al., 2022) is a better indication of generation quality.”

## Seeds and runs

- Averaged over 50k samples _[verified]_
  > p. 8: “w / OT 2.90 20.9 2017)), and averaged number of function evaluations (NFE) required for the adaptive solver to reach its a prespecified numerical tolerance, averaged over 50k samples.”
- Identical random seeds used for comparison _[verified]_
  > p. 9: “Figure 6 shows samples from ImageNet-64 models using identical random seeds, where we find that the OT path model starts generating images sooner than the diffusion path models, where noise dominates the image until the very last time point.”
- 256 random noise seeds _[verified]_
  > p. 9: “In Figure 7 (left), we compare the per-pixel MSE of low NFE solutions compared with 1000 NFE solutions (we use 256 random noise seeds), and notice that the FM with OT model produces the best numerical error, in terms of computational cost, requiring roughly only 60% of the NFEs to reach the same error threshold as diffusion models.”

## Ablations

- Choice of diffusion path in Flow Matching between standard variance preserving diffusion path and optimal transport path _[verified]_
  > p. 7: “We also ablate the choice of diffusion path in Flow Matching, particularly between the standard variance preserving diffusion path and the optimal transport path.”

## Claims

- Flow Matching on ImageNet leads to better performance than alternative diffusion-based methods in likelihood and sample quality. _[verified]_
  > p. 1: “Training CNFs using Flow Matching on ImageNet leads to consistently better performance than alternative diffusion-based methods in terms of both likelihood and sample quality, and allows fast and reliable sample generation using off-the-shelf numerical ODE solvers.”

## Future work

- Expect FM to enable a wide variety of probability paths, such as non-isotropic Gaussians or more general kernels. _[verified]_
  > p. 9: “We experimentally showed the ease of training and sampling when using the Flow Matching framework, and in the future, we expect FM to open the door to allowing a multitude of probability paths (e.g., non-isotropic Gaussians or more general kernels altogether).”

## Ethics

- Image generation can potentially be misused for harmful purposes, which can be mitigated via content-controlled training sets and image validation or classification. _[partial]_
  > p. 10: “Along side its many positive applications, image generation can also be used for harmful proposes.”
- The energy consumption of training large deep learning models is rapidly growing, so utilizing methods that require fewer gradient updates or less image throughput can result in major energy and time reductions. _[verified]_
  > p. 10: “Furthermore, the energy demand for training large deep learning models is increasing at a rapid pace (Amodei et al., 2018;Thompson et al., 2020), focusing on methods that are able to train using less gradient updates / image throughput can lead to significant time and energy savings.”

## Code

- https://github.com/tensorflow/gan _[verified]_
  > p. 21: “https://github.com/tensorflow/gan”
- https://github.com/openai/guided-diffusion _[verified]_
  > p. 21: “https://github.com/openai/guided-diffusion”


## 2304.08485

# Visual Instruction Tuning

Haotian Liu, Chunyuan Li, Qingyang Wu, Yong Jae Lee, -Madison, Microsoft Research

## Problem

- Instruction tuning using machine-generated data is less explored in the multimodal field. _[verified]_
  > p. 1: “Instruction tuning large language models (LLMs) using machine-generated instruction-following data has been shown to improve zero-shot capabilities on new tasks, but the idea is less explored in the multimodal field.”
- There is a general lack of vision-language instruction-following data. _[verified]_
  > p. 2: “One key challenge is the lack of vision-language instruction-following data.”

## Task

- Multimodal language-image instruction-following and general-purpose visual and language understanding. _[verified]_
  > p. 1: “By instruction tuning on such generated data, we introduce LLaVA: Large Language and Vision Assistant, an end-to-end trained large multimodal model that connects a vision encoder and an LLM for generalpurpose visual and language understanding.”

## Contributions

- We present a pipeline to convert image-text pairs into an instruction-following format using GPT models. _[verified]_
  > p. 2: “We present a data reformation perspective and pipeline to convert image-text pairs into an appropriate instruction-following format, using ChatGPT/GPT-4.”
- We develop a large multimodal model by connecting a visual encoder with a language decoder and fine-tuning it end-to-end. _[verified]_
  > p. 2: “We develop a large multimodal model (LMM), by connecting the open-set visual encoder of CLIP [40] with the language decoder Vicuna [9], and fine-tuning end-to-end on our generated instructional vision-language data.”
- We introduce LLaVA-Bench with two challenging benchmarks and diverse annotations. _[verified]_
  > p. 2: “We present LLaVA-Bench with two challenging benchmarks, with a diverse selection of paired images, instructions and detailed annotations.”
- We release the generated multimodal instruction data, codebase, model checkpoints, and demo to the public. _[verified]_
  > p. 2: “We release the following assets to the public: the generated multimodal instruction data, the codebase, the model checkpoints, and a visual chat demo.”

## Method

- We choose Vicuna as our language model and the pre-trained CLIP visual encoder ViT-L/14 to extract visual features. _[verified]_
  > p. 4: “We choose Vicuna [9] as our LLM f ϕ (•) parameterized by ϕ, as it has the best instruction following capabilities in language tasks among publicly available checkpoints [48,9,38].”
- A simple linear projection layer connects image features into the word embedding space by applying a trainable matrix W. _[verified]_
  > p. 4: “Specifically, we apply a trainable projection matrix W to convert Z v into language embedding tokens H v , which have the same dimensionality as the word embedding space in the language model:”
- The model is trained using the original auto-regressive training objective of the LLM on the prediction tokens of the assistant answers. _[verified]_
  > p. 4: “We perform instruction-tuning of the LLM on the prediction tokens, using its original auto-regressive training objective.”
- Stage 1 pre-training freezes both the visual encoder and LLM weights, optimizing only the projection matrix for feature alignment using filtered image-text pairs. _[verified]_
  > p. 5: “In training, we keep both the visual encoder and LLM weights frozen, and maximize the likelihood of (3) with trainable parameters θ = W (the projection matrix) only.”
- Stage 2 fine-tuning keeps the visual encoder frozen while updating both the projection layer and the LLM weights end-to-end on multimodal instruction-following data. _[verified]_
  > p. 5: “We always keep the visual encoder weights frozen, and continue to update both the pre-trained weights of the projection layer and LLM in LLaVA; i.e., the trainable parameters are θ = {W, ϕ} in (3).”

## Datasets

- CC-595K _[verified]_
  > p. 5: “We pre-train our model on the filtered CC-595K subset for 1 epoch with a learning rate of 2e-3 and a batch size of 128, and fine-tune on the proposed LLaVA-Instruct-158K dataset for 3 epochs, with a learning rate of 2e-5 and a batch size of 32.”
- LLaVA-Instruct-158K _[verified]_
  > p. 5: “We pre-train our model on the filtered CC-595K subset for 1 epoch with a learning rate of 2e-3 and a batch size of 128, and fine-tune on the proposed LLaVA-Instruct-158K dataset for 3 epochs, with a learning rate of 2e-5 and a batch size of 32.”
- COCO images _[verified]_
  > p. 3: “We use COCO images [31] and generate three types of instruction-following data.”
- COCO-Val-2014 (30 images) _[verified]_
  > p. 7: “We randomly select 30 images from COCO-Val-2014, and for each image, we generate three types of questions (conversation, detailed description, complex reasoning) using the proposed data generation pipeline in Sec. 3, totaling 90 questions.”
- ScienceQA (training, validation, and test, 21k) _[verified]_
  > p. 8: “The benchmark dataset is split into training, validation, and test splits with 12726, 4241, and 4241 examples, respectively.”

## Baselines

- BLIP-2 _[verified]_
  > p. 5: “For comparisons, we quote the prompt and response of the multimodal GPT-4 from their paper, and query BLIP-2 and OpenFlamingo model checkpoints to get their response.”
- OpenFlamingo _[verified]_
  > p. 5: “For comparisons, we quote the prompt and response of the multimodal GPT-4 from their paper, and query BLIP-2 and OpenFlamingo model checkpoints to get their response.”
- GPT-3.5 model with and without CoT _[unsupported]_
  > p. 8: “We consider two representative methods, including GPT-3.5 model (text-davinci-002) with and without chainof-thought (CoT), LLaMA-Adapter [59], as well as multimodal chain-of-thought (MM-CoT) [61], which is the current SoTA method on this dataset.”
- LLaMA-Adapter _[unsupported]_
  > p. 8: “We consider two representative methods, including GPT-3.5 model (text-davinci-002) with and without chainof-thought (CoT), LLaMA-Adapter [59], as well as multimodal chain-of-thought (MM-CoT) [61], which is the current SoTA method on this dataset.”
- Multimodal chain-of-thought (MM-CoT) _[unsupported]_
  > p. 8: “We consider two representative methods, including GPT-3.5 model (text-davinci-002) with and without chainof-thought (CoT), LLaMA-Adapter [59], as well as multimodal chain-of-thought (MM-CoT) [61], which is the current SoTA method on this dataset.”

## Metrics

- Overall score on a scale of 1 to 10 evaluated by GPT-4 _[verified]_
  > p. 6: “It evaluates the helpfulness, relevance, accuracy, and level of detail of the responses from the assistants, and gives an overall score on a scale of 1 to 10, where a higher score indicates better overall performance.”
- Accuracy percentage _[verified]_
  > p. 8: “It yields 90.92% accuracy, which is quite close to the SoTA 91.68%.”

## Hyperparameters

- learning rate (pre-training): 2e-3 _[verified]_
  > p. 5: “We pre-train our model on the filtered CC-595K subset for 1 epoch with a learning rate of 2e-3 and a batch size of 128, and fine-tune on the proposed LLaVA-Instruct-158K dataset for 3 epochs, with a learning rate of 2e-5 and a batch size of 32.”
- batch size (pre-training): 128 _[verified]_
  > p. 5: “We pre-train our model on the filtered CC-595K subset for 1 epoch with a learning rate of 2e-3 and a batch size of 128, and fine-tune on the proposed LLaVA-Instruct-158K dataset for 3 epochs, with a learning rate of 2e-5 and a batch size of 32.”
- epochs (pre-training): 1 _[verified]_
  > p. 5: “We pre-train our model on the filtered CC-595K subset for 1 epoch with a learning rate of 2e-3 and a batch size of 128, and fine-tune on the proposed LLaVA-Instruct-158K dataset for 3 epochs, with a learning rate of 2e-5 and a batch size of 32.”
- learning rate (fine-tuning): 2e-5 _[verified]_
  > p. 5: “We pre-train our model on the filtered CC-595K subset for 1 epoch with a learning rate of 2e-3 and a batch size of 128, and fine-tune on the proposed LLaVA-Instruct-158K dataset for 3 epochs, with a learning rate of 2e-5 and a batch size of 32.”
- batch size (fine-tuning): 32 _[verified]_
  > p. 5: “We pre-train our model on the filtered CC-595K subset for 1 epoch with a learning rate of 2e-3 and a batch size of 128, and fine-tune on the proposed LLaVA-Instruct-158K dataset for 3 epochs, with a learning rate of 2e-5 and a batch size of 32.”
- epochs (fine-tuning): 3 _[verified]_
  > p. 5: “We pre-train our model on the filtered CC-595K subset for 1 epoch with a learning rate of 2e-3 and a batch size of 128, and fine-tune on the proposed LLaVA-Instruct-158K dataset for 3 epochs, with a learning rate of 2e-5 and a batch size of 32.”
- epochs (ScienceQA training): 12 _[verified]_
  > p. 8: “For LLaVA, we use the visual features before the last layer, ask the model to first predict reasons and then the answer, and train it for 12 epochs.”
- optimizer: Adam _[verified]_
  > p. 20: “Following Vicuna, we use the Adam optimizer with no weight decay and a cosine learning rate with a warmup ratio of 3%.”
- weight decay: no weight decay _[verified]_
  > p. 20: “Following Vicuna, we use the Adam optimizer with no weight decay and a cosine learning rate with a warmup ratio of 3%.”
- warmup ratio: 3% _[verified]_
  > p. 20: “Following Vicuna, we use the Adam optimizer with no weight decay and a cosine learning rate with a warmup ratio of 3%.”

## Compute

- Hardware used for training models _[verified]_
  > p. 5: “We train all models with 8× A100s, following Vicuna's hyperparameters [9].”
- Pre-training completion time _[verified]_
  > p. 20: “Pretraining on CC-595K completes within 4 hours.”
- Instruct-158K finetuning completion time _[verified]_
  > p. 20: “Finetuning on Instruct-158K completes within 10 hours.”
- ScienceQA finetuning completion time _[verified]_
  > p. 20: “Finetuning on ScienceQA completes within 4 hours.”

## Seeds and runs

- Number of inference runs for evaluation _[verified]_
  > p. 7: “For the first three rows, we report three inference runs.”

## Ablations

- Ablation on different training data types _[verified]_
  > p. 7: “We vary the training datasets to study the effectiveness of different types of instruction-following data, and show the results in Table 4.”

## Claims

- LLaVA yields an 85.1% relative score compared with GPT-4 on a synthetic multimodal instruction-following dataset. _[verified]_
  > p. 1: “Our experiments show that LLaVA demonstrates impressive multimodal chat abilities, sometimes exhibiting the behaviors of multimodal GPT-4 on unseen images/instructions, and yields a 85.1% relative score compared with GPT-4 on a synthetic multimodal instruction-following dataset.”
- When fine-tuned on Science QA, LLaVA and GPT-4 achieve a new state-of-the-art accuracy of 92.53%. _[verified]_
  > p. 1: “When fine-tuned on Science QA, the synergy of LLaVA and GPT-4 achieves a new state-of-the-art accuracy of 92.53%.”
- LLaVA demonstrates impressive multimodal chat abilities and exhibits behaviors of multimodal GPT-4 on unseen images/instructions. _[verified]_
  > p. 1: “Our experiments show that LLaVA demonstrates impressive multimodal chat abilities, sometimes exhibiting the behaviors of multimodal GPT-4 on unseen images/instructions, and yields a 85.1% relative score compared with GPT-4 on a synthetic multimodal instruction-following dataset.”

## Limitations

- Assessment challenges due to combining language and visual tasks _[verified]_
  > p. 14: “Assessing the performance of LLaVA is challenging as it involves both language and visual tasks.”

## Future work

- Inspiration for future research on more capable multimodal models _[verified]_
  > p. 9: “We hope our work can inspire future research on building more capable multimodal models.”
- Evaluating robustness and unexplored aspects of GPT-4 based multimodal evaluation _[verified]_
  > p. 14: “While text-only GPT-4 based multimodal evaluation is consistent and accurate in our study, its robustness in different situations and capability to evaluate other unexplored aspects are subjects for future work.”

## Ethics

- Deployment and release of LLaVA bring both potential benefits and risks _[verified]_
  > p. 14: “The broader impact of LLaVA, a general-purpose visual assistant, has potential benefits and risks associated with its deployment and release.”
- Precautionary measures used to minimize malicious input risks _[verified]_
  > p. 14: “To minimize potential misuse and harmful consequences, we employ two precautionary measures for LLaVA: (1) OpenAI Filter API for user input text to prevent harmful or inappropriate text instructions from being processed by the model, and (2) NSFW Filter for uploaded user images to detect and block Not Safe For Work (NSFW) content or any other potentially harmful image inputs.”
- Hallucination concerns in critical applications _[verified]_
  > p. 14: “This raises concerns about inferences made, especially in critical applications (e.g., medical).”
- Transfer of bias from base models leading to unfair representations _[verified]_
  > p. 14: “Bias can be transferred from the base models to LLaVA, both from the vision encoder (CLIP) and the language decoder (LLaMA/Vicuna).”
- Energy consumption concerns when scaling up datasets or model sizes _[verified]_
  > p. 14: “Though energy consumption is not a primary concern for LLaVA due to a smaller pretraining dataset (see details in Sec. C), it may become a concern when scaling up the pretraining dataset or increasing the model size, e.g., to a larger LLaMA version like the 65B model.”


## 1502.03167

# Batch Normalization: Accelerating Deep Network Training by Reducing Internal Covariate Shift

Sergey Ioffe
2015 · arXiv:1502.03167v3[cs.LG]

## Problem

- Training deep neural networks is slowed down by changes in the distribution of layer inputs during training. _[verified]_
  > p. 1: “Training Deep Neural Networks is complicated by the fact that the distribution of each layer's inputs changes during training, as the parameters of the previous layers change.”

## Task

- Image classification _[verified]_
  > p. 1: “Applied to a state-of-the-art image classification model, Batch Normalization achieves the same accuracy with 14 times fewer training steps, and beats the original model by a significant margin.”

## Contributions

- Proposing a new mechanism called Batch Normalization to reduce internal covariate shift and accelerate training. _[verified]_
  > p. 2: “We propose a new mechanism, which we call Batch Normalization, that takes a step towards reducing internal covariate shift, and in doing so dramatically accelerates the training of deep neural nets.”

## Method

- Instead of joint whitening, each scalar feature is independently normalized to have a mean of zero and a variance of 1 over the training dataset. _[verified]_
  > p. 3: “The first is that instead of whitening the features in layer inputs and outputs jointly, we will normalize each scalar feature independently, by making it have the mean of zero and the variance of 1.”
- To preserve representation power and allow the identity transform, each normalized activation is scaled and shifted using learned parameters gamma and beta. _[verified]_
  > p. 3: “To accomplish this, we introduce, for each activation x (k) , a pair of parameters γ (k) , β (k) , which scale and shift the normalized value:”
- Mini-batch statistics are used to estimate the mean and variance during stochastic gradient training, enabling full participation in gradient backpropagation. _[verified]_
  > p. 3: “Therefore, we make the second simplification: since we use mini-batches in stochastic gradient training, each mini-batch produces estimates of the mean and variance of each activation.”
- For convolutional layers, activations are jointly normalized over all spatial locations within a mini-batch to preserve the convolutional property. _[verified]_
  > p. 5: “To achieve this, we jointly normalize all the activations in a minibatch, over all locations.”
- During inference, population statistics estimated via moving averages are used instead of mini-batch statistics to perform deterministic normalization. _[verified]_
  > p. 4: “For this, once the network has been trained, we use the normalization x = x - E[x] / Var[x] + epsilon using the population, rather than mini-batch, statistics.”

## Datasets

- MNIST _[verified]_
  > p. 5: “To verify the effects of internal covariate shift on training, and the ability of Batch Normalization to combat it, we considered the problem of predicting the digit class on the MNIST dataset (LeCun et al., 1998a).”
- ImageNet _[verified]_
  > p. 6: “We applied Batch Normalization to a new variant of the Inception network (Szegedy et al., 2014), trained on the ImageNet classification task (Russakovsky et al., 2014).”
- LSVRC2012 (training and validation data) _[verified]_
  > p. 7: “We evaluated the following networks, all trained on the LSVRC2012 training data, and tested on the validation data: Inception: the network described at the beginning of Section 4.2, trained with the initial learning rate of 0.0015.”

## Baselines

- Inception network _[verified]_
  > p. 6: “We refer to this model as Inception in the rest of the text.”
- Deep Image ensemble of traditional models and the ensemble model of He et al. _[verified]_
  > p. 7: “The current reported best results on the ImageNet Large Scale Visual Recognition Competition are reached by the Deep Image ensemble of traditional models (Wu et al., 2015) and the ensemble model of (He et al., 2015).”

## Metrics

- validation accuracy @1 _[verified]_
  > p. 6: “All networks are evaluated as training progresses by computing the validation accuracy @1, i.e. the probability of predicting the correct label out of 1000 possibilities, on a held-out set, using a single crop per image.”
- top-5 validation and test error _[verified]_
  > p. 7: “Here we report a top-5 validation error of 4.9%, and test error of 4.82% (according to the ILSVRC server).”

## Hyperparameters

- mini-batch size: 60 _[verified]_
  > p. 6: “We trained the network for 50000 steps, with 60 examples per mini-batch.”
- training steps: 50000 _[verified]_
  > p. 6: “We trained the network for 50000 steps, with 60 examples per mini-batch.”
- mini-batch size: 32 _[verified]_
  > p. 6: “The model was trained using a version of Stochastic Gradient Descent with momentum (Sutskever et al., 2013), using the mini-batch size of 32.”
- optimizer: Stochastic Gradient Descent with momentum _[verified]_
  > p. 6: “The model was trained using a version of Stochastic Gradient Descent with momentum (Sutskever et al., 2013), using the mini-batch size of 32.”
- initial learning rate (Inception training): 0.0015 _[verified]_
  > p. 7: “Inception: the network described at the beginning of Section 4.2, trained with the initial learning rate of 0.0015.”
- initial learning rate (BN-x5 training): 0.0075 _[verified]_
  > p. 7: “The initial learning rate was increased by a factor of 5, to 0.0075.”
- initial learning rate (BN-x30 training): 0.045 _[verified]_
  > p. 7: “BN-x30: Like BN-x5, but with the initial learning rate 0.045 (30 times that of Inception).”
- Dropout probability (ensemble training): 5% or 10% _[verified]_
  > p. 7: “using Dropout (with the Dropout probability of 5% or 10%, vs. 40% for the original Inception); and using non-convolutional”
- Dropout probability (original Inception): 40% _[verified]_
  > p. 7: “using Dropout (with the Dropout probability of 5% or 10%, vs. 40% for the original Inception); and using non-convolutional”

## Compute

- large-scale distributed architecture used for training _[verified]_
  > p. 6: “The training was performed using a large-scale, distributed architecture (similar to (Dean et al., 2012)).”

## Ablations

- Evaluating Inception modifications including higher learning rates, removing dropout, reducing L2 regularization, accelerating learning rate decay, removing Local Response Normalization, more thorough shuffling, and reducing photometric distortions _[partial]_
  > p. 6: “Simply adding Batch Normalization to a network does not take full advantage of our method. To do so, we further changed the network and its training parameters, as follows:”

## Claims

- Batch Normalization achieves the same accuracy with 14 times fewer training steps on an image classification model. _[verified]_
  > p. 1: “Applied to a state-of-the-art image classification model, Batch Normalization achieves the same accuracy with 14 times fewer training steps, and beats the original model by a significant margin.”
- An ensemble of batch-normalized networks reaches 4.9% top-5 validation error on ImageNet classification. _[verified]_
  > p. 1: “Using an ensemble of batchnormalized networks, we improve upon the best published result on ImageNet classification: reaching 4.9% top-5 validation error (and 4.8% test error), exceeding the accuracy of human raters.”

## Limitations

- The method increases parameter count and computational cost. _[verified]_
  > p. 10: “Also it increases the number of parameters by 25% and the computational cost is increased by about 30%.”

## Future work

- Apply the method to Recurrent Neural Networks. _[verified]_
  > p. 8: “Our future work includes applications of our method to Recurrent Neural Networks (Pascanu et al., 2013), where the internal covariate shift and the vanishing or exploding gradients may be especially severe, and which would allow us to more thoroughly test the hypothesis that normalization improves gradient propagation (Sec. 3.3).”
- Investigate if the normalization helps with domain adaptation. _[verified]_
  > p. 8: “We plan to investigate whether Batch Normalization can help with domain adaptation, in its traditional sense -i.e. whether the normalization performed by the network would allow it to more easily generalize to new data distributions, perhaps with just a recomputation of the population means and variances (Alg. 2).”
- Conduct further theoretical analysis of the algorithm for improvements and applications. _[verified]_
  > p. 8: “Finally, we believe that further theoretical analysis of the algorithm would allow still more improvements and applications.”


## 1711.05101

# DECOUPLED WEIGHT DECAY REGULARIZATION

Ilya Loshchilov, Frank Hutter
2019 · arXiv:1711.05101v3[cs.LG]

## Problem

- L2 regularization and weight decay are not equivalent for adaptive gradient algorithms like Adam, unlike in standard SGD. _[verified]_
  > p. 1: “While common implementations of these algorithms employ L 2 regularization (often calling it "weight decay" in what may be misleading due to the inequivalence we expose), we propose a simple modification to recover the original formulation of weight decay regularization by decoupling the weight decay from the optimization steps taken w.r.t. the loss function.”
- Adaptive gradient methods often generalize worse than SGD with momentum on various deep learning tasks. _[verified]_
  > p. 1: “Furthermore, Wilson et al. (2017) suggested that adaptive gradient methods do not generalize as well as SGD with momentum when tested on a diverse set of deep learning tasks, such as image classification, character-level language modeling and constituency parsing.”

## Task

- image classification _[verified]_
  > p. 1: “Our empirical evidence that our proposed modification (i) decouples the optimal choice of weight decay factor from the setting of the learning rate for both standard SGD and Adam and (ii) substantially improves Adam's generalization performance, allowing it to compete with SGD with momentum on image classification datasets (on which it was previously typically outperformed by the latter).”

## Contributions

- Proposing a modification to decouple weight decay from gradient-based updates in Adam to improve regularization. _[verified]_
  > p. 2: “The main contribution of this paper is to improve regularization in Adam by decoupling the weight decay from the gradient-based update.”

## Method

- Decouple the weight decay step from the gradient-based updates for SGD to form SGDW, allowing explicit separation of the weight decay rate and learning rate. _[partial]_
  > p. 2: “Looking first at the case of SGD, we propose to decay the weights simultaneously with the update of θ t based on gradient information in Line 9 of Algorithm 1.”
- Modify Adam to decouple weight decay and loss-based gradient updates, resulting in the AdamW optimization method. _[verified]_
  > p. 3: “We decouple weight decay and loss-based gradient updates in Adam as shown in line 12 of Algorithm 2; this gives rise to our variant of Adam with decoupled weight decay (AdamW).”
- Incorporate a schedule multiplier via a user-defined procedure to account for scheduling of both the learning rate and weight decay. _[verified]_
  > p. 2: “In order to account for a possible scheduling of both α and λ, we introduce a scaling factor η t delivered by a user-defined procedure SetScheduleM ultiplier(t).”

## Novelty

- Demonstrating that the equivalence between L2 regularization and weight decay does not hold for adaptive gradient methods. _[verified]_
  > p. 2: “However, as we will demonstrate later in this section, this equivalence does not hold for adaptive gradient methods.”

## Datasets

- CIFAR-10 _[partial]_
  > p. 5: “Our experimental setup follows that of Gastaldi (2017), who proposed, in addition to L 2 regularization, to apply the new Shake-Shake regularization to a 3-branch residual DNN that allowed to achieve new state-of-the-art results of 2.86% on the CIFAR-10 dataset (Krizhevsky, 2009).”
- ImageNet32x32 (1.2 million 32×32 pixels images) _[verified]_
  > p. 5: “We also perform experiments on the Im-ageNet32x32 dataset (Chrabaszcz et al., 2017), a downsampled version of the original ImageNet dataset with 1.2 million 32×32 pixels images.”
- WIDER FACE _[verified]_
  > p. 8: “For example, Wang et al. (2018) used AdamW to train a novel architecture for face detection on the standard WIDER FACE dataset (Yang et al., 2016), obtaining almost 10x faster predictions than the previous state of the art algorithms while achieving comparable performance.”

## Baselines

- Standard SGD with L2 regularization _[verified]_
  > p. 2: “For standard SGD, it is equivalent to standard L 2 regularization: Proposition 1 (Weight decay = L 2 reg for standard SGD).”
  > p. 5: “In our first experiment, we compare Adam with L 2 regularization to Adam with decoupled weight decay (AdamW), using three different learning rate schedules: a fixed learning rate, a drop-step schedule, and a cosine annealing schedule (Loshchilov & Hutter, 2016).”

## Metrics

- Test error _[verified]_
  > p. 8: “For the default learning rate of 0.001, AdamW achieved 15% relative improvement in test error compared to Adam both on CIFAR-10 (also see SuppFigure 5) and ImageNet32x32 (also see SuppFigure 6).”
- Test set accuracy _[verified]_
  > p. 8: “AdamW with the same hyperparameter setting as Adam yielded higher test set accuracy on Deep4Net (73.68% versus 71.37%) and statistically significantly higher test set accuracy on ResNet (72.04% versus 61.34%).”
- Cross-entropy training loss _[verified]_
  > p. 14: “The qualitative results are identical: weight decay leads to better training loss (crossentropy) than L 2 regularization, and to an even greater improvement of test error.”

## Hyperparameters

- batch size: 128 _[verified]_
  > p. 5: “We always used a batch size of 128 and applied the regular data augmentation procedure for the CI-FAR datasets.”
- initial learning rate: 0.001 _[verified]_
  > p. 7: “We fixed the initial learning rate to 0.001 which represents both the default learning rate for Adam and the one which showed reasonably good results in our experiments.”
- beta1: 0.9 _[verified]_
  > p. 3: “given α = 0.001, β1 = 0.9, β2 = 0.999, = 10 -8 , λ ∈ IR”
- beta2: 0.999 _[verified]_
  > p. 3: “given α = 0.001, β1 = 0.9, β2 = 0.999, = 10 -8 , λ ∈ IR”
- epsilon: 10 -8 _[verified]_
  > p. 3: “given α = 0.001, β1 = 0.9, β2 = 0.999, = 10 -8 , λ ∈ IR”

## Ablations

- Comparison of different learning rate schedules including fixed learning rate, drop-step schedule, and cosine annealing schedule. _[verified]_
  > p. 5: “In our first experiment, we compare Adam with L 2 regularization to Adam with decoupled weight decay (AdamW), using three different learning rate schedules: a fixed learning rate, a drop-step schedule, and a cosine annealing schedule (Loshchilov & Hutter, 2016).”

## Claims

- Adam with decoupled weight decay achieves a 15 percent relative improvement in test error. _[verified]_
  > p. 2: “In a comprehensive analysis, we show that Adam generalizes substantially better with decoupled weight decay than with L 2 regularization, achieving 15% relative improvement in test error (see Figures 2 and3); this holds true for various image recognition datasets (CIFAR-10 and ImageNet32x32), training budgets (ranging from 100 to 1800 epochs), and learning rate schedules (fixed, drop-step, and cosine annealing; see Figure 1).”

## Limitations

- Results need verification on a wider range of tasks, especially where regularization is important. _[verified]_
  > p. 9: “Our results obtained on image classification datasets must be verified on a wider range of tasks, especially ones where the use of regularization is expected to be important.”

## Future work

- Integrate findings on weight decay into other methods that attempt to improve Adam. _[verified]_
  > p. 9: “It would be interesting to integrate our findings on weight decay into other methods which attempt to improve Adam, e.g, normalized direction-preserving Adam (Zhang et al., 2017).”

## Code

- https://github.com/xgastaldi/shake-shake _[verified]_
  > p. 5: “https://github.com/xgastaldi/shake-shake”
- https://github.com/pytorch/pytorch/pull/4429 _[verified]_
  > p. 9: “Robin Schirrmeister, and Kashif Rasul for their implementations in PyTorch (see https://github.com/pytorch/pytorch/pull/4429)”
- https://github.com/sgugger/Adam-experiments _[verified]_
  > p. 9: “Robin Schirrmeister, and Kashif Rasul for their implementations in PyTorch (see https://github.com/pytorch/pytorch/pull/4429)”
- https://github.com/GLambard/AdamW_Keras _[verified]_
  > p. 9: “Robin Schirrmeister, and Kashif Rasul for their implementations in PyTorch (see https://github.com/pytorch/pytorch/pull/4429)”
- https://github.com/Yagami123/Caffe-AdamW-AdamWR _[verified]_
  > p. 9: “Robin Schirrmeister, and Kashif Rasul for their implementations in PyTorch (see https://github.com/pytorch/pytorch/pull/4429)”


## 1706.06083

# Towards Deep Learning Models Resistant to Adversarial Attacks

Aleksander M Ądry, Mit, Aleksandar Makelov, Ludwig Schmidt, Dimitris Tsipras, Adrian Vladu
2019 · arXiv:1706.06083v4[stat.ML]

## Problem

- Existing defense mechanisms lack a clear understanding of the guarantees they provide against adversarial attacks. _[verified]_
  > p. 2: “They, however, do not offer a good understanding of the guarantees they provide.”

## Task

- computer vision _[partial]_
  > p. 1: “Recent breakthroughs in computer vision [17,12] and natural language processing [7] are bringing trained classifiers into the center of security-critical systems.”

## Contributions

- An experimental study of the optimization landscape for the saddle point formulation showing that first-order methods can reliably solve it. _[partial]_
  > p. 2: “1. We conduct a careful experimental study of the optimization landscape corresponding to this saddle point formulation.”
- An exploration of how network architecture and model capacity impact adversarial robustness. _[verified]_
  > p. 2: “2. We explore the impact of network architecture on adversarial robustness and find that model capacity plays an important role here.”
- Training robust networks on MNIST and CIFAR10 against a wide range of adversarial attacks using projected gradient descent. _[partial]_
  > p. 2: “3. Building on the above insights, we train networks on MNIST [19] and CIFAR10 [16] that are robust to a wide range of adversarial attacks.”

## Method

- The proposed approach models adversarial robustness as a saddle point problem combining an inner maximization problem to find adversarial examples and an outer minimization problem to train robust parameters. _[partial]_
  > p. 3: “Instead of feeding samples from the distribution D directly into the loss L, we allow the adversary to perturb the input first.”
- The inner maximization problem is solved using projected gradient descent (PGD) as a universal first-order adversary to find adversarial examples within the allowed perturbation set. _[partial]_
  > p. 5: “The main tool in our experiments is projected gradient descent (PGD), since it is the standard method for large-scale constrained optimization.”
- The outer minimization problem is optimized using Stochastic Gradient Descent (SGD) based on gradients computed at the inner maximizers, drawing on Danskin's theorem. _[verified]_
  > p. 8: “By applying SGD using the gradient of the loss at adversarial examples we can consistently reduce the loss of the saddle point problem during training, as can be seen in Figure 5.”
- The approach utilizes architectures with substantially increased model capacity to handle the more complex decision boundaries required for robust classification. _[partial]_
  > p. 9: “At a high level, classifying examples in a robust way requires a stronger classifier, since the presence of adversarial examples changes the decision boundary of the problem to a more complicated one (see Figure 3 for an illustration).”

## Novelty

- The authors frame adversarial robustness through the lens of a saddle point optimization problem that unifies prior work by decomposing it into inner attack generation and outer robust training. _[partial]_
  > p. 4: “First, this formulation gives us a unifying perspective that encompasses much prior work on adversarial robustness.”
- The paper demonstrates that despite being non-concave, the inner maximization problem has a tractable structure of local maxima with well-concentrated loss values when explored with PGD. _[partial]_
  > p. 5: “One of our key contributions is demonstrating that, in practice, one can solve the saddle point problem after all.”

## Datasets

- MNIST _[verified]_
  > p. 10: “For both MNIST and CIFAR10, the adversary of choice will be projected gradient descent (PGD) starting from a random perturbation around the natural example.”
- CIFAR10 _[verified]_
  > p. 10: “For both MNIST and CIFAR10, the adversary of choice will be projected gradient descent (PGD) starting from a random perturbation around the natural example.”

## Metrics

- Accuracy _[verified]_
  > p. 11: “When trained with natural examples, this network reaches 99.2% accuracy on the evaluation set.”

## Hyperparameters

- step size: 0.01 _[verified]_
  > p. 11: “MNIST. We run 40 iterations of projected gradient descent as our adversary, with a step size of 0.01 (we choose to take gradient steps in the ∞ -norm, i.e. adding the sign of the gradient, since this makes the choice of the step size simpler).”
- epsilon: 0.3 _[verified]_
  > p. 11: “We train and evaluate against perturbations of size ε = 0.3.”
- fully connected layer size: 1024 _[verified]_
  > p. 11: “We use a network consisting of two convolutional layers with 32 and 64 filters respectively, each followed by 2 × 2 max-pooling, and a fully connected layer of size 1024.”
- step size: 2 _[verified]_
  > p. 12: “We trained the network against a PGD adversary with ∞ projected gradient descent again, this time using 7 steps of size 2, and a total ε = 8.”
- epsilon: 8 _[verified]_
  > p. 12: “We trained the network against a PGD adversary with ∞ projected gradient descent again, this time using 7 steps of size 2, and a total ε = 8.”
- steps (evaluation): 100 _[verified]_
  > p. 12: “For all PGD attacks, we use 100 steps and set the step size to be 2.5 • ε/100 to ensure that we can reach the boundary of the ε-ball from any starting point within it (and still allow for movement on the boundary).”

## Claims

- The best MNIST model achieves over 89% accuracy against the strongest adversaries in the test suite. _[verified]_
  > p. 2: “Our best MNIST model achieves an accuracy of more than 89% against the strongest adversaries in our test suite.”
- The CIFAR10 model achieves 46% accuracy against the same adversary. _[verified]_
  > p. 2: “Our CIFAR10 model achieves an accuracy of 46% against the same adversary.”
- Against weaker black box/transfer attacks, MNIST and CIFAR10 networks achieve accuracies of over 95% and 64% respectively. _[verified]_
  > p. 3: “Furthermore, in case of the weaker black box/transfer attacks, our MNIST and CIFAR10 networks achieve the accuracy of more than 95% and 64%, respectively.”

## Limitations

- Performance on CIFAR10 has not reached the same high level as MNIST yet. _[verified]_
  > p. 15: “Our experiments on CIFAR10 have not reached the same level of performance yet.”

## Future work

- Further explore the approach to build adversarially robust networks for the CIFAR10 dataset. _[verified]_
  > p. 15: “We believe that further exploring this direction will lead to adversarially robust networks for this dataset.”

## Code

- https://github.com/MadryLab/mnist_challenge _[verified]_
  > p. 3: “The complete code, along with the description of the challenge, is available at https://github.com/MadryLab/mnist_challenge”
- https://github.com/MadryLab/cifar10_challenge _[verified]_
  > p. 3: “The complete code, along with the description of the challenge, is available at https://github.com/MadryLab/mnist_challenge”


## 1803.03635

# THE LOTTERY TICKET HYPOTHESIS: FINDING SPARSE, TRAINABLE NEURAL NETWORKS

Jonathan Frankle, Michael Carbin
2019 · arXiv:1803.03635v5[cs.LG]

## Problem

- Sparse architectures produced by pruning are difficult to train from the start. _[verified]_
  > p. 1: “However, contemporary experience is that the sparse architectures produced by pruning are difficult to train from the start, which would similarly improve training performance.”

## Task

- Neural network pruning and training _[verified]_
  > p. 1: “We consistently find winning tickets that are less than 10-20% of the size of several fully-connected and convolutional feed-forward architectures for MNIST and CIFAR10.”

## Contributions

- Demonstrating that pruning uncovers trainable subnetworks matching original test accuracy and iterations. _[verified]_
  > p. 3: “• We demonstrate that pruning uncovers trainable subnetworks that reach test accuracy comparable to the original networks from which they derived in a comparable number of iterations.”
- Showing that pruning finds winning tickets that learn faster, reach higher test accuracy, and generalize better. _[verified]_
  > p. 3: “• We show that pruning finds winning tickets that learn faster than the original network while reaching higher test accuracy and generalizing better.”
- Proposing the lottery ticket hypothesis as a new perspective on neural network composition. _[verified]_
  > p. 3: “• We propose the lottery ticket hypothesis as a new perspective on the composition of neural networks to explain these findings.”

## Datasets

- MNIST _[verified]_
  > p. 3: “In this Section, we assess the lottery ticket hypothesis as applied to fully-connected networks trained on MNIST.”
- CIFAR10 _[verified]_
  > p. 5: “Here, we apply the lottery ticket hypothesis to convolutional networks on CIFAR10, increasing both the complexity of the learning problem and the size of the networks.”

## Metrics

- test accuracy _[verified]_
  > p. 4: “Figure 3 plots the average test accuracy when training winning tickets iteratively pruned to various extents.”
- validation loss _[verified]_
  > p. 4: “On the left is the iteration at which each network reaches minimum validation loss (i.e., when the early-stopping criterion would halt training) in relation to the percent of weights remaining after pruning; in the middle is test accuracy at that iteration.”
- training accuracy _[verified]_
  > p. 4: “At early stopping, training accuracy (Figure 4a, right) increases with pruning in a similar pattern to test accuracy, seemingly implying that winning tickets optimize more effectively but do not generalize better.”

## Hyperparameters

- dropout rate: 0.5 _[verified]_
  > p. 6: “Figure 6 shows the results of training Conv-2, Conv-4, and Conv-6 with a dropout rate of 0.5.”
- momentum: 0.9 _[verified]_
  > p. 8: “momentum (0.9) and decreasing the learning rate by a factor of 10 at 80 and 120 epochs.”
- learning rate: 0.1 _[verified]_
  > p. 8: “Figure 7 shows the results of iterative pruning and random reinitialization on VGG-19 at two initial learning rates: 0.1 (used in Liu et al. (2019)) and 0.01.”
- learning rate: 0.01 _[verified]_
  > p. 8: “Figure 7 shows the results of iterative pruning and random reinitialization on VGG-19 at two initial learning rates: 0.1 (used in Liu et al. (2019)) and 0.01.”
- warmup iterations: k = 10000 _[verified]_
  > p. 8: “Training VGG-19 with warmup (k = 10000, green line) at learning rate 0.1 improves the test accuracy of the unpruned network by about one percentage point.”
  > p. 40: “For the experiments in Section 4, we select k = 10000, as there is little benefit to larger values of k.”
- epochs/steps: 30,000 iterations _[verified]_
  > p. 8: “We train the network for 30,000 iterations with SGD with momentum (0.9), decreasing the learning rate by a factor of 10 at 20,000 and 25,000 iterations.”
- optimizer: SGD with momentum _[verified]_
  > p. 8: “We train the network for 30,000 iterations with SGD with momentum (0.9), decreasing the learning rate by a factor of 10 at 20,000 and 25,000 iterations.”
  > p. 40: “• We train using SGD with momentum (0.9).”
- warmup iterations: k = 20000 _[verified]_
  > p. 8: “Winning tickets trained with warmup close the accuracy gap with the unpruned network at the higher learning rate, reaching 90.5% test accuracy with learning rate 0.03 (warmup, k = 20000) at P m = 27.1%.”
- batch size: 128 _[verified]_
  > p. 40: “• We use a batch size of 128.”
- epochs/steps: 20,000, 5,000, and 5,000 iterations _[verified]_
  > p. 40: “Our stages last for 20,000, 5,000, and 5,000 iterations each, shorter than the 32,000, 16,000, and 16,000 used in He et al. (2016).”
- initialization: Gaussian Glorot _[verified]_
  > p. 40: “• We use Gaussian Glorot initialization.”

## Seeds and runs

- five runs with minimum and maximum error bars _[verified]_
  > p. 4: “Error bars are the minimum and maximum of five runs.”
- randomly reinitialize each winning ticket three times, making 15 total per point _[verified]_
  > p. 4: “We randomly reinitialize each winning ticket three times, making 15 total per point in Figure 4.”

## Ablations

- random reinitialization of winning tickets _[verified]_
  > p. 4: “To measure the importance of a winning ticket's initialization, we retain the structure of a winning ticket (i.e., the mask m) but randomly sample a new initialization θ 0 ∼ D θ .”
- one-shot pruning compared to iterative pruning _[verified]_
  > p. 5: “One-shot pruning makes it possible to identify winning tickets without this repeated training.”
- training networks with dropout _[verified]_
  > p. 6: “Figure 6 shows the results of training Conv-2, Conv-4, and Conv-6 with a dropout rate of 0.5.”
- exploring the effect of linear learning rate warmup over k iterations _[verified]_
  > p. 8: “To bridge the gap between the lottery ticket behavior of the lower learning rate and the accuracy advantage of the higher learning rate, we explore the effect of linear learning rate warmup from 0 to the initial learning rate over k iterations.”

## Claims

- Neural network pruning can reduce parameter counts by over 90% without compromising accuracy. _[verified]_
  > p. 1: “Neural network pruning techniques can reduce the parameter counts of trained networks by over 90%, decreasing storage requirements and improving computational performance of inference without compromising accuracy.”
- Winning tickets are less than 10-20% of the size of several architectures for MNIST and CIFAR10. _[verified]_
  > p. 1: “We consistently find winning tickets that are less than 10-20% of the size of several fully-connected and convolutional feed-forward architectures for MNIST and CIFAR10.”

## Limitations

- The study is limited to vision-centric classification tasks on smaller datasets like MNIST and CIFAR10. _[verified]_
  > p. 9: “We only consider vision-centric classification tasks on smaller datasets (MNIST, CIFAR10).”
- Larger datasets such as ImageNet were not investigated due to the high computational intensity of iterative pruning. _[verified]_
  > p. 9: “We do not investigate larger datasets (namely Imagenet (Russakovsky et al., 2015)): iterative pruning is computationally intensive, requiring training a network 15 or more times consecutively for multiple trials.”
- The sparse pruning method used does not result in architectures optimized for modern libraries or hardware. _[verified]_
  > p. 9: “Although we reduce parameter-counts, the resulting architectures are not optimized for modern libraries or hardware.”
- On deeper networks, iterative pruning fails to find winning tickets unless learning rate warmup is used. _[verified]_
  > p. 10: “On deeper networks , iterative pruning is unable to find winning tickets unless we train the networks with learning rate warmup.”

## Future work

- Explore more efficient methods for finding winning tickets to enable studies in more resource-intensive settings. _[verified]_
  > p. 9: “In future work, we intend to explore more efficient methods for finding winning tickets that will make it possible to study the lottery ticket hypothesis in more resource-intensive settings.”
- Study other pruning methods like structured pruning and non-magnitude pruning methods. _[verified]_
  > p. 9: “In future work, we intend to study other pruning methods from the extensive contemporary literature, such as structured pruning (which would produce networks optimized for contemporary hardware) and non-magnitude pruning methods (which could produce smaller winning tickets or find them earlier).”
- Study the properties of winning ticket initializations and their interactions with network architecture inductive biases. _[verified]_
  > p. 10: “In future work, we intend to study the properties of these initializations that, in concert with the inductive biases of the pruned network architectures, make these networks particularly adept at learning.”
- Explore why learning rate warmup is necessary for deeper networks and if other improvements can avoid hyperparameter modifications. _[verified]_
  > p. 10: “In future work, we plan to explore why warmup is necessary and whether other improvements to our scheme for identifying winning tickets could obviate the need for these hyperparameter modifications.”


## 2001.08361

# Scaling Laws for Neural Language Models

Jared Kaplan, Sam Mccandlish, Openai, Tom Henighan, Tom B Brown, Scott Gray, Alec Radford, Jeffrey Wu, Dario Amodei
2020 · arXiv:2001.08361v1[cs.LG]

## Task

- language modeling _[verified]_
  > p. 1: “We study empirical scaling laws for language model performance on the cross-entropy loss.”

## Contributions

- Providing basic theoretical motivation for Equation (1.5), an analysis of learning curve fits, and a breakdown of results per token. _[partial]_
  > p. 6: “We provide some basic theoretical motivation for Equation (1.5), an analysis of learning curve fits and their implications for training time, and a breakdown of our results per token.”
- Making brief comparisons to LSTMs and recurrent Transformers. _[verified]_
  > p. 6: “We also make some brief comparisons to LSTMs and recurrent Transformers [DGV + 18].”

## Method

- Language models are trained on WebText2 using byte-pair encoding with a vocabulary size of 50257. _[verified]_
  > p. 6: “We train language models on WebText2, an extended version of the WebText [RWC + 19] dataset, tokenized using byte-pair encoding [SHB15] with a vocabulary size n vocab = 50257.”
- The optimization objective is the autoregressive cross-entropy loss averaged over a 1024-token context. _[verified]_
  > p. 6: “We optimize the autoregressive log-likelihood (i.e. cross-entropy loss) averaged over a 1024-token context, which is also our principal performance metric.”
- The models are primarily decoder-only Transformers, alongside some LSTM models and Universal Transformers used for comparison. _[verified]_
  > p. 6: “We primarily train decoder-only [LSP + 18, RNSS18] Transformer [VSP + 17] models, though we also train LSTM models and Universal Transformers [DGV + 18] for comparison.”
- Training uses the Adam optimizer for 2.5 * 10^5 steps with a batch size of 512 sequences of 1024 tokens, while models exceeding 1B parameters use Adafactor due to memory constraints. _[partial]_
  > p. 7: “Unless otherwise noted, we train models with the Adam optimizer [KB14] for a fixed 2.5 × 10 5 steps with a batch size of 512 sequences of 1024 tokens.”

## Datasets

- WebText2 (23 billion tokens) _[verified]_
  > p. 9: “Although these models have been trained on the WebText2 dataset, their test loss on a variety of other datasets is also a power-law in N with nearly identical power, as shown in Figure 8.”

## Baselines

- LSTM models trained with the same dataset and context length _[partial]_
  > p. 9: “In Figure 7 we compare LSTM and Transformer performance as a function of non-embedding parameter count N .”
- Recurrent Transformers that re-use parameters _[verified]_
  > p. 9: “We also compare the performance of standard Transformers to recurrent Transformers [DGV + 18] in Figure 17 in the appendix.”

## Metrics

- Test loss _[unsupported]_
  > p. 7: “To characterize language model scaling we train a wide variety of models, varying a number of factors including:”

## Hyperparameters

- dropout: 10% _[verified]_
  > p. 11: “We regularize all our models with 10% dropout, and by tracking test loss and stopping once it is no longer decreasing.”
- context length: 1024 _[verified]_
  > p. 7: “• Context length (1024 for most runs, though we also experiment with shorter contexts)”
- batch size: 2 19 _[verified]_
  > p. 7: “• Batch size (2 19 for most runs, but we also vary it to measure the critical batch size) Figure 6 Left: When we include embedding parameters, performance appears to depend strongly on the number of layers in addition to the number of parameters.”
- model size: 768 to 1.5 billion _[verified]_
  > p. 7: “• Model size (ranging in size from 768 to 1.5 billion non-embedding parameters)”

## Seeds and runs

- Variation in loss with different random seeds estimated to be roughly 0.02 _[verified]_
  > p. 12: “We estimate that the variation in the loss with different random seeds is roughly 0.02, which means that to avoid overfitting when training to within that threshold of convergence we require”

## Ablations

- Varying model size N and dataset size D simultaneously _[verified]_
  > p. 10: “Here we will study the performance of a model of size N trained on a dataset with D tokens while varying N and D simultaneously.”
- Varying batch size to measure the critical batch size _[verified]_
  > p. 7: “• Batch size (2 19 for most runs, but we also vary it to measure the critical batch size) Figure 6 Left: When we include embedding parameters, performance appears to depend strongly on the number of layers in addition to the number of parameters.”
- Varying context length _[verified]_
  > p. 7: “• Context length (1024 for most runs, though we also experiment with shorter contexts)”

## Claims

- The loss scales as a power-law with model size, dataset size, and compute used for training across more than seven orders of magnitude. _[partial]_
  > p. 1: “The loss scales as a power-law with model size, dataset size, and the amount of compute used for training, with some trends spanning more than seven orders of magnitude.”
- The parameters for the learning curve fit are S_c approximately equal to 2.1 * 10^3 and alpha_S approximately equal to 0.76. _[verified]_
  > p. 5: “where S c ≈ 2.1 × 10 3 and α S ≈ 0.76, and S min (S) is the minimum possible number of optimization steps (parameter updates) estimated using Equation (5.4).”

## Limitations

- The formula for learning rate and parameter count breaks down for models larger than 10 billion parameters. _[verified]_
  > p. 26: “The formula also breaks down for N > 10 10 parameters.”

## Future work

- Test scaling relations on domains such as images, audio, video models, and random network distillation. _[verified]_
  > p. 19: “To this purpose, it will be interesting to test these relations on other domains, such as images, audio, and video models, and perhaps also for random network distillation.”
- Find a theoretical framework from which the scaling relations can be derived. _[verified]_
  > p. 19: “It would also be exciting to find a theoretical framework from which the scaling relations can be derived: a 'statistical mechanics' underlying the 'thermodynamics' we have observed.”
- Investigate whether continued loss improvement translates to relevant language task improvements. _[verified]_
  > p. 19: “In the domain of natural language, it will be important to investigate whether continued improvement on the loss translates into improvement on relevant language tasks.”
- Conduct further investigation into model parallelism. _[verified]_
  > p. 19: “In this context, further investigation into model parallelism is warranted.”


## 2203.15556

# Training Compute-Optimal Large Language Models

Jordan Hoffmann, Sebastian Borgeaud, Arthur Mensch, Elena Buchatskaya, Trevor Cai, Eliza Rutherford, Diego De, Las Casas, Lisa Anne Hendricks, Johannes Welbl, Aidan Clark, Tom Hennigan, Eric Noland, Katie Millican, George Van Den Driessche, Bogdan Damoc, Aurelia Guy, Simon Osindero, Karen Simonyan, Erich Elsen, Jack W Rae, Oriol Vinyals, Laurent Sifre
2022 · arXiv:2203.15556v1[cs.CL]

## Problem

- Current large language models are significantly undertrained because recent focus has been on scaling model size while keeping the amount of training data constant. _[verified]_
  > p. 1: “We find that current large language models are significantly undertrained, a consequence of the recent focus on scaling language models whilst keeping the amount of training data constant.”

## Task

- Training transformer language models under a given compute budget. _[verified]_
  > p. 1: “We investigate the optimal model size and number of tokens for training a transformer language model under a given compute budget.”

## Contributions

- Training over 400 language models to find that compute-optimal training requires scaling model size and training tokens equally. _[verified]_
  > p. 1: “By training over 400 language models ranging from 70 million to over 16 billion parameters on 5 to 500 billion tokens, we find that for compute-optimal training, the model size and the number of training tokens should be scaled equally: for every doubling of model size the number of training tokens should also be doubled.”
- Introducing Chinchilla, a compute-optimal model that outperforms existing large language models. _[verified]_
  > p. 1: “We test this hypothesis by training a predicted computeoptimal model, Chinchilla, that uses the same compute budget as Gopher but with 70B parameters and 4× more more data.”

## Method

- Varying training steps across a fixed family of models to extract minimum loss for given training FLOPs and fitting power laws. _[verified]_
  > p. 5: “In our first approach we vary the number of training steps for a fixed family of models (ranging from 70M to over 10B parameters), training each model for 4 different number of training sequences.”
- Varying model size for a fixed set of training FLOP counts and considering the final training loss to find the optimal parameter count per FLOP budget. _[verified]_
  > p. 5: “In our second approach we vary the model size for a fixed set of 9 different training FLOP counts (ranging from 6 × 10 18 to 3 × 10 21 FLOPs), and consider the final training loss for each point .”
- Minimizing the Huber loss using the L-BFGS algorithm on a parametric modeling of the loss to estimate optimal scaling. _[verified]_
  > p. 6: “To estimate ( , , , , ), we minimize the Huber loss (Huber, 1964) between the predicted and observed log loss using the L-BFGS algorithm (Nocedal, 1980)”

## Novelty

- The finding that parameter count and number of training tokens should be scaled equally with increased compute is in contrast to previous work. _[partial]_
  > p. 4: “This is in clear contrast to previous work on this topic and warrants further investigation.”

## Datasets

- MassiveText _[verified]_
  > p. 9: “• We train Chinchilla on MassiveText (the same dataset as Gopher) but use a slightly different subset distribution (shown in Table A1) to account for the increased number of training tokens.”
- The Pile _[verified]_
  > p. 10: “Chinchilla significantly outperforms Gopher on all evaluation subsets of The Pile (Gao et al., 2020), as shown in Figure 5.”
- Wikitext103 _[verified]_
  > p. 10: “On Wikitext103 (Merity et al., 2017), Chinchilla achieves a perplexity of 7.16 compared to 7.75 for Gopher.”
- Massive Multitask Language Understanding (MMLU) _[verified]_
  > p. 11: “The Massive Multitask Language Understanding (MMLU) benchmark (Hendrycks et al., 2020) consists of a range of exam-like questions on academic subjects.”
- LAMBADA _[verified]_
  > p. 11: “On the final word prediction dataset LAMBADA (Paperno et al., 2016), Chinchilla achieves 77.4% accuracy, compared to 74.5% accuracy from Gopher and 76.6% from MT-NLG 530B (see Table 7).”
- RACE-h and RACE-m _[verified]_
  > p. 11: “On RACE-h and RACE-m (Lai et al., 2017), Chinchilla greatly outperforms Gopher, improving accuracy by more than 10% in both cases-see Table 7.”
- BIG-bench _[verified]_
  > p. 11: “We analysed Chinchilla on the same set of BIG-bench tasks (BIG-bench collaboration, 2021) reported in Rae et al. (2021).”
- PIQA, SIQA, Winogrande, HellaSwag, and BoolQ _[verified]_
  > p. 12: “We evaluate Chinchilla on various common sense benchmarks: PIQA (Bisk et al., 2020), SIQA (Sap et al., 2019), Winogrande (Sakaguchi et al., 2020), HellaSwag (Zellers et al., 2019), and BoolQ (Clark et al., 2019).”
- TruthfulQA _[verified]_
  > p. 12: “On TruthfulQA (Lin et al., 2021), Chinchilla reaches 43.6%, 58.5%, and 66.7% accuracy with 0-shot, 5-shot, and 10-shot respectively.”
- Natural Questions (dev) _[verified]_
  > p. 13: “On the Natural Questions dataset (Kwiatkowski et al., 2019), Chinchilla achieves new closed-book SOTA accuracies: 31.5% 5-shot and 35.5% 64-shot, compared to 21% and 28% respectively, for Gopher.”
- TriviaQA (filtered and unfiltered) _[verified]_
  > p. 13: “On TriviaQA (Joshi et al., 2017) we show results for both the filtered (previously used in retrieval and open-book work) and unfiltered set (previously used in large language model evaluations).”
- C4 _[verified]_
  > p. 22: “We show scaling results from an IsoFLOP (Approach 2) analysis after training on two different datasets: C4 (Raffel et al., 2020b) and GitHub code (we show results with data from Rae et al. ( 2021)), results are shown in Table A2.”
- GitHub code _[verified]_
  > p. 22: “We show scaling results from an IsoFLOP (Approach 2) analysis after training on two different datasets: C4 (Raffel et al., 2020b) and GitHub code (we show results with data from Rae et al. ( 2021)), results are shown in Table A2.”

## Baselines

- Gopher model _[verified]_
  > p. 9: “In this section we compare this model, which we call Chinchilla, to Gopher and other LLMs.”
- Jurassic-1 (178B) _[verified]_
  > p. 10: “Compared to Jurassic-1 (178B) Lieber et al. (2021), Chinchilla is more performant on all but two subsets-dm_mathematics and ubuntu_irc-see Table A5 for a raw bits-per-byte comparison.”
- MT-NLG 530B _[verified]_
  > p. 11: “On the final word prediction dataset LAMBADA (Paperno et al., 2016), Chinchilla achieves 77.4% accuracy, compared to 74.5% accuracy from Gopher and 76.6% from MT-NLG 530B (see Table 7).”
- GPT-3 _[verified]_
  > p. 12: “We find that Chinchilla outperforms both Gopher and GPT-3 on all tasks and outperforms MT-NLG 530B on all but one task-see Table 8.”

## Metrics

- Language modelling loss _[verified]_
  > p. 9: “• We use AdamW (Loshchilov and Hutter, 2019) for Chinchilla rather than Adam (Kingma and Ba, 2014) as this improves the language modelling loss and the downstream task performance after finetuning.foot_7”
- Bits-per-byte _[verified]_
  > p. 10: “Compared to Jurassic-1 (178B) Lieber et al. (2021), Chinchilla is more performant on all but two subsets-dm_mathematics and ubuntu_irc-see Table A5 for a raw bits-per-byte comparison.”
- Perplexity _[verified]_
  > p. 10: “On Wikitext103 (Merity et al., 2017), Chinchilla achieves a perplexity of 7.16 compared to 7.75 for Gopher.”
- Accuracy _[verified]_
  > p. 11: “On this benchmark, Chinchilla significantly outperforms Gopher despite being much smaller, with an average accuracy of 67.6% (improving upon Gopher by 7.6%).”
- PerspectiveAPI toxicity score _[verified]_
  > p. 14: “We generate 25,000 unprompted samples from Chinchilla, and compare their PerspectiveAPI toxicity score distribution to that of Gopher-generated samples.”

## Hyperparameters

- optimizer: AdamW _[verified]_
  > p. 9: “• We use AdamW (Loshchilov and Hutter, 2019) for Chinchilla rather than Adam (Kingma and Ba, 2014) as this improves the language modelling loss and the downstream task performance after finetuning.foot_7”
- maximum learning rate: 4 × 10^−^5 _[partial]_
  > p. 9: “Gopher 280B | 80 | 128 | 128 | 16,384 | 4 × 10^−^5 | 3M → 6M”
- batch size: 3M → 6M _[partial]_
  > p. 9: “Gopher 280B | 80 | 128 | 128 | 16,384 | 4 × 10^−^5 | 3M → 6M”
- maximum learning rate: 1 × 10^−^4 _[partial]_
  > p. 9: “Chinchilla 70B | 80 | 64 | 128 | 8,192 | 1 × 10^−^4 | 1.5M → 3M”
- batch size: 1.5M → 3M _[partial]_
  > p. 9: “Chinchilla 70B | 80 | 64 | 128 | 8,192 | 1 × 10^−^4 | 1.5M → 3M”

## Compute

- Hardware used for training models _[verified]_
  > p. 9: “All models in this analysis have been trained on TPUv3/TPUv4 (Jouppi et al., 2017) with JAX (Bradbury et al., 2018) and Haiku (Hennigan et al., 2020).”

## Claims

- Chinchilla reaches a state-of-the-art average accuracy of 67.5% on the MMLU benchmark. _[verified]_
  > p. 1: “As a highlight, Chinchilla reaches a state-of-the-art average accuracy of 67.5% on the MMLU benchmark, greater than a 7% improvement over Gopher.”
- Chinchilla uniformly and significantly outperforms Gopher, GPT-3, Jurassic-1, and Megatron-Turing NLG. _[verified]_
  > p. 1: “Chinchilla uniformly and significantly outperforms Gopher (280B), GPT-3 (175B), Jurassic-1 (178B), and Megatron-Turing NLG (530B) on a large range of downstream evaluation tasks.”

## Limitations

- Only two large-scale training runs are available for comparison due to high costs. _[verified]_
  > p. 15: “Due to the cost of training large models, we only have two comparable training runs at large scale (Chinchilla and Gopher), and we do not have additional tests at intermediate scales.”
- The power-law assumption shows concavity at high compute budgets, risking overestimation of optimal model sizes. _[partial]_
  > p. 15: “Furthermore, we assume that the efficient computational frontier can be described by a power-law relationship between the compute budget, model size, and number of training tokens.”
- All training runs used less than a single epoch of data. _[verified]_
  > p. 15: “Finally, the training runs for our analysis have all been trained on less than an epoch of data; future work may consider the multiple epoch regime.”
- Chinchilla was only trained once because of the high costs of large language model training. _[verified]_
  > p. 32: “Due to the costs of training large language models, we did not train Chinchilla multiple times.”

## Future work

- Explore the multiple epoch regime in future training runs. _[verified]_
  > p. 15: “Finally, the training runs for our analysis have all been trained on less than an epoch of data; future work may consider the multiple epoch regime.”
- Better understand the interaction between large language model performance and toxicity. _[verified]_
  > p. 16: “Better understanding how performance of large language models and toxicity interact is an important future research question.”
- Account for curvature in the FLOP-minimal loss frontier for large FLOP budgets. _[partial]_
  > p. 27: “In this work, we do not take this in to account and we leave this as interesting future work as it suggests that even smaller models may be optimal for large FLOP budgets.”

## Ethics

- Training on trillions of tokens from web-scraped datasets introduces privacy, bias, and toxic language concerns. _[partial]_
  > p. 16: “Finally, training for trillions of tokens introduces many ethical and privacy concerns.”
- The model can output toxic language, emulate societal stereotypes, and reflect biased sentiment regarding race, religion, and country. _[partial]_
  > p. 33: “Our model is capable of outputting toxic language as measured by the PerspectiveAPI.”
- Internet-derived training data undoubtedly contains personal information, toxic content, and biases. _[partial]_
  > p. 34: “The data is collected from the internet, and thus undoubtedly there is toxic/biased content in our training dataset.”


## 2205.14135

# FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness

Tri Dao, Daniel Y Fu, Stefano Ermon, Atri Rudra, Christopher Ré
2022 · arXiv:2205.14135v2[cs.LG]

## Problem

- Transformers have quadratic time and memory complexity with respect to sequence length, making them slow and memory-hungry on long sequences. _[verified]_
  > p. 1: “Transformers are slow and memory-hungry on long sequences, since the time and memory complexity of self-attention are quadratic in sequence length.”
- Approximate attention methods fail to achieve wall-clock speedups because they overlook memory access overheads. _[verified]_
  > p. 1: “One main reason is that they focus on FLOP reduction (which may not correlate with wall-clock speed) and tend to ignore overheads from memory access (IO).”

## Task

- natural language processing _[verified]_
  > p. 1: “Transformer models [82] have emerged as the most widely used architecture in applications such as natural language processing and image classification.”
- image classification _[verified]_
  > p. 1: “Transformer models [82] have emerged as the most widely used architecture in applications such as natural language processing and image classification.”

## Contributions

- Proposing FlashAttention, an IO-aware exact attention algorithm using tiling to reduce memory reads and writes. _[verified]_
  > p. 1: “We propose FlashAttention, an IO-aware exact attention algorithm that uses tiling to reduce the number of memory reads/writes between GPU high bandwidth memory (HBM) and GPU on-chip SRAM.”
- Analyzing the IO complexity of FlashAttention and showing it requires fewer HBM accesses than standard attention. _[verified]_
  > p. 1: “We analyze the IO complexity of FlashAttention, showing that it requires fewer HBM accesses than standard attention, and is optimal for a range of SRAM sizes.”
- Extending FlashAttention to block-sparse attention to create a faster approximate attention method. _[verified]_
  > p. 1: “We also extend FlashAttention to block-sparse attention, yielding an approximate attention algorithm that is faster than any existing approximate attention method.”

## Method

- The proposed method computes exact attention using tiling and recomputation to reduce HBM memory accesses. _[verified]_
  > p. 4: “We apply two established techniques (tiling, recomputation) to overcome the technical challenge of computing exact attention in sub-quadratic HBM accesses.”
- Tiling is used to split inputs into blocks, compute softmax with scaling statistics across blocks, and combine the results. _[verified]_
  > p. 4: “The main idea is that we split the inputs Q, K, V into blocks, load them from slow HBM to fast SRAM, then compute the attention output with respect to those blocks.”
- The method recomputes attention matrices in the backward pass using saved outputs and softmax statistics instead of storing large intermediate matrices. _[verified]_
  > p. 5: “However, by storing the output O and the softmax normalization statistics (m, ℓ), we can recompute the attention matrix S and P easily in the backward pass from blocks of Q, K, V in SRAM.”
- The algorithm is implemented via kernel fusion in a single CUDA kernel to avoid repeatedly reading and writing inputs and outputs to HBM. _[verified]_
  > p. 5: “Tiling enables us to implement our algorithm in one CUDA kernel, loading input from HBM, performing all the computation steps (matrix multiply, softmax, optionally masking and dropout, matrix multiply), then write the result back to HBM (masking and dropout in Appendix B).”

## Novelty

- FlashAttention computes exact attention with fewer HBM reads and writes and without storing large intermediate matrices for the backward pass, yielding a memory-efficient and faster algorithm. _[verified]_
  > p. 4: “We show how to compute exact attention with fewer HBM reads/writes and without storing large intermediate matrices for the backward pass.”
- Unlike standard gradient checkpointing that trades speed for memory, FlashAttention's recomputation speeds up the backward pass by reducing HBM accesses despite using more FLOPs. _[verified]_
  > p. 5: “In contrast, even with more FLOPs, our recomputation speeds up the backward pass due to reduced HBM accesses (Fig. 2).”

## Datasets

- Wikipedia _[verified]_
  > p. 7: “We train a BERT-large [22] model with FlashAttention on Wikipedia.”
- OpenWebText (large) _[verified]_
  > p. 7: “GPT-2. FlashAttention yields faster training times for GPT-2 [67] on the large OpenWebText dataset [32] than the widely used HuggingFace [87] and Megatron-LM [77] implementations.”
- long-range arena (LRA) _[verified]_
  > p. 8: “FlashAttention) on the long-range arena (LRA [80]) benchmark.”
- MIMIC-III _[verified]_
  > p. 9: “Table 5 shows that sequence length 16K outperforms length 512 by 4.3 points on MIMIC, and that length 8K outperforms length 512 by 8.5 points on ECtHR.”
- ECtHR _[verified]_
  > p. 9: “Table 5 shows that sequence length 16K outperforms length 512 by 4.3 points on MIMIC, and that length 8K outperforms length 512 by 8.5 points on ECtHR.”
- Path-X and Path-256 _[verified]_
  > p. 9: “The Path-X and Path-256 benchmarks are challenging tasks from the long-range arena benchmark designed to test long context.”

## Baselines

- Nvidia implementation from MLPerf 1.1 _[verified]_
  > p. 7: “Table 1 compares our training time to the implementation from Nvidia that set the training speed record for MLPerf 1.1 [58].”
- HuggingFace and Megatron-LM implementations for GPT-2 _[verified]_
  > p. 7: “GPT-2. FlashAttention yields faster training times for GPT-2 [67] on the large OpenWebText dataset [32] than the widely used HuggingFace [87] and Megatron-LM [77] implementations.”
- Rabe and Staats _[verified]_
  > p. 22: “We describe here some similarities and differences between our FlashAttention algorithm and the algorithm of Rabe and Staats [66].”
- Apex FMHA _[verified]_
  > p. 27: “We compare our method/implementation with Apex FMHA (https://github.com/NVIDIA/apex/tree/ master/apex/contrib/csrc/fmha).”
- Reference implementations for exact attention from PyTorch/HuggingFace and Megatron, approximate attention, and sparse attention _[verified]_
  > p. 30: “We compare against reference implementations for exact attention from PyTorch/HuggingFace and Megatron, approximate attention, and sparse attention.”

## Metrics

- Target accuracy of 72.0% on masked language modeling _[verified]_
  > p. 7: “Table 1: Training time of BERT-large, starting from the same initialization provided by the MLPerf benchmark, to reach the target accuracy of 72.0% on masked language modeling.”
- Perplexity _[verified]_
  > p. 7: “FlashAttention trains GPT-2 with context length 4K faster than Megatron trains GPT-2 with context length 1K, while achieving 0.7 better perplexity.”
- Accuracy, throughput, and training time _[verified]_
  > p. 8: “We measure accuracy, throughput, and training time of all models.”
- Micro F1 score _[partial]_
  > p. 4: “Table 5: Long Document performance (micro 1 ) at different sequence lengths using FlashAttention.”

## Hyperparameters

- learning rate (BERT-large training): 3.75e-3 _[verified]_
  > p. 26: “In particular, we use the LAMB optimizer with learning rate 3.75e-3, with batch size 448, trained for at most 7100 steps.”
- batch size (BERT-large training): 448 _[verified]_
  > p. 26: “In particular, we use the LAMB optimizer with learning rate 3.75e-3, with batch size 448, trained for at most 7100 steps.”
- steps (BERT-large training): 7100 _[verified]_
  > p. 26: “In particular, we use the LAMB optimizer with learning rate 3.75e-3, with batch size 448, trained for at most 7100 steps.”
- optimizer (BERT-large training): LAMB _[verified]_
  > p. 26: “In particular, we use the LAMB optimizer with learning rate 3.75e-3, with batch size 448, trained for at most 7100 steps.”
- dropout (attention benchmarking): 0.1 _[verified]_
  > p. 30: “For dropout, we use dropout 0.1; for masking, we use a padding mask with uniformly-random mask lengths between the total sequence length and the total sequence length minus 20.”
- effective batch size (GPT-2 training): 512 _[verified]_
  > p. 26: “We use an effective batch size of 512, and use gradient accumulation to fit into available GPU memory.”
- learning rate (GPT-2 small training): 6e-4 _[verified]_
  > p. 26: “We use the AdamW optimizer, with learning rate 6e-4 for GPT-2 small and 1.5e-4 for GPT-2 medium, and weight decay of 0.1.”
- learning rate (GPT-2 medium training): 1.5e-4 _[verified]_
  > p. 26: “We use the AdamW optimizer, with learning rate 6e-4 for GPT-2 small and 1.5e-4 for GPT-2 medium, and weight decay of 0.1.”
- weight decay (GPT-2 training): 0.1 _[verified]_
  > p. 26: “We use the AdamW optimizer, with learning rate 6e-4 for GPT-2 small and 1.5e-4 for GPT-2 medium, and weight decay of 0.1.”
- optimizer (GPT-2 training): AdamW _[verified]_
  > p. 26: “We use the AdamW optimizer, with learning rate 6e-4 for GPT-2 small and 1.5e-4 for GPT-2 medium, and weight decay of 0.1.”
- steps (GPT-2 training): 400K _[verified]_
  > p. 26: “All models are trained with the same hyperparameters for 400K steps.”

## Compute

- 8x A100 GPUs for BERT-large _[verified]_
  > p. 7: “Averaged over 10 runs on 8×A100 GPUs.”
- One A100 GPU with 40 GB HBM for attention benchmarks _[verified]_
  > p. 9: “We vary sequence length and measure runtime and memory usage of FlashAttention and block-sparse FlashAttention against various attention baselines on one A100 GPU with 40 GB HBM, with dropout and a padding mask.”
- 8x A100-80GB GPUs for training _[verified]_
  > p. 26: “We train the model on 8×A100-80GB GPUs.”
- 8x A100-40GB GPUs for GPT-2 training _[verified]_
  > p. 26: “We train the model on 8×A100-40GB GPUs, and we measure the wall-clock training time.”

## Seeds and runs

- Averaged over 10 runs for BERT training _[verified]_
  > p. 7: “Averaged over 10 runs on 8×A100 GPUs.”
- Average of 100 measurements for attention runtime _[verified]_
  > p. 30: “To measure runtime, we take the average of 100 measurements of the attention call.”
- Averaged results of 10 runs for BERT training _[verified]_
  > p. 26: “Each training run takes between 16 and 19 minutes, and we average the results of 10 runs.”

## Claims

- FlashAttention achieves a 15% end-to-end wall-clock speedup on BERT-large, a 3x speedup on GPT-2, and a 2.4x speedup on long-range arena. _[verified]_
  > p. 1: “FlashAttention trains Transformers faster than existing baselines: 15% end-to-end wall-clock speedup on BERT-large (seq. length 512) compared to the MLPerf 1.1 training speed record, 3× speedup on GPT-2 (seq. length 1K), and 2.4× speedup on long-range arena (seq. length 1K-4K).”
- FlashAttention yields better perplexity on GPT-2 and higher scores on long-document classification. _[verified]_
  > p. 1: “FlashAttention and block-sparse FlashAttention enable longer context in Transformers, yielding higher quality models (0.7 better perplexity on GPT-2 and 6.4 points of lift on long-document classification) and entirely new capabilities: the first Transformers to achieve better-than-chance performance on the Path-X challenge (seq. length 16K, 61.4% accuracy) and Path-256 (seq. length 64K, 63.1% accuracy).”

## Limitations

- Writing IO-aware CUDA kernels requires significant engineering effort and a lower-level language than PyTorch. _[verified]_
  > p. 10: “This requires writing the attention algorithm in a considerably lower-level language than PyTorch, and requires significant engineering effort.”
- Current implementations may not be easily transferrable across different GPU architectures. _[verified]_
  > p. 10: “Implementations may also not be transferrable across GPU architectures.”

## Future work

- Prove parameterized complexity lower bounds in terms of block size as future work. _[verified]_
  > p. 6: “We leave proving parameterized complexity [27] lower bounds in terms of as exciting future work.”
- Develop methods to support writing attention algorithms in high-level languages like PyTorch and compiling to IO-aware CUDA implementations. _[verified]_
  > p. 10: “These limitations suggest the need for a method that supports writing attention algorithms in a high-level language (e.g., PyTorch), and compiling to IO-aware implementations in CUDA-similar to efforts such as Halide in image processing [70].”
- Inspire IO-aware implementations of additional deep learning modules beyond attention layers. _[verified]_
  > p. 10: “We hope our work inspires IO-aware implementations of additional modules.”
- Explore multi-GPU IO-aware methods that account for data transfer between GPUs. _[partial]_
  > p. 10: “We hope our work inspires future work in this direction.”

## Code

- https://github.com/NVIDIA/apex/tree/master/apex/contrib/csrc/fmha _[verified]_
  > p. 27: “We compare our method/implementation with Apex FMHA (https://github.com/NVIDIA/apex/tree/ master/apex/contrib/csrc/fmha).”
- https://github.com/HazyResearch/flash-attention _[verified]_
  > p. 3: “FlashAttention code is available at https://github.com/HazyResearch/flash-attention”


## 2312.00752

# Mamba: Linear-Time Sequence Modeling with Selective State Spaces

Albert Gu, Tri Dao
2024 · arXiv:2312.00752v2[cs.LG]

## Problem

- Transformers suffer from computational inefficiency on long sequences due to quadratic scaling with respect to the window length. _[unsupported]_
  > p. 1: “An enormous body of research has appeared on more efficient variants of attention to overcome these drawbacks (Tay, Dehghani, Bahri, et al. 2022), but often at the expense of the very properties that makes it effective.”
- Subquadratic-time architectures like SSMs have been less effective at modeling discrete, information-dense data such as text. _[verified]_
  > p. 2: “However, they have been less effective at modeling discrete and information-dense data such as text.”

## Task

- language modeling _[verified]_
  > p. 1: “On language modeling, our Mamba-3B model outperforms Transformers of the same size and matches Transformers twice its size, both in pretraining and downstream evaluation.”
- audio modeling _[verified]_
  > p. 2: “Mamba out-performs prior state-of-the-art models such as SaShiMi, Hyena, and Transformers on modeling audio waveforms and DNA sequences, both in pretraining quality and downstream metrics (e.g. reducing FID on a challenging speech generation dataset by more than half).”
- genomics modeling _[verified]_
  > p. 2: “Mamba out-performs prior state-of-the-art models such as SaShiMi, Hyena, and Transformers on modeling audio waveforms and DNA sequences, both in pretraining quality and downstream metrics (e.g. reducing FID on a challenging speech generation dataset by more than half).”

## Contributions

- Designing a simple selection mechanism by parameterizing SSM parameters based on the input. _[verified]_
  > p. 2: “Building on intuition based on important synthetic tasks such as selective copy and induction heads, we design a simple selection mechanism by parameterizing the SSM parameters based on the input.”
- Developing a hardware-aware recurrent algorithm using a scan that avoids materializing the expanded state. _[verified]_
  > p. 2: “We overcome this with a hardware-aware algorithm that computes the model recurrently with a scan instead of convolution, but does not materialize the expanded state in order to avoid IO access between different levels of the GPU memory hierarchy.”
- Introducing Mamba, a simplified homogeneous neural network architecture combining selective state spaces with Transformer MLP blocks. _[verified]_
  > p. 2: “We simplify prior deep sequence model architectures by combining the design of prior SSM architectures (Dao, Fu, Saab, et al. 2023) with the MLP block of Transformers into a single block, leading to a simple and homogenous architecture design (Mamba) incorporating selective state spaces.”

## Method

- The proposed Mamba architecture combines the H3 block and MLP block into a single homogeneous block, repeating it with normalization and residual connections. _[verified]_
  > p. 7: “We simplify this architecture by combining these two components into one, which is stacked homogenously (Figure 3).”
- A selection mechanism is introduced by making parameters such as B, C, and Delta functions of the input, turning the model into a time-varying SSM. _[verified]_
  > p. 5: “The main difference is simply making several parameters Δ, B, C functions of the input, along with the associated changes to tensor shapes throughout.”
- A hardware-aware algorithm is used to compute selective SSMs efficiently on GPUs by leveraging kernel fusion, parallel scan, and recomputation to avoid materializing the full expanded state. _[verified]_
  > p. 7: “We address this with three classical techniques: kernel fusion, parallel scan, and recomputation.”
- The model uses real values as the default for the state h, alongside initialization strategies derived from prior SSM and HIPPO theory. _[partial]_
  > p. 9: “We use real values as the default, which work well for all but one of our tasks; we hypothesize that the complex-real tradeoff is related to the continuous-discrete spectrum in data modalities, where complex numbers are helpful for continuous modalities (e.g. audio, video) but not discrete (e.g. text, DNA).”

## Novelty

- The authors introduce a selection mechanism to state space models, removing the linear time invariance (LTI) constraint to allow input-dependent dynamics. _[verified]_
  > p. 4: “However, a core insight of this work is that LTI models have fundamental limitations in modeling certain types of data, and our technical contributions involve removing the LTI constraint while overcoming the efficiency bottlenecks.”
- A novel hardware-aware algorithm avoids full state materialization through recomputation and kernel fusion, enabling efficient selective SSM computations. _[partial]_
  > p. 5: “We overcome this with a hardware-aware algorithm that exploits the memory hierarchy on modern hardware (Section 3.3).”

## Datasets

- Pile _[partial]_
  > p. 11: “We use the Pile dataset (L.”
- HG38 (training, 4.5 billion tokens) _[verified]_
  > p. 12: “For the dataset, we largely follow the setup of HyenaDNA (Nguyen, Poli, et al. 2023), which uses the HG38 dataset for pretraining consisting of a single human genome with about 4.5 billion tokens (DNA base pairs) in the training split.”
- YouTubeMix (4 hours) _[verified]_
  > p. 14: “We evaluate pretraining quality (autoregressive next-sample prediction) on YouTubeMix (DeepSound 2017), a standard piano music dataset used by prior work consisting of 4 hours of solo piano music, sampled at a rate of 16000 Hz.”

## Baselines

- Transformer architecture (GPT3 architecture) _[verified]_
  > p. 11: “For baselines, we compare against the standard Transformer architecture (GPT3 architecture), as well as the strongest Transformer recipe we know of (here referred to as Transformer++), based on the PaLM and LLaMa architectures (e.g. rotary embedding, SwiGLU MLP, RMSNorm instead of LayerNorm, no linear bias, and higher learning rates).”
- Transformer++ architecture _[verified]_
  > p. 11: “For baselines, we compare against the standard Transformer architecture (GPT3 architecture), as well as the strongest Transformer recipe we know of (here referred to as Transformer++), based on the PaLM and LLaMa architectures (e.g. rotary embedding, SwiGLU MLP, RMSNorm instead of LayerNorm, no linear bias, and higher learning rates).”
- Pythia open source models _[verified]_
  > p. 12: “We compare against the most well-known open source models at these sizes, most importantly Pythia (Biderman et”
- RWKV open source models _[verified]_
  > p. 12: “al. 2023) and RWKV (B.Peng et al. 2023) which were trained with the same tokenizer, dataset, and training length (300B tokens) as our models.(Note that Mamba and Pythia are trained with context length 2048, while RWKV was trained with context length 1024.)”
- HyenaDNA _[verified]_
  > p. 13: “Figure 5 (Left) shows that Mamba's pretraining perplexity improves smoothly with model size, and that Mamba scales better than both HyenaDNA and Transformer++.”
- SaShiMi architecture for audio waveform modeling _[verified]_
  > p. 14: “For the audio waveform modality, we compare primarily to the SaShiMi architecture and training protocols (Goel et al. 2022).”

## Metrics

- Perplexity _[verified]_
  > p. 11: “We evaluate the Mamba architecture on standard autoregressive language modeling against other architectures, on both pretraining metrics (perplexity) and zero-shot evaluations.”
- Zero-shot evaluation metrics including LAMBADA, HellaSwag, PIQA, Arc-E, Arc-C, and WinoGrande accuracy and perplexity _[partial]_
  > p. 12: “Table 3: (Zero-shot Evaluations.)Best results for each size in bold.We compare against open source LMs with various tokenizers, trained for up to 300B tokens.Pile refers to the validation split, comparing only against models trained on the same dataset and tokenizer (GPT-NeoX-20B).For each model size, Mamba is best-in-class on every single evaluation result, and generally matches baselines at twice the model size.”
- Bits per byte (BPB) _[verified]_
  > p. 14: “The main metric is bits per byte (BPB), which is a constant factor log(2) of the standard negative log-likelihood (NLL) loss for pretraining other modalities.”
- Negative log-likelihood (NLL) _[verified]_
  > p. 14: “The main metric is bits per byte (BPB), which is a constant factor log(2) of the standard negative log-likelihood (NLL) loss for pretraining other modalities.”
- Fréchet Inception Distance (FID) _[verified]_
  > p. 15: “Model | Params | NLL ↓ | FID ↓ | IS ↑ | mIS ↑ | AM ↓”
- Inception Score (IS) _[verified]_
  > p. 15: “Model | Params | NLL ↓ | FID ↓ | IS ↑ | mIS ↑ | AM ↓”
- Mean Inception Score (mIS) _[verified]_
  > p. 15: “Model | Params | NLL ↓ | FID ↓ | IS ↑ | mIS ↑ | AM ↓”
- AM _[verified]_
  > p. 15: “Model | Params | NLL ↓ | FID ↓ | IS ↑ | mIS ↑ | AM ↓”

## Hyperparameters

- learning rate: {1 -3, 2 -3, 4 -3, 8 -3} _[verified]_
  > p. 33: “For each model (Transformer++, HyenaDNA, Mamba), we swept the learning rate across {1 -3, 2 -3, 4 -3, 8 -3}.”
- learning rate: 2e-3 _[verified]_
  > p. 33: “The optimal Transformer and HyenaDNA learning rates were 2e-3 across all sizes.”
- learning rate: 8e-3 _[verified]_
  > p. 33: “The optimal Mamba learning rate was 8e-3; note that Mamba performed better than baselines with matched learning rates (2e-3), but was more stable and improved even more at higher learning rates.”
- batch size (pretraining): 1024 _[verified]_
  > p. 13: “We fix a global batch size of 1024, for a total of 2 20 ≈ 1 tokens per batch.”
- batch size (training step): 2 24 _[verified]_
  > p. 33: “We use a total batch size of 2 24 ≈ 16 tokens per training step, for every sequence length (e.g. at length 2 20 there are 16 segments per batch and at length 2 10 there are 16384 segments per batch).”
- learning rate (DNA pretraining): 0.008 _[verified]_
  > p. 33: “The learning rate used was 0.008 for Mamba and 0.001 for HyenaDNA; we initially attempted to use the same learning rate of 0.002 from the previous section for HyenaDNA, but found that it was unstable at the longest context length.”
- learning rate (DNA pretraining): 0.001 _[verified]_
  > p. 33: “The learning rate used was 0.008 for Mamba and 0.001 for HyenaDNA; we initially attempted to use the same learning rate of 0.002 from the previous section for HyenaDNA, but found that it was unstable at the longest context length.”
- batch size (classification task): 64 _[verified]_
  > p. 33: “Each gradient step uses batch size 64, which are all independently randomly drawn by uniformly picking a species, uniformly picking a chromosome, and then uniformly picking a contiguous segment of DNA.”
- learning rate (fine-tuning): 4e -5 _[verified]_
  > p. 33: “The learning rate for all Hyena models is 4e -5, while the learning rate for all Mamba models is 1e -4.”
- learning rate (fine-tuning): 1e -4 _[verified]_
  > p. 33: “The learning rate for all Hyena models is 4e -5, while the learning rate for all Mamba models is 1e -4.”

## Compute

- Machine with 8 GPUs _[verified]_
  > p. 33: “This is a large batch size relative to the model size by usual LM standards, but note that a batch size of 2 23 is the minimum possible on a machine with 8 GPUs and sequence length of 2 2 0, and that HyenaDNA used much larger batches of 2 28 .”

## Ablations

- Ablation of model architecture and inner SSM layer comparing non-selective and selective SSMs _[verified]_
  > p. 15: “Table 6 investigates the effects of the architecture (block) and its inner SSM layer (Figure 3).”
- Ablation of selective SSM layer considering different combinations of selective parameters _[partial]_
  > p. 16: “Table 7 ablates the selective SSM layer by considering different combinations of selective Δ, , and parameters (Algorithm 2), showing that Δ is the most important parameter due to its connection to RNN gating (Theorem 1).”
- Ablation of different initializations of the SSM _[verified]_
  > p. 16: “Table 8 considers different initializations of the SSM, which have been shown to make a large difference in some data modalities and settings (Gu, Goel, and Ré 2022; Gu, Gupta, et al. 2022).”
- Ablation varying the dimension of Δ and B, C projections _[partial]_
  > p. 16: “Table 9 and Table 10 consider varying the dimension of the Δ and (, ) projections respectively.”
- Ablation on interleaving the Mamba block with other blocks such as MLP and MHA _[verified]_
  > p. 30: “Mamba Architecture: Interleaving Blocks. We test the effect of different architectural blocks combined with the Mamba block.”

## Claims

- Mamba achieves 5x higher inference throughput than Transformers. _[verified]_
  > p. 1: “Mamba enjoys fast inference (5× higher throughput than Transformers) and linear scaling in sequence length, and its performance improves on real data up to million-length sequences.”
- Mamba-3B matches the quality of Transformers twice its size on language modeling. _[verified]_
  > p. 1: “On language modeling, our Mamba-3B model outperforms Transformers of the same size and matches Transformers twice its size, both in pretraining and downstream evaluation.”
- The hardware-aware algorithm is up to 3x faster on A100 GPUs compared to previous methods. _[verified]_
  > p. 2: “The resulting implementation is faster than previous methods both in theory (scaling linearly in sequence length, compared to pseudo-linear for all convolution-based SSMs) and on modern hardware (up to 3× faster on A100 GPUs).”
- Mamba reduces FID on a challenging speech generation dataset by more than half. _[verified]_
  > p. 2: “Mamba out-performs prior state-of-the-art models such as SaShiMi, Hyena, and Transformers on modeling audio waveforms and DNA sequences, both in pretraining quality and downstream metrics (e.g. reducing FID on a challenging speech generation dataset by more than half).”
- Mamba-3B scores 4 points higher on average on common sense reasoning compared to Pythia-3B and exceeds Pythia-7B. _[verified]_
  > p. 2: “Our Mamba language model has 5× generation throughput compared to Transformers of similar size, and Mamba-3B's quality matches that of Transformers twice its size (e.g. 4 points higher avg. on common sense reasoning compared to Pythia-3B and even exceeding Pythia-7B).”

## Future work

- Apply selective SSMs generically to meta-RL settings _[verified]_
  > p. 25: “It would be interesting to apply selective SSMs generically to this setting and probe if the model has learned to automatically reset its state on episode boundaries.”

## Code

- https://github.com/state-spaces/mamba _[verified]_
  > p. 2: “Model code and pre-trained checkpoints are open-sourced at https://github.com/state-spaces/mamba.”


## 2404.19756

# KAN: Kolmogorov-Arnold Networks

Ziming Liu, Yixuan Wang, Sachin Vaidya, Fabian Ruehle, James Halverson, Marin Soljačić, Thomas Y Hou, Max Tegmark
2025 · arXiv:2404.19756v5[cs.LG]

## Problem

- Today's deep learning models rely heavily on MLPs. _[verified]_
  > p. 1: “In summary, KANs are promising alternatives for MLPs, opening opportunities for further improving today's deep learning models which rely heavily on MLPs.”

## Task

- Small-scale AI and Science tasks including function fitting. _[verified]_
  > p. 1: “We show that this seemingly simple change makes KANs outperform MLPs in terms of accuracy and interpretability, on small-scale AI + Science tasks.”

## Contributions

- Proposing Kolmogorov-Arnold Networks (KANs) as alternatives to MLPs with learnable activation functions on edges. _[verified]_
  > p. 1: “Inspired by the Kolmogorov-Arnold representation theorem, we propose Kolmogorov-Arnold Networks (KANs) as promising alternatives to Multi-Layer Perceptrons (MLPs).”

## Method

- Designing Kolmogorov-Arnold Networks (KANs) which replace fixed linear weights and node activation functions with learnable univariate activation functions parametrized as B-splines placed on the network edges. _[verified]_
  > p. 4: “This inspires us to design a neural network which explicitly parametrizes Eq. (2.1).”
- Defining KAN layers and stacking multiple layers to build deeper and wider KAN architectures capable of processing multivariate functions. _[verified]_
  > p. 5: “It turns out that a KAN layer with n in -dimensional inputs and n out -dimensional outputs can be defined as a matrix of 1D functions”
- Training KANs using backpropagation with specific implementation techniques including residual activation functions (combining a basis function with a spline function), custom initialization scales, and on-the-fly updates of spline grids. _[verified]_
  > p. 6: “Notice that all the operations are differentiable, so we can train KANs with back propagation.”
- Employing a grid extension technique to transition a trained KAN from coarse to finer spline grids via least squares fitting, improving accuracy without retraining from scratch. _[verified]_
  > p. 9: “By contrast, for KANs, one can first train a KAN with fewer parameters and then extend it to a KAN with more parameters by simply making its spline grids finer, without the need to retraining the larger model from scratch.”
- Applying sparsity regularization via L1 norm and entropy of activation functions, followed by network pruning and symbolic fitting interfaces to yield interpretable models. _[verified]_
  > p. 11: “To make KANs maximally interpretable, we propose a few simplification techniques in Section 2.5.1, and an example of how users can interact with KANs to make them more interpretable in Section 2.5.2.”

## Novelty

- Introducing Kolmogorov-Arnold networks (KANs) that place activation functions on the edges instead of nodes, contrasting with traditional MLPs which separate linear transformations and nonlinearities. _[verified]_
  > p. 6: “It is clear that MLPs treat linear transformations and nonlinearities separately as W and σ, while KANs treat them all together in Φ.”
- Utilizing both external degrees of freedom (network connectivity for compositional structures) and internal degrees of freedom (grid points inside activation functions for univariate functions). _[verified]_
  > p. 11: “A new concept that KANs highlights is a distinction between external versus internal degrees of freedom (parameters).”
- Achieving better neural scaling laws and avoiding the curse of dimensionality by leveraging compositional structures and smooth Kolmogorov-Arnold representations. _[verified]_
  > p. 10: “In addition, KANs still have much better scaling laws than MLPs, for data fitting (Figure 3.1) and PDE solving (Figure 3.3).”

## Datasets

- Special functions (15 functions) _[verified]_
  > p. 15: “We collect 15 special functions common in math and physics, summarized in Table 1.”
- Feynman_no_units _[verified]_
  > p. 16: “For our purpose, we are interested in problems in the Feynman_no_units dataset that have at least 2 variables, since univariate problems are trivial for KANs (they simplify to 1D splines).”
- Knot dataset _[partial]_
  > p. 23: “To investigate (1), we treat 17 knot invariants as inputs and signature as outputs.”

## Baselines

- MLPs with different depths and widths _[verified]_
  > p. 14: “We train MLPs with different depths and widths as baselines.”
- MLPs with fixed width 5 or 100 and depths swept in {2, 3, 4, 5, 6} _[verified]_
  > p. 15: “We choose MLPs with fixed width 5 or 100 and depths swept in {2, 3, 4, 5, 6}.”
- Deepmind's 4-layer width-300 MLP for signature classification _[verified]_
  > p. 23: “while Deepmind's 4-layer width-300 MLP achieves 78% test accuracy”

## Metrics

- Test RMSE loss _[verified]_
  > p. 14: “In Section 2.3, our theory suggested that test RMSE loss ℓ scales as ℓ ∝ N -4 with model parameters N .”
- RMSE _[verified]_
  > p. 15: “For each dataset and each model family (KANs or MLPs), we plot the Pareto frontier 5 , in the (number of parameters, RMSE) plane, shown in Figure 3”
- Error in the L2 norm and energy (H1) norm _[verified]_
  > p. 18: “We measure both the error in the L 2 norm and energy (H 1 ) norm and see that KAN achieves a much better scaling law with a smaller error, using smaller networks and fewer parameters; see Figure 3.3.”
- MSE _[verified]_
  > p. 18: “A 2-Layer width-10 KAN is 100 times more accurate than a 4-Layer width-100 MLP (10 -7 vs 10 -5 MSE) and 100 times more parameter efficient (10 2 vs 10 4 parameters).”
- Cross-entropy loss _[verified]_
  > p. 14: “Similar to the setup in [45], signatures (which are even numbers) are encoded as one-hot vectors and networks are trained with cross-entropy loss.”
- Test accuracy _[verified]_
  > p. 23: “We find that an extremely small [17,1,14] KAN is able to achieve 81.6% test accuracy (while Deepmind's 4-layer width-300 MLP achieves 78% test accuracy).”

## Hyperparameters

- grid points: {3, 5, 10, 20, 50, 100, 200, 500, 1000} _[verified]_
  > p. 14: “We train these KANs by increasing grid points every 200 steps, in total covering G = {3, 5, 10, 20, 50, 100, 200, 500, 1000}.”
- training steps: 1800 _[verified]_
  > p. 14: “Both MLPs and KANs are trained with LBFGS for 1800 steps in total.”
- optimizer: LBFGS _[verified]_
  > p. 14: “Both MLPs and KANs are trained with LBFGS for 1800 steps in total.”
- sparsification lambda: 10 -2 or 10 -3 _[verified]_
  > p. 15: “We use the sparsification (λ = 10 -2 or 10 -3 ) and pruning technique in Section 2.5.1 to obtain a smaller KAN pruned from a fixed-shape KAN.”
- interior points ni: 10000 _[verified]_
  > p. 18: “We compare the KAN architecture with that of MLPs using the same hyperparameters n i = 10000, n b = 800, and α = 0.01.”
- boundary points nb: 800 _[verified]_
  > p. 18: “We compare the KAN architecture with that of MLPs using the same hyperparameters n i = 10000, n b = 800, and α = 0.01.”
- alpha: 0.01 _[verified]_
  > p. 18: “We compare the KAN architecture with that of MLPs using the same hyperparameters n i = 10000, n b = 800, and α = 0.01.”

## Seeds and runs

- 3 random seeds for each hyperparameter combination _[verified]_
  > p. 15: “For each hyperparameter combination, we run 3 random seeds.”

## Ablations

- Ablation study on signature dependence showing µr contributes more to accuracy than µi _[verified]_
  > p. 23: “(a) ablation studies. We show that µ r contributes more to accuracy than µ i (see Figure 4.3): for example, µ r alone can achieve 65.0% accuracy, while µ i alone can only achieve 43.8% accuracy.”

## Claims

- Smaller KANs can achieve comparable or better accuracy than larger MLPs in function fitting tasks. _[verified]_
  > p. 1: “For accuracy, smaller KANs can achieve comparable or better accuracy than larger MLPs in function fitting tasks.”
- KANs possess faster neural scaling laws than MLPs. _[verified]_
  > p. 1: “Theoretically and empirically, KANs possess faster neural scaling laws than MLPs.”

## Limitations

- Our mathematical understanding of KANs is still very limited. _[verified]_
  > p. 32: “Although we have presented preliminary mathematical analysis of KANs (Theorem 2.1), our mathematical understanding of them is still very limited.”
- KANs currently suffer from slow training speeds. _[verified]_
  > p. 33: “Currently, the biggest bottleneck of KANs lies in its slow training.”

## Future work

- Apply KANs to solve Navier-Stokes equations, density functional theory, or other regression and PDE tasks. _[verified]_
  > p. 32: “We would like to apply KANs to solve Navier-Stokes equations, density functional theory, or any other tasks that can be formulated as regression or PDE solving.”
- Integrate KANs into current architectures such as transformers to propose kansformers. _[verified]_
  > p. 32: “We would also like to apply KANs to machinelearning-related tasks, which would require integrating KANs into current architectures, e.g., transformers -one may propose "kansformers" which replace MLPs by KANs in transformers.”

## Code

- https://github.com/KindXiaoming/pykan _[verified]_
  > p. 3: “Codes are available at https://github.com/KindXiaoming/pykan”


## 1609.02907

# SEMI-SUPERVISED CLASSIFICATION WITH GRAPH CONVOLUTIONAL NETWORKS

Thomas N Kipf, Max Welling
2017 · arXiv:1609.02907v4[cs.LG]

## Problem

- Graph edges do not necessarily encode node similarity and may contain additional information, which can restrict modeling capacity when using explicit graph-based regularization. _[verified]_
  > p. 1: “This assumption, however, might restrict modeling capacity, as graph edges need not necessarily encode node similarity, but could contain additional information.”

## Task

- Semi-supervised learning on graph-structured data and node classification. _[verified]_
  > p. 1: “We consider the problem of classifying nodes (such as documents) in a graph (such as a citation network), where labels are only available for a small subset of nodes.”

## Contributions

- Introduction of a simple and well-behaved layer-wise propagation rule for neural networks operating directly on graphs, motivated by a first-order approximation of spectral graph convolutions. _[verified]_
  > p. 1: “Firstly, we introduce a simple and well-behaved layer-wise propagation rule for neural network models which operate directly on graphs and show how it can be motivated from a first-order approximation of spectral graph convolutions (Hammond et al., 2011).”
- Demonstration that graph-based neural network models can be utilized for fast and scalable semi-supervised classification of nodes in a graph. _[verified]_
  > p. 1: “Secondly, we demonstrate how this form of a graph-based neural network model can be used for fast and scalable semi-supervised classification of nodes in a graph.”

## Method

- The proposed approach uses a multi-layer Graph Convolutional Network with a specific layer-wise propagation rule involving normalized adjacency matrices and trainable weight matrices. _[verified]_
  > p. 2: “We consider a multi-layer Graph Convolutional Network (GCN) with the following layer-wise propagation rule: l) .”
- The model uses a linear formulation of graph convolutions by limiting the layer-wise convolution operation to K = 1 and applying a renormalization trick to avoid numerical instabilities. _[partial]_
  > p. 3: “To alleviate this problem, we introduce the following renormalization trick:”

## Datasets

- Citeseer (3,327 nodes) _[verified]_
  > p. 5: “In the citation network datasets-Citeseer, Cora and Pubmed(Sen et al., 2008)-nodes are documents and edges are citation links.”
- Cora (2,708 nodes) _[verified]_
  > p. 5: “In the citation network datasets-Citeseer, Cora and Pubmed(Sen et al., 2008)-nodes are documents and edges are citation links.”
- Pubmed (19,717 nodes) _[verified]_
  > p. 5: “In the citation network datasets-Citeseer, Cora and Pubmed(Sen et al., 2008)-nodes are documents and edges are citation links.”
- NELL (65,755 nodes) _[verified]_
  > p. 5: “NELL(Carlson et al., 2010;Yang et al., 2016) is a bipartite graph dataset extracted from a knowledge graph with 55,864 relation nodes and 9,891 entity nodes.”
- Random graphs _[verified]_
  > p. 6: “We simulate random graph datasets of various sizes for experiments where we measure training time per epoch.”

## Baselines

- Label propagation _[verified]_
  > p. 6: “We compare against the same baseline methods as in Yang et al. (2016), i.e. label propagation (LP) (Zhu et al., 2003), semi-supervised embedding (SemiEmb) (Weston et al., 2012), manifold regularization (ManiReg) (Belkin et al., 2006) and skip-gram based graph embeddings (DeepWalk) (Perozzi et al., 2014).”
- Semi-supervised embedding _[verified]_
  > p. 6: “We compare against the same baseline methods as in Yang et al. (2016), i.e. label propagation (LP) (Zhu et al., 2003), semi-supervised embedding (SemiEmb) (Weston et al., 2012), manifold regularization (ManiReg) (Belkin et al., 2006) and skip-gram based graph embeddings (DeepWalk) (Perozzi et al., 2014).”
- Manifold regularization _[verified]_
  > p. 6: “We compare against the same baseline methods as in Yang et al. (2016), i.e. label propagation (LP) (Zhu et al., 2003), semi-supervised embedding (SemiEmb) (Weston et al., 2012), manifold regularization (ManiReg) (Belkin et al., 2006) and skip-gram based graph embeddings (DeepWalk) (Perozzi et al., 2014).”
- DeepWalk _[verified]_
  > p. 6: “We compare against the same baseline methods as in Yang et al. (2016), i.e. label propagation (LP) (Zhu et al., 2003), semi-supervised embedding (SemiEmb) (Weston et al., 2012), manifold regularization (ManiReg) (Belkin et al., 2006) and skip-gram based graph embeddings (DeepWalk) (Perozzi et al., 2014).”
- Iterative classification algorithm _[verified]_
  > p. 6: “We further compare against the iterative classification algorithm (ICA) proposed in Lu & Getoor (2003) in conjunction with two logistic regression classifiers, one for local node features alone and one for relational classification using local features and an aggregation operator as described in Sen et al. (2008).”
- Planetoid _[verified]_
  > p. 6: “Lastly, we compare against Planetoid (Yang et al., 2016), where we always choose their bestperforming model variant (transductive vs. inductive) as a baseline.”

## Metrics

- Classification accuracy in percent _[verified]_
  > p. 7: “Reported numbers denote classification accuracy in percent.”

## Hyperparameters

- dropout rate: 0.5 _[verified]_
  > p. 7: “We used the following sets of hyperparameters for Citeseer, Cora and Pubmed: 0.5 (dropout rate), 5 • 10 -4 (L2 regularization) and 16 (number of hidden units); and for NELL: 0.1 (dropout rate), 1 • 10 -5 (L2 regularization) and 64 (number of hidden units).”
- L2 regularization: 5 • 10 -4 _[verified]_
  > p. 7: “We used the following sets of hyperparameters for Citeseer, Cora and Pubmed: 0.5 (dropout rate), 5 • 10 -4 (L2 regularization) and 16 (number of hidden units); and for NELL: 0.1 (dropout rate), 1 • 10 -5 (L2 regularization) and 64 (number of hidden units).”
- number of hidden units: 16 _[verified]_
  > p. 7: “We used the following sets of hyperparameters for Citeseer, Cora and Pubmed: 0.5 (dropout rate), 5 • 10 -4 (L2 regularization) and 16 (number of hidden units); and for NELL: 0.1 (dropout rate), 1 • 10 -5 (L2 regularization) and 64 (number of hidden units).”
- dropout rate: 0.1 _[verified]_
  > p. 7: “We used the following sets of hyperparameters for Citeseer, Cora and Pubmed: 0.5 (dropout rate), 5 • 10 -4 (L2 regularization) and 16 (number of hidden units); and for NELL: 0.1 (dropout rate), 1 • 10 -5 (L2 regularization) and 64 (number of hidden units).”
- L2 regularization: 1 • 10 -5 _[verified]_
  > p. 7: “We used the following sets of hyperparameters for Citeseer, Cora and Pubmed: 0.5 (dropout rate), 5 • 10 -4 (L2 regularization) and 16 (number of hidden units); and for NELL: 0.1 (dropout rate), 1 • 10 -5 (L2 regularization) and 64 (number of hidden units).”
- number of hidden units: 64 _[verified]_
  > p. 7: “We used the following sets of hyperparameters for Citeseer, Cora and Pubmed: 0.5 (dropout rate), 5 • 10 -4 (L2 regularization) and 16 (number of hidden units); and for NELL: 0.1 (dropout rate), 1 • 10 -5 (L2 regularization) and 64 (number of hidden units).”
- epochs: 200 _[verified]_
  > p. 6: “We train all models for a maximum of 200 epochs (training iterations) using Adam (Kingma & Ba, 2015) with a learning rate of 0.01 and early stopping with a window size of 10, i.e. we stop training if the validation loss does not decrease for 10 consecutive epochs.”
- optimizer: Adam _[verified]_
  > p. 6: “We train all models for a maximum of 200 epochs (training iterations) using Adam (Kingma & Ba, 2015) with a learning rate of 0.01 and early stopping with a window size of 10, i.e. we stop training if the validation loss does not decrease for 10 consecutive epochs.”
- learning rate: 0.01 _[verified]_
  > p. 6: “We train all models for a maximum of 200 epochs (training iterations) using Adam (Kingma & Ba, 2015) with a learning rate of 0.01 and early stopping with a window size of 10, i.e. we stop training if the validation loss does not decrease for 10 consecutive epochs.”
- early stopping window size: 10 _[verified]_
  > p. 6: “We train all models for a maximum of 200 epochs (training iterations) using Adam (Kingma & Ba, 2015) with a learning rate of 0.01 and early stopping with a window size of 10, i.e. we stop training if the validation loss does not decrease for 10 consecutive epochs.”

## Compute

- GPU-based implementation using TensorFlow _[verified]_
  > p. 4: “In practice, we make use of TensorFlow (Abadi et al., 2015) for an efficient GPU-based implementationfoot_1 of Eq. 9 using sparse-dense matrix multiplications.”

## Seeds and runs

- Mean accuracy of 100 runs with random node orderings for ICA _[verified]_
  > p. 7: “For ICA, we report the mean accuracy of 100 runs with random node orderings.”
- Mean accuracy of 100 runs with random weight initializations _[verified]_
  > p. 7: “We trained and tested our model on the same dataset splits as in Yang et al. (2016) and report mean accuracy of 100 runs with random weight initializations.”

## Ablations

- Comparison of different per-layer propagation models _[verified]_
  > p. 7: “We compare different variants of our proposed per-layer propagation model on the citation network datasets.”

## Claims

- The proposed approach outperforms related methods by a significant margin on citation networks and a knowledge graph dataset. _[verified]_
  > p. 1: “In a number of experiments on citation networks and on a knowledge graph dataset we demonstrate that our approach outperforms related methods by a significant margin.”
- The model compares favorably against state-of-the-art semi-supervised learning methods in classification accuracy and efficiency. _[verified]_
  > p. 1: “Experiments on a number of datasets demonstrate that our model compares favorably both in classification accuracy and efficiency (measured in wall-clock time) against state-of-the-art methods for semi-supervised learning.”

## Limitations

- Memory usage grows linearly with the size of the dataset when using full-batch gradient descent. _[verified]_
  > p. 8: “In the current setup with full-batch gradient descent, memory requirement grows linearly in the size of the dataset.”
- The current framework does not naturally support edge features and is limited to undirected graphs. _[verified]_
  > p. 8: “Our framework currently does not naturally support edge features and is limited to undirected graphs (weighted or unweighted).”

## Future work

- Mini-batch stochastic gradient descent can be used to alleviate memory issues. _[verified]_
  > p. 8: “Mini-batch stochastic gradient descent can alleviate this issue.”

## Code

- https://github.com/tkipf/gcn _[verified]_
  > p. 4: “Code to reproduce our experiments is available at https://github.com/tkipf/gcn.”
- https://github.com/kimiyoung/planetoid _[verified]_
  > p. 7: “https://github.com/kimiyoung/planetoid”


## 1710.10903

# GRAPH ATTENTION NETWORKS

Petar Veličković, Guillem Cucurull, Arantxa Casanova, Adriana Romero, Pietro Liò, Yoshua Bengio
2018 · arXiv:1710.10903v3[stat.ML]

## Problem

- Spectral graph neural networks depend on the Laplacian eigenbasis, which ties the learned filters to a specific graph structure and prevents direct application to graphs with different structures. _[verified]_
  > p. 2: “Thus, a model trained on a specific structure can not be directly applied to a graph with a different structure.”
- Non-spectral approaches struggle to define an operator that accommodates varying neighborhood sizes while preserving the weight sharing characteristics of CNNs. _[verified]_
  > p. 2: “One of the challenges of these approaches is to define an operator which works with different sized neighborhoods and maintains the weight sharing property of CNNs.”

## Task

- node classification _[verified]_
  > p. 2: “Inspired by this recent work, we introduce an attention-based architecture to perform node classification of graph-structured data.”

## Contributions

- Introduction of graph attention networks (GATs), which use masked self-attentional layers to process graph-structured data. _[verified]_
  > p. 1: “We present graph attention networks (GATs), novel neural network architectures that operate on graph-structured data, leveraging masked self-attentional layers to address the shortcomings of prior methods based on graph convolutions or their approximations.”

## Method

- A shared linear transformation parametrized by a weight matrix is initially applied to every node to transform input features into higher-level features. _[verified]_
  > p. 3: “To that end, as an initial step, a shared linear transformation, parametrized by a weight matrix, W ∈ R F ×F , is applied to every node.”
- Masked self-attention is performed on the nodes using a single-layer feedforward neural network with LeakyReLU nonlinearity to compute importance coefficients between neighbors. _[verified]_
  > p. 3: “In our experiments, the attention mechanism a is a single-layer feedforward neural network, parametrized by a weight vector a ∈ R 2F , and applying the LeakyReLU nonlinearity (with negative input slope α = 0.2).”
- Attention coefficients are normalized using a softmax function and used to compute a linear combination of neighbor features followed by a nonlinearity. _[verified]_
  > p. 3: “Once obtained, the normalized attention coefficients are used to compute a linear combination of the features corresponding to them, to serve as the final output features for every node (after potentially”
- Multi-head attention with independent mechanisms is employed to stabilize the learning process, using concatenation for intermediate layers and averaging for the final prediction layer. _[verified]_
  > p. 4: “Specifically, K independent attention mechanisms execute the transformation of Equation 4, and then their features are concatenated, resulting in the following output feature representation:”

## Novelty

- The model allows for implicitly assigning different importances to nodes of the same neighborhood, enabling higher model capacity and interpretability compared to GCNs. _[verified]_
  > p. 5: “• As opposed to GCNs, our model allows for (implicitly) assigning different importances to nodes of a same neighborhood, enabling a leap in model capacity.”
- The approach does not depend on upfront access to the global graph structure, making it directly applicable to inductive learning on unseen graphs. _[verified]_
  > p. 5: “The attention mechanism is applied in a shared manner to all edges in the graph, and therefore it does not depend on upfront access to the global graph structure or (features of) all of its nodes (a limitation of many prior techniques).”
- Unlike some prior inductive methods, the approach works with the entirety of the neighborhood without assuming any consistent sequential node ordering. _[verified]_
  > p. 5: “Our technique does not suffer from either of these issues-it works with the entirety of the neighborhood (at the expense of a variable computational footprint, which is still on-par with methods like the GCN), and does not assume any ordering within it.”

## Datasets

- Cora (Transductive, 2708 (1 graph)) _[partial]_
  > p. 6: “Table 1: Summary of the datasets used in our experiments.”
- Citeseer (Transductive, 3327 (1 graph)) _[partial]_
  > p. 6: “Table 1: Summary of the datasets used in our experiments.”
- Pubmed (Transductive, 19717 (1 graph)) _[partial]_
  > p. 6: “Table 1: Summary of the datasets used in our experiments.”
- PPI (Inductive, 56944 (24 graphs)) _[partial]_
  > p. 6: “Table 1: Summary of the datasets used in our experiments.”

## Baselines

- Label propagation (LP) _[verified]_
  > p. 6: “This includes label propagation (LP) (Zhu et al., 2003), semi-supervised embedding (SemiEmb) (Weston et al., 2012), manifold regularization (ManiReg) (Belkin et al., 2006), skip-gram based graph embeddings (Deep-Walk) (Perozzi et al., 2014), the iterative classification algorithm (ICA) (Lu & Getoor, 2003) and Planetoid (Yang et al., 2016).”
- Semi-supervised embedding (SemiEmb) _[verified]_
  > p. 6: “This includes label propagation (LP) (Zhu et al., 2003), semi-supervised embedding (SemiEmb) (Weston et al., 2012), manifold regularization (ManiReg) (Belkin et al., 2006), skip-gram based graph embeddings (Deep-Walk) (Perozzi et al., 2014), the iterative classification algorithm (ICA) (Lu & Getoor, 2003) and Planetoid (Yang et al., 2016).”
- Manifold regularization (ManiReg) _[verified]_
  > p. 6: “This includes label propagation (LP) (Zhu et al., 2003), semi-supervised embedding (SemiEmb) (Weston et al., 2012), manifold regularization (ManiReg) (Belkin et al., 2006), skip-gram based graph embeddings (Deep-Walk) (Perozzi et al., 2014), the iterative classification algorithm (ICA) (Lu & Getoor, 2003) and Planetoid (Yang et al., 2016).”
- DeepWalk _[verified]_
  > p. 6: “This includes label propagation (LP) (Zhu et al., 2003), semi-supervised embedding (SemiEmb) (Weston et al., 2012), manifold regularization (ManiReg) (Belkin et al., 2006), skip-gram based graph embeddings (Deep-Walk) (Perozzi et al., 2014), the iterative classification algorithm (ICA) (Lu & Getoor, 2003) and Planetoid (Yang et al., 2016).”
- Iterative classification algorithm (ICA) _[verified]_
  > p. 6: “This includes label propagation (LP) (Zhu et al., 2003), semi-supervised embedding (SemiEmb) (Weston et al., 2012), manifold regularization (ManiReg) (Belkin et al., 2006), skip-gram based graph embeddings (Deep-Walk) (Perozzi et al., 2014), the iterative classification algorithm (ICA) (Lu & Getoor, 2003) and Planetoid (Yang et al., 2016).”
- Planetoid _[verified]_
  > p. 6: “This includes label propagation (LP) (Zhu et al., 2003), semi-supervised embedding (SemiEmb) (Weston et al., 2012), manifold regularization (ManiReg) (Belkin et al., 2006), skip-gram based graph embeddings (Deep-Walk) (Perozzi et al., 2014), the iterative classification algorithm (ICA) (Lu & Getoor, 2003) and Planetoid (Yang et al., 2016).”
- GCNs _[verified]_
  > p. 6: “We also directly compare our model against GCNs (Kipf & Welling, 2017), as well as graph convolutional models utilising higher-order Chebyshev filters (Defferrard et al., 2016), and the MoNet model presented in Monti et al. (2016).”
- Chebyshev filters graph convolutional models _[verified]_
  > p. 6: “We also directly compare our model against GCNs (Kipf & Welling, 2017), as well as graph convolutional models utilising higher-order Chebyshev filters (Defferrard et al., 2016), and the MoNet model presented in Monti et al. (2016).”
- MoNet _[verified]_
  > p. 6: “We also directly compare our model against GCNs (Kipf & Welling, 2017), as well as graph convolutional models utilising higher-order Chebyshev filters (Defferrard et al., 2016), and the MoNet model presented in Monti et al. (2016).”
- GraphSAGE-GCN _[verified]_
  > p. 6: “For the inductive learning task, we compare against the four different supervised GraphSAGE inductive methods presented in Hamilton et al. (2017).”
- GraphSAGE-mean _[verified]_
  > p. 6: “For the inductive learning task, we compare against the four different supervised GraphSAGE inductive methods presented in Hamilton et al. (2017).”
- GraphSAGE-LSTM _[verified]_
  > p. 6: “For the inductive learning task, we compare against the four different supervised GraphSAGE inductive methods presented in Hamilton et al. (2017).”
- GraphSAGE-pool _[verified]_
  > p. 6: “For the inductive learning task, we compare against the four different supervised GraphSAGE inductive methods presented in Hamilton et al. (2017).”
- Per-node shared multilayer perceptron (MLP) classifier _[verified]_
  > p. 7: “Additionally, for both tasks we provide the performance of a per-node shared multilayer perceptron (MLP) classifier (that does not incorporate graph structure at all).”

## Metrics

- Mean classification accuracy (with standard deviation) _[verified]_
  > p. 7: “For the transductive tasks, we report the mean classification accuracy (with standard deviation) on the test nodes of our method after 100 runs, and reuse the metrics already reported in Kipf & Welling (2017) and Monti et al. (2016) for state-of-the-art techniques.”
- Micro-averaged F1 score _[verified]_
  > p. 7: “For the inductive task, we report the micro-averaged F 1 score on the nodes of the two unseen test graphs, averaged after 10 runs, and reuse the metrics already reported in Hamilton et al. (2017) for the other techniques.”

## Hyperparameters

- L2 regularization (transductive training): ͕ = 0.0005 _[verified]_
  > p. 7: “During training, we apply L 2 regularization with ͕ = 0.0005.”
- dropout (transductive training): p = 0.6 _[verified]_
  > p. 7: “Furthermore, dropout (Srivastava et al., 2014) with p = 0.6 is applied to both layers' inputs, as well as to the normalized attention coefficients (critically, this means that at each training iteration, each node is exposed to a stochastically sampled neighborhood).”
- L2 regularization (Pubmed training): ͕ = 0.001 _[verified]_
  > p. 7: “Similarly as observed by Monti et al. (2016), we found that Pubmed's training set size (60 examples) required slight changes to the GAT architecture: we have applied K = 8 output attention heads (instead of one), and strengthened the L 2 regularization to ͕ = 0.001.”
- batch size (inductive training): 2 graphs _[verified]_
  > p. 7: “We utilize a batch size of 2 graphs during training.”
- learning rate (Pubmed training): 0.01 _[verified]_
  > p. 7: “Both models are initialized using Glorot initialization (Glorot & Bengio, 2010) and trained to minimize cross-entropy on the training nodes using the Adam SGD optimizer (Kingma & Ba, 2014) with an initial learning rate of 0.01 for Pubmed, and 0.005 for all other datasets.”
- learning rate (non-Pubmed training): 0.005 _[verified]_
  > p. 7: “Both models are initialized using Glorot initialization (Glorot & Bengio, 2010) and trained to minimize cross-entropy on the training nodes using the Adam SGD optimizer (Kingma & Ba, 2014) with an initial learning rate of 0.01 for Pubmed, and 0.005 for all other datasets.”
- early stopping patience: 100 epochs _[verified]_
  > p. 7: “In both cases we use an early stopping strategy on both the cross-entropy loss and accuracy (transductive) or micro-F 1 (inductive) score on the validation nodes, with a patience of 100 epochsfoot_0 .”

## Seeds and runs

- 100 runs for transductive tasks _[verified]_
  > p. 7: “For the transductive tasks, we report the mean classification accuracy (with standard deviation) on the test nodes of our method after 100 runs, and reuse the metrics already reported in Kipf & Welling (2017) and Monti et al. (2016) for state-of-the-art techniques.”
- 10 runs for inductive task _[verified]_
  > p. 7: “For the inductive task, we report the micro-averaged F 1 score on the nodes of the two unseen test graphs, averaged after 10 runs, and reuse the metrics already reported in Hamilton et al. (2017) for the other techniques.”

## Ablations

- GCN-64* model for transductive tasks evaluating ELU and ReLU activations _[verified]_
  > p. 7: “In order to fairly assess the benefits of the attention mechanism, we further evaluate a GCN model that computes 64 hidden features, attempting both the ReLU and ELU activation, and reporting (as GCN-64 * ) the better result after 100 runs (which was the ReLU in all three cases).”
- Constant attention GAT model (Const-GAT) for inductive task to evaluate attention mechanism _[verified]_
  > p. 7: “To strictly evaluate the benefits of applying an attention mechanism in this setting (i.e. comparing with a near GCN-equivalent model), we also provide the results when a constant attention mechanism, a(x, y) = 1, is used, with the same architecture-this will assign the same weight to every neighbor.”

## Claims

- The GAT models achieved or matched state-of-the-art results on four graph benchmarks. _[verified]_
  > p. 1: “Our GAT models have achieved or matched state-of-the-art results across four established transductive and inductive graph benchmarks: the Cora, Citeseer and Pubmed citation network datasets, as well as a proteinprotein interaction dataset (wherein test graphs remain unseen during training).”

## Future work

- Overcome practical issues to handle larger batch sizes _[verified]_
  > p. 9: “There are several potential improvements and extensions to graph attention networks that could be addressed as future work, such as overcoming the practical problems described in subsection 2.2 to be able to handle larger batch sizes.”
- Analyze model interpretability using the attention mechanism _[verified]_
  > p. 9: “A particularly interesting research direction would be taking advantage of the attention mechanism to perform a thorough analysis on the model interpretability.”
- Extend the method for graph classification instead of node classification _[verified]_
  > p. 9: “Moreover, extending the method to perform graph classification instead of node classification would also be relevant from the application perspective.”

## Code

- https://github.com/PetarV-/GAT _[verified]_
  > p. 7: “Our implementation of the GAT layer may be found at: https://github.com/PetarV-/GAT.”


## 1707.06347

# Proximal Policy Optimization Algorithms

John Schulman, Filip Wolski, Prafulla Dhariwal, Alec Radford, Oleg Klimov
2017 · arXiv:1707.06347v2[cs.LG]

## Problem

- Existing reinforcement learning methods either fail on simple problems, lack data efficiency and robustness, or are relatively complicated and incompatible with certain architectures. _[verified]_
  > p. 1: “Q-learning (with function approximation) fails on many simple problemsfoot_0 and is poorly understood, vanilla policy gradient methods have poor data effiency and robustness; and trust region policy optimization (TRPO) is relatively complicated, and is not compatible with architectures that include noise (such as dropout) or parameter sharing (between the policy and value function, or with auxiliary tasks).”

## Task

- reinforcement learning _[verified]_
  > p. 1: “We propose a new family of policy gradient methods for reinforcement learning, which alternate between sampling data through interaction with the environment, and optimizing a "surrogate" objective function using stochastic gradient ascent.”

## Contributions

- We propose proximal policy optimization (PPO), a new family of policy gradient methods that enable multiple epochs of minibatch updates and strike a favorable balance between sample complexity, simplicity, and wall-time. _[partial]_
  > p. 1: “The new methods, which we call proximal policy optimization (PPO), have some of the benefits of trust region policy optimization (TRPO), but they are much simpler to implement, more general, and have better sample complexity (empirically).”
- We introduce an algorithm that attains TRPO's data efficiency and reliable performance while using only first-order optimization, proposing a novel objective with clipped probability ratios. _[partial]_
  > p. 1: “This paper seeks to improve the current state of affairs by introducing an algorithm that attains the data efficiency and reliable performance of TRPO, while using only first-order optimization.”

## Method

- The main proposed objective is a clipped surrogate objective that penalizes policy updates moving the probability ratio away from 1 by taking the minimum of clipped and unclipped objectives. _[verified]_
  > p. 3: “L CLIP (θ) = Êt min(r t (θ) Ât , clip(r t (θ), 1 -, 1 + ) Ât ) (7”
- An alternative or additional approach uses a KL divergence penalty with an adaptive coefficient to target a specific KL divergence value each update. _[verified]_
  > p. 4: “Another approach, which can be used as an alternative to the clipped surrogate objective, or in addition to it, is to use a penalty on KL divergence, and to adapt the penalty coefficient so that we achieve some target value of the KL divergence d targ each policy update.”
- The overall objective function combines the clipped policy surrogate, a squared-error value function term, and an optional entropy bonus. _[verified]_
  > p. 2: “Combining these terms, we obtain the following objective, which is (approximately) maximized each iteration: L CLIP +V F +S t (θ) = Êt L CLIP t (θ) -c 1 L V F t (θ) + c 2 S[π θ ](s t ) ,(9)”
- The algorithm collects fixed-length trajectory segments from parallel actors and optimizes the surrogate loss using minibatch SGD or Adam over multiple epochs. _[partial]_
  > p. 5: “A proximal policy optimization (PPO) algorithm that uses fixed-length trajectory segments is shown below.”
- The policy is represented using a fully-connected multi-layer perceptron with two hidden layers of 64 units and tanh nonlinearities, outputting the mean of a Gaussian distribution. _[verified]_
  > p. 6: “To represent the policy, we used a fully-connected MLP with two hidden layers of 64 units, and tanh nonlinearities, outputting the mean of a Gaussian distribution, with variable standard deviations, following [Sch+15b;Dua+16].”

## Datasets

- continuous control benchmark (7 environments) _[verified]_
  > p. 6: “Each algorithm was run on all 7 environments, with 3 random seeds on each.”
- Atari games (49 games) _[verified]_
  > p. 10: “Here we include a comparison of PPO against A2C on a larger collection of 49 Atari games.”

## Baselines

- A2C _[verified]_
  > p. 10: “Here we include a comparison of PPO against A2C on a larger collection of 49 Atari games.”

## Metrics

- Average total reward of the last 100 episodes _[verified]_
  > p. 6: “We scored each run of the algorithm by computing the average total reward of the last 100 episodes.”
- Average normalized score _[verified]_
  > p. 6: “Average normalized scores (over 21 runs of the algorithm, on 7 environments) for each algorithm / hyperparameter setting .β was initialized at 1.”
- Mean performance _[verified]_
  > p. 10: “Figure 6 shows the learning curves of each of three random seeds, while Table 6 shows the mean performance.”

## Hyperparameters

- epochs: K _[verified]_
  > p. 5: “Then we construct the surrogate loss on these N T timesteps of data, and optimize it with minibatch SGD (or usually for better performance, Adam [KB14]), for K epochs.”
- ϵ: 0.1 _[verified]_
  > p. 6: “Clipping, ϵ = 0.1 |  | 0.76”
- ϵ: 0.2 _[verified]_
  > p. 6: “Clipping, | ϵ = 0.2 | 0.82”
- ϵ: 0.3 _[verified]_
  > p. 6: “Clipping, ϵ = 0.3 |  | 0.70”
  > p. 6: “Fixed KL, β = 0.3 |  | 0.62”
- dtarg: 0.003 _[verified]_
  > p. 6: “Adaptive KL dtarg = 0.003 | 0.68”
- dtarg: 0.01 _[verified]_
  > p. 6: “Adaptive KL dtarg = 0.01 | 0.74”
- dtarg: 0.03 _[verified]_
  > p. 6: “Adaptive KL dtarg = 0.03 | 0.71”
- β: 1. _[verified]_
  > p. 6: “Fixed KL, β = 1. |  | 0.71”
- β: 3. _[verified]_
  > p. 6: “Fixed KL, β = 3. |  | 0.72”
- β: 10. _[verified]_
  > p. 6: “Fixed KL, β = 10. |  | 0.69”
- β initialization: 1 _[verified]_
  > p. 6: “Average normalized scores (over 21 runs of the algorithm, on 7 environments) for each algorithm / hyperparameter setting .β was initialized at 1.”

## Seeds and runs

- 3 random seeds per environment _[verified]_
  > p. 6: “Each algorithm was run on all 7 environments, with 3 random seeds on each.”
- Averaged over 21 runs to produce a single scalar _[verified]_
  > p. 6: “We shifted and scaled the scores for each environment so that the random policy gave a score of 0 and the best result was set to 1, and averaged over 21 runs to produce a single scalar for each algorithm setting.”

## Ablations

- Comparison of surrogate objective L CLIP to natural variations and ablated versions with different hyperparameters _[verified]_
  > p. 5: “Here, we compare the surrogate objective L CLIP to several natural variations and ablated versions.”

## Claims

- PPO outperforms other online policy gradient methods across benchmark tasks including simulated robotic locomotion and Atari game playing. _[verified]_
  > p. 1: “Our experiments test PPO on a collection of benchmark tasks, including simulated robotic locomotion and Atari game playing, and we show that PPO outperforms other online policy gradient methods, and overall strikes a favorable balance between sample complexity, simplicity, and wall-time.”
- On continuous control tasks, PPO performs better than the compared algorithms, and on Atari it performs significantly better in sample complexity than A2C and similarly to ACER. _[partial]_
  > p. 1: “On continuous control tasks, it performs better than the algorithms we compare against.”

## Code

- https://github.com/berkeleydeeprlcourse/homework/tree/master/hw4 _[verified]_
  > p. 6: “An implementation is available at https://github.com/berkeleydeeprlcourse/homework/tree/master/hw4.”


## 1801.01290

# Soft Actor-Critic: Off-Policy Maximum Entropy Deep Reinforcement Learning with a Stochastic Actor

Tuomas Haarnoja, Aurick Zhou, Pieter Abbeel, Sergey Levine
2018 · arXiv:1801.01290v2[cs.LG]

## Problem

- Model-free deep RL methods suffer from very high sample complexity and brittle convergence properties. _[partial]_
  > p. 1: “However, these methods typically suffer from two major challenges: very high sample complexity and brittle convergence properties, which necessitate meticulous hyperparameter tuning.”

## Task

- Continuous decision making and control tasks. _[partial]_
  > p. 1: “Model-free deep reinforcement learning (RL) algorithms have been demonstrated on a range of challenging decision making and control tasks.”

## Contributions

- We propose soft actor-critic, an off-policy actor-critic deep RL algorithm based on maximum entropy reinforcement learning. _[verified]_
  > p. 1: “In this paper, we propose soft actor-critic, an offpolicy actor-critic deep RL algorithm based on the maximum entropy reinforcement learning framework.”
- We present a convergence proof for policy iteration in the maximum entropy framework and introduce a practically implementable algorithm. _[verified]_
  > p. 2: “We present a convergence proof for policy iteration in the maximum entropy framework, and then introduce a new algorithm based on an approximation to this procedure that can be practically implemented with deep neural networks, which we call soft actor-critic.”

## Method

- The approach introduces a soft policy iteration algorithm for learning maximum entropy policies by alternating between soft policy evaluation and soft policy improvement steps. _[verified]_
  > p. 4: “We will begin by deriving soft policy iteration, a general algorithm for learning optimal maximum entropy policies that alternates between policy evaluation and policy improvement in the maximum entropy framework.”
- The practical deep reinforcement learning algorithm uses function approximators for a parameterized state value function, two Q-functions, and a tractable policy network. _[verified]_
  > p. 4: “We will consider a parameterized state value function V ψ (s t ), soft Q-function Q θ (s t , a t ), and a tractable policy π φ (a t |s t ).”
- The networks are trained using stochastic gradient descent on objectives derived from the soft Bellman residual, soft value function squared error, and expected KL-divergence for the policy. _[partial]_
  > p. 4: “To that end, we will use function approximators for both the Q-function and the policy, and instead of running evaluation and improvement to convergence, alternate between optimizing both networks with stochastic gradient descent.”
- The policy is reparameterized using a neural network transformation with input noise to enable a low-variance gradient estimator. _[verified]_
  > p. 5: “To that end, we reparameterize the policy using a neural network transformation a t = f φ ( t ; s t ),(11)”
- Two independently trained Q-functions are utilized, and their minimum is used for value and policy gradients to mitigate positive bias. _[partial]_
  > p. 5: “In particular, we parameterize two Q-functions, with parameters θ i , and train them independently to optimize J Q (θ i ).”

## Novelty

- The authors state that this is the first off-policy actor-critic method within the maximum entropy reinforcement learning framework. _[verified]_
  > p. 3: “Though such algorithms have previously been proposed for conventional reinforcement learning, our method is, to our knowledge, the first off-policy actor-critic method in the maximum entropy reinforcement learning framework.”

## Datasets

- OpenAI gym benchmark suite _[partial]_
  > p. 6: “We compare our method to prior techniques on a range of challenging continuous control tasks from the OpenAI gym benchmark suite (Brockman et al., 2016) and also on the rllab implementation of the Humanoid task (Duan et al., 2016).”
- rllab implementation of the Humanoid task _[partial]_
  > p. 6: “We compare our method to prior techniques on a range of challenging continuous control tasks from the OpenAI gym benchmark suite (Brockman et al., 2016) and also on the rllab implementation of the Humanoid task (Duan et al., 2016).”

## Baselines

- Deep deterministic policy gradient (DDPG) _[verified]_
  > p. 6: “We compare our method to deep deterministic policy gradient (DDPG) (Lillicrap et al., 2015), an algorithm that is regarded as one of the more efficient off-policy deep RL methods (Duan et al., 2016); proximal policy optimization (PPO) (Schulman et al., 2017b), a stable and effective on-policy policy gradient algorithm; and soft Q-learning (SQL) (Haarnoja et al., 2017), a recent off-policy algorithm for learning maximum entropy policies.”
- Proximal policy optimization (PPO) _[verified]_
  > p. 6: “We compare our method to deep deterministic policy gradient (DDPG) (Lillicrap et al., 2015), an algorithm that is regarded as one of the more efficient off-policy deep RL methods (Duan et al., 2016); proximal policy optimization (PPO) (Schulman et al., 2017b), a stable and effective on-policy policy gradient algorithm; and soft Q-learning (SQL) (Haarnoja et al., 2017), a recent off-policy algorithm for learning maximum entropy policies.”
- Soft Q-learning (SQL) _[verified]_
  > p. 6: “We compare our method to deep deterministic policy gradient (DDPG) (Lillicrap et al., 2015), an algorithm that is regarded as one of the more efficient off-policy deep RL methods (Duan et al., 2016); proximal policy optimization (PPO) (Schulman et al., 2017b), a stable and effective on-policy policy gradient algorithm; and soft Q-learning (SQL) (Haarnoja et al., 2017), a recent off-policy algorithm for learning maximum entropy policies.”
- Twin delayed deep deterministic policy gradient algorithm (TD3) _[verified]_
  > p. 6: “We additionally compare to twin delayed deep deterministic policy gradient algorithm (TD3) (Fujimoto et al., 2018), using the author-provided implementation.”
- Trust region path consistency learning (Trust-PCL) _[verified]_
  > p. 6: “We have included trust region path consistency learning (Trust-PCL) (Nachum et al., 2017b) and two other variants of SAC in Appendix E.”

## Metrics

- Total average return of evaluation rollouts _[verified]_
  > p. 7: “Figure 1 shows the total average return of evaluation rollouts during training for DDPG, PPO, and TD3.”

## Hyperparameters

- target value update smoothing constant tau: 0.005 _[verified]_
  > p. 8: “However, we found the range of suitable values of τ to be relatively wide and we used the same value (0.005) across all of the tasks.”

## Seeds and runs

- Five different instances with different random seeds _[verified]_
  > p. 7: “We train five different instances of each algorithm with different random seeds, with each performing one evaluation rollout every 1000 environment steps.”

## Ablations

- Deterministic variant of SAC _[verified]_
  > p. 7: “To compare how the stochasticity of the policy and entropy maximization affects the performance, we compare to a deterministic variant of SAC that does not maximize the entropy and that closely resembles DDPG, with the exception of having two Q-functions, using hard target updates, not having a separate target actor, and using fixed rather than learned exploration noise.”
- SAC variant with periodic direct target network weight copies instead of exponential moving average _[verified]_
  > p. 14: “The figure also includes variants of SAC: a variant that periodically copies the target value network weights directly instead of using exponentially moving average, and a deterministic ablation which assumes a deterministic policy in the value update (Equation 6) and the policy update (Equation 13), and thus strongly resembles DDPG with the exception of having two Q-functions, using hard target updates, not having a separate target actor, and using fixed exploration noise rather than learned.”

## Claims

- The proposed method achieves state-of-the-art performance on continuous control benchmark tasks and outperforms prior methods. _[verified]_
  > p. 1: “By combining off-policy updates with a stable stochastic actor-critic formulation, our method achieves state-of-the-art performance on a range of continuous control benchmark tasks, outperforming prior on-policy and off-policy methods.”

## Future work

- Further explore maximum entropy methods, including second-order information and more expressive policy classes. _[verified]_
  > p. 8: “Our results suggest that stochastic, entropy maximizing reinforcement learning algorithms can provide a promising avenue for improved robustness and stability, and further exploration of maximum entropy methods, including methods that incorporate second order information (e.g., trust regions (Schulman et al., 2015)) or more expressive policy classes is an exciting avenue for future work.”


## 2006.11477

# wav2vec 2.0: A Framework for Self-Supervised Learning of Speech Representations

Alexei Baevski, Henry Zhou, Abdelrahman Mohamed, Michael Auli

## Problem

- Labeled training data is much scarcer than unlabeled data, making current speech recognition systems difficult to scale for thousands of languages. _[verified]_
  > p. 1: “However, in many settings labeled data is much harder to come by than unlabeled data: current speech recognition systems require thousands of hours of transcribed speech to reach acceptable performance which is not available for the vast majority of the nearly 7,000 languages spoken worldwide [31].”

## Task

- speech recognition _[verified]_
  > p. 1: “This demonstrates the feasibility of speech recognition with limited amounts of labeled data.”
- phoneme recognition _[verified]_
  > p. 2: “We set a new state of the art on TIMIT phoneme recognition as well as the 100 hour clean subset of Librispeech.”

## Contributions

- We present a framework for self-supervised learning of representations directly from raw audio data. _[verified]_
  > p. 1: “In this paper, we present a framework for self-supervised learning of representations from raw audio data.”
- We learn discrete speech units via a gumbel softmax to represent latent representations in the contrastive task. _[verified]_
  > p. 1: “As part of training, we learn discrete speech units [53,32,7,18] via a gumbel softmax [24,5] to represent the latent representations in the contrastive task (Figure 1) which we find to be more effective than non-quantized targets.”

## Method

- The architecture comprises a multi-layer convolutional feature encoder that converts raw audio into latent representations, a Transformer context network, and a quantization module using product quantization and Gumbel-softmax. _[partial]_
  > p. 2: “Our model is composed of a multi-layer convolutional feature encoder f : X → Z which takes as input raw audio X and outputs latent speech representations z 1 , . . . , z T for T time-steps.”
- The self-supervised pre-training objective involves masking portions of the feature encoder outputs and solving a contrastive task to identify the true quantized latent speech representation among distractors, combined with a codebook diversity loss. _[verified]_
  > p. 3: “During pre-training, we learn representations of speech audio by solving a contrastive task L m which requires to identify the true quantized latent speech representation for a masked time step within a set of distractors.”
- Fine-tuning for speech recognition is performed by adding a randomly initialized linear projection on top of the context network and optimizing via CTC loss while keeping the feature encoder frozen. _[partial]_
  > p. 4: “Pre-trained models are fine-tuned for speech recognition by adding a randomly initialized linear projection on top of the context network into C classes representing the vocabulary of the task [4].”

## Novelty

- Unlike prior work such as vq-wav2vec, the model builds context representations over continuous speech representations and uses self-attention to capture dependencies over the entire sequence end-to-end. _[verified]_
  > p. 2: “Compared to vq-wav2vec [5], our model builds context representations over continuous speech representations and self-attention captures dependencies over the entire sequence of latent representations end-to-end.”
- Instead of fixed positional embeddings, the model uses a convolutional layer acting as a relative positional embedding followed by GELU and layer normalization. _[verified]_
  > p. 2: “Instead of fixed positional embeddings which encode absolute positional information, we use a convolutional layer similar to [37,4,57] which acts as relative positional embedding.”

## Datasets

- Librispeech (LS-960, 960 hours) _[verified]_
  > p. 4: “As unlabeled data we consider the Librispeech corpus [40] without transcriptions containing 960 hours of audio (LS-960) or the audio data from LibriVox (LV-60k).”
- LibriVox (LV-60k, 53.2k hours) _[verified]_
  > p. 4: “As unlabeled data we consider the Librispeech corpus [40] without transcriptions containing 960 hours of audio (LS-960) or the audio data from LibriVox (LV-60k).”
- train-clean-100 (train-clean-100, 100 hours) _[verified]_
  > p. 4: “We fine-tune on five labeled data settings: 960 hours of transcribed Librispeech, the train-clean-100 subset comprising 100 hours (100 hours labeled), as well as the Libri-light limited resource training subsets originally extracted from Librispeech, these are train-10h (10 hours labeled), train-1h (1 hour labeled), train-10min (10 min labeled).”
- train-10h (train-10h, 10 hours) _[verified]_
  > p. 4: “We fine-tune on five labeled data settings: 960 hours of transcribed Librispeech, the train-clean-100 subset comprising 100 hours (100 hours labeled), as well as the Libri-light limited resource training subsets originally extracted from Librispeech, these are train-10h (10 hours labeled), train-1h (1 hour labeled), train-10min (10 min labeled).”
- train-1h (train-1h, 1 hour) _[verified]_
  > p. 4: “We fine-tune on five labeled data settings: 960 hours of transcribed Librispeech, the train-clean-100 subset comprising 100 hours (100 hours labeled), as well as the Libri-light limited resource training subsets originally extracted from Librispeech, these are train-10h (10 hours labeled), train-1h (1 hour labeled), train-10min (10 min labeled).”
- train-10min (train-10min, 10 min) _[verified]_
  > p. 4: “We fine-tune on five labeled data settings: 960 hours of transcribed Librispeech, the train-clean-100 subset comprising 100 hours (100 hours labeled), as well as the Libri-light limited resource training subsets originally extracted from Librispeech, these are train-10h (10 hours labeled), train-1h (1 hour labeled), train-10min (10 min labeled).”
- TIMIT _[verified]_
  > p. 7: “Next, we evaluate accuracy on TIMIT phoneme recognition by fine-tuning the pre-trained models on the labeled TIMIT training data.”

## Baselines

- Discrete BERT baseline _[verified]_
  > p. 6: “Discrete BERT [4] | LS-960 | 4-gram | 15.7 | 24.1 | 16.3 | 25.2”
- Iterative pseudo-labeling baseline _[verified]_
  > p. 6: “Iter. pseudo-labeling [58] | LS-960 | 4-gram+Transf. | 23.51 | 25.48 | 24.37 | 26.02”
- Hybrid DNN/HMM baseline _[verified]_
  > p. 6: “Hybrid DNN/HMM [34] | - | 4-gram | 5.0 | 19.5 | 5.8 | 18.6”
- TTS data augmentation baseline _[verified]_
  > p. 6: “TTS data augm. [30] | - | LSTM |  |  | 4.3 | 13.5”
- Noisy student baseline _[verified]_
  > p. 6: “Noisy student [42] | LS-860 | LSTM | 3.9 | 8.8 | 4.2 | 8.6”
- CTC Transformer supervised baseline _[verified]_
  > p. 7: “CTC Transf [51] |  | - | CLM+Transf. | 2.20 | 4.94 | 2.47 | 5.45”
- Sequence-to-sequence Transformer supervised baseline _[verified]_
  > p. 7: “S2S Transf. | [51] | - | CLM+Transf. | 2.10 | 4.79 | 2.33 | 5.17”
- Transformer Transducer baseline _[verified]_
  > p. 7: “Transf. Transducer [60] |  | - | Transf. | - | - | 2.0 | 4.6”
- ContextNet baseline _[verified]_
  > p. 7: “ContextNet [17] |  | - | LSTM | 1.9 | 3.9 | 1.9 | 4.1”
- Conformer baseline _[verified]_
  > p. 7: “Conformer [15] |  | - | LSTM | 2.1 | 4.3 | 1.9 | 3.9”
- CNN + TD-filterbanks baseline for TIMIT _[verified]_
  > p. 8: “CNN + TD-ﬁlterbanks [59] | 15.6 | 18.0”
- PASE+ baseline for TIMIT _[verified]_
  > p. 8: “PASE+ [47] | - | 17.2”
- Li-GRU + fMLLR baseline for TIMIT _[verified]_
  > p. 8: “Li-GRU + fMLLR [46] | – | 14.9”
- wav2vec baseline for TIMIT _[verified]_
  > p. 8: “wav2vec [49] | 12.9 | 14.7”
  > p. 8: “vq-wav2vec [5] | 9.6 | 11.6”

## Metrics

- Word Error Rate (WER) _[verified]_
  > p. 5: “For Libri-light, we train three seeds with two different learning rates (2e-5 and 3e-5) for all subsets and choose the configuration with lowest WER on dev-other subset decoded with the official 4-gram language model (LM) with beam 50 and fixed model weights (LM weight 2, word insertion penalty -1).”
- Phoneme Error Rate (PER) _[verified]_
  > p. 7: “Table 3 shows that our approach can achieve a new state of the art on this dataset, reducing PER by a relative 23%/29% over the next best result on the dev/test sets.”

## Hyperparameters

- dropout: 0.1 _[verified]_
  > p. 4: “We use dropout 0.1 in the Transformer, at the output of the feature encoder and the input to the quantization module.”
- layer drop rate (BASE): 0.05 _[verified]_
  > p. 4: “Layers are dropped at a rate of 0.05 for BASE and 0.2 for LARGE [22,12]; there is no layer drop for LV-60k.”
- layer drop rate (LARGE): 0.2 _[verified]_
  > p. 4: “Layers are dropped at a rate of 0.05 for BASE and 0.2 for LARGE [22,12]; there is no layer drop for LV-60k.”
- optimizer: Adam _[verified]_
  > p. 5: “We optimize with Adam [29], warming up the learning rate for the first 8% of updates to a peak of 5 × 10 -4 for BASE and 3 × 10 -4 for LARGE, and then linearly decay it.”
- learning rate peak (BASE): 5 × 10 -4 _[verified]_
  > p. 5: “We optimize with Adam [29], warming up the learning rate for the first 8% of updates to a peak of 5 × 10 -4 for BASE and 3 × 10 -4 for LARGE, and then linearly decay it.”
- learning rate peak (LARGE): 3 × 10 -4 _[verified]_
  > p. 5: “We optimize with Adam [29], warming up the learning rate for the first 8% of updates to a peak of 5 × 10 -4 for BASE and 3 × 10 -4 for LARGE, and then linearly decay it.”
- epochs/steps (LARGE): 250k updates _[verified]_
  > p. 5: “LARGE trains for 250k updates, BASE for 400k updates, and LARGE on LV-60k for 600k updates.”
- epochs/steps (BASE): 400k updates _[verified]_
  > p. 5: “LARGE trains for 250k updates, BASE for 400k updates, and LARGE on LV-60k for 600k updates.”
- epochs/steps (LARGE on LV-60k): 600k updates _[verified]_
  > p. 5: “LARGE trains for 250k updates, BASE for 400k updates, and LARGE on LV-60k for 600k updates.”
- diversity loss weight: α = 0.1 _[verified]_
  > p. 5: “We use weight α = 0.1 for the diversity loss Equation 2.”
- quantization groups and codebook size: G = 2 and V = 320 _[verified]_
  > p. 5: “For the quantization module we use G = 2 and V = 320 for both models, resulting in a theoretical maximum of 102.4k codewords.”
- contrastive loss temperature: κ = 0.1 _[verified]_
  > p. 5: “The temperature in the contrastive loss (Equation 3) is set to κ = 0.1.”
- number of distractors: K = 100 _[verified]_
  > p. 5: “In the contrastive loss we use K = 100 distractors.”
- learning rate (Libri-light fine-tuning): 2e-5 and 3e-5 _[verified]_
  > p. 5: “For Libri-light, we train three seeds with two different learning rates (2e-5 and 3e-5) for all subsets and choose the configuration with lowest WER on dev-other subset decoded with the official 4-gram language model (LM) with beam 50 and fixed model weights (LM weight 2, word insertion penalty -1).”
- learning rate (BASE on labeled 960h subset): 1e-4 _[verified]_
  > p. 5: “For BASE on the labeled 960h subset we use a learning rate of 1e-4.”
- optimizer (fine-tuning): Adam _[verified]_
  > p. 5: “We optimize with Adam and a tri-state rate schedule where the learning rate is warmed up for the first 10% of updates, held constant for the next 40% and then linearly decayed for the remainder.”
- classifier-only update steps (fine-tuning): 10k updates _[verified]_
  > p. 5: “For the first 10k updates only the output classifier is trained, after which the Transformer is also updated.”
- model size (BASE): 12 transformer blocks, model dimension 768, inner dimension (FFN) 3,072 and 8 attention heads _[verified]_
  > p. 4: “BASE contains 12 transformer blocks, model dimension 768, inner dimension (FFN) 3,072 and 8 attention heads.”
- model size (LARGE): 24 transformer blocks with model dimension 1,024, inner dimension 4,096 and 16 attention heads _[verified]_
  > p. 4: “The LARGE model contains 24 transformer blocks with model dimension 1,024, inner dimension 4,096 and 16 attention heads.”
- masking probability (ablation pre-training): p = 0.075 _[verified]_
  > p. 8: “we pre-train BASE on LS-960 for 250k updates with masking probability p = 0.075, fine-tune on train-10h for 60k updates on a single GPU with 640k samples per batch, or 40 sec of s”
- LayerDrop rate (BASE fine-tuning): 0.05 _[verified]_
  > p. 13: “We use LayerDrop [22,12] at a rate of 0.05 for BASE and 0.1 for LARGE during fine-tuning.”
- LayerDrop rate (LARGE fine-tuning): 0.1 _[verified]_
  > p. 13: “We use LayerDrop [22,12] at a rate of 0.05 for BASE and 0.1 for LARGE during fine-tuning.”

## Compute

- Training on a total of 64 V100 GPUs for 1.6 days for BASE _[verified]_
  > p. 4: “Crops are batched together to not exceed 1.4m samples per GPU and we train on a total of 64 V100 GPUs for 1.6 days [38]; the total batch size is 1.6h.”
- Training on 128 V100 GPUs over 2.3 days for Librispeech and 5.2 days for LibriVox for LARGE _[verified]_
  > p. 4: “We crop 320k audio samples, or 20sec, with a limit of 1.2m samples per GPU and train on 128 V100 GPUs over 2.3 days for Librispeech and 5.2 days for LibriVox; the total batch size is 2.7h.”

## Seeds and runs

- Training three seeds for Libri-light and reporting average WER and standard deviation _[partial]_
  > p. 5: “For Libri-light, we train three seeds with two different learning rates (2e-5 and 3e-5) for all subsets and choose the configuration with lowest WER on dev-other subset decoded with the official 4-gram language model (LM) with beam 50 and fixed model weights (LM weight 2, word insertion penalty -1).”
- Reporting average WER and standard deviation for three seeds of fine-tuning in ablation setup _[verified]_
  > p. 8: “We report the average WER and standard deviation on the concatenation of dev-clean and dev-other (dev PER) for three seeds of fine-tuning.”

## Ablations

- Ablating quantizing the context network input and the targets in the contrastive loss _[verified]_
  > p. 8: “We ablate quantizing the context network input and the targets in the contrastive loss.”
- Ablating adding an MLP on top of continuous targets and using separate encoders for input and target representations _[verified]_
  > p. 18: “First, we tried to improve the continuous input and continuous target model ( § 5.4) by adding an MLP on top of the continuous target representation and we also tried to use a separate set of encoder parameters for the representations used as input and targets (Separate encoders).”
- Ablating receptive field size, diversity penalty weight, number of relative positional embeddings, gradient flow from quantizer, number of negatives, negative sampling strategy, Gumbel noise, and number of codebooks _[partial]_
  > p. 18: “Increasing the receptive field size from 25ms to 30ms had little effect.”

## Claims

- Experiments using all labeled data of Librispeech achieve 1.8/3.3 WER on the clean/other test sets. _[verified]_
  > p. 1: “Experiments using all labeled data of Librispeech achieve 1.8/3.3 WER on the clean/other test sets.”
- Using just ten minutes of labeled data and pre-training on 53k hours of unlabeled data achieves 4.8/8.2 WER. _[verified]_
  > p. 1: “Using just ten minutes of labeled data and pre-training on 53k hours of unlabeled data still achieves 4.8/8.2 WER.”
- Jointly learning discrete speech units with contextualized representations achieves substantially better results than fixed units learned in a prior step. _[verified]_
  > p. 2: “Our results show that jointly learning discrete speech units with contextualized representations achieves substantially better results than fixed units learned in a prior step [4].”

## Future work

- Switching to a sequence-to-sequence architecture and word piece vocabulary for performance gains _[verified]_
  > p. 8: “We expect performance gains by switching to a seq2seq architecture and a word piece vocabulary.”

## Ethics

- Making speech recognition technology available to more languages and dialects _[verified]_
  > p. 9: “We hope our work will make speech recognition technology more broadly available to many more languages and dialects.”

## Code

- https://github.com/pytorch/fairseqPreprint _[verified]_
  > p. 1: “Code and models are available at https://github.com/pytorch/fairseqPreprint.Under review.”
- https://github.com/facebook/Ax _[verified]_
  > p. 5: “https://github.com/facebook/Ax”


## 2212.04356

# Robust Speech Recognition via Large-Scale Weak Supervision

Alec Radford, Jong Wook Kim, Tao Xu, Greg Brockman, Christine Mcleavey, Ilya Sutskever

## Problem

- Unsupervised pre-trained audio encoders lack equivalent performant decoders, which makes a fine-tuning stage necessary to perform tasks like speech recognition. _[verified]_
  > p. 1: “These pre-trained audio encoders learn high-quality representations of speech, but because they are purely unsupervised they lack an equivalently performant decoder mapping those representations to usable outputs, necessitating a finetuning stage in order to actually perform a task such as speech recognition 1 .”

## Task

- speech recognition _[verified]_
  > p. 2: “To serve as a foundation for further research on robust speech recognition, we release inference code and models at the following URL: https://github.com/openai/ whisper.”

## Contributions

- Scaling weakly supervised speech recognition to 680,000 hours of labeled audio data. _[verified]_
  > p. 2: “In this work we close that gap, scaling weakly supervised speech recognition the next order of magnitude to 680,000 hours of labeled audio data.”
- Broadening the scope of weakly supervised pre-training to be multilingual and multitask. _[verified]_
  > p. 2: “In addition to scale, our work also focuses on broadening the scope of weakly supervised pre-training beyond English-only speech recognition to be both multilingual and multitask.”
- Releasing inference code and models to serve as a foundation for further research. _[verified]_
  > p. 2: “To serve as a foundation for further research on robust speech recognition, we release inference code and models at the following URL: https://github.com/openai/ whisper.”

## Method

- An off-the-shelf encoder-decoder Transformer architecture is used as the core model to avoid confounding findings with model design changes. _[verified]_
  > p. 3: “We chose an encoder-decoder Transformer (Vaswani et al., 2017) as this architecture has been well validated to scale reliably.”
- Input audio is processed as an 80-channel log-magnitude Mel spectrogram computed on 25-millisecond windows with a 10-millisecond stride. _[verified]_
  > p. 3: “All audio is re-sampled to 16,000 Hz, and an 80-channel logmagnitude Mel spectrogram representation is computed on 25-millisecond windows with a stride of 10 milliseconds.”
- A minimalist data pre-processing and training approach is used to predict raw transcripts without standardization, removing the need for inverse text normalization. _[verified]_
  > p. 2: “In contrast to a lot of work on speech recognition, we train Whisper models to predict the raw text of transcripts without any significant standardization, relying on the expressiveness of sequence-to-sequence models to learn to map between utterances and their transcribed form.”
- A multitask sequence-to-sequence format uses special tokens fed into the decoder to specify tasks like transcription, translation, language identification, and timestamps. _[verified]_
  > p. 3: “We use a simple format to specify all tasks and conditioning information as a sequence of input tokens to the decoder.”
- Models are optimized using AdamW, gradient norm clipping, and linear learning rate decay with data parallelism and FP16 precision. _[verified]_
  > p. 4: “Models were trained with AdamW (Loshchilov & Hutter, 2017) and gradient norm clipping (Pascanu et al., 2013) with a linear learning rate decay to zero after a warmup over the first 2048 updates.”

## Novelty

- The approach uses a minimalist data pre-processing pipeline that trains on raw transcripts without significant standardization or inverse text normalization. _[verified]_
  > p. 2: “In contrast to a lot of work on speech recognition, we train Whisper models to predict the raw text of transcripts without any significant standardization, relying on the expressiveness of sequence-to-sequence models to learn to map between utterances and their transcribed form.”
- A single multitask model replaces many individual stages of a traditional speech processing pipeline by handling transcription, translation, voice activity detection, and language identification. _[partial]_
  > p. 4: “The multitask training format uses a set of special tokens that serve as task specifiers or classification targets, as further explained in Section 2.3.”

## Datasets

- Multilingual LibriSpeech (MLS) _[verified]_
  > p. 6: “In order to compare to prior work on multilingual speech recognition, we report results on two low-data benchmarks: Multilingual LibriSpeech (MLS) (Pratap et al., 2020b) and VoxPopuli (Wang et al., 2021) in Table 3.”
- VoxPopuli _[verified]_
  > p. 6: “In order to compare to prior work on multilingual speech recognition, we report results on two low-data benchmarks: Multilingual LibriSpeech (MLS) (Pratap et al., 2020b) and VoxPopuli (Wang et al., 2021) in Table 3.”
- Fleurs _[verified]_
  > p. 7: “To study the performance of Whisper more broadly we also report performance on the Fleurs dataset (Conneau et al., 2022).”
- CoVoST2 (X→en) _[verified]_
  > p. 8: “We study the translation capabilities of Whisper models by measuring their performance on the X→en subset of CoVoST2 (Wang et al., 2020b).”

## Baselines

- XLS-R _[verified]_
  > p. 6: “Whisper performs well on Multilingual LibriSpeech, outperforming XLS-R (Babu et al., 2021), mSLAM (Bapna (Chen et al., 2022b) in a zero-shot setting.”
- mSLAM _[verified]_
  > p. 6: “Whisper performs well on Multilingual LibriSpeech, outperforming XLS-R (Babu et al., 2021), mSLAM (Bapna (Chen et al., 2022b) in a zero-shot setting.”
- VP-10K+FT _[verified]_
  > p. 7: “On VoxPopuli, however, Whisper significantly underperforms prior work and only beats the VP-10K+FT baseline from the original paper.”
- Maestro _[verified]_
  > p. 8: “We compare with Maestro, mSLAM, and XLS-R, the highest-performing prior work.”

## Metrics

- Word error rate _[verified]_
  > p. 5: “Speech recognition research typically evaluates and compares systems based on the word error rate (WER) metric.”
- BLEU _[verified]_
  > p. 8: “We achieve a new state of the art of 29.1 BLEU zero-shot without using any of the CoVoST2 training data.”

## Hyperparameters

- optimizer: AdamW _[verified]_
  > p. 4: “Models were trained with AdamW (Loshchilov & Hutter, 2017) and gradient norm clipping (Pascanu et al., 2013) with a linear learning rate decay to zero after a warmup over the first 2048 updates.”
- warmup: 2048 updates _[verified]_
  > p. 4: “Models were trained with AdamW (Loshchilov & Hutter, 2017) and gradient norm clipping (Pascanu et al., 2013) with a linear learning rate decay to zero after a warmup over the first 2048 updates.”
- batch size: 256 _[verified]_
  > p. 4: “A batch size of 256 segments was used, and the models are trained for 2 20 updates which is between two and three passes over the dataset.”
- learning rate (Tiny): 1.5 × 10 -3 _[verified]_
  > p. 28: “Max Learning Rate Tiny 1.5 × 10 -3”
- learning rate (Base): 1 × 10 -3 _[verified]_
  > p. 28: “Base 1 × 10 -3”
- learning rate (Small): 5 × 10 -4 _[verified]_
  > p. 28: “Small 5 × 10 -4”
- learning rate (Medium): 2.5 × 10 -4 _[verified]_
  > p. 28: “Medium 2.5 × 10 -4”
- learning rate (Large): 1.75 × 10 -4 _[verified]_
  > p. 28: “Large 1.75 × 10 -4”

## Claims

- The models generalize well to standard benchmarks and are competitive with prior fully supervised results in a zero-shot setting. _[verified]_
  > p. 1: “When scaled to 680,000 hours of multilingual and multitask supervision, the resulting models generalize well to standard benchmarks and are often competitive with prior fully supervised results but in a zeroshot transfer setting without the need for any finetuning.”
- A computer vision model showed a 9.2% increase in object classification accuracy when fine-tuned on ImageNet without improvement on seven other natural image datasets. _[verified]_
  > p. 1: “In a particularly disturbing example, Radford et al. ( 2021) documented a 9.2% increase in object classification accuracy when fine-tuning a computer vision model on the ImageNet dataset (Russakovsky et al., 2015) without observing any improvement in average accuracy when classifying the same objects on seven other natural image datasets.”
- SpeechStew mixes 7 pre-existing datasets totaling 5,140 hours of supervision. _[verified]_
  > p. 1: “SpeechStew (Chan et al., 2021) mixes together 7 pre-existing datasets totalling 5,140 hours of supervision.”

## Limitations

- Speech recognition performance is poor for many languages due to a lack of training data. _[verified]_
  > p. 14: “As Figure 3 shows, Whisper's speech recognition performance is still quite poor on many languages.”

## Future work

- Fine-tuning models on supervised datasets or using reinforcement learning to optimize decoding performance. _[verified]_
  > p. 14: “Although the decoding details discussed in Section 4.5 help significantly, we suspect fine-tuning Whisper models on a high-quality supervised dataset and/or using reinforcement learning to more directly optimize for decoding performance could help further reduce these errors.”
- Targeted efforts to increase the amount of training data for lower-resource languages. _[verified]_
  > p. 14: “A targeted effort at increasing the amount of data for these rarer languages could result in a large improvement to average speech recognition performance even with only a small increase in our overall training dataset size.”
- Studying fine-tuning to potentially improve results where high-quality supervised speech data exists. _[verified]_
  > p. 14: “While this is a crucial setting to study due to it being representative of general reliability, for many domains where high-quality supervised speech data does exist, it is likely that results can be improved further by fine-tuning.”
- Investigating whether benefits stem from the encoder, decoder, or both through targeted ablations. _[verified]_
  > p. 14: “This could be studied by either ablating various design components of Whisper, such as training a decoder-less CTC model, or by studying how the performance of existing speech recognition encoders such as wav2vec 2.0 change when used together with a language model.”

## Code

- https://github.com/openai/ _[verified]_
  > p. 2: “To serve as a foundation for further research on robust speech recognition, we release inference code and models at the following URL: https://github.com/openai/ whisper.”


## 2211.14730

# Untitled paper

Yuqi Nie, Nam H Nguyen, Phanwadee Sinthong, Jayant Kalagnanam
2023 · arXiv:2211.14730v2[cs.LG]

## Problem

- Recent findings challenge the usefulness of Transformer models for time series forecasting because a simple linear model can outperform them. _[verified]_
  > p. 1: “Unfortunately, regardless of the complicated design of Transformer-based models, it is shown in the recent paper (Zeng et al., 2022) that a very simple linear model can outperform all of the previous models on a variety of common benchmarks and it challenges the usefulness of Transformer for time series forecasting.”

## Task

- Multivariate time series forecasting _[verified]_
  > p. 1: “We propose an efficient design of Transformer-based models for multivariate time series forecasting and self-supervised representation learning.”
- Self-supervised representation learning _[verified]_
  > p. 1: “We propose an efficient design of Transformer-based models for multivariate time series forecasting and self-supervised representation learning.”

## Contributions

- Proposing the segmentation of time series into subseries-level patches as input tokens for Transformers. _[verified]_
  > p. 1: “It is based on two key components: (i) segmentation of time series into subseries-level patches which are served as input tokens to Transformer; (ii) channel-independence where each channel contains a single univariate time series that shares the same embedding and Transformer weights across all the series.”
- Introducing channel-independence where each channel contains a single univariate time series sharing embedding and weights. _[verified]_
  > p. 1: “It is based on two key components: (i) segmentation of time series into subseries-level patches which are served as input tokens to Transformer; (ii) channel-independence where each channel contains a single univariate time series that shares the same embedding and Transformer weights across all the series.”

## Method

- The model utilizes a vanilla Transformer encoder as its core architecture under a channel-independence setting. _[verified]_
  > p. 3: “Our PatchTST is illustrated in Figure 1 where the model makes use of the vanilla Transformer encoder as its core architecture.”
- Input univariate time series are divided into patches to reduce the number of input tokens and computational complexity. _[verified]_
  > p. 4: “Each input univariate time series x (i) is first divided into patches which can be either overlapped or non-overlapped.”
- Patches are mapped to the Transformer latent space using a trainable linear projection and combined with a learnable additive position encoding. _[verified]_
  > p. 4: “The patches are mapped to the Transformer latent space of dimension D via a trainable linear projection W p ∈ R D×P , and a learnable additive position encoding W pos ∈ R D×N is applied to monitor the temporal order of patches:”
- Mean squared error (MSE) loss is employed to measure discrepancy and optimize the model. _[verified]_
  > p. 5: “We choose to use the MSE loss to measure the discrepancy between the prediction and the ground truth.”
- Instance normalization is applied before patching to mitigate distribution shift between training and testing data. _[verified]_
  > p. 5: “It simply normalizes each time series instance x (i) with zero mean and unit standard deviation.”

## Novelty

- Patching univariate time series to reduce memory usage and computational complexity while allowing the model to process longer historical sequences. _[verified]_
  > p. 4: “Thus constrained on the training time and GPU memory, patch design can allow the model to see the longer historical sequence, which can significantly improve the forecasting performance, as demonstrated in Table 1.”
- PatchTST naturally overcomes previous issues by masking patches rather than single time steps and removing the prediction head in favor of a D x P linear layer during self-supervised pre-training. _[verified]_
  > p. 5: “Our proposed PatchTST can naturally overcome the aforementioned issues.”

## Datasets

- Traffic _[partial]_
  > p. 6: “These datasets have been extensively utilized for benchmarking and publicly available on (Wu et al., 2021).”
- Electricity _[partial]_
  > p. 6: “These datasets have been extensively utilized for benchmarking and publicly available on (Wu et al., 2021).”
- Weather _[partial]_
  > p. 6: “These datasets have been extensively utilized for benchmarking and publicly available on (Wu et al., 2021).”
- ILI _[partial]_
  > p. 6: “These datasets have been extensively utilized for benchmarking and publicly available on (Wu et al., 2021).”
- ETTh1 _[verified]_
  > p. 6: “We evaluate the performance of our proposed PatchTST on 8 popular datasets, including Weather, Traffic, Electricity, ILI and4 ETT datasets (ETTh1, ETTh2, ETTm1, ETTm2).”
- ETTh2 _[verified]_
  > p. 6: “We evaluate the performance of our proposed PatchTST on 8 popular datasets, including Weather, Traffic, Electricity, ILI and4 ETT datasets (ETTh1, ETTh2, ETTm1, ETTm2).”
- ETTm1 _[verified]_
  > p. 6: “We evaluate the performance of our proposed PatchTST on 8 popular datasets, including Weather, Traffic, Electricity, ILI and4 ETT datasets (ETTh1, ETTh2, ETTm1, ETTm2).”
- ETTm2 _[verified]_
  > p. 6: “We evaluate the performance of our proposed PatchTST on 8 popular datasets, including Weather, Traffic, Electricity, ILI and4 ETT datasets (ETTh1, ETTh2, ETTm1, ETTm2).”

## Baselines

- FEDformer baseline _[verified]_
  > p. 6: “We choose the SOTA Transformer-based models, including FEDformer (Zhou et al., 2022), Autoformer (Wu et al., 2021), Informer (Zhou et al., 2021), Pyraformer (Liu et al., 2022), LogTrans (Li et al., 2019), and a recent non-Transformer-based model DLinear (Zeng et al., 2022)”
- Autoformer baseline _[verified]_
  > p. 6: “We choose the SOTA Transformer-based models, including FEDformer (Zhou et al., 2022), Autoformer (Wu et al., 2021), Informer (Zhou et al., 2021), Pyraformer (Liu et al., 2022), LogTrans (Li et al., 2019), and a recent non-Transformer-based model DLinear (Zeng et al., 2022)”
- Informer baseline _[verified]_
  > p. 6: “We choose the SOTA Transformer-based models, including FEDformer (Zhou et al., 2022), Autoformer (Wu et al., 2021), Informer (Zhou et al., 2021), Pyraformer (Liu et al., 2022), LogTrans (Li et al., 2019), and a recent non-Transformer-based model DLinear (Zeng et al., 2022)”
- Pyraformer baseline _[verified]_
  > p. 6: “We choose the SOTA Transformer-based models, including FEDformer (Zhou et al., 2022), Autoformer (Wu et al., 2021), Informer (Zhou et al., 2021), Pyraformer (Liu et al., 2022), LogTrans (Li et al., 2019), and a recent non-Transformer-based model DLinear (Zeng et al., 2022)”
- LogTrans baseline _[verified]_
  > p. 6: “We choose the SOTA Transformer-based models, including FEDformer (Zhou et al., 2022), Autoformer (Wu et al., 2021), Informer (Zhou et al., 2021), Pyraformer (Liu et al., 2022), LogTrans (Li et al., 2019), and a recent non-Transformer-based model DLinear (Zeng et al., 2022)”
- DLinear baseline _[verified]_
  > p. 6: “We choose the SOTA Transformer-based models, including FEDformer (Zhou et al., 2022), Autoformer (Wu et al., 2021), Informer (Zhou et al., 2021), Pyraformer (Liu et al., 2022), LogTrans (Li et al., 2019), and a recent non-Transformer-based model DLinear (Zeng et al., 2022)”
- BTSF baseline _[verified]_
  > p. 8: “We compare our self-supervised model with BTSF (Yang & Hong, 2022), TS2Vec (Yue et al., 2022), TNC (Tonekaboni et al., 2021), and TS-TCC (Eldele et al., 2021) which are among the state-of-the-art contrastive learning representation methods for time seriesfoot_2 .”
- TS2Vec baseline _[verified]_
  > p. 8: “We compare our self-supervised model with BTSF (Yang & Hong, 2022), TS2Vec (Yue et al., 2022), TNC (Tonekaboni et al., 2021), and TS-TCC (Eldele et al., 2021) which are among the state-of-the-art contrastive learning representation methods for time seriesfoot_2 .”
- TNC baseline _[verified]_
  > p. 8: “We compare our self-supervised model with BTSF (Yang & Hong, 2022), TS2Vec (Yue et al., 2022), TNC (Tonekaboni et al., 2021), and TS-TCC (Eldele et al., 2021) which are among the state-of-the-art contrastive learning representation methods for time seriesfoot_2 .”
- TS-TCC baseline _[verified]_
  > p. 8: “We compare our self-supervised model with BTSF (Yang & Hong, 2022), TS2Vec (Yue et al., 2022), TNC (Tonekaboni et al., 2021), and TS-TCC (Eldele et al., 2021) which are among the state-of-the-art contrastive learning representation methods for time seriesfoot_2 .”

## Metrics

- Mean Squared Error _[verified]_
  > p. 2: “Models | L | N | patch | method | MSE |  |  |  |”
- Mean Absolute Error _[verified]_
  > p. 7: “Metric | MSE | MAE | MSE | MAE | MSE | MAE | MSE | MAE | MSE | MAE | MSE | MAE | MSE | MAE | MSE | MAE”

## Hyperparameters

- input sequence length (representation learning): 512 _[verified]_
  > p. 6: “Otherwise stated, across all representation learning experiments the input sequence length is chosen to be 512 and patch size is set to 12, which results in 42 patches.”
- patch size (representation learning): 12 _[verified]_
  > p. 6: “Otherwise stated, across all representation learning experiments the input sequence length is chosen to be 512 and patch size is set to 12, which results in 42 patches.”
- masking ratio: 40% _[verified]_
  > p. 6: “We consider high masking ratio where 40% of the patches are masked with zero values.”
- epochs (self-supervised pre-training): 100 _[verified]_
  > p. 6: “We first apply self-supervised pre-training on the datasets mentioned in Section 4.1 for 100 epochs.”
- epochs (linear probing option (a)): 20 _[verified]_
  > p. 6: “With (a), we only train the model head for 20 epochs while freezing the rest of the network; With (b), we apply linear probing for 10 epochs to update the model head and then end-to-end fine-tuning the entire network for 20 epochs.”
- epochs (linear probing option (b)): 10 _[verified]_
  > p. 6: “With (a), we only train the model head for 20 epochs while freezing the rest of the network; With (b), we apply linear probing for 10 epochs to update the model head and then end-to-end fine-tuning the entire network for 20 epochs.”
- epochs (end-to-end fine-tuning option (b)): 20 _[verified]_
  > p. 6: “With (a), we only train the model head for 20 epochs while freezing the rest of the network; With (b), we apply linear probing for 10 epochs to update the model head and then end-to-end fine-tuning the entire network for 20 epochs.”

## Ablations

- Ablation study on patching and channel-independence _[verified]_
  > p. 8: “We study the effects of patching and channel-independence in Table 7.”

## Claims

- PatchTST improves long-term forecasting accuracy significantly compared to state-of-the-art Transformer-based models. _[verified]_
  > p. 1: “Our channel-independent patch time series Transformer (PatchTST) can improve the long-term forecasting accuracy significantly when compared with that of SOTA Transformer-based models.”
- Training time is reduced by as much as 22 times on large datasets using patching. _[verified]_
  > p. 2: “By setting patch length P = 16 and stride S = 8 with L = 336, the training time is significantly reduced as much as 22 time on large datasets.”
- Increasing the look-back window L from 96 to 336 reduces MSE from 0.518 to 0.397. _[verified]_
  > p. 2: “Table 1 shows that by increasing lookback window L from 96 to 336, MSE can be reduced from 0.518 to 0.397.”
- MSE score is further reduced with patching when L equals 336. _[verified]_
  > p. 2: “As evident in Table 1, MSE score is further reduced from 0.397 to 0.367 with patching when L = 336.”

## Future work

- Model cross-channel dependencies properly by further exploiting channel-independence. _[verified]_
  > p. 9: “It would be an important future step to model the cross-channel dependencies properly.”

## Code

- https://github.com/zhouhaoyi/ETDataset _[verified]_
  > p. 13: “https://github.com/zhouhaoyi/ETDataset”
- https://github.com/laiguokun/multivariate-time-series-data _[verified]_
  > p. 13: “https://github.com/laiguokun/multivariate-time-series-data”


## 2310.06625

# ITRANSFORMER: INVERTED TRANSFORMERS ARE EFFECTIVE FOR TIME SERIES FORECASTING

Yong Liu, Tengge Hu, Haoran Zhang, Haixu Wu, Shiyu Wang, Lintao Ma, Mingsheng Long
2024 · arXiv:2310.06625v4[cs.LG]

## Problem

- Transformers struggle with forecasting time series that use larger lookback windows. _[verified]_
  > p. 1: “However, Transformers are challenged in forecasting series with larger lookback windows due to performance degradation and computation explosion.”
- Embedding each temporal token by fusing multiple variates fails to learn variate-centric representations. _[verified]_
  > p. 1: “Besides, the embedding for each temporal token fuses multiple variates that represent potential delayed events and distinct physical measurements, which may fail in learning variate-centric representations and result in meaningless attention maps.”

## Task

- time series forecasting _[verified]_
  > p. 1: “The recent boom of linear forecasting models questions the ongoing passion for architectural modifications of Transformer-based forecasters.”

## Contributions

- Repurposing the Transformer architecture without modifying basic components. _[verified]_
  > p. 1: “In this work, we reflect on the competent duties of Transformer components and repurpose the Transformer architecture without any modification to the basic components.”
- Proposing iTransformer which applies attention and feed-forward networks on inverted dimensions. _[verified]_
  > p. 1: “We propose iTransformer that simply applies the attention and feed-forward network on the inverted dimensions.”

## Method

- The model uses an encoder-only Transformer architecture composed of embedding, projection, and Transformer blocks. _[verified]_
  > p. 3: “Our proposed iTransformer illustrated in Figure 4 adopts the encoder-only architecture of Transformer (Vaswani et al., 2017), including the embedding, projection, and Transformer blocks.”
- Each time series is tokenized to describe variate properties, interacts via self-attention for mutual correlations, and is processed by feed-forward networks. _[verified]_
  > p. 4: “Each time series driven by the underlying complicated process is firstly tokenized to describe the properties of the variate, applied by self-attention for mutual interactions, and individually processed by feed-forward networks for series representations.”
- The final prediction task for generating future series is delivered to linear projection layers. _[verified]_
  > p. 4: “Notably, the task to generate the predicted series is essentially delivered to linear layers, which has been proven competent by previous work (Das et al., 2023) and we provide a detailed analysis in the next section.”

## Novelty

- Unlike typical forecasters treating timestamps as tokens, the proposed iTransformer inverts the architecture to treat each entire time series of a variate as a token. _[partial]_
  > p. 4: “Instead, our proposed encoder-only iTransformer focuses on representation learning and adaptive correlating of multivariate series.”
- Layer normalization and feed-forward networks are applied to the series representation of individual variates rather than across timestamps to diminish measurement discrepancies. _[verified]_
  > p. 5: “In our inverted version, the normalization is applied to the series representation of individual variate as Equation 2, which has been studied and proved effective in tackling non-stationary problems (Kim et al., 2021;Liu et al., 2022b).”
- Position embeddings are no longer needed because the order of the sequence is implicitly stored in the neuron permutation of the feed-forward network. _[verified]_
  > p. 4: “Specifically, as the order of sequence is implicitly stored in the neuron permutation of the feed-forward network, the position embedding in the vanilla Transformer is no longer needed here.”

## Datasets

- ECL _[verified]_
  > p. 5: “We extensively include 7 real-world datasets in our experiments, including ECL, ETT (4 subsets), Exchange, Traffic, Weather used by Autoformer (Wu et al., 2021), Solar-Energy datasets proposed in LSTNet (Lai et al., 2018), and PEMS (4 subsets) evaluated in SCINet (Liu et al., 2022a).”
- ETT (4 subsets) _[verified]_
  > p. 5: “We extensively include 7 real-world datasets in our experiments, including ECL, ETT (4 subsets), Exchange, Traffic, Weather used by Autoformer (Wu et al., 2021), Solar-Energy datasets proposed in LSTNet (Lai et al., 2018), and PEMS (4 subsets) evaluated in SCINet (Liu et al., 2022a).”
- Exchange _[verified]_
  > p. 5: “We extensively include 7 real-world datasets in our experiments, including ECL, ETT (4 subsets), Exchange, Traffic, Weather used by Autoformer (Wu et al., 2021), Solar-Energy datasets proposed in LSTNet (Lai et al., 2018), and PEMS (4 subsets) evaluated in SCINet (Liu et al., 2022a).”
- Traffic _[verified]_
  > p. 5: “We extensively include 7 real-world datasets in our experiments, including ECL, ETT (4 subsets), Exchange, Traffic, Weather used by Autoformer (Wu et al., 2021), Solar-Energy datasets proposed in LSTNet (Lai et al., 2018), and PEMS (4 subsets) evaluated in SCINet (Liu et al., 2022a).”
- Weather _[verified]_
  > p. 5: “We extensively include 7 real-world datasets in our experiments, including ECL, ETT (4 subsets), Exchange, Traffic, Weather used by Autoformer (Wu et al., 2021), Solar-Energy datasets proposed in LSTNet (Lai et al., 2018), and PEMS (4 subsets) evaluated in SCINet (Liu et al., 2022a).”
- Solar-Energy _[verified]_
  > p. 5: “We extensively include 7 real-world datasets in our experiments, including ECL, ETT (4 subsets), Exchange, Traffic, Weather used by Autoformer (Wu et al., 2021), Solar-Energy datasets proposed in LSTNet (Lai et al., 2018), and PEMS (4 subsets) evaluated in SCINet (Liu et al., 2022a).”
- PEMS (4 subsets) _[verified]_
  > p. 5: “We extensively include 7 real-world datasets in our experiments, including ECL, ETT (4 subsets), Exchange, Traffic, Weather used by Autoformer (Wu et al., 2021), Solar-Energy datasets proposed in LSTNet (Lai et al., 2018), and PEMS (4 subsets) evaluated in SCINet (Liu et al., 2022a).”
- Market (6 subsets) _[verified]_
  > p. 6: “We also provide the experiments on Market (6 subsets) in Appendix F.4.”

## Baselines

- Autoformer baseline model _[verified]_
  > p. 6: “Baselines We carefully choose 10 well-acknowledged forecasting models as our benchmark, including (1) Transformer-based methods: Autoformer (Wu et al., 2021), FEDformer (Zhou et al., 2022), Stationary (Liu et al., 2022b), Crossformer (Zhang & Yan, 2023), PatchTST (Nie et al., 2023);”
- FEDformer baseline model _[verified]_
  > p. 6: “Baselines We carefully choose 10 well-acknowledged forecasting models as our benchmark, including (1) Transformer-based methods: Autoformer (Wu et al., 2021), FEDformer (Zhou et al., 2022), Stationary (Liu et al., 2022b), Crossformer (Zhang & Yan, 2023), PatchTST (Nie et al., 2023);”
- Stationary baseline model _[verified]_
  > p. 6: “Baselines We carefully choose 10 well-acknowledged forecasting models as our benchmark, including (1) Transformer-based methods: Autoformer (Wu et al., 2021), FEDformer (Zhou et al., 2022), Stationary (Liu et al., 2022b), Crossformer (Zhang & Yan, 2023), PatchTST (Nie et al., 2023);”
- Crossformer baseline model _[verified]_
  > p. 6: “Baselines We carefully choose 10 well-acknowledged forecasting models as our benchmark, including (1) Transformer-based methods: Autoformer (Wu et al., 2021), FEDformer (Zhou et al., 2022), Stationary (Liu et al., 2022b), Crossformer (Zhang & Yan, 2023), PatchTST (Nie et al., 2023);”
- PatchTST baseline model _[verified]_
  > p. 6: “Baselines We carefully choose 10 well-acknowledged forecasting models as our benchmark, including (1) Transformer-based methods: Autoformer (Wu et al., 2021), FEDformer (Zhou et al., 2022), Stationary (Liu et al., 2022b), Crossformer (Zhang & Yan, 2023), PatchTST (Nie et al., 2023);”
- DLinear baseline model _[verified]_
  > p. 6: “(2) Linear-based methods: DLinear (Zeng et al., 2023), TiDE (Das et al., 2023), RLinear (Li et al., 2023); and (3) TCN-based methods: SCINet (Liu et al., 2022a), TimesNet (Wu et al., 2023).”
- TiDE baseline model _[verified]_
  > p. 6: “(2) Linear-based methods: DLinear (Zeng et al., 2023), TiDE (Das et al., 2023), RLinear (Li et al., 2023); and (3) TCN-based methods: SCINet (Liu et al., 2022a), TimesNet (Wu et al., 2023).”
- SCINet baseline model _[verified]_
  > p. 6: “(2) Linear-based methods: DLinear (Zeng et al., 2023), TiDE (Das et al., 2023), RLinear (Li et al., 2023); and (3) TCN-based methods: SCINet (Liu et al., 2022a), TimesNet (Wu et al., 2023).”
- TimesNet baseline model _[verified]_
  > p. 6: “(2) Linear-based methods: DLinear (Zeng et al., 2023), TiDE (Das et al., 2023), RLinear (Li et al., 2023); and (3) TCN-based methods: SCINet (Liu et al., 2022a), TimesNet (Wu et al., 2023).”

## Metrics

- MSE _[verified]_
  > p. 6: “The lower MSE/MAE indicates the more accurate prediction result.”
- MAE _[verified]_
  > p. 6: “The lower MSE/MAE indicates the more accurate prediction result.”

## Hyperparameters

- initial learning rate: {10 -3 , 5 × 10 -4 , 10 -4 } _[verified]_
  > p. 14: “We utilize ADAM (Kingma & Ba, 2015) with an initial learning rate in {10 -3 , 5 × 10 -4 , 10 -4 } and L2 loss for the model optimization.”
- batch size: 32 _[verified]_
  > p. 14: “The batch size is uniformly set to 32 and the number of training epochs is fixed to 10.”
- epochs: 10 _[verified]_
  > p. 14: “The batch size is uniformly set to 32 and the number of training epochs is fixed to 10.”
- number of Transformer blocks: {2, 3, 4} _[verified]_
  > p. 14: “We set the number of inverted Transformer blocks in our proposed model L ∈ {2, 3, 4}.”
- hidden dimension: {256, 512} _[verified]_
  > p. 14: “The dimension of series representations D is set from {256, 512}.”
- optimizer: ADAM _[verified]_
  > p. 14: “We utilize ADAM (Kingma & Ba, 2015) with an initial learning rate in {10 -3 , 5 × 10 -4 , 10 -4 } and L2 loss for the model optimization.”

## Compute

- Experiments conducted on a single NVIDIA P100 16GB GPU using PyTorch _[verified]_
  > p. 14: “All the experiments are implemented in PyTorch (Paszke et al., 2019) and conducted on a single NVIDIA P100 16GB GPU.”

## Seeds and runs

- Performance evaluated under five runs with different random seeds _[verified]_
  > p. 14: “We also report the standard deviation of iTransformer performance under five runs with different random seeds in Table 5, which exhibits that the performance of iTransformer is stable.”

## Ablations

- Ablation studies replacing and removing components on variate and temporal dimensions _[partial]_
  > p. 15: “To elaborate on the rational business of Transformer components, we conduct detailed ablations covering replacing components (Replace) and removing components (w/o).”

## Claims

- The iTransformer model achieves state-of-the-art results on challenging real-world datasets. _[verified]_
  > p. 1: “The iTransformer model achieves state-of-the-art on challenging real-world datasets, which further empowers the Transformer family with promoted performance, generalization ability across different variates, and better utilization of arbitrary lookback windows, making it a nice alternative as the fundamental backbone of time series forecasting.”

## Limitations

- Under univariate scenarios, iTransformer degrades into a stackable linear forecaster, which requires further enhancement to better exploit temporal dependencies. _[verified]_
  > p. 25: “Under univariate scenarios, iTransformer actually becomes a stackable linear forecaster (attention degradation), which leaves further enhancement to exploit the temporal dependency better.”

## Future work

- Explore large-scale pre-training and other time series analysis tasks in future work. _[verified]_
  > p. 9: “In the future, we will explore large-scale pre-training and more time series analysis tasks.”
- Design components based on the inverted architecture like efficient attention, structural temporal dependency modeling, fine-grained variate tokenization, and embedding mechanisms. _[verified]_
  > p. 25: “We believe the capability and scalability of Transformer have stood the test by extensive fields, but there is still improvement room to elaborately design components based on the inverted architecture, such as efficient attention for multivariate correlation, structural temporal dependency modeling under distribution shift, fine-grained variate tokenization and well-designed embedding mechanisms.”

## Ethics

- The work focuses solely on time series forecasting, presenting no potential ethical risks. _[verified]_
  > p. 10: “Our work only focuses on the time series forecasting problem, so there is no potential ethical risk.”

## Code

- https://github.com/thuml/iTransformer _[verified]_
  > p. 1: “Code is available at this repository: https://github.com/thuml/iTransformer.”

