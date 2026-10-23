# Phase 2 extraction check

## 1409.0473

# NEURAL MACHINE TRANSLATION BY JOINTLY LEARNING TO ALIGN AND TRANSLATE

Dzmitry Bahdanau, Kyunghyun Cho, Yoshua Bengio
2016 · arXiv:1409.0473v7[cs.CL]

## Problem

- Using a fixed-length vector in encoder-decoder architectures is a performance bottleneck. _[verified]_
  > p. 1: “In this paper, we conjecture that the use of a fixed-length vector is a bottleneck in improving the performance of this basic encoder-decoder architecture, and propose to extend this by allowing a model to automatically (soft-)search for parts of a source sentence that are relevant to predicting a target word, without having to form these parts as a hard segment explicitly.”
- Neural networks struggle to compress all necessary information of a source sentence into a single fixed-length vector. _[verified]_
  > p. 1: “A potential issue with this encoder-decoder approach is that a neural network needs to be able to compress all the necessary information of a source sentence into a fixed-length vector.”
- The performance of basic encoder-decoder models deteriorates rapidly as input sentence length increases. _[verified]_
  > p. 1: “Cho et al. (2014b) showed that indeed the performance of a basic encoder-decoder deteriorates rapidly as the length of an input sentence increases.”

## Task

- Neural machine translation _[verified]_
  > p. 1: “Neural machine translation is a recently proposed approach to machine translation.”
- English-to-French translation _[verified]_
  > p. 1: “With this new approach, we achieve a translation performance comparable to the existing state-of-the-art phrase-based system on the task of English-to-French translation.”

## Contributions

- Proposing an extension to the encoder-decoder model that automatically searches for relevant source sentence parts to predict target words. _[verified]_
  > p. 1: “In this paper, we conjecture that the use of a fixed-length vector is a bottleneck in improving the performance of this basic encoder-decoder architecture, and propose to extend this by allowing a model to automatically (soft-)search for parts of a source sentence that are relevant to predicting a target word, without having to form these parts as a hard segment explicitly.”
- Introducing an extension to the encoder-decoder model that learns to align and translate jointly. _[verified]_
  > p. 1: “In order to address this issue, we introduce an extension to the encoder-decoder model which learns to align and translate jointly.”

## Method

- The proposed architecture consists of a bidirectional recurrent neural network as an encoder and a decoder that computes a distinct context vector for each target word via an attention mechanism. _[partial]_
  > p. 3: “The new architecture consists of a bidirectional RNN as an encoder (Sec. 3.2) and a decoder that emulates searching through a source sentence during decoding a translation (Sec. 3.1).”
- The alignment model computes soft alignment weights using a feedforward neural network, allowing the model to be trained jointly end-to-end via backpropagation. _[verified]_
  > p. 3: “We parametrize the alignment model a as a feedforward neural network which is jointly trained with all the other components of the proposed system.”
- Training is performed using the stochastic gradient descent algorithm with Adadelta for adaptive learning rates. _[partial]_
  > p. 14: “We used the stochastic gradient descent (SGD) algorithm.”

## Novelty

- Unlike standard encoder-decoder models that use a single fixed-length vector, this approach conditions each target word probability on a distinct context vector derived from an expected annotation over alignments. _[verified]_
  > p. 3: “It should be noted that unlike the existing encoder-decoder approach (see Eq. ( 2)), here the probability is conditioned on a distinct context vector c i for each target word y i .”
- The alignment is computed softly by the neural network rather than treated as a latent variable, enabling direct gradient backpropagation. _[verified]_
  > p. 4: “Instead, the alignment model directly computes a soft alignment, which allows the gradient of the cost function to be backpropagated through.”
- A bidirectional RNN is used as an encoder so that each word annotation summarizes both preceding and following words. _[partial]_
  > p. 4: “Hence, we propose to use a bidirectional RNN (BiRNN, Schuster and Paliwal, 1997), which has been successfully used recently in speech recognition (see, e.g., Graves et al., 2013).”

## Datasets

- ACL WMT '14 (348M words) _[partial]_
  > p. 4: “WMT '14 contains the following English-French parallel corpora: Europarl (61M words), news commentary (5.5M), UN (421M) and two crawled corpora of 90M and 272.5M words respectively, totaling 850M words.”

## Baselines

- RNN Encoder-Decoder proposed by Cho et al. (2014a) _[verified]_
  > p. 4: “As a comparison, we also report the performance of an RNN Encoder-Decoder which was proposed recently by Cho et al. (2014a).”
- Conventional phrase-based translation system (Moses) _[verified]_
  > p. 5: “More importantly, the performance of the RNNsearch is as high as that of the conventional phrase-based translation system (Moses), when only the sentences consisting of known words are considered.”

## Metrics

- BLEU score _[verified]_
  > p. 5: “In Table 1, we list the translation performances measured in BLEU score.”

## Hyperparameters

- hidden units: 1000 _[partial]_
  > p. 5: “The encoder and decoder of the RNNencdec have 1000 hidden units each.”
- optimizer: SGD with Adadelta _[verified]_
  > p. 5: “We use a minibatch stochastic gradient descent (SGD) algorithm together with Adadelta (Zeiler, 2012) to train each model.”
- batch size: 80 sentences _[verified]_
  > p. 5: “Each SGD update direction is computed using a minibatch of 80 sentences.”
- epsilon: 10 -6 _[verified]_
  > p. 14: “Adadelta (Zeiler, 2012) was used to automatically adapt the learning rate of each parameter ( = 10 -6 and ρ = 0.95).”
- rho: 0.95 _[verified]_
  > p. 14: “Adadelta (Zeiler, 2012) was used to automatically adapt the learning rate of each parameter ( = 10 -6 and ρ = 0.95).”

## Compute

- Training time per model approximately 5 days _[verified]_
  > p. 5: “We trained each model for approximately 5 days.”

## Ablations

- Training models with sentences of length up to 30 words versus up to 50 words _[verified]_
  > p. 5: “We train each model twice: first with the sentences of length up to 30 words (RNNencdec-30, RNNsearch-30) and then with the sentences of length up to 50 word (RNNencdec-50, RNNsearch-50).”

## Claims

- The new approach achieves translation performance comparable to existing state-of-the-art phrase-based systems. _[verified]_
  > p. 1: “With this new approach, we achieve a translation performance comparable to the existing state-of-the-art phrase-based system on the task of English-to-French translation.”
- Qualitative analysis shows the model's soft-alignments agree well with human intuition. _[verified]_
  > p. 1: “Furthermore, qualitative analysis reveals that the (soft-)alignments found by the model agree well with our intuition.”
- The proposed approach allows models to cope better with long sentences. _[verified]_
  > p. 2: “We show this allows a model to cope better with long sentences.”
- The proposed approach of jointly learning to align and translate significantly improves performance over the basic encoder-decoder. _[verified]_
  > p. 2: “In this paper, we show that the proposed approach of jointly learning to align and translate achieves significantly improved translation performance over the basic encoder-decoder approach.”
- The proposed approach achieves performance comparable to conventional phrase-based systems on English-to-French translation with a single model. _[verified]_
  > p. 2: “On the task of English-to-French translation, the proposed approach achieves, with a single model, a translation performance comparable, or close, to the conventional phrase-based system.”

## Future work

- Improving handling of unknown or rare words. _[verified]_
  > p. 9: “One of challenges left for the future is to better handle unknown, or rare words.”

## Code

- https://github.com/lisa-groundhog/GroundHog _[verified]_
  > p. 4: “Implementations are available at https://github.com/lisa-groundhog/GroundHog.”


## 1409.1556

# VERY DEEP CONVOLUTIONAL NETWORKS FOR LARGE-SCALE IMAGE RECOGNITION

Karen Simonyan, Andrew Zisserman
2015 · arXiv:1409.1556v6[cs.CV]

## Problem

- Understanding how the depth of convolutional networks affects their accuracy in large-scale image recognition. _[verified]_
  > p. 1: “In this work we investigate the effect of the convolutional network depth on its accuracy in the large-scale image recognition setting.”

## Task

- Large-scale image recognition _[verified]_
  > p. 1: “In this work we investigate the effect of the convolutional network depth on its accuracy in the large-scale image recognition setting.”

## Contributions

- Thorough evaluation of networks of increasing depth using very small convolution filters, showing improvement by pushing depth to 16-19 layers. _[verified]_
  > p. 1: “Our main contribution is a thorough evaluation of networks of increasing depth using an architecture with very small (3 × 3) convolution filters, which shows that a significant improvement on the prior-art configurations can be achieved by pushing the depth to 16-19 weight layers.”
- Demonstration that the learned representations generalise well to other datasets with state-of-the-art results. _[verified]_
  > p. 1: “We also show that our representations generalise well to other datasets, where they achieve state-of-the-art results.”
- Public release of the two best-performing ConvNet models. _[verified]_
  > p. 1: “We have made our two best-performing ConvNet models publicly available to facilitate further research on the use of deep visual representations in computer vision.”

## Method

- The network architecture uses fixed 224x224 RGB image inputs, stacks of convolutional layers with small 3x3 receptive fields, max-pooling layers, and three fully-connected layers followed by a soft-max layer. _[partial]_
  > p. 2: “The image is passed through a stack of convolutional (conv.) layers, where we use filters with a very small receptive field: 3 × 3 (which is the smallest size to capture the notion of left/right, up/down, center).”
- Training is performed by optimizing a multinomial logistic regression objective with mini-batch gradient descent using momentum, weight decay, and dropout regularisation. _[partial]_
  > p. 4: “Namely, the training is carried out by optimising the multinomial logistic regression objective using mini-batch gradient descent (based on back-propagation (LeCun et al., 1989)) with momentum.”
- The training images undergo data augmentation including random cropping from rescaled images, horizontal flipping, and random RGB colour shifts. _[partial]_
  > p. 4: “To further augment the training set, the crops underwent random horizontal flipping and random RGB colour shift (Krizhevsky et al., 2012).”
- Training scale is managed either by fixing the smallest side S to a single scale (256 or 384) or by multi-scale training with scale jittering by randomly sampling S from a range. _[verified]_
  > p. 4: “The second approach to setting S is multi-scale training, where each training image is individually rescaled by randomly sampling S from a certain range [S min , S max ] (we used S min = 256 and S max = 512).”
- At test time, the fully-connected layers are converted to convolutional layers and the network is applied densely over the entire rescaled image to produce a class score map. _[partial]_
  > p. 5: “Namely, the fully-connected layers are first converted to convolutional layers (the first FC layer to a 7 × 7 conv. layer, the last two FC layers to 1 × 1 conv. layers).”
- Multi-GPU training is implemented using data parallelism by splitting training batches across multiple GPUs and synchronously averaging their computed gradients. _[verified]_
  > p. 5: “Multi-GPU training exploits data parallelism, and is carried out by splitting each batch of training images into several GPU batches, processed in parallel on each GPU.”

## Datasets

- ILSVRC validation set _[verified]_
  > p. 6: “For the majority of experiments, we used the validation set as the test set.”
- ILSVRC-2014 competition test set (test) _[verified]_
  > p. 6: “Certain experiments were also carried out on the test set and submitted to the official ILSVRC server as a "VGG" team entry to the ILSVRC-2014 competition (Russakovsky et al., 2014).”

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

- top-5 error _[verified]_
  > p. 6: “main evaluation criterion used in ILSVRC, and is computed as the proportion of images such that the ground-truth category is outside the top-5 predicted categories.”
  > p. 7: “Our best single-network performance on the validation set is 24.8%/7.5% top-1/top-5 error (highlighted in bold in Table 4).”
- top-1 val. error _[verified]_
  > p. 7: “Our best single-network performance on the validation set is 24.8%/7.5% top-1/top-5 error (highlighted in bold in Table 4).”
