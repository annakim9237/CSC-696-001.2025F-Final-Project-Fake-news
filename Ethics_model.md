# ETHICS 기반 윤리 분류기 (NLP Final Project)

이 프로젝트는 Hendrycks의 **ETHICS 데이터셋**을 활용하여  
문장을 **윤리적으로 문제 있음 / 문제 없음**으로 분류하는 **DistilBERT 기반 분류기**를 학습하고,  
이후 **AI가 생성한 뉴스(fake news)**에 적용하여  
얼마나 많은 문장이 윤리적으로 문제가 있는지를 분석하는 것을 목표로 한다.

본 README는 **모델 품질을 개선하기 위해 진행한 실험 및 튜닝 과정**을  
한국어와 영어로 정리한 문서이다.

---

## 목차 (Table of Contents)

- [프로젝트 개요 (Korean)](#-프로젝트-개요-korean)
  - [1. 데이터 수준 실험](#1-데이터-수준-실험)
  - [2. 모델 구조 조정](#2-모델-구조-조정)
  - [3. 학습 과정 최적화](#3-학습-과정-최적화)
  - [4. 손실 함수 개선](#4-손실-함수-개선)
  - [5. 성능 비교 및 최종 모델 선택](#5-성능-비교-및-최종-모델-선택)
  - [한국어 요약](#한국어-3줄-요약)
- [Project Overview (English)](#-project-overview-english)
  - [1. Data-Level Experiments](#1-data-level-experiments)
  - [2. Model Architecture Adjustments](#2-model-architecture-adjustments)
  - [3. Training Process Optimization](#3-training-process-optimization)
  - [4. Loss Function Improvements](#4-loss-function-improvements)
  - [5. Final Model Selection](#5-final-model-selection)
  - [English Summary](#english-3-line-summary)

---

## 프로젝트 개요 (Korean)

이 프로젝트에서는 Hendrycks의 **ETHICS 데이터셋**을 활용하여  
문장을 윤리적으로 **문제 있음(1)** / **문제 없음(0)**으로 분류하는 모델을 학습하고,  
이 모델을 **AI 생성 뉴스(fake news)**에 적용하여  
“얼마나 많은 문장이 도덕적으로 문제가 있는지”를 정량적으로 분석한다.

모델 품질을 높이기 위해 다음과 같은 단계별 실험과 튜닝을 수행했다.

---

### 1. 데이터 수준 실험

#### 1-1. 전체 ETHICS(full) vs commonsense vs justice 분리 실험

- ETHICS는 여러 서브태스크(예: `commonsense`, `justice` 등)로 구성되어 있으며,  
  **각 서브셋마다 문장 유형과 분포가 상당히 다르다.**
- 초기에는 **full(commonsense + justice)** 데이터를 합쳐 학습했으나,  
  서로 다른 분포가 섞이면서 **성능이 불안정해지는 현상**이 관찰되었다.
- 이에 따라:
  - `commonsense`만 사용한 모델
  - `justice`만 사용한 모델  
  을 따로 학습하여, **데이터 일관성이 성능에 미치는 영향**을 비교했다.
- 실험 결과:
  - `commonsense`는 validation 성능이 매우 높았으나,
  - **`justice` 모델이 test 기준에서 가장 안정적인 F1 스코어를 보였다.**
- 테스트 환경(분포 변화, 노이즈 등)을 고려했을 때,  
  **`justice` 서브셋이 실제 downstream task에 더 적합하다고 판단했다.**

---

### 2. 모델 구조 조정

#### 2-1. Dropout 증가

- 기본 DistilBERT는 dropout 비율이 상대적으로 낮아,  
  **노이즈가 많은 ETHICS 데이터에서 금방 과적합(overfitting)** 되는 문제가 있었다.
- 이를 완화하기 위해:
  - `dropout = 0.2`
  - `attention_dropout = 0.2`  
  로 증가시켜 **일반화 성능을 개선**하고자 했다.
- 이 조정은 validation과 test에서 **과도한 confidence를 줄이고,  
  보다 완만한 decision boundary**를 형성하는 데 도움을 주었다.

---

### 3. 학습 과정 최적화

#### 3-1. Epoch 조정 (3 → 1)

- 초기 설정(3 epoch)에서는:
  - Training / Validation 성능은 계속 상승하는 반면,
  - Test 성능은 오히려 떨어지는 **전형적인 과적합 패턴**이 관찰되었다.
- 과적합을 줄이기 위해:
  - 학습 epoch을 **3 → 1**로 줄이며 실험을 진행했다.
- 그 결과:
  - Validation과 Test 성능 사이의 격차가 줄어들었고,
  - **Test F1과 Test Loss 관점에서 더 안정적인 모델**을 얻을 수 있었다.

---

### 4. 손실 함수 개선

#### 4-1. Label Smoothing 적용

- ETHICS 라벨은 실제로:
  - 문장이 애매하거나,
  - annotator 간 합의가 낮은 경우가 많아  
  **“완전히 0 또는 1이라고 확신하는 hard label”이 모델에 불리**한 면이 있었다.
- 이를 보완하기 위해:
  - `label_smoothing_factor = 0.1`을 사용하여  
    정답 라벨 주변을 조금 부드럽게(smoothing) 만들었다.
- 효과:
  - 모델이 각 클래스에 대해 **극단적인 확률을 내는 경향이 줄어들고,**
  - Test Loss가 크게 감소하며  
    **더 잘 calibrated된(probability calibration이 좋은) 모델**로 개선되었다.

---

### 5. 성능 비교 및 최종 모델 선택

- 위의 모든 설정을 조합한 여러 모델을 비교했다:
  - `full_v1`, `full_v2`
  - `commonsense_v1`, `commonsense_v2`
  - `justice_v1`, `justice_v2`
- 비교 기준:
  - Validation F1 (분포 내 일반화)
  - Test F1 / Test Loss (분포 변화 및 실제 활용 가능성)
- 결과:
  - `commonsense_v1`은 Validation F1이 가장 높았으나,
  - **`justice` 기반 모델이 test 환경에서 더 안정적인 성능을 보였다.**
  - 특히, dropout/weight decay/label smoothing을 적용한  
    **`justice_v2` 모델이 Test Loss와 F1 측면에서 가장 균형 잡힌 결과**를 보였다.
- 따라서:
  - **최종 윤리 분류기(final classifier)**로  
    **`justice_v2` (DistilBERT + dropout 0.2 + weight decay + label smoothing 0.1)**  
    를 선택하였다.

---

### 한국어 3줄 요약

- 데이터 분리 실험(Full vs Commonsense vs Justice), dropout/epoch 조정, label smoothing을 통해 **과적합을 줄이고 일반화 성능을 향상**시켰다.  
- Validation 기준으로는 commonsense 모델이 가장 높았지만,  
  **실제 테스트 환경에서는 justice 기반 모델이 더 안정적**이었다.  
- 최종적으로 **`justice_v2` (dropout + weight decay + label smoothing)** 모델을  
  이후 fake news 분석 파이프라인의 핵심 분류기로 사용한다.

---

## 🇺🇸 Project Overview (English)

This project uses the **ETHICS dataset (Hendrycks)** to train a DistilBERT-based classifier that labels sentences as **ethically acceptable (0)** or **ethically problematic (1)**.  
The trained classifier is then applied to **AI-generated fake news** to estimate  
**how many sentences in the corpus are ethically problematic**.

Below is a summary of the main efforts made to improve model quality and robustness.

---

### 1. Data-Level Experiments

#### 1-1. Full ETHICS vs. Commonsense vs. Justice

- The ETHICS dataset consists of multiple sub-tasks (e.g., `commonsense`, `justice`) with very different distributions.
- Initially, I trained on the **full dataset (commonsense + justice)**,  
