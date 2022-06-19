---
title: "Week 1 — Hyperparameter tuning: searching for the best architecture"
description: ""
lead: ""
date: 2022-03-26T14:41:39+01:00
lastmod: 2022-03-26T14:41:39+01:00
draft: false
images: []
type: docs
menu:
  mle-for-production:
    parent: "ml-modeling-pipeline"
weight: 100
toc: true
---

{{< alert title="Overview">}}

This course is focuses on tools and techniques to effectively manage modeling resources and best serve batch and real-time inference requests.

- Effective search strategies for the best model that will scale for various serving needs
- Constraining model complexity and hardware requirements
- Optimize and manage compute storage and IO needs
- We'll be going through TensorFlow Model Analysis (TFMA)

{{< figure src="/images/ml/mle_for_production/ml_modeling_pipeline_in_production/tfma.png" >}}

{{< /alert >}}

## Neural Architecture Search

- Neural architecture search (NAS) is a technique for automating the design of artificial neural networks
- It helps finding the optimal architecture
- This is a search over a huge space
- AutoML is an algorithm to automate this search

### Types of parameters in ML models

- Trainable parameters
    - Learned by the algorithm during training
    - e.g., weights of a neural network
- Hyperparameters
    - Set before launching the learning process
    - not updated in each training step
    
    Hyperparameters are of two types:
    
    1. ***Model hyperparameters*** which influence model selection such as the number and width of hidden layers
    2. ***Algorithm hyperparameters*** which influence the speed and quality of the learning algorithm such as the learning rate for Stochastic Gradient Descent (SGD) and the number of nearest neighbors for a k Nearest Neighbors (KNN) classifier.
    - e.g., learning rate or the number of units in a dense layer

### Manual hyperparameter tuning is not scalable

<mark class="y">The process of finding the optimal set of hyperparameters is called *hyperparameter tuning* or *hypertuning*.</mark>

- Hyperparameters can be numerous even for small models
- e.g., shallow DNN
    - Architecture choices
    - activation functions
    - Weight initialization strategy
    - Optimization hyperparameters such as learning rate, stop condition
- Tuning them manually can be a real brain teaser
- helps boost model performance.

### Automating hyperparameter tuning with Keras Tuner

- Automation is key.
- Keras Tunes:
    - Hyperparameter tuning with TensorFlow 2.0
    - Many methods available>

## Keras Autotuner Demo

- Do the model need more or less hidden units to perform well?
- How does model size affect the convergence spped?
- Is there any trade off between convergence speed, model size and accuracy?
- Search automation is the natural path to take
- keras tuner built in search functionality will help!
- Keras Tuner has four tuners available with built-in strategies:
    - `RandomSearch`
    - `Hyperband`
    - `BayesianOptimization`
    - `Sklearn`

```python
import keras_tuner as kt


def model_builder(hp):
  '''
  Builds the model and sets up the hyperparameters to tune.
  Args:
    hp - Keras tuner object
  Returns:
    model with hyperparameters to tune
  '''
  # The model you set up for hypertuning is called a hypermodel.
  model = keras.Sequential()
  model.add(keras.layers.Flatten(input_shape=(28, 28)))

  hp_units = hp.Int('units', min_value=16, max_value=512, step=16)
  model.add(keras.layers.Dense(units=hp_units, activation='relu'))
  model.add(tf.keras.layers.Dropout(0.2))
  model.add(keras.layer.Dense(10))

  model.compile(
    optimizer='adam', 
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
  return model

# Keras tuner support multiple strategies, one we're using is Hyperband strategy
# Keras Tuner has four tuners available with built-in strategies - RandomSearch, Hyperband, BayesianOptimization, and Sklearn
tuner = kt.Hyperband(
  model_builder,
  objective='val_accuracy',
  max_epochs=10, 
  factor=3,
  directory='my_dir',
  project_name='intro_to_kt')

# callback configuration
stop_early = tf.keras.callbacks.EarlyStopping(
  monior='val_loss', patience=5)

tuner.search(
  X_train, y_train,
  epochs=50,
  validation_split=0.2,
  callbacks=[stop_early])
```

### Search Output
{{< figure src="/images/ml/mle_for_production/ml_modeling_pipeline_in_production/search_output.png" >}}

