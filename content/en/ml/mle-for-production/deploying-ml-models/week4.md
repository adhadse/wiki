---
title: "Week 4 — Model monitoring, Logging & model decay, GDPR, and Privacy"
description: "Model Monitoring and logging, observabilit, model decay, GDPR and Privacy, Responsible AI and Right to Be Forgotten"
lead: ""
date: 2022-03-26T14:41:39+01:00
lastmod: 2022-03-26T14:41:39+01:00
draft: false
images: []
type: docs
menu:
  intro_to_mlops:
    parent: "deploying-ml-models"
weight: 400
toc: true
---

# Model Monitoring and Logging

## Why Monitoring Matters

Monitoring not only include monitoring of our ML models, but also the monitoring of the systems and infrastructure which are included in our entire product or service such as Databases and web servers

{{< figure src="/images/ml/mle_for_production/deploying_ml_models_in_production/ml_lifecycle_revisited.png">}}

> "An ounce of prevention is worth a pound of cure" — Benjamin Franklin

- Immediate Data Skews
    - Training data is too old, not representative of live data
- Model Staleness
    - Environment shifts
    - Consumer behaviour
    - Adversarial scenarios
- Negative Feedback Loops: when you train your models on data collected in production. If that data is biased/corrupted in any way, then the model trained on that data will also perform poorlly.

{{< figure src="/images/ml/mle_for_production/deploying_ml_models_in_production/monitoring_in_ml_systems.png">}}

### Why is ML monitoring different?

Unlike a pure software system, there are two additional components to consider in an ML system, the data and the model. Unlike in traditional software systems, the accuracy of an ML system depends on how well the model reflects the world it is meant to model which in turn depends on the data used for training and on the data that it receives while serving requests.

Code and config also take on additional complexity and sensitivity in an ML system due to two aspects:

1. Entanglement: Refers to the issue where changing anything, changes everything
2. Configuration: Model hyperparameters, versions and features are often controlled in a system config and the slightest error here can cause radically different model behavior that won't be picked by traditional software tests.

## Observability in ML

<mark class="y">Observability measures how well the internal states of a system can be inferred by knowing the inputs and outputs.</mark>

For ML, that means monitoring and analyzing the prediction requests and the generated predictions from your models.

Observability comes from control system theory where observability and controllability are closely linked.

i.e., controlling the accuracy of results overall usually across different versions of the model, requires observability.

### Complexity of observing modern systems

- Modern systems can make observability difficult
    - Cloud-based systems
    - Containerized infrastructure
    - Distributed systems
    - Microservices

### Deep observability for ML

- Not only top-level metrics
    - Data slices provide a way to analyze different groups of people or different type of conditions
- Domain knowledge is important for observability
- TensorFlow Model Analysis (TFMA)
- Both supervised and unsupervised analysis

### Goals of ML observability

The main goal here in the context of observability is to prevent or act upon system failures.

Observations need to provide alert when a failure happens and ideally provide recommended actions to bring the system back to normal behavior.

- **Alertable**
    - Metrics and thresholds designed to make failures obvious
- **Actionable**
    - Root cause clearly identified

## Monitoring Targets in ML

### Basics: Input and output monitoring

- Model input distribution
    
    Measure high level statistics on slices of data relevant to domain
    
- Model prediction distribution
- Model versions
- Input/prediction correlation

{{< figure src="/images/ml/mle_for_production/deploying_ml_models_in_production/input_monitoring.png">}}
{{< figure src="/images/ml/mle_for_production/deploying_ml_models_in_production/prediction_monitoring.png">}}
{{< figure src="/images/ml/mle_for_production/deploying_ml_models_in_production/operational_monitoring.png">}}

Collecting all the context information is often not practical, as the amount of data to process and store could be very large, so it's important the most relevant context and try to gather that information.

## Logging for ML Monitoring

<mark class="y">A log is an immutable, time stamped record of discrete events that happened over time for the system along with additional information.</mark>

### Steps for building observability

- Start with the out-of-the-box logs, metrics and dashboards
- Add agents to collect additional logs and metrics
- Add logs-based metrics and alerting to create your own metrics and alerts
- Use aggregated sinks and workspaces to centralize your logs and monitoring

### Tools for building observability