- top-5 test error _[verified]_
  > p. 7: “On the test set, the configuration E achieves 7.3% top-5 error.”

## Hyperparameters

- optimizer: mini-batch gradient descent with momentum _[verified]_
  > p. 4: “Namely, the training is carried out by optimising the multinomial logistic regression objective using mini-batch gradient descent (based on back-propagation (LeCun et al., 1989)) with momentum.”
- batch size: 256 _[verified]_
  > p. 4: “The batch size was set to 256, momentum to 0.9.”
- momentum: 0.9 _[verified]_
  > p. 4: “The batch size was set to 256, momentum to 0.9.”
- weight decay: 5 • 10 -4 _[verified]_
  > p. 4: “The training was regularised by weight decay (the L 2 penalty multiplier set to 5 • 10 -4 ) and dropout regularisation for the first two fully-connected layers (dropout ratio set to 0.5).”
- dropout ratio: 0.5 _[verified]_
  > p. 4: “The training was regularised by weight decay (the L 2 penalty multiplier set to 5 • 10 -4 ) and dropout regularisation for the first two fully-connected layers (dropout ratio set to 0.5).”
- learning rate: 10 -2 _[partial]_
  > p. 4: “The learning rate was initially set to 10 -2 , and then decreased by a factor of 10 when the validation set accuracy stopped improving.”
- epochs: 74 _[verified]_
  > p. 4: “In total, the learning rate was decreased 3 times, and the learning was stopped after 370K iterations (74 epochs).”
- learning rate (S = 384 network training): 10 -3 _[verified]_
  > p. 4: “To speed-up training of the S = 384 network, it was initialised with the weights pre-trained with S = 256, and we used a smaller initial learning rate of 10 -3 .”

## Compute

- Four NVIDIA Titan Black GPUs _[verified]_
  > p. 5: “On a system equipped with four NVIDIA Titan Black GPUs, training a single net took 2-3 weeks depending on the architecture.”
- Training a single net took 2-3 weeks depending on the architecture _[verified]_
  > p. 5: “On a system equipped with four NVIDIA Titan Black GPUs, training a single net took 2-3 weeks depending on the architecture.”

## Ablations

- Comparison of different ConvNet depths and filter sizes _[partial]_
  > p. 6: “Second, we observe that the classification error decreases with the increased ConvNet depth: from 11 layers in A to 19 layers in E.”

## Claims

- Achieved first and second places in the localisation and classification tracks of the ImageNet Challenge 2014. _[verified]_
  > p. 1: “These findings were the basis of our ImageNet Challenge 2014 submission, where our team secured the first and the second places in the localisation and classification tracks respectively.”


## 1512.03385

# Deep Residual Learning for Image Recognition

Kaiming He, Xiangyu Zhang, Shaoqing Ren, Jian Sun
2015 · arXiv:1512.03385v1[cs.CV]

## Problem

- Deeper neural networks are difficult to train due to vanishing or exploding gradients and degradation problems. _[partial]_
  > p. 1: “Deeper neural networks are more difficult to train.”

## Task

- image classification _[verified]_
  > p. 1: “This result won the 1st place on the ILSVRC 2015 classification task.”
- visual recognition tasks _[verified]_
  > p. 1: “The depth of representations is of central importance for many visual recognition tasks.”

## Contributions

- A residual learning framework is introduced to ease the training of substantially deeper networks. _[verified]_
  > p. 1: “We present a residual learning framework to ease the training of networks that are substantially deeper than those used previously.”
- Comprehensive empirical evidence shows that residual networks are easier to optimize and gain accuracy from increased depth. _[verified]_
  > p. 1: “We provide comprehensive empirical evidence showing that these residual networks are easier to optimize, and can gain accuracy from considerably increased depth.”

## Method

- Instead of expecting stacked layers to approximate an underlying mapping H(x), the layers are explicitly designed to approximate a residual function F(x) := H(x) - x, with the original function represented as F(x) + x. _[partial]_
  > p. 3: “So rather than expect stacked layers to approximate H(x), we explicitly let these layers approximate a residual function F(x) := H(x)x.”
- The building block of the residual network is defined by y = F(x, {Wi}) + x, where x and y are input and output vectors, F represents the residual mapping, and element-wise addition via a shortcut connection is used. _[verified]_
  > p. 3: “Formally, in this paper we consider a building block defined as: y = F(x, {W i }) + x.”
- When input and output dimensions need to be matched, a linear projection Ws is used via shortcut connections, otherwise identity mapping is used. _[verified]_
  > p. 3: “If this is not the case (e.g., when changing the input/output channels), we can perform a linear projection W s by the shortcut connections to match the dimensions: y = F(x, {W i }) + W s x.”
- The network architecture uses 3x3 filters for convolutional layers following design rules similar to VGG nets, ending with global average pooling and a fully-connected layer with softmax, with shortcut connections inserted to form the residual version. _[partial]_
  > p. 4: “Based on the above plain network, we insert shortcut connections (Fig. 3, right) which turn the network into its counterpart residual version.”
- Models are trained using SGD with batch normalization right after each convolution and before activation, starting with a learning rate of 0.1 and trained from scratch. _[partial]_
  > p. 4: “We adopt batch normalization (BN) [16] right after each convolution and before activation, following [16].”

## Novelty

- The use of shortcut connections in residual learning introduces neither extra parameters nor computational complexity compared to plain networks. _[verified]_
  > p. 3: “The shortcut connections in Eqn.(1) introduce neither extra parameter nor computation complexity.”

## Datasets

- ImageNet 2012 classification dataset (training, validation, test, 1.28 million training images, 50k validation images, 100k test images) _[partial]_
  > p. 4: “We evaluate our method on the ImageNet 2012 classification dataset [36] that consists of 1000 classes.”
- PASCAL VOC 2007 and 2012 _[verified]_
  > p. 8: “Table 7 and8 show the object detection baseline results on PASCAL VOC 2007 and 2012 [5] and COCO [26].”
- COCO _[verified]_
  > p. 10: “The MS COCO dataset [26] involves 80 object categories.”
- CIFAR-10 _[verified]_
  > p. 6: “left) also gain accuracy from increased depth (as shown on CIFAR-10), but are not as economical as the bottleneck ResNets.”
- ImageNet Detection DET _[verified]_
  > p. 11: “The ImageNet Detection (DET) task involves 200 object categories.”

## Baselines

- VGG-16 _[verified]_
  > p. 8: “Here we are interested in the improvements of replacing VGG-16 [41] with ResNet-101.”
- GoogLeNet _[unlocated]_
  > p. 6: “GoogLeNet [44] | - | 9.15”
- PReLU-net _[unlocated]_
  > p. 6: “PReLU-net [13] | 24.27 | 7.38”
- BN-inception _[verified]_
  > p. 5: “BN-inception [16] 4.82”
- Maxout _[unlocated]_
  > p. 7: “Maxout [10] | | 9.38”
- NIN _[unlocated]_
  > p. 7: “NIN [25] | | 8.81”
- DSN _[unlocated]_
  > p. 7: “DSN [24] | | 8.22”
- FitNet _[unlocated]_
  > p. 7: “FitNet [35] | 19 | 2.5M | 8.39”
- Highway _[unlocated]_
  > p. 7: “Highway [42, 43] | 19 | 2.3M | 7.54 (7.72±0.16)”

## Metrics

- top-1 and top-5 error rates _[verified]_
  > p. 4: “We evaluate both top-1 and top-5 error rates.”
- mAP@[.5, .95] standard COCO metric _[verified]_
  > p. 8: “Most remarkably, on the challenging COCO dataset we obtain a 6.0% increase in COCO's standard metric (mAP@[.5, .95]), which is a 28% relative improvement.”
- mAP @ IoU = 0.5 PASCAL VOC metric _[verified]_
  > p. 10: “We evaluate the PASCAL VOC metric (mAP @ IoU = 0.5) and the standard COCO metric (mAP @ IoU = .5:.05:.95).”

## Hyperparameters

- optimizer: SGD _[partial]_
  > p. 4: “We use SGD with a mini-batch size of 256.”
- mini-batch size: 256 _[verified]_
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
- mini-batch size (detection training): 8 images (RPN), 16 images (Fast R-CNN) _[verified]_
  > p. 10: “We train the COCO models with an 8-GPU implementation, and thus the RPN step has a mini-batch size of 8 images (i.e., 1 per GPU) and the Fast R-CNN step has a mini-batch size of 16 images.”
- learning rate (RPN and Fast R-CNN training): 0.001 and 0.0001 _[verified]_
  > p. 10: “The RPN step and Fast R-CNN step are both trained for 240k iterations with a learning rate of 0.001 and then for 80k iterations with 0.0001.”

## Compute

- 8-GPU implementation _[verified]_
  > p. 10: “We train the COCO models with an 8-GPU implementation, and thus the RPN step has a mini-batch size of 8 images (i.e., 1 per GPU) and the Fast R-CNN step has a mini-batch size of 16 images.”

## Seeds and runs

- Ran 5 times for ResNet-110 on CIFAR-10 and reported best (mean plus-minus std) _[verified]_
  > p. 7: “For ResNet-110, we run it 5 times and show "best (mean±std)" as in [43].”

## Ablations

- Comparison of plain networks and residual networks (ResNets) _[partial]_
  > p. 4: “Plain Networks. We first evaluate 18-layer and 34-layer plain nets.”
- Comparison of different shortcut options (A, B, C) for increasing dimensions _[verified]_
  > p. 6: “In Table 3 we compare three options: (A) zero-padding shortcuts are used for increasing dimensions, and all shortcuts are parameter-free (the same as Table 2 and Fig. 4 right); (B) projection shortcuts are used for increasing dimensions, and other shortcuts are identity; and (C) all shortcuts are projections.”

## Claims

- An ensemble of residual nets achieves 3.57% error on the ImageNet test set. _[verified]_
  > p. 1: “An ensemble of these residual nets achieves 3.57% error on the ImageNet test set.”
- A 28% relative improvement is obtained on the COCO object detection dataset. _[verified]_
  > p. 1: “Solely due to our extremely deep representations, we obtain a 28% relative improvement on the COCO object detection dataset.”

## Future work

- Combining deep architectures with stronger regularization to potentially improve results _[verified]_
  > p. 8: “But combining with stronger regularization may improve results, which we will study in the future.”


## 1706.03762

# Provided proper attribution is provided, Google hereby grants permission to reproduce the tables and figures in this paper solely for use in journalistic or scholarly works. Attention Is All You Need

Ashish Vaswani, Noam Shazeer, Google Brain, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N Gomez, Łukasz Kaiser
2023 · arXiv:1706.03762v7[cs.CL]

## Problem

- Recurrent models compute sequentially along input and output symbol positions, which prevents parallelization within training examples. _[verified]_
  > p. 2: “This inherently sequential nature precludes parallelization within training examples, which becomes critical at longer sequence lengths, as memory constraints limit batching across examples.”

## Task

- machine translation _[verified]_
  > p. 1: “Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train.”
- English constituency parsing _[verified]_
  > p. 1: “We show that the Transformer generalizes well to other tasks by applying it successfully to English constituency parsing both with large and limited training data.”

## Contributions

- We propose the Transformer, a simple new network architecture based solely on attention mechanisms instead of recurrence and convolutions. _[verified]_
  > p. 1: “We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.”

## Method

- The model follows an encoder-decoder architecture using stacked self-attention and point-wise fully connected layers. _[verified]_
  > p. 3: “The Transformer follows this overall architecture using stacked self-attention and point-wise, fully connected layers for both the encoder and decoder, shown in the left and right halves of Figure 1, respectively.”
- Scaled dot-product attention computes outputs as a weighted sum of values, where weights are determined by scaled query-key dot products passed through a softmax function. _[verified]_
  > p. 4: “We compute the dot products of the query with all keys, divide each by √ d k , and apply a softmax function to obtain the weights on the values.”
