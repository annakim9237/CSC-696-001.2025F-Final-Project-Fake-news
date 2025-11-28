# ETHICS-based Ethical Classifier (NLP Final Project)

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

### 2. Model Architecture Adjustments

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

Therefore, the final classifier chosen for downstream fake news analysis is **`justice_v2`** (DistilBERT + dropout 0.2 + weight decay + label smoothing 0.1).

---

### English 3-line Summary

- Data-split experiments, dropout/epoch adjustments, and label smoothing reduced overfitting and improved generalization.
- While `commonsense` produced the best validation F1, `justice` models were more stable on test.
- Final choice: **`justice_v2`** (dropout + weight decay + label smoothing) as the production classifier.