- Google Cloud Monitoring
- Amazon CloudWatch
- Azure Monitor

### Logging - Advantages

- Easy to generate
- Great when it comes to providing valuable insight
- Focus on specific events

### Logging - Disadvantages

- Excessive logging can impact system performance
- Aggregation operations on logs can be expensive (i.e., treat logs-based alerts with caution)
- Setting up & maintaining tooling carries with it a significant operational cost

### Logging in Machine Learning

Key areas: Use logs to keep track of the model inputs and predictions

Input red flags:

- A feature becoming unavailable
- Notable shifts in the distribution
- Patterns specific to your model

### Storing log data for analysis

- Basic log storage is often unstructured
- Parsing and storing log data in a queryable format enables analysis
    - Extracting values to generate distributions and statistics
    - Associating events with timestamps
    - Identifying the systems
- Enables automated reporting, dashboards, and alerting

### New Training Data

- Prediction requests form new training datasets
- For supervised learning, labels are required
    - Direct labeling
    - Manual labeling
    - Active learning
    - Weak supervision

## Tracing for ML systems

Tracing focuses on monitoring and understanding system performance, especially for microservice-based applications.

In monolithic systems, it's relatively easy to collect diagnostic data form different parts of a system. All modules might even run within one process and share common resources for logging.

{{< figure src="/images/ml/mle_for_production/deploying_ml_models_in_production/distributed_tracing.png">}}
Solving this problem becomes even more difficult if your services are running as separate processes in a distributed system. We can't depend on the traditional approaches that help diagnose monolithic systems. We somehow need to know the fine grain information of what's going on inside each service.
{{< figure src="/images/ml/mle_for_production/deploying_ml_models_in_production/distributed_tracing1.png">}}

### Tools for building observability

- Sequence and parallelism of service requests
- Distributed tracing
    - Dapper
    - Zipkin
    - Jaeger

### Dapper-Style Tracing

In service based architectures, Dapper style tracing works by propagating tracing data between services.

Each service annotate the trace with additional data and passes the tracing header to other services until the final request completes

Services are responsible for uploading their traces to a tracing back-end. The tracing backend then puts related latency data together like pieces of a puzzle.

Each trace is a call tree, beginning with the entry point of a request and ending with the server's response including all of the RPCs along the way. Each trace consists of small units called spans.

{{< figure src="/images/ml/mle_for_production/deploying_ml_models_in_production/dapper_style_tracing.png">}}