- Multi-head attention linearly projects queries, keys, and values multiple times in parallel to jointly attend to information from different representation subspaces. _[partial]_
  > p. 4: “On each of these projected versions of queries, keys and values we then perform the attention function in parallel, yielding d v -dimensional output values.”
- Positional encodings based on sine and cosine functions are added to input embeddings to inject sequence order information since the model contains no recurrence or convolution. _[partial]_
  > p. 6: “To this end, we add "positional encodings" to the input embeddings at the bottoms of the encoder and decoder stacks.”
- The training procedure uses the Adam optimizer with a warm-up learning rate schedule alongside residual dropout and label smoothing regularization. _[partial]_
  > p. 7: “We used the Adam optimizer [20] with β 1 = 0.9, β 2 = 0.98 and ϵ = 10 -9 .”

## Novelty

- The Transformer is the first transduction model relying entirely on self-attention to compute input and output representations without sequence-aligned RNNs or convolutions. _[verified]_
  > p. 2: “To the best of our knowledge, however, the Transformer is the first transduction model relying entirely on self-attention to compute representations of its input and output without using sequence-aligned RNNs or convolution.”

## Datasets

- WMT 2014 English-to-German _[verified]_
  > p. 8: “On the WMT 2014 English-to-German translation task, the big transformer model (Transformer (big) in Table 2) outperforms the best previously reported models (including ensembles) by more than 2.0 BLEU, establishing a new state-of-the-art BLEU score of 28.4.”

## Baselines

- ByteNet _[unlocated]_
  > p. 8: “ByteNet [18] | 23.75 |  |  |”
- Deep-Att + PosUnk _[unlocated]_
  > p. 8: “Deep-Att + PosUnk [39] |  | 39.2 |  | 1.0 · 10^20”
- GNMT + RL _[unlocated]_
  > p. 8: “GNMT + RL [38] | 24.6 | 39.92 | 2.3 · 10^19 | 1.4 · 10^20”
- ConvS2S _[unlocated]_
  > p. 8: “ConvS2S [9] | 25.16 | 40.46 | 9.6 · 10^18 | 1.5 · 10^20”
- MoE _[unlocated]_
  > p. 8: “MoE [32] | 26.03 | 40.56 | 2.0 · 10^19 | 1.2 · 10^20”
- Deep-Att + PosUnk Ensemble _[unlocated]_
  > p. 8: “Deep-Att + PosUnk Ensemble [39] |  | 40.4 |  | 8.0 · 10^20”
- GNMT + RL Ensemble _[unlocated]_
  > p. 8: “GNMT + RL Ensemble [38] | 26.30 | 41.16 | 1.8 · 10^20 | 1.1 · 10^21”
- ConvS2S Ensemble _[unlocated]_
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

- BLEU _[verified]_
  > p. 8: “On the WMT 2014 English-to-German translation task, the big transformer model (Transformer (big) in Table 2) outperforms the best previously reported models (including ensembles) by more than 2.0 BLEU, establishing a new state-of-the-art BLEU score of 28.4.”
- Perplexity _[verified]_
  > p. 9: “Listed perplexities are per-wordpiece, according to our byte-pair encoding, and should not be compared to per-word perplexities.”
- F1 score _[unlocated]_
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
- beam size (inference): 21 _[verified]_
  > p. 10: “We used a beam size of 21 and α = 0.3 for both WSJ only and the semi-supervised setting.”
- alpha (inference): 0.3 _[verified]_
  > p. 10: “We used a beam size of 21 and α = 0.3 for both WSJ only and the semi-supervised setting.”

## Compute

- Training on 8 NVIDIA P100 GPUs _[verified]_
  > p. 7: “We trained our models on one machine with 8 NVIDIA P100 GPUs.”
- Base models training time and steps _[verified]_
  > p. 7: “We trained the base models for a total of 100,000 steps or 12 hours.”
  > p. 7: “The big models were trained for 300,000 steps (3.5 days).”

## Ablations

- Variations on the Transformer architecture including attention heads, layer depth, hidden dimensions, dropout, label smoothing, and positional embeddings _[partial]_
  > p. 9: “Table 3: Variations on the Transformer architecture.Unlisted values are identical to those of the base model.All metrics are on the English-to-German translation development set, newstest2013.Listed perplexities are per-wordpiece, according to our byte-pair encoding, and should not be compared to per-word perplexities.”

## Claims

- Our model achieves 28.4 BLEU on the WMT 2014 English-to-German translation task, improving over existing best results by over 2 BLEU. _[verified]_
  > p. 1: “Our model achieves 28.4 BLEU on the WMT 2014 Englishto-German translation task, improving over the existing best results, including ensembles, by over 2 BLEU.”
- On the WMT 2014 English-to-French translation task, our model establishes a new single-model state-of-the-art BLEU score of 41.8. _[verified]_
  > p. 1: “On the WMT 2014 English-to-French translation task, our model establishes a new single-model state-of-the-art BLEU score of 41.8 after training for 3.5 days on eight GPUs, a small fraction of the training costs of the best models from the literature.”

## Future work

- Extend the Transformer to handle input and output modalities other than text. _[verified]_
  > p. 10: “We plan to extend the Transformer to problems involving input and output modalities other than text and to investigate local, restricted attention mechanisms to efficiently handle large inputs and outputs such as images, audio and video.”
- Investigate local, restricted attention mechanisms to efficiently handle large inputs and outputs. _[verified]_
  > p. 10: “We plan to extend the Transformer to problems involving input and output modalities other than text and to investigate local, restricted attention mechanisms to efficiently handle large inputs and outputs such as images, audio and video.”
- Make generation less sequential. _[verified]_
  > p. 10: “Making generation less sequential is another research goals of ours.”

## Code

- https://github.com/tensorflow/tensor2tensor _[verified]_
  > p. 10: “The code we used to train and evaluate our models is available at https://github.com/ tensorflow/tensor2tensor.”


## 1810.04805

# BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding

Jacob Devlin, Ming-Wei Chang, Kenton Lee, Kristina Toutanova
2019 · arXiv:1810.04805v2[cs.CL]

## Problem

- Standard language models are unidirectional, which restricts the choice of architectures during pre-training and limits the power of pre-trained representations. _[verified]_
  > p. 1: “The major limitation is that standard language models are unidirectional, and this limits the choice of architectures that can be used during pre-training.”

## Task

- question answering _[verified]_
  > p. 1: “As a result, the pre-trained BERT model can be finetuned with just one additional output layer to create state-of-the-art models for a wide range of tasks, such as question answering and language inference, without substantial taskspecific architecture modifications.”
- language inference _[verified]_
  > p. 1: “As a result, the pre-trained BERT model can be finetuned with just one additional output layer to create state-of-the-art models for a wide range of tasks, such as question answering and language inference, without substantial taskspecific architecture modifications.”

## Contributions

- Demonstrating the importance of bidirectional pre-training for language representations. _[verified]_
  > p. 2: “• We demonstrate the importance of bidirectional pre-training for language representations.”
- Showing that pre-trained representations reduce the need for heavily-engineered task-specific architectures. _[verified]_
  > p. 2: “• We show that pre-trained representations reduce the need for many heavily-engineered taskspecific architectures.”
- Advancing the state of the art for eleven NLP tasks. _[verified]_
  > p. 2: “• BERT advances the state of the art for eleven NLP tasks.”

## Method

- The model architecture is based on a multi-layer bidirectional Transformer encoder. _[verified]_
  > p. 3: “BERT's model architecture is a multi-layer bidirectional Transformer encoder based on the original implementation described in Vaswani et al. (2017) and released in the tensor2tensor library.foot_0”
- The framework consists of two main steps: unsupervised pre-training and supervised fine-tuning. _[verified]_
  > p. 3: “There are two steps in our framework: pre-training and fine-tuning.”
- BERT is pre-trained using two unsupervised tasks: Masked LM (MLM) and Next Sentence Prediction (NSP). _[verified]_
  > p. 4: “Instead, we pre-train BERT using two unsupervised tasks, described in this section.”
- During fine-tuning, the pre-trained parameters are initialized and all parameters are updated end-to-end using labeled downstream task data. _[verified]_
  > p. 5: “For each task, we simply plug in the task-specific inputs and outputs into BERT and finetune all the parameters end-to-end.”

## Novelty

- Unlike previous models that use traditional left-to-right or right-to-left language models, BERT uses a deep bidirectional architecture enabled by a masked language model objective. _[partial]_
  > p. 4: “Unlike Peters et al. (2018a) and Radford et al. (2018), we do not use traditional left-to-right or right-to-left language models to pre-train BERT.”
- Instead of transferring only sentence embeddings like prior work, BERT transfers all pre-trained parameters to initialize end-task models. _[verified]_
  > p. 5: “However, in prior work, only sentence embeddings are transferred to down-stream tasks, where BERT transfers all parameters to initialize end-task model parameters.”
- BERT features a unified architecture across different tasks with minimal differences between pre-trained and downstream architectures. _[verified]_
  > p. 3: “A distinctive feature of BERT is its unified architecture across different tasks.”

## Datasets

- GLUE _[verified]_
  > p. 5: “Detailed descriptions of GLUE datasets are included in Appendix B.1.”
- SQuAD v1.1 (100k crowdsourced question/answer pairs) _[verified]_
  > p. 6: “The Stanford Question Answering Dataset (SQuAD v1.1) is a collection of 100k crowdsourced question/answer pairs (Rajpurkar et al., 2016).”
- TriviaQA _[verified]_
  > p. 7: “The TriviaQA data we used consists of paragraphs from TriviaQA-Wiki formed of the first 400 tokens in documents, that contain at least one of the provided possible answers.”
- SQuAD 2.0 _[verified]_
  > p. 7: “The SQuAD 2.0 task extends the SQuAD 1.1 problem definition by allowing for the possibility that no short answer exists in the provided paragraph, making the problem more realistic.”
- SWAG (113k sentence-pair completion examples) _[verified]_
  > p. 7: “The Situations With Adversarial Generations (SWAG) dataset contains 113k sentence-pair completion examples that evaluate grounded commonsense inference (Zellers et al., 2018).”
- CoNLL-2003 _[verified]_
  > p. 9: “In this section, we compare the two approaches by applying BERT to the CoNLL-2003 Named Entity Recognition (NER) task (Tjong Kim Sang and De Meulder, 2003).”

## Baselines

- OpenAI GPT _[verified]_
  > p. 6: “On the official GLUE leaderboard 10 , BERT LARGE obtains a score of 80.5, compared to OpenAI GPT, which obtains 72.8 as of the date of writing.”
- ESIM+ELMo system _[verified]_
  > p. 7: “BERT LARGE outperforms the authors' baseline ESIM+ELMo system by +27.1% and OpenAI GPT by 8.3%.”
- BiDAF+ELMo _[partial]_
  > p. 7: “BiDAF+ELMo (Single)”

## Metrics

- Accuracy _[verified]_
  > p. 6: “Both BERT BASE and BERT LARGE outperform all systems on all tasks by a substantial margin, obtaining 4.5% and 7.0% respective average accuracy improvement over the prior state of the art.”
- F1 score _[verified]_
  > p. 6: “Our best performing system outperforms the top leaderboard system by +1.5 F1 in ensembling and +1.3 F1 as a single system.”
- Exact Match (EM) and F1 _[partial]_
  > p. 7: “Table 2: Without TriviaQA fine-SQuAD 1.1 results.”
- Spearman correlations, F1, and accuracy _[verified]_
  > p. 6: “F1 scores are reported for QQP and MRPC, Spearman correlations are reported for STS-B, and accuracy scores are reported for the other tasks.”

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
- learning rate (fine-tuning): 5e-5 _[verified]_
  > p. 6: “We fine-tune for 3 epochs with a learning rate of 5e-5 and a batch size of 32.”
  > p. 7: “We fine-tuned for 2 epochs with a learning rate of 5e-5 and a batch size of 48.”