Then, we can set the hidden units to be `48`

```python
best_hps=tuner.get_best_hyperparameters()[0]
h_model = tuner.hypermodel.build(best_hps)
h_model.fit(X_train, y_train, epochs=NUM_EPOCHS, validation_split=0.2)
```

## AutoML — Intro to AutoML (Automated Machine Learning)

It is aimed at developers with very little experience in ML to make use of ML model and techniques by trying to automate entire workflow end-to-end.

{{< figure src="/images/ml/mle_for_production/ml_modeling_pipeline_in_production/automl.png" >}}

### Neural Architecture Search (❤️ of AutoML)

The process of automating architecture engineering is strictly called NAS.

Three main parts:

- Search space: Defines the range of architecture which can be represented.
- Search strategy: Defines how we explore the search space.
- Performance estimation strategy: Helps measure the comparing the performance of various architectures.

{{< figure src="/images/ml/mle_for_production/ml_modeling_pipeline_in_production/nas1.png" >}}

{{< figure src="/images/ml/mle_for_production/ml_modeling_pipeline_in_production/nas2.png" >}}

{{< figure src="/images/ml/mle_for_production/ml_modeling_pipeline_in_production/real_world_example.png" >}}

## Understanding Search Spaces

### Types of Search Space:

- Macro
- Micro

Node: A node is a layer in a neural network. 

An arrow from layer $\text{L}_i$ to $\text{L}_j$ indicates the layer $\text{L}_j$receives the output of $\text{L}_i$as input.

{{< figure src="/images/ml/mle_for_production/ml_modeling_pipeline_in_production/types_of_search_spaces.png" >}}

### Macro Architecture Search Space

<mark class="y">A macro search space contains the individual layers and connection types of neural network.</mark>

- A NAS searches within that space for the best model,<mark class="y"> building the model layer by layer.</mark>

{{< figure src="/images/ml/mle_for_production/ml_modeling_pipeline_in_production/macro_architecture_search_space.png" >}}

In a chain-structured Neural Network Architecture (NNA), space is parametrized as:

- The operation every layer can execute
- Hyperparameters associated with the operation
- A number of n sequentially fully-connected layers

### Micro Architecture Search Space

<mark class="y">In a micro search space, NAS build a neural network from cells where each cell is a smaller network.</mark>

- Cells are stacked to produce the final network.

{{< figure src="/images/ml/mle_for_production/ml_modeling_pipeline_in_production/micro_architecture_search_space.png.png" >}}

## Search Strategies

- Find the architecture that produces the best performance

A few search strategies

1. Grid Search
2. Random Search
3. Bayesian Optimization
4. Evolutionary Algorithms
5. Reinforcement Learning

### Grid Search & Random Search

Grid Search

- Exhaustive search approach on fixed grid values

Random Search:

- Select the next options randomly within the search space.

Both Suitable for small search space.

Both quickly fail with growing size of search space

### Bayesian Optimization

- Assumes that a specific probability distribution, is underlying the performance.
- Tested architectures constrain the probability distribution and guide the selection of the next option.
- This way, promising architectures can be stochastically determined and tested.

### Evolutionary Methods

{{< figure src="/images/ml/mle_for_production/ml_modeling_pipeline_in_production/evolutionary_methods.png" >}}

### Reinforcement Learning

- Agents goal is to maximise a reward.
- The available options are selected from the search space.
- The performance estimation strategy determines the reward

### Reinforcement Learning for NAS

- A NN can also be specified by a variable length string.
- Hence RNN can be used generate that string, referred as controller.
- After training model on real data called, child network, we measure the accuracy on validation set.
- This accuracy then determines the reinforcement learning reward.

{{< figure src="/images/ml/mle_for_production/ml_modeling_pipeline_in_production/reinforcement_learning_for_nas.png" >}}

{{< panel title="Neural Architecture Search" >}}

  ## Neural Architecture Search

If you wish to dive more deeply into neural architecture search , feel free to check out these optional references. You won’t have to read these to complete this week’s practice quizzes.