{{< panel title="Monitoring Machine Learning Models in Production" >}}
    
  ## Monitoring Machine Learning Models in Production
  
  Check this [resource](https://christophergs.com/machine%20learning/2020/03/14/how-to-monitor-machine-learning-models/) out to learn more about ML monitoring and logging.

{{< /panel >}}

# Model Decay

## What is Model Decay?

### Model Decay

- Production ML models often operate in a dynamic environments
- The ground truth in dynamic environments changes
- If the model is static and does not change, then it gradually moves farther and farther away from the ground truth

<mark class="v">**Two main causes of model drift**:

- <mark class="v">Data Drift</mark>
- <mark class="v">Concept Drift</mark>

### Data Drift (aka Feature Drift)

- Statistical properties of input changes
- Trained model is not relevant for changed data
- For e.g., distribution of demographic data like age might change over time.

### Concept Drift

- Relationship between features and labels changes
- The very meaning of what you are trying to predict changes
- Prediction drift and label drift are similar

### Detecting Drift on Time

- Drift creeps into the system slowly with time
- If it goes undetected, model accuracy suffers
- Important to monitor and detect drift early

## Model Decay Detection

### Detecting Concept and Data Drift

**Log Predictions (Full Requests and Reponses)**

- Incoming prediction requests and generated prediction should be logged
- If possible log the ground truth that should have been predicted
    - Can be used as labels for new training data
- At a minimum log data in prediction request
    - This data can be analyzed using unsupervised statistical methods to detect data drift that will cause model decay

### Detecting Drift

- Detected by observing the statistical properties of logged data, model predictions, and possible ground truth.
- Deploy dashboard that plot statistical properties to observe how they change over time
- Use specialized libraries for detecting drift
    - TensorFlow Data Validation (TFDV)
    - Scikit-multiflow library

### Continuous Evaluation and Labelling in Vertex Prediction

- Vertex Prediction offers continuous evaluation
- Vertex Labelling Service can be used to assign ground truth labels to prediction input for retraining.
- Azure, AWS, and other cloud providers provide similar services.

## Ways to Mitigate Model Decay

**When you've detected model decay**:

- At the minimum operational and business stakeholders should be notified of the decay
- Take steps to bring model back to acceptable performance

### Steps in Mitigating Model Decay

- What if Drift is Detected?
    - If possible, determine the portion of your training set that is still correct using unsupervised methods, such as clustering or statistical methods that look at divergence, KL divergence, JS divergence, KS test.
    - Keep the good data, discard the bad, and add new data **OR**
    - Discard data collected before a certain date and add new data **OR**
    - Create an entirely new training set from new data

### Fine Tune, or Start Over?

- you can either continue training your model, fine tuning from the last checkpoint using new data **OR**
- Start over, reinitialize your model, and completely retrain it
- Either approach is valid, so it really depends on results
    - How much new labelled data do you have?
    - How far has it drifted?
- Ideally Try both and compare the results

### Model Re-Training Policy

It's usually a good idea to establish policies around when you're going to retrain your model, well it depends.

{{< figure src="/images/ml/mle_for_production/deploying_ml_models_in_production/model_retraining_policy.png">}}

### Automated Model Retraining
{{< figure src="/images/ml/mle_for_production/deploying_ml_models_in_production/automated_model_retraining.png">}}

### Redesign Data Processing Steps and Model Architecture

- When model performance decays beyond an acceptable threshold you might have to consider redesigning your entire pipeline
- Re-think feature engineering, feature-selection
- You may have to train your model from scrath
- Investigate on alternative architectures
- Addressing Model Decay

{{< panel title="Addressing Model Decay">}}
  ## Addressing Model Decay
  
  Check this [blog](https://neptune.ai/blog/retraining-model-during-deployment-continuous-training-continuous-testing) out to figure out best retraining strategies toi prevent model decay.
{{< /panel >}}

# GDPR and Privacy

## Responsible AI

### Responsible AI Practices

- Development of AI **Creates new opportunities** to improve the lives of people around the world
    - Business, healthcare, education, etc
- But it also **Raises new questions** about implementing responsible practices
    - Fairness, interpretability, privacy, and security
    - Far from solved, active areas of research and development

### Human-Centered Desing

Actual users's experience is essential

- Design your features with appropriate disclosures built-in
- Consider augmentation and assistance
    - Offering multiple suggestions instead of one right answer
- Model potential adverse feedback early in the design process
- Engage with a diverse set of users and use-case scenarios

### Identify Multiple Metrics

- Using several metrics help you understand the tradeoffs
    - Feedback from user suverys
    - Quantiles that track overall system performance
    - False positive and false negative sliced across subgroups
- Metrics must be appropriate for the context and goals of your system

### Analyze your raw data carefully

- For sensitive raw data, respect privacy
    - Compute aggregate, annonymized summaries
- Does your data reflect your users?
    - e.g., will be used for all ages, but all data from senior citizens
- Imperfect proxy labels?
    - Relationships between the labels and actual targets
- Responsible AI
    
## Responsible AI

New technologies always bring new challenges. Ensuring that your applications adhere to responsible AI is a must. Please read this [resource](https://ai.google/responsibilities/responsible-ai-practices/) to keep yourself updated with this fascinating active research  subject.
    

## Legal Requirements for Secure and Private AI

### Legal Implications of Data Security and Privacy

Companies must comply with data privacy protection laws in regions where they operate

In Europe for example, you need to comply with **GDPR, General Data Protection Regulation**.

In California, with **CCPA, California Consumer Privacy Act**

### General Data Protection Regulation (GDPR)

- Regulation in EU law on data protection and privacy in the European Union (EU) and the European Economic Area (EEA)
- Give control to individuals over their data
- Companies should protect the data of employees
- When the data processing is based on consent, the data subject has the right to revoke their consent at any time.

### California Consumer Privacy Act (CCPA)

- Similar to GDPR
- Intended to enhance privacy rights and consumer protection for residents of California
- User has the right to know what personal data is being collected about them, whether the personal data is sold or disclosed, and to whom
- User can access the personal data, block the sale of their data, and request a business to delete their data.

### Security and Privacy Harms from ML Models
{{< figure src="/images/ml/mle_for_production/deploying_ml_models_in_production/security_and_privacy_harms_from_ml_models.png">}}

### Defenses
{{< figure src="/images/ml/mle_for_production/deploying_ml_models_in_production/defenses.png">}}

### Cryptography

- Privacy-enhancing tools (like SMPC and FHE) should be considered to securely train supervised machine learning models
- Users can send encrypted prediction requests while preserving the confidentiality of the model
- Protects confidentiality of the training data

### Differential Privacy

Roughly speaking, <mark class="y">a model is differentially private if an attacker seeing its predictions cannot tell if a particular user's information was included in the training data.</mark>

System for publicly sharing information about a dataset by describing the patterns of groups within the dataset while withholding information about individuals in the dataset.

<mark class="v">There are three different approaches to implement differential privacy:</mark>

1. <mark class="v">DP-SGD (Differentially Private Stochastic Gradient Descent)
2. <mark class="v">PATE (Private Aggregation of Teacher Ensembles)</mark>
3. <mark class="v">CaPC (Confidential and Private Collaborative learning)</mark>

### Differentially-Private Stochastic Gradient Descent (DP-SGD)

If an attacker is able to get a copy of a normally trained model, then they can use the weights to extract private information.

DP-SGD eliminates that possibility by applying differential privacy during model training.

- Modifies the minibatch stochastic optimization process by adding noise.
- Trained model retains differential privacy because of the post processing immunity property of differential privacy.
    - Post-processing immunity is a fundamental property of a differential privacy.
    - It means that regardless how you process the models predictions, you can't affect their privacy guarantees.

### Private Aggregation of Teacher Ensembles (PATE)

- Begins by dividing sensitive information into k partitions with no overlaps. It trains k models on that data separately as teacher models and then aggregate the result in an aggregate teacher model.
- During the aggregation for the aggregate teacher, we will add noise to the output in a way that won't affect the resulting predictions.
- For deployment, we will create a student model. To train the student model, we'll take unlabeled public data and feed it to aggregate teacher model, outputting a labeled data, which maintains privacy. This data is then used as the training set for the student model.
- Discard everything on left side of diagram and deploy student model.

{{< figure src="/images/ml/mle_for_production/deploying_ml_models_in_production/private_aggregations_of_teacher_ensembles.png">}}

### Confidential and Private Collaborative Learning (CaPC)

- Enables models to collaborate while preserving the privacy of the underlying data
- Integrates building blocks from cryptography and differential privacy to provide confidential and private collaborative learning.
- Encrypts prediction requests using Homomorphic Encryption (HE)
- Uses PATE to add noise to predictions for voting

{{< panel title="GDPR and CCPA" >}}

## GDPR and CCPA

Check the [GDPR](https://gdpr.eu/)  and [CCPA](https://oag.ca.gov/privacy/ccpa) websites  out to learn more about its regulations and compliance.
{{< /panel >}}

## Anonymization and Pseudonymisation

### Data Anonymization in GDPR

- GDPR includes many regulations to preserve privacy of user data
- Since introduction of GDPR, two terms have been discussed widely
    1. Anonymization
    2. Pseudonymisation

### Data Anonymization

Removes Personally Identifiable Information (PII) form data sets.

**Recital 26 of GDPR defines Data Anonymization**

True data anonymization is :

- Irreversible
- Done in such a way that it is impossible to identify the person
- Impossible to derive insights or discrete information, even by the party responsible for a anonymization

GDPR does not apply to data that has been anonymized

### Pseudonymisation

- GDPR Article 4(5) defines pseudonymisation as:
    
    "...the processing of personal data in such a way that the data can no longer be attributed to a specific data subject without the use of additional information"
    
- The data is anonymized by switching the identifiers (like email or name) with an alias or pseudonym.

{{< figure src="/images/ml/mle_for_production/deploying_ml_models_in_production/anonymization_vs_pseudonymization.png">}}

### Spectrum of Privary prevention
{{< figure src="/images/ml/mle_for_production/deploying_ml_models_in_production/spectrum_of_privacy_prevention.png">}}

### What data should be Anonymized?

- Any data that reveals the identify of a person, referred to as identifies
- Identifiers applies to any natural or legal person, living or dead, including their dependents, ascendants, and descendants.
- Included are other related persons, direct or through interaction
- For example: Family names, patronyms, first names, maiden names, aliases, address, phone, bank account details, credit cards, IDs like SSN.

## Right to be Forgotten

### What is Right to Be Forgotten?

"The data subject shall have the right to obtain from the controller the erasure of personal data concerning him or her without undue delay and the controller shall have the obligation to erase personal data without undue delay"

- Recitals 65 and 66 and in Article 17 of the GDPR

### Right to Rectification

"The data subject shall have the right to obtain from the controller without undue delay the rectification of inaccurate personal data concerning him or her. Taking into account the purposes of the processing, the data subject shall have the right to have incomplete personal data completed, including by means of providing a supplementary statement."

- Chapter 3, Art. 16 GDPR

### Other Rights of the Data Subject

Chapter 3 defines a number of other rights of the data subject, including:

- Art. 15 GDPR - Right of access by the data subject
- Art. 18 GDPR - Right to restriction of processing
- Art. 20 GDPR - Right to data portability
- Art. 21 GDPR - Right to object

### Implementing Right To Be Forgotten: Tracking Data

For a valid erasure claim

- Company need to identify all of the information related to the content requested to be removed.
- All of the associated metadata must also be erased
    - e.g., Derived data, logs etc.

### Forgetting Digital Memories
{{< figure src="/images/ml/mle_for_production/deploying_ml_models_in_production/forgetting_digital_memories.png">}}

### Issues with Hard Delete

- Deleting records from a database can cause havoc
- User data is often referenced in multiple tables
- Deletion breaks the connections, which can be difficult in large, complex databases
- Can break foreign keys
- Anonymization keeps the records, and only anonymizes the fields containing PII.

### Challenges in Implementing Right to Be Forgotten

- Identifying if data privacy is violated
- Organisational changes for enforcing GDPR
- Deleting personal data from multiple back-ups

{{< panel title="Course 4 Optional References" >}}
  ## Course 4 Optional References

# Machine Learning Modeling Pipelines in Production

This is a compilation of resources including URLs and papers appearing in lecture videos. If you wish to dive more deeply into the topics covered this week, feel free to check out these optional references.

## Week 1. Model Serving: introduction

### **NoSQL Databases:**

- [Google Cloud Memorystore](https://cloud.google.com/memorystore)
- [Google Cloud Firestore](https://cloud.google.com/firestore)
- [Google Cloud Bigtable](https://cloud.google.com/bigtable)
- [Amazon DynamoDB](https://aws.amazon.com/dynamodb/)

### **MobileNets:**

- [MobileNets](https://arxiv.org/abs/1704.04861)

### **Serving Systems:**

- [Clipper](https://rise.cs.berkeley.edu/projects/clipper/)
- [TensorFlow Serving](https://www.tensorflow.org/tfx/guide/serving)

## Week 2. Model Serving: patterns and infrastructure

### **Model Serving Architecture:**

- [Model Server Architecture](https://medium.com/@vikati/the-rise-of-the-model-servers-9395522b6c58)
- [TensorFlow Serving](https://www.tensorflow.org/tfx/serving/architecture)
- [NVIDIA Triton Inference Server](https://developer.nvidia.com/nvidia-triton-inference-server)
- [Torch Serve](https://github.com/pytorch/serve)
- [Kubeflow Serving](https://www.kubeflow.org/docs/components/serving/)

### **Scaling Infrastructure:**

- [Container Orchestration](https://phoenixnap.com/blog/what-is-container-orchestration)
- [Kubernetes](https://kubernetes.io/)
- [Docker Swarm](https://docs.docker.com/engine/swarm/)
- [Kubeflow](https://www.kubeflow.org/)

### **Online Inference:**

- [Batch vs. Online Inference](https://mlinproduction.com/batch-inference-vs-online-inference/)

### **Batch Processing with ETL:**

- [Kafka ML](https://github.com/ertis-research/kafka-ml#:~:text=Kafka%2DML%20is%20a%20framework,(ML)%20models%20on%20Kubernetes.&text=The%20training%20and%20inference%20datasets,ones%20provided%20by%20the%20IoT.)
- [Pub Sub](https://cloud.google.com/pubsub)
- [Cloud DataFlow](https://cloud.google.com/dataflow)
- [Apache Spark](https://spark.apache.org/)

## Week 3. Model Management and Delivery

### **Experiment Tracking and Management:**

- [Tracking](https://towardsdatascience.com/machine-learning-experiment-tracking-93b796e501b0)
- [Management](https://neptune.ai/blog/experiment-management)

### **Notebooks:**

- [nbconvert](https://nbconvert.readthedocs.io/)
- [nbdime](https://nbdime.readthedocs.io/)
- [jupytext](https://jupytext.readthedocs.io/en/latest/install.html)
- [neptune-notebooks](https://docs.neptune.ai/)
- [git](https://git-scm.com/)

### **Tools for Data Versioning:**

- [Neptune](https://docs.neptune.ai/how-to-guides/data-versioning)
- [Pachyderm](https://www.pachyderm.com/)
- [Delta Lake](https://delta.io/)
- [Git LFS](https://git-lfs.github.com/)
- [DoIt](https://github.com/dolthub/dolt)
- [lakeFS](https://lakefs.io/data-versioning/)
- [DVC](https://dvc.org/)
- [ML-Metadata](https://blog.tensorflow.org/2021/01/ml-metadata-version-control-for-ml.html)

### **Tooling for Teams:**

- [Image Summaries](https://www.tensorflow.org/tensorboard/image_summaries)
- [neptune-ai](https://neptune.ai/for-teams)
- [Vertex TensorBoard](https://cloud.google.com/vertex-ai/docs/experiments/tensorboard-overview)

### **MLOps:**

- [MLOps: Continuous delivery and automation pipelines in machine learning](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)

### **Orchestrated Workflows with TFX:**

- [Creating a Custom TFX Component](https://blog.tensorflow.org/2020/01/creating-custom-tfx-component.html)
- [Building Fully Custom Components](https://github.com/tensorflow/tfx/blob/master/docs/guide/custom_component.md)

### **Continuous and Progressive Delivery:**

- [Progressive Delivery](https://www.split.io/glossary/progressive-delivery/)
- [Continuous, Incremental, & Progressive Delivery](https://launchdarkly.com/blog/continuous-incrementalprogressive-delivery-pick-three/)
- [Deployment Strategies](https://dev.to/mostlyjason/intro-to-deployment-strategies-blue-green-canary-and-more-3a3)
- [Blue/Green Deployment](https://martinfowler.com/bliki/BlueGreenDeployment.html)
- [A/B Testing](https://medium.com/capital-one-tech/the-role-of-a-b-testing-in-the-machine-learning-future-3d2ba035daeb)

## Week 4. Model Monitoring and Logging

- [Hidden Technical Debt in Machine Learning Systems](https://papers.nips.cc/paper/2015/file/86df7dcfd896fcaf2674f757a2463eba-Paper.pdf)
- [Monitoring Machine Learning Models in Production](https://christophergs.com/machine%20learning/2020/03/14/how-to-monitor-machine-learning-models/)
- [Google Cloud Monitoring](https://cloud.google.com/monitoring)
- [Amazon CloudWatch](https://aws.amazon.com/cloudwatch/)
- [Azure Monitor](https://docs.microsoft.com/en-us/azure/azure-monitor/overview#:~:text=Azure%20Monitor%20helps%20you%20maximize,cloud%20and%20on%2Dpremises%20environments.&text=Collect%20data%20from%20monitored%20resources%20using%20Azure%20Monitor%20Metrics.)
- [Dapper](https://storage.googleapis.com/pub-tools-public-publication-data/pdf/36356.pdf)
- [Jaeger](https://www.jaegertracing.io/)
- [Zipkin](https://zipkin.io/)
- [Vertex Prediction](https://cloud.google.com/vertex-ai)
- [Vertex Labelling Service](https://cloud.google.com/vertex-ai/docs/datasets/label-using-console)
- [How “Anonymous” is Anonymized Data?](https://www.kdnuggets.com/2020/08/anonymous-anonymized-data.html)
- [Pseudonymization](https://dataprivacymanager.net/pseudonymization-according-to-the-gdpr/)
{{< /panel >}}