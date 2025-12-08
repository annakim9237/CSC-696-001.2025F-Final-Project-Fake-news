# ETHICS 기반 윤리 분류기 (NLP Final Project)

이 프로젝트는 Hendrycks의 **ETHICS 데이터셋**을 활용하여
문장을 **윤리적으로 문제 있음 / 문제 없음**으로 분류하는 **DistilBERT 기반 분류기**를 학습하고,
이후 **AI가 생성한 뉴스(fake news)**에 적용하여
얼마나 많은 문장이 윤리적으로 문제가 있는지를 분석하는 것을 목표로 한다.

본 README는 **모델 품질을 개선하기 위해 진행한 실험 및 튜닝 과정**을
한국어로 정리한 문서이다.

---

## 목차 (Table of Contents)

- [프로젝트 개요 (Korean)](#-프로젝트-개요-korean)
  - [1. 데이터 수준 실험](#1-데이터-수준-실험)
  - [2. 모델 구조 조정](#2-모델-구조-조정)
  - [3. 학습 과정 최적화](#3-학습-과정-최적화)
  - [4. 손실 함수 개선](#4-손실-함수-개선)
  - [5. 성능 비교 및 최종 모델 선택](#5-성능-비교-및-최종-모델-선택)
  - [한국어 요약](#한국어-3줄-요약)

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

## 6. Justice_v1 이후 확장 실험: 왜 추가 단계가 필요했는가?

최종적으로 `justice_v1` 모델을 선택했지만,  
AI-generated fake news를 실제로 분석하는 과정에서 여러 한계가 드러났다.  
이 문제들을 해결하기 위해 아래와 같은 추가 확장 실험과 파이프라인 개선 작업을 수행했다.

---

## 6-1. 문제 인식: Justice 모델은 ‘공정성’ 외 윤리 위험을 거의 탐지하지 못함

Justice 모델은 ETHICS의 *impartiality/desert* 태스크 기반이므로 다음 유형 탐지에 취약했다:

- 혐오(hate speech)
- 공격적 표현(offensive)
- 집단 비하(discriminatory framing)
- 정치·사회적 선동(propaganda-style tone)
- 공포 조장(fear-mongering)

## 6. Justice_v2 이후 확장 실험: 왜 추가 단계가 필요했는가?

최종적으로 `justice_v1` 모델을 선택했지만,  
AI-generated fake news를 실제로 분석하는 과정에서 여러 한계가 드러났다.  
이 문제들을 해결하기 위해 아래와 같은 추가 확장 실험과 파이프라인 개선 작업을 수행했다.

---

## 6-1. 문제 인식: Justice 모델은 ‘공정성’ 외 윤리 위험을 거의 탐지하지 못함

Justice 모델은 ETHICS의 *impartiality/desert* 태스크 기반이므로 다음 유형 탐지에 취약했다:

- 혐오(hate speech)
- 공격적 표현(offensive)
- 집단 비하(discriminatory framing)
- 정치·사회적 선동(propaganda-style tone)
- 공포 조장(fear-mongering)


→ 실제로는 매우 위험한 문장임에도 `unethical = 0` 으로 분류되는 경우가 발생.

**한계 원인**
- Justice 서브태스크는 “부당한 대우” 중심
- Hate/Toxicity/Propaganda 관련 표현을 포착하도록 설계되지 않음

---

## 6-2. 해결: HateXplain 기반 혐오·공격성 분류 모델 추가 구축

Justice 모델을 보완하기 위해 HateXplain 기반 3-class 분류기를 구축했다.

- 3개 클래스  
  - `hatespeech`  
  - `offensive`  
  - `normal`
- 각 문장에 대해 확률 생성  
  - `p_hate`, `p_offensive`, `p_normal`
- 두 위험도를 합산  
  - `prob_hate_offensive = p_hate + p_offensive`

두 모델을 결합하여 4종류의 multi-risk 유형을 정의했다.

| risk_type | 의미 |
|-----------|------|
| both | justice + hate/offensive 둘 다 위험 |
| justice_only | 공정성 위반만 존재 |
| hate_only | 혐오/공격성만 존재 |
| none | 위험 없음 |

---

## 6-3. 문제 인식: “위험하다”는 정보만으로는 *왜* 위험한지 알 수 없음

문장 분류 결과만으로는 다음을 구분하기 어려웠다.

- 어떤 윤리 원칙을 위반했는가?
- 사회적 해악인지, 공정성 문제인지, 안전성 문제인지?
- 모델 판단의 근거는 무엇인가?

즉, **설명 가능성이 부족한 상황**이었음.

---

## 6-4. 해결: UNESCO AI Ethics Framework(11개 원칙)에 문장 의미 매핑

문장 임베딩과 UNESCO 11개 윤리 원칙 문구 간 cosine similarity를 사용하여  
각 문장을 다음과 같이 확장 태깅했다.

- `unesco_principle_final`  
- `unesco_score_final`

이를 통해 다음이 가능해짐:

- 모델이 문장을 왜 위험하다고 판단했는지 설명  
- 위반 가능성이 높은 윤리 영역 파악  
- 기사(article) 단위에서 윤리 위험 패턴 비교

---

## 6-5. 문제 인식: 기사(article) 단위 위험은 단순 합산으로는 왜곡될 수 있음

문장 단위 위험을 그대로 더하면 기사 간 리스크 비교가 어려움.

예시:
- 1/100 문장만 매우 위험한 기사  
- 4/10 문장이 중간 위험인 기사  
→ 둘 중 어떤 기사가 더 위험한가?

이를 해결하기 위해 article-level 집계를 수행했다.

- `avg_unethical`
- `avg_hate_off`
- `unethical_ratio`
- `hate_offensive_ratio`
- `top_unesco_principles`

---

## 6-6. 시각화 자동화: 위험 패턴을 사람이 이해하기 쉬운 형태로 표현

다음 시각화를 생성하여 분석 결과를 구조화함.

- `unethical_ratio` 히스토그램
- `hate_offensive_ratio` 히스토그램
- `risk_type` 별 UNESCO principle 바플롯
- high-risk 문장 Top-K 리스트
- hate_top_label 분포

---

## 6-7. 최종 파이프라인 요약

1. 뉴스 문장 분리  
2. `justice_v1`로 윤리적 위험 탐지  
3. HateXplain으로 혐오·공격성 탐지  
4. 두 결과를 합쳐 risk type 생성  
5. UNESCO AI Ethics Framework에 semantic 매핑  
6. article-level 위험 집계  
7. 시각화 및 사례 분석 리포트 생성

---