- epochs (fine-tuning): 2 _[partial]_
  > p. 7: “We fine-tuned for 2 epochs with a learning rate of 5e-5 and a batch size of 48.”
- batch size (fine-tuning): 48 _[partial]_
  > p. 7: “We fine-tuned for 2 epochs with a learning rate of 5e-5 and a batch size of 48.”
- learning rate (fine-tuning): 2e-5 _[partial]_
  > p. 7: “We fine-tune the model for 3 epochs with a learning rate of 2e-5 and a batch size of 16.”
- batch size (fine-tuning): 16 _[partial]_
  > p. 7: “We fine-tune the model for 3 epochs with a learning rate of 2e-5 and a batch size of 16.”

## Compute

- Training time on a single Cloud TPU _[verified]_
  > p. 5: “All of the results in the paper can be replicated in at most 1 hour on a single Cloud TPU, or a few hours on a GPU, starting from the exact same pre-trained model.”

## Seeds and runs

- Random restarts for small datasets on BERT LARGE _[verified]_
  > p. 6: “Additionally, for BERT LARGE we found that finetuning was sometimes unstable on small datasets, so we ran several random restarts and selected the best model on the Dev set.”
- Averaging over 5 random restarts for CoNLL-2003 _[verified]_
  > p. 9: “The reported Dev and Test scores are averaged over 5 random restarts using those hyperparameters.”

## Ablations

- Evaluating pretraining objectives: No NSP and Left-to-Right LM _[verified]_
  > p. 8: “We demonstrate the importance of the deep bidirectionality of BERT by evaluating two pretraining objectives using exactly the same pretraining data, fine-tuning scheme, and hyperparameters as BERT BASE :”
- Exploring the effect of model size _[verified]_
  > p. 8: “In this section, we explore the effect of model size on fine-tuning task accuracy.”
- Comparing fine-tuning and feature-based approaches on NER _[verified]_
  > p. 9: “To ablate the fine-tuning approach, we apply the feature-based approach by extracting the activations from one or more layers without fine-tuning any parameters of BERT.”
- Evaluating different masking strategies for MLM pre-training _[verified]_
  > p. 16: “The following is an ablation study to evaluate the effect of different masking strategies.”

## Claims

- BERT achieves new state-of-the-art results on eleven natural language processing tasks with specific score improvements. _[verified]_
  > p. 1: “It obtains new state-of-the-art results on eleven natural language processing tasks, including pushing the GLUE score to 80.5% (7.7% point absolute improvement), MultiNLI accuracy to 86.7% (4.6% absolute improvement), SQuAD v1.1 question answering Test F1 to 93.2 (1.5 point absolute improvement) and SQuAD v2.0 Test F1 to 83.1 (5.1 point absolute improvement).”
- BERT is conceptually simple and empirically powerful. _[verified]_
  > p. 1: “BERT is conceptually simple and empirically powerful.”

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

- Comparing different language model pretraining approaches is challenging because training is expensive, datasets vary, and hyperparameter choices heavily impact results. _[verified]_
  > p. 1: “Training is computationally expensive, often done on private datasets of different sizes, and, as we will show, hyperparameter choices have significant impact on the final results.”

## Task

- Language model pretraining _[verified]_
  > p. 1: “Language model pretraining has led to significant performance gains but careful comparison between different approaches is challenging.”

## Contributions

- We present a set of important BERT design choices and training strategies and introduce alternatives that lead to better downstream task performance. _[verified]_
  > p. 1: “(1) We present a set of important BERT design choices and training strategies and introduce alternatives that lead to better downstream task performance;”
- We use a novel dataset, CC-NEWS, and confirm that using more data for pretraining further improves performance on downstream tasks. _[verified]_
  > p. 1: “(2) We use a novel dataset, CC-NEWS, and confirm that using more data for pretraining further improves performance on downstream tasks;”
- Our training improvements show that masked language model pretraining, under the right design choices, is competitive with all other recently published methods. _[verified]_
  > p. 1: “(3) Our training improvements show that masked language model pretraining, under the right design choices, is competitive with all other recently published methods.”

## Method

- BERT utilizes a transformer architecture consisting of L layers, A self-attention heads, and a hidden dimension of H. _[partial]_
  > p. 2: “We use a transformer architecture with L layers.”
- During pretraining, the model is optimized using masked language modeling and next sentence prediction objectives. _[verified]_
  > p. 2: “During pretraining, BERT uses two objectives: masked language modeling and next sentence prediction.”
- The model is optimized using the Adam optimizer with specific parameters including beta values, weight decay, a warmup and linear decay learning rate schedule, dropout, and GELU activation. _[verified]_
  > p. 2: “BERT is optimized with Adam (Kingma and Ba, 2015) using the following parameters: β 1 = 0.9, β 2 = 0.999, ǫ = 1e-6 and L 2 weight decay of 0.01.”
- Pretraining is conducted on a combined corpus of BookCorpus and English Wikipedia totaling 16GB of text. _[verified]_
  > p. 2: “BERT is trained on a combination of BOOKCOR-PUS (Zhu et al., 2015) plus English WIKIPEDIA, which totals 16GB of uncompressed text.foot_1”

## Novelty

- RoBERTa is introduced as a robustly optimized BERT approach trained with dynamic masking, full sentences without NSP loss, large mini-batches, and a larger byte-level BPE. _[verified]_
  > p. 6: “Specifically, RoBERTa is trained with dynamic masking (Section 4.1), FULL-SENTENCES without NSP loss (Section 4.2), large mini-batches (Section 4.3) and a larger byte-level BPE (Section 4.4).”

## Datasets

- BOOKCORPUS plus English WIKIPEDIA (16GB) _[verified]_
  > p. 3: “• BOOKCORPUS (Zhu et al., 2015) plus English WIKIPEDIA.”
- CC-NEWS (76GB) _[verified]_
  > p. 3: “• CC-NEWS, which we collected from the English portion of the CommonCrawl News dataset (Nagel, 2016).”
- OPENWEBTEXT (38GB) _[verified]_
  > p. 3: “• OPENWEBTEXT (Gokaslan and Cohen, 2019), an open-source recreation of the WebText cor-pus described in Radford et al. (2019).”
- STORIES (31GB) _[verified]_
  > p. 3: “• STORIES, a dataset introduced in Trinh and Le (2018) containing a subset of CommonCrawl data filtered to match the story-like style of Winograd schemas.”
- GLUE _[verified]_
  > p. 3: “The General Language Understanding Evaluation (GLUE) benchmark (Wang et al., 2019b) is a collection of 9 datasets for evaluating natural language understanding systems.”
- SQuAD _[verified]_
  > p. 3: “We evaluate on two versions of SQuAD: V1.1 and V2.0 (Rajpurkar et al., 2016(Rajpurkar et al., , 2018)).”
- RACE (more than 28,000 passages and nearly 100,000 questions) _[verified]_
  > p. 4: “The ReAding Comprehension from Examinations (RACE) (Lai et al., 2017) task is a large-scale reading comprehension dataset with more than 28,000 passages and nearly 100,000 questions.”

## Baselines

- BERT BASE _[verified]_
  > p. 5: “Results for BERT BASE and XLNet BASE are fromYang et al. (2019).”
- XLNet BASE _[verified]_
  > p. 5: “Results for BERT BASE and XLNet BASE are fromYang et al. (2019).”
- BERT LARGE _[verified]_
  > p. 7: “RoBERTa matches the architecture and training objective of BERT LARGE .”
- XLNet LARGE _[unsupported]_
  > p. 7: “RoBERTa matches the architecture and training objective of BERT LARGE .”

## Metrics

- F1 for SQuAD and accuracy for MNLI-m, SST-2 and RACE _[verified]_
  > p. 5: “We report F1 for SQuAD and accuracy for MNLI-m, SST-2 and RACE.”
- Exact Match (EM) and F1 for SQuAD _[unlocated]_
  > p. 9: “EM | F1”
- Accuracy for RACE _[unlocated]_
  > p. 9: “Model | Accuracy | Middle | High”

## Hyperparameters

- max_sequence_length (pretraining): 512 _[verified]_
  > p. 3: “We pretrain with sequences of at most T = 512 tokens.”
- beta2 (pretraining): 0.98 _[verified]_
  > p. 3: “Similarly, we found setting β 2 = 0.98 to improve stability when training with large batch sizes.”
- model_size (pretraining): 355M _[verified]_
  > p. 6: “We begin by training RoBERTa following the BERT LARGE architecture (L = 24, H = 1024, A = 16, 355M parameters).”
- layers (pretraining): 24 _[verified]_
  > p. 6: “We begin by training RoBERTa following the BERT LARGE architecture (L = 24, H = 1024, A = 16, 355M parameters).”
- hidden_size (pretraining): 1024 _[verified]_
  > p. 6: “We begin by training RoBERTa following the BERT LARGE architecture (L = 24, H = 1024, A = 16, 355M parameters).”
- attention_heads (pretraining): 16 _[verified]_
  > p. 6: “We begin by training RoBERTa following the BERT LARGE architecture (L = 24, H = 1024, A = 16, 355M parameters).”
- epochs_steps (pretraining): 100K _[partial]_
  > p. 6: “We pretrain for 100K steps over a comparable BOOK-CORPUS plus WIKIPEDIA dataset as was used in 2019) and Yang et al. (2019), respectively.”
- batch_size (finetuning): {16, 32} _[verified]_
  > p. 7: “We consider a limited hyperparameter sweep for each task, with batch sizes ∈ {16, 32} and learning rates ∈ {1e-5, 2e-5, 3e-5}, with a linear warmup for the first 6% of steps followed by a linear decay to 0.”
- learning_rate (finetuning): {1e-5, 2e-5, 3e-5} _[verified]_
  > p. 7: “We consider a limited hyperparameter sweep for each task, with batch sizes ∈ {16, 32} and learning rates ∈ {1e-5, 2e-5, 3e-5}, with a linear warmup for the first 6% of steps followed by a linear decay to 0.”
- warmup (finetuning): 6% _[verified]_
  > p. 7: “We consider a limited hyperparameter sweep for each task, with batch sizes ∈ {16, 32} and learning rates ∈ {1e-5, 2e-5, 3e-5}, with a linear warmup for the first 6% of steps followed by a linear decay to 0.”
- epochs_steps (finetuning): 10 _[verified]_
  > p. 7: “We finetune for 10 epochs and perform early stopping based on each task's evaluation metric on the dev set.”

## Compute

- DGX-1 machines with 8 x 32GB Nvidia V100 GPUs _[verified]_
  > p. 3: “We train with mixed precision floating point arithmetic on DGX-1 machines, each with 8 × 32GB Nvidia V100 GPUs interconnected by Infiniband (Micikevicius et al., 2018).”
- 1024 V100 GPUs for approximately one day _[verified]_
  > p. 7: “We pretrain our model using 1024 V100 GPUs for approximately one day.”

## Seeds and runs

- Medians over five random initializations (seeds) _[verified]_
  > p. 5: “Reported results are medians over five random initializations (seeds).”

## Ablations

- Comparison of SEGMENT-PAIR versus SENTENCE-PAIR input format _[verified]_
  > p. 5: “We first compare the original SEGMENT-PAIR input format from Devlin et al. (2019) to the SENTENCE-PAIR format; both formats retain the NSP loss, but the latter uses single sentences.”
- Comparison of training without NSP loss and with DOC-SENTENCES blocks _[verified]_
  > p. 5: “We next compare training without the NSP loss and training with blocks of text from a single document (DOC-SENTENCES).”
