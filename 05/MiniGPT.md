데이터 수집, 토큰화, 학습은 Google Colab (A100 GPU)에서 수행했고,
추론 서버(FastAPI)는 로컬 환경(Mac)에서 실행한다.

## 데이터 & 토크나이저

**데이터셋**
- 한국어 위키백과 (`wikimedia/wikipedia`, 20231101.ko): 647,897개 문서, 1.23GB
- FineWeb-2 Korean (`HuggingFaceFW/fineweb-2`, kor_Hang): 3,000,000개 문서, 12.37GB
- 최종 코퍼스 크기: **13.6GB**

**토크나이저**
- SentencePiece BPE, vocab_size=16,000
- character_coverage=0.9995 (한국어 특화 설정)
- 결과물: `tokenizer.model`, `tokenizer.vocab`

**토큰화**
- corpus.txt → tokens.bin (uint16 형식, 5.69GB)
- 총 토큰 수: **3,054,800,116개** (약 30.5억 토큰)

## 모델 구조

Decoder-only Transformer (GPT 계열)를 PyTorch로 직접 구현.

| 항목 | 값 |
|---|---|
| n_layer (블록 수) | 12 |
| n_head (어텐션 헤드) | 8 |
| n_embd (임베딩 차원) | 512 |
| block_size (컨텍스트 길이) | 256 |
| dropout | 0.1 |
| vocab_size | 16,000 |
| **총 파라미터 수** | **54,289,408개 (54.3M)** |

**구성 요소**
- `MultiHeadAttention`: scaled_dot_product_attention 기반 Self-Attention
- `FeedForward`: 4배 확장 후 GELU 활성화하는 MLP
- `TransformerBlock`: Attention + FeedForward + Residual Connection, 12개 스택
- `MiniGPT`: 토큰 임베딩 + 위치 임베딩 → 12개 블록 → 다음 토큰 예측
- `generate()`: temperature/top-k 샘플링 기반 autoregressive 문장 생성

## 학습

- 방식: Next Token Prediction (다음 단어 예측)
- Optimizer: AdamW (lr=1e-3, cosine decay 스케줄)
- Batch size: 128
- Steps: 30,000
- 학습 토큰: 2,749,320,104개 / 검증 토큰: 305,480,012개
- 학습 장비: Google Colab A100 GPU

**학습 결과**

| Step | val_loss |
|---|---|
| 0 | 9.4564 |
| 10,000 | 4.0261 |
| 20,000 | 3.8042 |
| 29,500 (최종) | **3.7147** |

## 추론 및 서빙

**추론 (inference.py)**
- 학습된 `minigpt.pt`와 `tokenizer.model`을 로드해서 문장 생성
- temperature=0.8, top_k=40 기본 설정

**서빙 (main.py, FastAPI)**
- `GET /` : 서버 상태 확인
- `POST /generate` : 프롬프트를 받아 문장 생성 후 반환
- Swagger UI(`/docs`)로 API 테스트 가능

## 실험 결과 (정성 평가)

문법적으로 완결된 한국어 문장은 생성하지만, 질문의 의도를 이해하고 답하는 능력은
없다 (다음 단어 예측만 학습했기 때문). RAG 등 질의응답 목적으로 활용하려면
검색된 문서를 기반으로 답을 생성/추출하는 추가 학습이 필요하다.

예시:
- 입력: "인공지능이란" → 문법적으로 자연스러운 문장 생성, 다만 사실 정확도는 보장되지 않음
- 입력: "조선의 역사에 대해 설명해줄수 있어?" (질의응답 형태) → 질문 의도를 반영하지 못하고
  특정 단어("한학으로")를 반복하는 현상 확인

## 실행 방법

```bash
# 1. 필요 라이브러리 설치
pip3 install torch fastapi uvicorn sentencepiece numpy

# 2. 모델 구조 확인
python3 model.py

# 3. 서버 실행
python3 main.py

# 4. 브라우저에서 Swagger UI 접속
# http://localhost:8000/docs
```

## 회고

- 처음에는 한국어 문장 100개 정도의 소규모 데이터로 시작했으나, 정성 평가 결과
  의미 있는 문장을 거의 생성하지 못해 데이터 규모를 대폭 늘려 재구축했다.
- 위키백과와 FineWeb-2를 합쳐 13.6GB 코퍼스로 처음부터 다시 학습시킨 결과,
  검증 손실이 9.45 → 3.71까지 감소했고 문법적으로 완결된 문장을 생성하게 됐다.
- 다만 순수 다음 단어 예측 방식의 한계로, 질의응답이나 RAG 활용 시에는
  추가적인 파인튜닝(Q&A 포맷 학습 등)이 필요하다는 것을 확인했다. 이는 6주차
  RAG 작업에서 LLM을 자체 모델이 아닌 Gemini 2.5 Flash API로 대체한 이유이기도 하다.