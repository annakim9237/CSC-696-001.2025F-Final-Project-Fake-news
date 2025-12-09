# Ethical Analysis of AI-Generated Fake News: Justice + HateXplain + UNESCO Mapping

This project uses the **ETHICS dataset (Hendrycks)** to train a DistilBERT-based classifier that labels sentences as **ethically acceptable (0)** or **ethically problematic (1)**.  
The trained classifier is then applied to **AI-generated fake news** to estimate how many sentences in the corpus are ethically problematic.

Below is a summary of the main efforts made to improve model quality and robustness.

---

##  Table of Contents

- [Project Overview (English)](#-project-overview-english)
  - [1. Data-Level Experiments](#1-data-level-experiments)
  - [2. Model Architecture Adjustments](#2-model-architecture-adjustments)
  - [3. Training Process Optimization](#3-training-process-optimization)
  - [4. Loss Function Improvements](#4-loss-function-improvements)
  - [5. Final Model Selection](#5-final-model-selection)
  - [English Summary](#english-3-line-summary)

---

### 1. Data-Level Experiments

#### 1-1. Full ETHICS vs. Commonsense vs. Justice

- The ETHICS dataset consists of multiple sub-tasks (e.g., `commonsense`, `justice`) with very different distributions.
- Initially, I trained on the **full dataset (commonsense + justice)**, but mixing different distributions caused unstable performance.
- I therefore trained separate models on:
  - `commonsense` only
  - `justice` only
- Results:
  - `commonsense` produced high validation performance,
  - **`justice` models showed the most stable F1 on the test set.**
- Considering distribution shift and noise in test conditions, **`justice` appears more suitable for downstream usage.**

---

### 2. Model Architecture Adjustments(ver2)

#### 2-1. Increase Dropout

- DistilBERT's default dropout is relatively low, which led to quick overfitting on the noisy ETHICS data.
- To mitigate this, I increased:
  - `dropout = 0.2`
  - `attention_dropout = 0.2`
- This helped reduce overconfident predictions and produced a smoother decision boundary, improving generalization.

---

### 3. Training Process Optimization

#### 3-1. Epoch adjustment (3 → 1)

- With 3 epochs the model showed high training/validation but degraded test performance — a classic overfitting pattern.
- Reducing epochs to **1** lowered overfitting and produced more stable test F1 and loss.

---

### 4. Loss Function Improvements

#### 4-1. Apply Label Smoothing

- ETHICS labels can be noisy or ambiguous due to annotator disagreement. Hard 0/1 labels can hurt model calibration.
- I applied `label_smoothing_factor = 0.1` to soften labels.
- This reduced extreme probability outputs and improved test loss and calibration.

---

### 5. Final Model Selection

- Compared models: `full_v1`, `full_v2`, `commonsense_v1`, `commonsense_v2`, `justice_v1`, `justice_v2`.
- Metrics: validation F1, test F1, and test loss.
- Findings:
  - `commonsense_v1` had the best validation F1,
  - **`justice` models were more robust on the test set,**
  - `justice_v2` (with dropout, weight decay, and label smoothing) achieved the best balance of test loss and F1.

Therefore, the final classifier chosen for downstream fake news analysis is **`justice_v1`** (DistilBERT + dropout 0.2 + weight decay + label smoothing 0.1).

---

## 6. Why Additional Experiments Were Necessary After Selecting `justice_v1`

Although `justice_v1` was selected as the primary ETHICS-based classifier,  
applying it to AI-generated fake news revealed several critical limitations.  
Addressing these limitations required additional modeling, semantic mapping, and  
article-level risk aggregation. The following sections describe the motivation and  
steps taken to expand the pipeline.

---

## 6-1. Problem: The Justice model detects *fairness* violations only

The Justice subset focuses on *impartiality* and *desert*.  
As a result, it fails to capture other forms of social or ethical harm such as:

- Hate speech  
- Offensive or derogatory language  
- Group-based discrimination  
- Propaganda-like or fear-mongering rhetoric  
- Politically manipulative or inflammatory framing  


Although harmful, this sentence is often classified as `unethical = 0`  
because the Justice task is **not designed** to detect toxicity or hate.

**Underlying limitation:**
- Justice = fairness violations only  
- Real-world ethical risks are multi-dimensional  
- A single-axis classifier cannot capture the full spectrum of harm  

---

## 6-2. Solution: Add a HateXplain-based Hate/Offensive Classifier

To complement Justice, a second classifier was built using HateXplain.

- 3-class model:  
  - `hatespeech`  
  - `offensive`  
  - `normal`
- Per-sentence probability scores:  
  - `p_hate`, `p_offensive`, `p_normal`
- Combined toxicity score:  
  - `prob_hate_offensive = p_hate + p_offensive`

This allowed us to define **four multi-risk categories**:

| risk_type | Meaning |
|-----------|---------|
| both | High Justice risk + High hate/offensive risk |
| justice_only | Fairness-related ethical issue only |
| hate_only | Toxicity/hate issue only |
| none | No detected risk |

This multi-axis structure captures **distinct sources of harm** that Justice alone cannot detect.

---

## 6-3. Problem: A risk label alone does not explain *why* a sentence is harmful

Even with two classifiers, the results still lacked interpretability.  
Questions remained unanswered:

- Which ethical domain is being violated?  
- Is the harm related to fairness, safety, discrimination, privacy, or something else?  
- What is the underlying principle being challenged?  

A risk prediction without explanation was insufficient for ethical analysis.

---

## 6-4. Solution: Map sentences to UNESCO AI Ethics Principles (11 principles)

To provide interpretability, each sentence embedding was matched to  
UNESCO’s 11 AI Ethics principles via cosine similarity.

Each sentence obtains:

- `unesco_principle_final`  
- `unesco_score_final`

This semantic mapping enables:

- Understanding *why* a sentence is considered harmful  
- Identifying consistent ethical patterns across articles  
- Connecting model predictions to globally recognized ethical standards  
- Supporting downstream reports, policy analysis, and interpretation  

---

## 6-5. Problem: Sentence-level risk does not translate directly to article-level risk

Summing sentence risks does not reflect a realistic article-level assessment.

Example:
- One extremely harmful sentence in a 100-sentence article  
- Four moderately harmful sentences in a 10-sentence article  

Raw counts distort the true risk.  
A structured aggregation method was needed.

**Solution: Compute article-level metrics**

- `avg_unethical`  
- `avg_hate_off`  
- `unethical_ratio`  
- `hate_offensive_ratio`  
- Dominant UNESCO principle(s) per article  

This allows for fair comparison and detection of genuinely high-risk articles.

---

## 6-6. Visualization: Making complex results interpretable for humans

To make risk patterns understandable, the following visualizations were implemented:

- Histogram of `unethical_ratio`
- Histogram of `hate_offensive_ratio`
- UNESCO principle distribution per risk_type (`justice_only`, `hate_only`, `both`)
- Top-K high-risk sentence lists
- Distribution of HateXplain’s predicted labels

These visualizations highlight risk hotspots and thematic patterns.

---

## 6-7. Final Pipeline Overview

The complete multi-dimensional ethical analysis pipeline:

1. Split article into sentences  
2. Classify each sentence with `justice_v1`  
3. Classify each sentence with HateXplain  
4. Assign combined multi-risk type (`both`, `justice_only`, etc.)  
5. Map each sentence to a UNESCO principle via embeddings  
6. Aggregate to article-level risk metrics  
7. Generate visualizations and high-risk summaries  

---