- Comparison of DOC-SENTENCES versus FULL-SENTENCES sequence restriction _[verified]_
  > p. 5: “Finally we find that restricting sequences to come from a single document (DOC-SENTENCES) performs slightly better than packing sequences from multiple documents (FULL-SENTENCES).”

## Claims

- Our best model achieves state-of-the-art results on GLUE, RACE and SQuAD. _[verified]_
  > p. 1: “Our best model achieves state-of-the-art results on GLUE, RACE and SQuAD.”
- Our model achieves a score of 88.5 on the public GLUE leaderboard, matching the 88.4 reported by Yang et al. (2019). _[partial]_
  > p. 1: “When trained for longer over additional data, our model achieves a score of 88.5 on the public GLUE leaderboard, matching the 88.4 reported by Yang et al. (2019).”
- Our model establishes a new state-of-the-art on 4/9 of the GLUE tasks. _[partial]_
  > p. 1: “Our model establishes a new state-of-the-art on 4/9 of the GLUE tasks: MNLI, QNLI, RTE and STS-B.”

## Future work

- Leave further exploration of the limits of large batch training to future work _[verified]_
  > p. 6: “We leave further exploration of the limits of large batch training to future work.”
- Leave a more detailed comparison of BPE encodings to future work _[verified]_
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
- The growing computational and memory requirements of larger models may hinder their wide adoption on-device. _[verified]_
  > p. 1: “Second, while operating these models on-device in real-time has the potential to enable novel and interesting language processing applications, the growing computational and memory requirements of these models may hamper wide adoption.”

## Task

- Natural Language Processing _[verified]_
  > p. 1: “As Transfer Learning from large-scale pre-trained models becomes more prevalent in Natural Language Processing (NLP), operating these large models in on-theedge and/or under constrained computational training or inference budgets remains challenging.”

## Contributions

- We propose a method to pre-train a smaller general-purpose language representation model called DistilBERT using knowledge distillation. _[partial]_
  > p. 1: “In this work, we propose a method to pre-train a smaller general-purpose language representation model, called DistilBERT, which can then be finetuned with good performances on a wide range of tasks like its larger counterparts.”
- We introduce a triple loss combining language modeling, distillation, and cosine-distance losses during pre-training. _[verified]_
  > p. 1: “To leverage the inductive biases learned by larger models during pre-training, we introduce a triple loss combining language modeling, distillation and cosine-distance losses.”
- We released the trained weights and training code in the Transformers library. _[verified]_
  > p. 2: “We have made the trained weights available along with the training code in the Transformersfoot_1 library from HuggingFace [Wolf et al., 2019].”

## Method

- The student model (DistilBERT) shares the same general architecture as BERT but has its number of layers reduced by half, with token-type embeddings and the pooler removed. _[partial]_
  > p. 2: “In the present work, the student -DistilBERT -has the same general architecture as BERT.”
- The student is trained using a combination of a distillation loss over the soft target probabilities of the teacher, the masked language modeling loss, and a cosine embedding loss. _[partial]_
  > p. 2: “The final training objective is a linear combination of the distillation loss L ce with the supervised training loss, in our case the masked language modeling loss L mlm [Devlin et al., 2018].”
- The student network is initialized by taking every other layer from the teacher model. _[verified]_
  > p. 2: “Taking advantage of the common dimensionality between teacher and student networks, we initialize the student from the teacher by taking one layer out of two.”

## Datasets

- General Language Understanding Evaluation (GLUE) (development sets) _[verified]_
  > p. 3: “We assess the language understanding and generalization capabilities of DistilBERT on the General Language Understanding Evaluation (GLUE) benchmark [Wang et al., 2018], a collection of 9 datasets for evaluating natural language understanding systems.”
- IMDb sentiment classification (test) _[verified]_
  > p. 3: “We further study the performances of DistilBERT on several downstream tasks under efficient inference constraints: a classification task (IMDb sentiment classification - Maas et al. [2011]) and a question answering task (SQuAD v1.1 -Rajpurkar et al. [2016]).”
- SQuAD v1.1 _[verified]_
  > p. 3: “We further study the performances of DistilBERT on several downstream tasks under efficient inference constraints: a classification task (IMDb sentiment classification - Maas et al. [2011]) and a question answering task (SQuAD v1.1 -Rajpurkar et al. [2016]).”

## Baselines

- ELMo encoder followed by two BiLSTMs _[verified]_
  > p. 3: “We compare the results to the baseline provided by the authors of GLUE: an ELMo (Peters et al. [2018]) encoder followed by two BiLSTMs.”
- BERT model _[partial]_
  > p. 3: “DistilBERT also compares surprisingly well to BERT, retaining 97% of the performance with 40% fewer parameters.”
- BERT-base _[verified]_
  > p. 4: “We compare the average inference time on a recent smartphone (iPhone 7 Plus) against our previously trained question answering model based on BERT-base.”

## Metrics

- macro-score _[partial]_
  > p. 3: “We report scores on the development sets for each task by fine-tuning DistilBERT without the use of ensembling or multi-tasking scheme for fine-tuning (which are mostly orthogonal to the present work).”
- accuracy _[verified]_
  > p. 3: “As shown in Table 2, DistilBERT is only 0.6% point behind BERT in test accuracy on the IMDb benchmark while being 40% smaller.”
- F1 score _[verified]_
  > p. 4: “In this case, we were able to reach interesting performances given the size of the model: 79.8 F1 and 70.4 EM, i.e. within 3 points of the full model.”
- Exact Match (EM) _[verified]_
  > p. 4: “In this case, we were able to reach interesting performances given the size of the model: 79.8 F1 and 70.4 EM, i.e. within 3 points of the full model.”

## Hyperparameters

- batch size (inference): 1 _[verified]_
  > p. 4: “To further investigate the speed-up/size trade-off of DistilBERT, we compare (in Table 3) the number of parameters of each model along with the inference time needed to do a full pass on the STS-B development set on CPU (Intel Xeon E5-2690 v3 Haswell @2.9GHz) using a batch size of 1.”

## Compute

- CPU Intel Xeon E5-2690 v3 Haswell @2.9GHz _[verified]_
  > p. 4: “To further investigate the speed-up/size trade-off of DistilBERT, we compare (in Table 3) the number of parameters of each model along with the inference time needed to do a full pass on the STS-B development set on CPU (Intel Xeon E5-2690 v3 Haswell @2.9GHz) using a batch size of 1.”
- iPhone 7 Plus smartphone _[verified]_
  > p. 4: “We compare the average inference time on a recent smartphone (iPhone 7 Plus) against our previously trained question answering model based on BERT-base.”

## Seeds and runs

- Results are medians of 5 runs with different seeds _[verified]_
  > p. 3: “BERT and DistilBERT results are the medians of 5 runs with different seeds.”

## Ablations

- Ablation study varying components of the triple loss and student initialization, measuring impact on GLUE macro-score _[partial]_
  > p. 4: “Table 4 presents the deltas with the full triple loss: removing the Masked Language Modeling loss has little impact while the two distillation losses account for a large portion of the performance.”

## Claims

- It is possible to reduce the size of a BERT model by 40% while retaining 97% of its language understanding capabilities and being 60% faster. _[verified]_
  > p. 1: “While most prior work investigated the use of distillation for building task-specific models, we leverage knowledge distillation during the pre-training phase and show that it is possible to reduce the size of a BERT model by 40%, while retaining 97% of its language understanding capabilities and being 60% faster.”

## Code

- https://github.com/huggingface/transformers _[verified]_
  > p. 2: “https://github.com/huggingface/transformers”
- https://github.com/huggingface/swift-coreml-transformers _[verified]_
  > p. 4: “https://github.com/huggingface/swift-coreml-transformers”


## 2002.05709

# A Simple Framework for Contrastive Learning of Visual Representations

Ting Chen, Simon Kornblith, Mohammad Norouzi, Geoffrey Hinton

## Problem

- Learning effective visual representations without human supervision remains challenging. _[verified]_
  > p. 1: “Learning effective visual representations without human supervision is a long-standing problem.”
- Discriminative approaches often rely on heuristic pretext tasks that can limit the generality of learned representations. _[verified]_
  > p. 1: “Many such approaches have relied on heuristics to design pretext tasks (Doersch et al., 2015;Zhang et al., 2016;Noroozi & Favaro, 2016;Gidaris et al., 2018), which could limit the generality of the learned representations.”

## Task

- contrastive learning of visual representations _[verified]_
  > p. 1: “This paper presents SimCLR: a simple framework for contrastive learning of visual representations.”

## Contributions

- We introduce SimCLR, a simple framework for contrastive learning of visual representations. _[verified]_
  > p. 1: “This paper presents SimCLR: a simple framework for contrastive learning of visual representations.”
- We systematically study the major components of our framework to understand what enables effective contrastive prediction tasks. _[verified]_
  > p. 1: “In order to understand what enables the contrastive prediction tasks to learn useful representations, we systematically study the major components of our framework.”

## Method

- SimCLR utilizes a stochastic data augmentation module to create two correlated views of a data example through sequential random cropping, color distortions, and Gaussian blur. _[verified]_
  > p. 2: “In this work, we sequentially apply three simple augmentations: random cropping followed by resize back to the original size, random color distortions, and random Gaussian blur.”
- A standard ResNet is employed as the base encoder network to extract representation vectors from the augmented data examples. _[unsupported]_
  > p. 2: “Our framework allows various choices of the network architecture without any constraints.”
- A small neural network projection head consisting of an MLP with one hidden layer and a ReLU nonlinearity maps the representations to the latent space for the contrastive loss. _[verified]_
  > p. 2: “We use a MLP with one hidden layer to obtain z i = g(h i ) = W (2) σ(W (1) h i ) where σ is a ReLU nonlinearity.”
- The framework optimizes the normalized temperature-scaled cross entropy loss (NT-Xent) across positive pairs in a mini-batch. _[partial]_
  > p. 2: “A base encoder network f (•) and a projection head g(•) are trained to maximize agreement using a contrastive loss.”

## Novelty

- The authors demonstrate that unsupervised contrastive learning benefits significantly more from stronger color data augmentation compared to supervised learning. _[verified]_
  > p. 5: “Thus, our experiments show that unsupervised contrastive learning benefits from stronger (color) data augmentation than supervised learning.”

## Datasets

- ImageNet _[partial]_
  > p. 7: “ImageNet accuracies of linear classifiers trained on representations learned with different self-supervised methods.”
- Food-101 _[verified]_
  > p. 16: “We investigated transfer learning performance on the Food-101 dataset (Bossard et al., 2014), CIFAR-10 and CIFAR-100 (Krizhevsky & Hinton, 2009), Birdsnap (Berg et al., 2014), the SUN397 scene dataset (Xiao et al., 2010), Stanford Cars (Krause et al., 2013), FGVC Aircraft (Maji et al., 2013), the PASCAL VOC 2007 classification task (Everingham et al., 2010), the Describable Textures Dataset (DTD) (Cimpoi et al., 2014), Oxford-IIIT Pets (Parkhi et al., 2012), Caltech-101 (Fei-Fei et al., 2004), and Oxford 102 Flowers (Nilsback & Zisserman, 2008).”
- CIFAR-10 _[verified]_
  > p. 16: “We investigated transfer learning performance on the Food-101 dataset (Bossard et al., 2014), CIFAR-10 and CIFAR-100 (Krizhevsky & Hinton, 2009), Birdsnap (Berg et al., 2014), the SUN397 scene dataset (Xiao et al., 2010), Stanford Cars (Krause et al., 2013), FGVC Aircraft (Maji et al., 2013), the PASCAL VOC 2007 classification task (Everingham et al., 2010), the Describable Textures Dataset (DTD) (Cimpoi et al., 2014), Oxford-IIIT Pets (Parkhi et al., 2012), Caltech-101 (Fei-Fei et al., 2004), and Oxford 102 Flowers (Nilsback & Zisserman, 2008).”