- [Neural Architecture Search](https://arxiv.org/pdf/1808.05377.pdf)
- [Bayesian Optimization](https://distill.pub/2020/bayesian-optimization/)
- [Neural Architecture Search with Reinforcement Learning](https://arxiv.org/pdf/1611.01578.pdf)
- [Progressive Neural Architecture Search](https://arxiv.org/pdf/1712.00559.pdf)
- [Network Morphism](https://arxiv.org/abs/1603.01670)
{{< /panel >}}

## Measuring AutoML Efficacy

### Performance Estimation Strategy

The search strategies in neural architecture search need to estimate the performance of generated architectures, so that they can in turn generate even better performing architectures.

The simplest approach is to measure validation accuracy...

{{< figure src="/images/ml/mle_for_production/ml_modeling_pipeline_in_production/performance_estimation_strategy.png" >}}

### Strategies to Reduce the Cost

1. Lower fidelity estimates
2. Learning Curve Extrapolation
3. Weight Inheritance/ Network Morphisms

### Lower fidelity estiamtes

Lower fidelity or precision estimates <mark class="y">try to reduce training time by reframing the problem make is easier to solve.</mark>

This is done either by:

- Training on subset of data
- lower resolution images
- Fewer filters per layer and fewer cells

{{< figure src="/images/ml/mle_for_production/ml_modeling_pipeline_in_production/lower_fidelity_estimates.png" >}}

### Learning Curve Extrapolation

Based on the assumption that you have mechanisms to <mark class="y">predict the learning curve reliably.</mark>

- Extrapolates based on initial learning
- Removes poor performers
- Progressive NAS, uses a similar approach by training a surrogate model and using it to predict the performance using architectural properties.

### Weight Inheritance/Network Morphisms

- Initialize weights of new architectures based on previously trained architectures.
    - Similar to transfer learning
- Uses **Network Morphism**
    -  <mark class="y">Modifies the architecture without changing the underlying function.</mark>
    - New network inherits knowledge from parent network
    - Computational speed up: only a few days of GPU usage
    - Network size not inherently bounded

## AutoML on the Cloud
{{< figure src="/images/ml/mle_for_production/ml_modeling_pipeline_in_production/popular_cloud_offerings.png" >}}

### Amazon SageMaker Autopilot

Automatically trains and tunes the model for classification or regression based on your data.

{{< figure src="/images/ml/mle_for_production/ml_modeling_pipeline_in_production/amazon_sagemaker_autopilot.png" >}}

{{< figure src="/images/ml/mle_for_production/ml_modeling_pipeline_in_production/amazon_sagemaker_keyfeatures.png" >}}

{{< figure src="/images/ml/mle_for_production/ml_modeling_pipeline_in_production/amazon_sagemaker_typical_use_cases.png" >}}

### Microsoft Azure AutoML
{{< figure src="/images/ml/mle_for_production/ml_modeling_pipeline_in_production/ms_azure_automl.png" >}}

{{< figure src="/images/ml/mle_for_production/ml_modeling_pipeline_in_production/ms_azure_keyfeatures.png" >}}

{{< figure src="/images/ml/mle_for_production/ml_modeling_pipeline_in_production/ms_azure_keyfeatures1.png" >}}

### Google Cloud AutoML
{{< figure src="/images/ml/mle_for_production/ml_modeling_pipeline_in_production/gc_automl.png" >}}

{{< figure src="/images/ml/mle_for_production/ml_modeling_pipeline_in_production/gc_automl_products.png" >}}

{{< figure src="/images/ml/mle_for_production/ml_modeling_pipeline_in_production/gc_automl_vision_products.png" >}}

{{< figure src="/images/ml/mle_for_production/ml_modeling_pipeline_in_production/gc_automl_vidio_intelligence_products.png" >}}

### How do these Cloud offerings perform AutoML?

- We don't know (or can't say) and they're not about to tell us.
- The underlying algorithms will be similar to what we've learned.
- The algorithms will evolve with the state of the art

{{< panel title="AutoML" >}}
  ## AutoML

If you wish to dive more deeply into AutoMLs, feel free to check out these cloud-based tools. You won’t have to read these to complete this week’s practice quizzes.

- [Amazon SageMaker Autopilot](https://aws.amazon.com/sagemaker/autopilot)
- [Microsoft Azure Automated Machine Learning](https://azure.microsoft.com/en-in/services/machine-learning/automatedml/)\
- [Google Cloud AutoML](https://cloud.google.com/automl)
{{< /panel >}}
