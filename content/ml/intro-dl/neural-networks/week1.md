# Week 1 — Neural Networks and Deep Learning

**Notations** ([source](https://d3c33hcgiwev3.cloudfront.net/_106ac679d8102f2bee614cc67e9e5212_deep-learning-notation.pdf?Expires=1620000000&Signature=fe~qRZvLw6SimSF12-T5HtrkfXkSimV5guX598PhKSOqjhkoGAKMFHrbJThtMzFJl0ZzDITzj43relXQnxoGzWr-Y2r~4otSFE2hCJv8xPwUaQEovPt4Fk2p~mS9ff5SZ2iaZFnbwaH4p9guk1sID82Pcs691QWZrx0EIezXYrM_&Key-Pair-Id=APKAJLTNE6QMUY6HBC5A)) :

![](/assets/images/ml/intro_dl/neural_networks/0001.jpg){ loading=lazy }

![](/assets/images/ml/intro_dl/neural_networks/0002.jpg){ loading=lazy }

<iframe width="1478" height="400" src="https://www.youtube.com/embed/CS4cs9xVecg" title="Welcome (Deep Learning Specialization C1W1L01)" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

<iframe width="1478" height="400" src="https://www.youtube.com/embed/aircAruvnKk" title="But what is a neural network? | Chapter 1, Deep learning" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

## Week 1 — Introduction to Deep Learning

May 1, 2021

### Welcome

- AI (Artificial Intelligence) is the new Electricity to bring about a change and a new era
- Parts of this course:
  - Neural Networks and Deep Learning. → Recognizing cats
  - Improving Deep Neural Networks: Hyperparmeter tuning, Regularization and Optimization
  - Structuring your Machine Learning Project → Best Practices for project
  - Convolutional Neural Networks
  - Natural Language Processing: Building sequence models

### Introduction to Deep Learning

!!! success "What Deep Learning/ML is good for"

    1. **Problems with long lists of rules**: When the traditional approach fails, machine learning/deep leanring may help

    2. **Continually changing environments**: Deep Learning can adapt ('lear') to new scenarios

    3. **Discovering insights withing large collections of data**: Imaging trying to hand-craft rules for what 101 different kinds of food look like?

!!! warning "Where Deep Learning is (typically) not good?"

    1. **When you need explainability**: the patterns learned by a deep learnign model are *typically* uninterpretable by human
    2. **When the traditional approach is a better option**: if you can accomplish what you need with a simple rule-based system.
    3. **When errors are unacceptable**: since the outputs of deep learning aren't always predictable.<mark class="v"> The outputs are probabilistic and not deterministic.</mark>
    4. **When you don't have much data**: deep learning models usually require a fairly large amount of data to produce great results.

### What is neural networks?

Neural networks are created by structuring layers, with each layer consisting of "neurons" which get activated depending on its activation function and the input.

### Supervised Learning with Neural Networks

Supervised learning refers to problems when we have inputs as well as labels (outputs) to predict using machine learning techniques. Then the models figure out the mapping from inputs to output.

The data can be:

- Structured Data (tables)
- Unstructured Data (images, audio, etc.)

### Why is Deep Learning taking off?

Three reasons:

- Backpropagation algorithm
- Glorot and He initialization
- ReLU (Rectified Linear Unit) activation function

Other reasons:

- Data
- Computation power
- Algorithms

The scale at which we creating data is also important, as neural networks performance don't stagnant unlike traditional machine learning algorithms

In this course <mark class="y">$m$ denotes no of training examples.</mark>

### About this Course

- Week 1: Introduction
- Week 2: Basics of Neural Network programming
- Week 3: One hidden layer Neural Networks
- Week 4: Deep Neural Networks

!!! info

    Any image used here for illustration if not mentioned, is attributed to Andrew Ng's lecture slides.