- CIFAR-100 _[verified]_
  > p. 16: “We investigated transfer learning performance on the Food-101 dataset (Bossard et al., 2014), CIFAR-10 and CIFAR-100 (Krizhevsky & Hinton, 2009), Birdsnap (Berg et al., 2014), the SUN397 scene dataset (Xiao et al., 2010), Stanford Cars (Krause et al., 2013), FGVC Aircraft (Maji et al., 2013), the PASCAL VOC 2007 classification task (Everingham et al., 2010), the Describable Textures Dataset (DTD) (Cimpoi et al., 2014), Oxford-IIIT Pets (Parkhi et al., 2012), Caltech-101 (Fei-Fei et al., 2004), and Oxford 102 Flowers (Nilsback & Zisserman, 2008).”
- Birdsnap _[verified]_
  > p. 16: “We investigated transfer learning performance on the Food-101 dataset (Bossard et al., 2014), CIFAR-10 and CIFAR-100 (Krizhevsky & Hinton, 2009), Birdsnap (Berg et al., 2014), the SUN397 scene dataset (Xiao et al., 2010), Stanford Cars (Krause et al., 2013), FGVC Aircraft (Maji et al., 2013), the PASCAL VOC 2007 classification task (Everingham et al., 2010), the Describable Textures Dataset (DTD) (Cimpoi et al., 2014), Oxford-IIIT Pets (Parkhi et al., 2012), Caltech-101 (Fei-Fei et al., 2004), and Oxford 102 Flowers (Nilsback & Zisserman, 2008).”
- SUN397 (first split) _[verified]_
  > p. 16: “We investigated transfer learning performance on the Food-101 dataset (Bossard et al., 2014), CIFAR-10 and CIFAR-100 (Krizhevsky & Hinton, 2009), Birdsnap (Berg et al., 2014), the SUN397 scene dataset (Xiao et al., 2010), Stanford Cars (Krause et al., 2013), FGVC Aircraft (Maji et al., 2013), the PASCAL VOC 2007 classification task (Everingham et al., 2010), the Describable Textures Dataset (DTD) (Cimpoi et al., 2014), Oxford-IIIT Pets (Parkhi et al., 2012), Caltech-101 (Fei-Fei et al., 2004), and Oxford 102 Flowers (Nilsback & Zisserman, 2008).”
- Stanford Cars _[verified]_
  > p. 16: “We investigated transfer learning performance on the Food-101 dataset (Bossard et al., 2014), CIFAR-10 and CIFAR-100 (Krizhevsky & Hinton, 2009), Birdsnap (Berg et al., 2014), the SUN397 scene dataset (Xiao et al., 2010), Stanford Cars (Krause et al., 2013), FGVC Aircraft (Maji et al., 2013), the PASCAL VOC 2007 classification task (Everingham et al., 2010), the Describable Textures Dataset (DTD) (Cimpoi et al., 2014), Oxford-IIIT Pets (Parkhi et al., 2012), Caltech-101 (Fei-Fei et al., 2004), and Oxford 102 Flowers (Nilsback & Zisserman, 2008).”
- FGVC Aircraft _[verified]_
  > p. 16: “We investigated transfer learning performance on the Food-101 dataset (Bossard et al., 2014), CIFAR-10 and CIFAR-100 (Krizhevsky & Hinton, 2009), Birdsnap (Berg et al., 2014), the SUN397 scene dataset (Xiao et al., 2010), Stanford Cars (Krause et al., 2013), FGVC Aircraft (Maji et al., 2013), the PASCAL VOC 2007 classification task (Everingham et al., 2010), the Describable Textures Dataset (DTD) (Cimpoi et al., 2014), Oxford-IIIT Pets (Parkhi et al., 2012), Caltech-101 (Fei-Fei et al., 2004), and Oxford 102 Flowers (Nilsback & Zisserman, 2008).”
- PASCAL VOC 2007 _[verified]_
  > p. 16: “We investigated transfer learning performance on the Food-101 dataset (Bossard et al., 2014), CIFAR-10 and CIFAR-100 (Krizhevsky & Hinton, 2009), Birdsnap (Berg et al., 2014), the SUN397 scene dataset (Xiao et al., 2010), Stanford Cars (Krause et al., 2013), FGVC Aircraft (Maji et al., 2013), the PASCAL VOC 2007 classification task (Everingham et al., 2010), the Describable Textures Dataset (DTD) (Cimpoi et al., 2014), Oxford-IIIT Pets (Parkhi et al., 2012), Caltech-101 (Fei-Fei et al., 2004), and Oxford 102 Flowers (Nilsback & Zisserman, 2008).”
- Describable Textures Dataset (DTD) (first split) _[verified]_
  > p. 16: “We investigated transfer learning performance on the Food-101 dataset (Bossard et al., 2014), CIFAR-10 and CIFAR-100 (Krizhevsky & Hinton, 2009), Birdsnap (Berg et al., 2014), the SUN397 scene dataset (Xiao et al., 2010), Stanford Cars (Krause et al., 2013), FGVC Aircraft (Maji et al., 2013), the PASCAL VOC 2007 classification task (Everingham et al., 2010), the Describable Textures Dataset (DTD) (Cimpoi et al., 2014), Oxford-IIIT Pets (Parkhi et al., 2012), Caltech-101 (Fei-Fei et al., 2004), and Oxford 102 Flowers (Nilsback & Zisserman, 2008).”
- Oxford-IIIT Pets _[verified]_
  > p. 16: “We investigated transfer learning performance on the Food-101 dataset (Bossard et al., 2014), CIFAR-10 and CIFAR-100 (Krizhevsky & Hinton, 2009), Birdsnap (Berg et al., 2014), the SUN397 scene dataset (Xiao et al., 2010), Stanford Cars (Krause et al., 2013), FGVC Aircraft (Maji et al., 2013), the PASCAL VOC 2007 classification task (Everingham et al., 2010), the Describable Textures Dataset (DTD) (Cimpoi et al., 2014), Oxford-IIIT Pets (Parkhi et al., 2012), Caltech-101 (Fei-Fei et al., 2004), and Oxford 102 Flowers (Nilsback & Zisserman, 2008).”
- Caltech-101 _[verified]_
  > p. 16: “We investigated transfer learning performance on the Food-101 dataset (Bossard et al., 2014), CIFAR-10 and CIFAR-100 (Krizhevsky & Hinton, 2009), Birdsnap (Berg et al., 2014), the SUN397 scene dataset (Xiao et al., 2010), Stanford Cars (Krause et al., 2013), FGVC Aircraft (Maji et al., 2013), the PASCAL VOC 2007 classification task (Everingham et al., 2010), the Describable Textures Dataset (DTD) (Cimpoi et al., 2014), Oxford-IIIT Pets (Parkhi et al., 2012), Caltech-101 (Fei-Fei et al., 2004), and Oxford 102 Flowers (Nilsback & Zisserman, 2008).”
- Oxford 102 Flowers _[partial]_
  > p. 16: “We investigated transfer learning performance on the Food-101 dataset (Bossard et al., 2014), CIFAR-10 and CIFAR-100 (Krizhevsky & Hinton, 2009), Birdsnap (Berg et al., 2014), the SUN397 scene dataset (Xiao et al., 2010), Stanford Cars (Krause et al., 2013), FGVC Aircraft (Maji et al., 2013), the PASCAL VOC 2007 classification task (Everingham et al., 2010), the Describable Textures Dataset (DTD) (Cimpoi et al., 2014), Oxford-IIIT Pets (Parkhi et al., 2012), Caltech-101 (Fei-Fei et al., 2004), and Oxford 102 Flowers (Nilsback & Zisserman, 2008).”

## Baselines

- Local Aggregation _[unlocated]_
  > p. 7: “Local Agg. | ResNet-50 |  | 24 | 60.2 | -”
- MoCo _[unlocated]_
  > p. 7: “MoCo | ResNet-50 |  | 24 | 60.6 | -”
- PIRL _[unlocated]_
  > p. 7: “PIRL | ResNet-50 |  | 24 | 63.6 | -”
- CPC v2 _[unlocated]_
  > p. 7: “CPC v2 | ResNet-50 |  | 24 | 63.8 | 85.3”
- Rotation _[unlocated]_
  > p. 7: “Rotation | RevNet-50 (4×) |  | 86 | 55.4 | -”
- BigBiGAN _[unlocated]_
  > p. 7: “BigBiGAN | RevNet-50 (4×) |  | 86 | 61.3 | 81.9”
- AMDIM _[unlocated]_
  > p. 7: “AMDIM | Custom-ResNet |  | 626 | 68.1 | -”
- CMC _[unlocated]_
  > p. 7: “CMC | ResNet-50 (2×) |  | 188 | 68.4 | 88.2”
- Supervised baseline _[unlocated]_
  > p. 7: “Supervised baseline | ResNet-50 | 48.4 | 80.4”
- Pseudo-label _[unlocated]_
  > p. 7: “Pseudo-label | ResNet-50 | 51.6 | 82.4”
- VAT+Entropy Min. _[unlocated]_
  > p. 7: “VAT+Entropy Min. | ResNet-50 | 47.0 | 83.4”
- UDA (w. RandAug) _[unlocated]_
  > p. 7: “UDA (w. RandAug) | ResNet-50 | - | 88.5”
- FixMatch (w. RandAug) _[unlocated]_
  > p. 7: “FixMatch (w. RandAug) | ResNet-50 | - | 89.1”
- S4L (Rot+VAT+En. M.) _[unlocated]_
  > p. 7: “S4L (Rot+VAT+En. M.) | ResNet-50 (4×) | - | 91.2”
- InstDisc _[unlocated]_
  > p. 7: “InstDisc | ResNet-50 | 39.2 | 77.4”

## Metrics

- Top 1 accuracy _[unlocated]_
  > p. 7: “Method | Architecture |  | Param (M) | Top 1 | Top 5”
- Top 5 accuracy _[unlocated]_
  > p. 7: “Method | Architecture |  | Param (M) | Top 1 | Top 5”
- Mean per-class accuracy _[verified]_
  > p. 16: “We follow the evaluation protocols in the papers introducing these datasets, i.e., we report top-1 accuracy for Food-101, CIFAR-10, CIFAR-100, Birdsnap, SUN397, Stanford Cars, and DTD; mean per-class accuracy for FGVC Aircraft, Oxford-IIIT Pets, Caltech-101, and Oxford 102 Flowers; and the 11-point mAP metric as defined in Everingham et al. (2010) for PASCAL VOC 2007.”
- 11-point mAP metric _[verified]_
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
- warmup epochs (pre-training): 10 _[verified]_
  > p. 3: “Furthermore, we use linear warmup for the first 10 epochs, and decay the learning rate with the cosine decay schedule without restarts (Loshchilov & Hutter, 2016).”
- batch size (fine-tuning): 4096 _[verified]_
  > p. 15: “Fine-tuning Procedure We fine-tune using the Nesterov momentum optimizer with a batch size of 4096, momentum of 0.9, and a learning rate of 0.8 (following LearningRate = 0.05 × BatchSize/256) without warmup.”
- optimizer (fine-tuning): Nesterov momentum _[verified]_
  > p. 15: “Fine-tuning Procedure We fine-tune using the Nesterov momentum optimizer with a batch size of 4096, momentum of 0.9, and a learning rate of 0.8 (following LearningRate = 0.05 × BatchSize/256) without warmup.”
- momentum (fine-tuning): 0.9 _[verified]_
  > p. 15: “Fine-tuning Procedure We fine-tune using the Nesterov momentum optimizer with a batch size of 4096, momentum of 0.9, and a learning rate of 0.8 (following LearningRate = 0.05 × BatchSize/256) without warmup.”
- learning rate (fine-tuning): 0.8 _[verified]_
  > p. 15: “Fine-tuning Procedure We fine-tune using the Nesterov momentum optimizer with a batch size of 4096, momentum of 0.9, and a learning rate of 0.8 (following LearningRate = 0.05 × BatchSize/256) without warmup.”
- epochs (fine-tuning (1% labeled data)): 60 _[verified]_
  > p. 15: “For 1% labeled data we fine-tune for 60 epochs, and for 10% labeled data we fine-tune for 30 epochs.”
- epochs (fine-tuning (10% labeled data)): 30 _[verified]_
  > p. 15: “For 1% labeled data we fine-tune for 60 epochs, and for 10% labeled data we fine-tune for 30 epochs.”

## Compute

- Cloud TPUs using 32 to 128 cores _[verified]_
  > p. 3: “We train our model with Cloud TPUs, using 32 to 128 cores depending on the batch size.”
- 1.5 hours using 128 TPU v3 cores for ResNet-50 with batch size 4096 for 100 epochs _[verified]_
  > p. 3: “2 With 128 TPU v3 cores, it takes ∼1.5 hours to train our ResNet-50 with a batch size of 4096 for 100 epochs.”

## Claims

- A linear classifier trained on SimCLR representations achieves 76.5 percent top-1 accuracy on ImageNet. _[verified]_
  > p. 1: “A linear classifier trained on self-supervised representations learned by Sim-CLR achieves 76.5% top-1 accuracy, which is a 7% relative improvement over previous state-of-the-art, matching the performance of a supervised ResNet-50.”
- Fine-tuning on 1 percent of labels achieves 85.8 percent top-5 accuracy. _[verified]_
  > p. 1: “When fine-tuned on only 1% of the labels, we achieve 85.8% top-5 accuracy, outperforming AlexNet with 100× fewer labels.”
- Composition of data augmentations plays a critical role in defining effective predictive tasks. _[verified]_
  > p. 1: “We show that (1) composition of data augmentations plays a critical role in defining effective predictive tasks, (2) introducing a learnable nonlinear transformation between the representation and the contrastive loss substantially improves the quality of the learned representations, and (3) contrastive learning benefits from larger batch sizes and more training steps compared to supervised learning.”

## Code

- https://github.com/google-research/simclr _[verified]_
  > p. 1: “1 Code available at https://github.com/google-research/simclr.”


## 2010.11929

# AN IMAGE IS WORTH 16X16 WORDS: TRANSFORMERS FOR IMAGE RECOGNITION AT SCALE

Alexey Dosovitskiy, Lucas Beyer, Alexander Kolesnikov, Dirk Weissenborn, Xiaohua Zhai, Thomas Unterthiner, Mostafa Dehghani, Matthias Minderer, Georg Heigold, Sylvain Gelly, Jakob Uszkoreit, Neil Houlsby
2021 · arXiv:2010.11929v2[cs.CV]

## Problem

- Applications of the Transformer architecture to computer vision remain limited compared to natural language processing. _[verified]_
  > p. 1: “While the Transformer architecture has become the de-facto standard for natural language processing tasks, its applications to computer vision remain limited.”

## Task

- Image classification _[verified]_
  > p. 1: “We show that this reliance on CNNs is not necessary and a pure transformer applied directly to sequences of image patches can perform very well on image classification tasks.”

## Method

- The model follows the original Transformer design closely, mapping flattened image patches to a constant latent dimension with a trainable linear projection. _[verified]_
  > p. 3: “The Transformer uses constant latent vector size D through all of its layers, so we flatten the patches and map to D dimensions with a trainable linear projection (Eq. 1).”
- A learnable classification token is prepended to the patch embeddings, and a classification head is attached to this token's output state during both pre-training and fine-tuning. _[verified]_
  > p. 3: “Both during pre-training and fine-tuning, a classification head is attached to z 0 L .”
- Standard learnable 1D position embeddings are added to the patch embeddings to retain positional information. _[verified]_
  > p. 3: “We use standard learnable 1D position embeddings, since we have not observed significant performance gains from using more advanced 2D-aware position embeddings (Appendix D.4).”
- The Transformer encoder consists of alternating layers of multiheaded self-attention and MLP blocks, with layernorm applied before and residual connections applied after every block. _[verified]_
  > p. 3: “The Transformer encoder (Vaswani et al., 2017) consists of alternating layers of multiheaded selfattention (MSA, see Appendix A) and MLP blocks (Eq. 2, 3).”
- The model is typically pre-trained on large datasets and then fine-tuned on smaller downstream tasks by replacing the prediction head. _[verified]_
  > p. 4: “Typically, we pre-train ViT on large datasets, and fine-tune to (smaller) downstream tasks.”

## Datasets

- ImageNet (original validation labels and cleaned-up ReaL labels, 1.3M images) _[verified]_
  > p. 4: “To explore model scalability, we use the ILSVRC-2012 ImageNet dataset with 1k classes and 1.3M images (we refer to it as ImageNet in what follows), its superset ImageNet-21k with 21k classes and 14M images (Deng et al., 2009), and JFT (Sun et al., 2017) with 18k classes and 303M high-resolution images.”
- JFT (303M high-resolution images) _[verified]_
  > p. 4: “To explore model scalability, we use the ILSVRC-2012 ImageNet dataset with 1k classes and 1.3M images (we refer to it as ImageNet in what follows), its superset ImageNet-21k with 21k classes and 14M images (Deng et al., 2009), and JFT (Sun et al., 2017) with 18k classes and 303M high-resolution images.”
- CIFAR-10/100 _[verified]_
  > p. 4: “We transfer the models trained on these dataset to several benchmark tasks: ImageNet on the original validation labels and the cleaned-up ReaL labels (Beyer et al., 2020), CIFAR-10/100 (Krizhevsky, 2009), Oxford-IIIT Pets (Parkhi et al., 2012), and Oxford Flowers-102 (Nilsback & Zisserman, 2008).”
- Oxford-IIIT Pets _[verified]_
  > p. 4: “We transfer the models trained on these dataset to several benchmark tasks: ImageNet on the original validation labels and the cleaned-up ReaL labels (Beyer et al., 2020), CIFAR-10/100 (Krizhevsky, 2009), Oxford-IIIT Pets (Parkhi et al., 2012), and Oxford Flowers-102 (Nilsback & Zisserman, 2008).”
- Oxford Flowers-102 _[verified]_
  > p. 4: “We transfer the models trained on these dataset to several benchmark tasks: ImageNet on the original validation labels and the cleaned-up ReaL labels (Beyer et al., 2020), CIFAR-10/100 (Krizhevsky, 2009), Oxford-IIIT Pets (Parkhi et al., 2012), and Oxford Flowers-102 (Nilsback & Zisserman, 2008).”
- VTAB (1 000 training examples per task) _[verified]_
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

- few-shot or fine-tuning accuracy _[verified]_
  > p. 5: “We report results on downstream datasets either through few-shot or fine-tuning accuracy.”
- top-5 accuracy and top-1 accuracy _[verified]_
  > p. 20: “We also evaluate our flagship ViT-H/14 model on the ObjectNet benchmark following the evaluation setup in Kolesnikov et al. (2020), resulting in 82.1% top-5 accuracy and 61.7% top-1 accuracy.”

## Hyperparameters

- optimizer (pre-training): Adam _[verified]_
  > p. 5: “We train all models, including ResNets, using Adam (Kingma & Ba, 2015) with β 1 = 0.9, β 2 = 0.999, a batch size of 4096 and apply a high weight decay of 0.1, which we found to be useful for transfer of all models (Appendix D.1 shows that, in contrast to common practices, Adam works slightly better than SGD for ResNets in our setting).”
- beta 1 (pre-training): 0.9 _[verified]_
  > p. 5: “We train all models, including ResNets, using Adam (Kingma & Ba, 2015) with β 1 = 0.9, β 2 = 0.999, a batch size of 4096 and apply a high weight decay of 0.1, which we found to be useful for transfer of all models (Appendix D.1 shows that, in contrast to common practices, Adam works slightly better than SGD for ResNets in our setting).”
- beta 2 (pre-training): 0.999 _[verified]_
  > p. 5: “We train all models, including ResNets, using Adam (Kingma & Ba, 2015) with β 1 = 0.9, β 2 = 0.999, a batch size of 4096 and apply a high weight decay of 0.1, which we found to be useful for transfer of all models (Appendix D.1 shows that, in contrast to common practices, Adam works slightly better than SGD for ResNets in our setting).”
- batch size (pre-training): 4096 _[verified]_
  > p. 5: “We train all models, including ResNets, using Adam (Kingma & Ba, 2015) with β 1 = 0.9, β 2 = 0.999, a batch size of 4096 and apply a high weight decay of 0.1, which we found to be useful for transfer of all models (Appendix D.1 shows that, in contrast to common practices, Adam works slightly better than SGD for ResNets in our setting).”
- weight decay (pre-training): 0.1 _[verified]_
  > p. 5: “We train all models, including ResNets, using Adam (Kingma & Ba, 2015) with β 1 = 0.9, β 2 = 0.999, a batch size of 4096 and apply a high weight decay of 0.1, which we found to be useful for transfer of all models (Appendix D.1 shows that, in contrast to common practices, Adam works slightly better than SGD for ResNets in our setting).”
- optimizer (fine-tuning): SGD with momentum _[verified]_
  > p. 5: “For fine-tuning we use SGD with momentum, batch size 512, for all models, see Appendix B.1.1.”
- batch size (fine-tuning): 512 _[verified]_
  > p. 5: “For fine-tuning we use SGD with momentum, batch size 512, for all models, see Appendix B.1.1.”
- momentum (fine-tuning): 0.9 _[verified]_
  > p. 13: “We fine-tune all ViT models using SGD with a momentum of 0.9.”
- Polyak averaging factor (fine-tuning): 0.9999 _[verified]_
  > p. 5: “For ImageNet results in Table 2, we fine-tuned at higher resolution: 512 for ViT-L/16 and 518 for ViT-H/14, and also used Polyak & Juditsky (1992) averaging with a factor of 0.9999 (Ramachandran et al., 2019;Wang et al., 2020b).”

## Compute

- all models trained on TPUv3 hardware _[verified]_
  > p. 5: “All models were trained on TPUv3 hardware, and we report the number of TPUv3-core-days taken to pre-train each of them, that is, the number of TPU v3 cores (2 per chip) used for training multiplied by the training time in days.”
- ViT-L/16 pre-trained on ImageNet-21k trained using standard cloud TPUv3 with 8 cores in approximately 30 days _[verified]_
  > p. 6: “Finally, the ViT-L/16 model pre-trained on the public ImageNet-21k dataset performs well on most datasets too, while taking fewer resources to pre-train: it could be trained using a standard cloud TPUv3 with 8 cores in approximately 30 days.”

## Seeds and runs

- results averaged over three fine-tuning runs _[verified]_
  > p. 6: “We report mean and standard deviation of the accuracies, averaged over three fine-tuning runs.Vision Transformer models pre-trained on the JFT-300M dataset outperform ResNet-based baselines on all datasets, while taking substantially less”

## Ablations

- evaluation of different ways of encoding positional information on ViT-B/16 _[verified]_
  > p. 18: “Table 8 summarizes the results from this ablation study on a ViT-B/16 model.”

## Claims

- Vision Transformer attains excellent results compared to state-of-the-art convolutional networks while requiring substantially fewer computational resources to train. _[verified]_
  > p. 1: “When pre-trained on large amounts of data and transferred to multiple mid-sized or small image recognition benchmarks (ImageNet, CIFAR-100, VTAB, etc.), Vision Transformer (ViT) attains excellent results compared to state-of-the-art convolutional networks while requiring substantially fewer computational resources to train.”
- The best model reaches high accuracy on ImageNet, ImageNet-ReaL, CIFAR-100, and the VTAB suite. _[verified]_
  > p. 2: “In particular, the best model reaches the accuracy of 88.55% on ImageNet, 90.72% on ImageNet-ReaL, 94.55% on CIFAR-100, and 77.63% on the VTAB suite of 19 tasks.”

## Limitations

- Gap between self-supervised and large-scale supervised pre-training _[verified]_
  > p. 9: “Our initial experiments show improvement from self-supervised pre-training, but there is still large gap between self-supervised and large-scale supervised pretraining.”

## Future work

- Apply ViT to other computer vision tasks like detection and segmentation _[verified]_
  > p. 9: “One is to apply ViT to other computer vision tasks, such as detection and segmentation.”
- Continue exploring self-supervised pre-training methods _[verified]_
  > p. 9: “Another challenge is to continue exploring selfsupervised pre-training methods.”
- Scale ViT further to improve performance _[verified]_
  > p. 9: “Finally, further scaling of ViT would likely lead to improved performance.”

## Code

- https://github.com/google-research/vision_transformer _[verified]_
  > p. 1: “Fine-tuning code and pre-trained models are available at https://github.com/ google-research/vision_transformer”
- https://github.com/csrhddlam/axial-deeplab.In _[verified]_
  > p. 19: “Our implementation is based on the open-sourced PyTorch implementation in https://github.com/ csrhddlam/axial-deeplab.In our experiments, we reproduced the scores reported in(Wang et al., 2020b) in terms of accuracy, however, our implementation, similar to the open-source implementation, is very slow on TPUs.Therefore, we were not able to use it for extensive large-scale experiments.These may be unlocked by a carefully optimized implementation.”


## 2106.09685

# LORA: LOW-RANK ADAPTATION OF LARGE LAN-GUAGE MODELS

Edward Hu, Yelong Shen, Phillip Wallis, Zeyuan Allen-Zhu, Yuanzhi Li, Shean Wang, Lu Wang, Weizhu Chen
2021 · arXiv:2106.09685v2[cs.CL]

## Problem

- Full fine-tuning of extremely large language models like GPT-3 175B is prohibitively expensive because it requires retraining all model parameters. _[verified]_
  > p. 1: “Using GPT-3 175B as an example -deploying independent instances of fine-tuned models, each with 175B parameters, is prohibitively expensive.”
- Existing parameter-efficient adaptation methods often introduce inference latency or reduce the usable sequence length, while failing to match full fine-tuning performance. _[unsupported]_
  > p. 2: “More importantly, these method often fail to match the fine-tuning baselines, posing a trade-off between efficiency and model quality.”

## Task

- Natural language processing model pretraining and adaptation to downstream tasks. _[verified]_
  > p. 1: “An important paradigm of natural language processing consists of large-scale pretraining on general domain data and adaptation to particular tasks or domains.”

## Contributions

- We propose Low-Rank Adaptation (LoRA), which freezes pretrained weights and injects trainable rank decomposition matrices into Transformer layers. _[verified]_
  > p. 1: “We propose Low-Rank Adaptation, or LoRA, which freezes the pretrained model weights and injects trainable rank decomposition matrices into each layer of the Transformer architecture, greatly reducing the number of trainable parameters for downstream tasks.”
- We provide an empirical investigation into rank-deficiency in language model adaptation to explain LoRA's efficacy. _[verified]_
  > p. 1: “We also provide an empirical investigation into rank-deficiency in language model adaptation, which sheds light on the efficacy of LoRA.”
- We release a software package and implementations with model checkpoints for RoBERTa, DeBERTa, and GPT-2. _[verified]_
  > p. 1: “We release a package that facilitates the integration of LoRA with PyTorch models and provide our implementations and model checkpoints for RoBERTa, DeBERTa, and GPT-2 at https://github.com/microsoft/LoRA.”

## Method

- Adapting pre-trained autoregressive language models to downstream tasks by freezing original weights and parameterizing weight updates with a low-rank decomposition. _[verified]_
  > p. 4: “For a pre-trained weight matrix W 0 ∈ R d×k , we constrain its update by representing the latter with a low-rank decomposition W 0 + ∆W = W 0 + BA, where B ∈ R d×r , A ∈ R r×k , and the rank r min(d, k).”
- Using random Gaussian initialization for matrix A and zero initialization for matrix B so that the update term starts at zero. _[verified]_
  > p. 4: “We use a random Gaussian initialization for A and zero for B, so ∆W = BA is zero at the beginning of training.”
- Limiting the application of low-rank adaptation specifically to the attention weights in the Transformer architecture while freezing the MLP modules. _[verified]_
  > p. 5: “We limit our study to only adapting the attention weights for downstream tasks and freeze the MLP modules (so they are not trained in downstream tasks) both for simplicity and parameter-efficiency.”

## Novelty

- Using a low-rank representation to encode weight updates (Delta W) that is compute- and memory-efficient compared to full fine-tuning. _[verified]_
  > p. 3: “In the subsequent sections, we propose to use a low-rank representation to encode ∆Φ that is both compute-and memory-efficient.”
- Guaranteeing no additional inference latency by allowing trained low-rank matrices to be explicitly computed and stored with the original weights. _[verified]_
  > p. 4: “Critically, this guarantees that we do not introduce any additional latency during inference compared to a fine-tuned model by construction.”

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
- Prefix-embedding tuning _[verified]_
  > p. 6: “Prefix-embedding tuning (PreEmbed) inserts special tokens among the input tokens.”
- Prefix-layer tuning _[verified]_
  > p. 6: “Prefix-layer tuning (PreLayer) is an extension to prefix-embedding tuning.”
- Adapter H _[verified]_
  > p. 6: “We call this original design Adapter H .”
- Adapter L _[verified]_
  > p. 6: “We call it Adapter L .”
- Adapter P _[verified]_
  > p. 6: “This is very similar to another deign proposed in Pfeiffer et al. (2021), which we call Adapter P .”
- AdapterDrop _[verified]_
  > p. 6: “We also include another baseline call AdapterDrop (Rücklé et al., 2020) which drops some adapter layers for greater efficiency (Adapter D ).”

## Metrics

- BLEU _[unsupported]_
  > p. 7: “For all metrics, higher is better.LoRA outperforms several baselines with comparable or fewer trainable parameters.Confidence intervals are shown for experiments we ran.* indicates numbers published in prior works.”
- NIST _[unsupported]_
  > p. 7: “For all metrics, higher is better.LoRA outperforms several baselines with comparable or fewer trainable parameters.Confidence intervals are shown for experiments we ran.* indicates numbers published in prior works.”
- MET _[unsupported]_
  > p. 7: “For all metrics, higher is better.LoRA outperforms several baselines with comparable or fewer trainable parameters.Confidence intervals are shown for experiments we ran.* indicates numbers published in prior works.”
- ROUGE-1, ROUGE-2, ROUGE-L _[verified]_
  > p. 7: “For all metrics, higher is better.LoRA outperforms several baselines with comparable or fewer trainable parameters.Confidence intervals are shown for experiments we ran.* indicates numbers published in prior works.”
  > p. 8: “We report the logical form validation accuracy on WikiSQL, validation accuracy on MultiNLI-matched, and Rouge-1/2/L on SAMSum.”
- CIDEr _[unsupported]_
  > p. 7: “For all metrics, higher is better.LoRA outperforms several baselines with comparable or fewer trainable parameters.Confidence intervals are shown for experiments we ran.* indicates numbers published in prior works.”
- Logical form validation accuracy _[verified]_
  > p. 8: “We report the logical form validation accuracy on WikiSQL, validation accuracy on MultiNLI-matched, and Rouge-1/2/L on SAMSum.”
- Validation accuracy _[verified]_
  > p. 8: “We report the logical form validation accuracy on WikiSQL, validation accuracy on MultiNLI-matched, and Rouge-1/2/L on SAMSum.”

## Hyperparameters

- sequence length: 128 _[verified]_
  > p. 7: “First, we use the same batch size for all tasks and use a sequence length of 128 to match the adapter baselines.”

## Compute

- NVIDIA Quadro RTX8000 used for latency experiments _[verified]_
  > p. 4: “We use an NVIDIA Quadro RTX8000.”
- NVIDIA Tesla V100 used for all experiments _[verified]_
  > p. 5: “We use NVIDIA Tesla V100 for all experiments.”

## Seeds and runs

- Latency averaged over 100 trials _[verified]_
  > p. 4: “Table 1: Infernece latency of a single forward pass in GPT-2 medium measured in milliseconds, averaged over 100 trials.We use an NVIDIA Quadro RTX8000."|Θ|" denotes the number of trainable parameters in adapter layers.Adapter L and Adapter H are two variants of adapter tuning, which we describe in S”
- Standard deviation reported across random seeds _[verified]_
  > p. 10: “We find the standard deviation across random seeds to be consistent for a given dataset, which we report in the first column.”

## Ablations

- Ablation of which subset of weight matrices in self-attention to adapt _[verified]_
  > p. 10: “Table 5: Validation accuracy on WikiSQL and MultiNLI after applying LoRA to different types of attention weights in GPT-3, given the same number of trainable parameters. Adapting both W q and W v gives the best performance overall. We find the standard deviation across random seeds to be consistent for a given dataset, which we report in the first column.”
- Ablation of rank r on model performance _[verified]_
  > p. 10: “We turn our attention to the effect of rank r on model performance.”

## Claims

- LoRA can reduce the number of trainable parameters by 10,000 times and GPU memory requirements by 3 times compared to fine-tuned GPT-3 175B. _[verified]_
  > p. 1: “Compared to GPT-3 175B fine-tuned with Adam, LoRA can reduce the number of trainable parameters by 10,000 times and the GPU memory requirement by 3 times.”
- LoRA performs on-par or better than fine-tuning in model quality across multiple models without adding inference latency. _[verified]_
  > p. 1: “LoRA performs on-par or better than finetuning in model quality on RoBERTa, DeBERTa, GPT-2, and GPT-3, despite having fewer trainable parameters, a higher training throughput, and, unlike adapters, no additional inference latency.”

## Limitations

- A small rank r may not be effective for every task or dataset, such as when the downstream task uses a completely different language than pre-training. _[verified]_
  > p. 10: “However, we do not expect a small r to work for every task or dataset.Consider the following thought experiment: if the downstream task were in a different language than the one used for pre-training, retraining the entire model (similar to LoRA with r = d model ) could certainly outperform LoRA with a small r.”

## Future work

- Combining LoRA with other efficient adaptation methods to potentially achieve orthogonal improvements. _[verified]_
  > p. 12: “1) LoRA can be combined with other efficient adaptation methods, potentially providing orthogonal improvement.”
- Investigating the mechanisms behind fine-tuning and LoRA regarding how pre-training features transform for downstream tasks. _[verified]_
  > p. 12: “2) The mechanism behind fine-tuning or LoRA is far from clear -how are features learned during pre-training transformed to do well on downstream tasks?”
- Finding more principled ways to select the weight matrices for applying LoRA instead of relying on heuristics. _[verified]_
  > p. 13: “3) We mostly depend on heuristics to select the weight matrices to apply LoRA to.”
- Exploring whether the rank-deficiency of Delta W implies that W could also be rank-deficient as a source of inspiration. _[verified]_
  > p. 13: “4) Finally, the rank-deficiency of ∆W suggests that W could be rank-deficient as well, which can also be a source of inspiration for future works.”

## Code

- https://github.com/microsoft/LoRA _[verified]_
  > p. 1: “We release a package that facilitates the integration of LoRA with PyTorch models and provide our implementations and model checkpoints for RoBERTa, DeBERTa, and GPT-2 at https://github.com/microsoft/LoRA. * Equal contribution. 0”

