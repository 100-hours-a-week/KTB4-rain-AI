# 한국어 Mini-GPT 챗봇 (5주차)

한국어 위키백과와 FineWeb-2 데이터로 처음부터 학습시킨 5,400만 파라미터 규모의
Decoder-only Transformer 언어모델. BPE 토크나이저 직접 구현, 모델 설계, 학습,
추론, FastAPI 서빙까지 전 과정을 직접 구현했다.

## 과제 요구사항
[ 한국어 또는 영어 챗봇을 만드세요. ]

1. 사용자가 문장을 넣으면 다음 단어를 생성하는 모델을 만드세요.
2. 그 모델을 재귀 반복적(autoregressive)으로 사용하여 완전한 문장을 생성하세요.
3. FastAPI로 감싸서 웹에서 사용할 수 있도록 하세요.

## 개요

처음에는 한국어 문장 100개 정도의 소규모 데이터로 챗봇을 만들었으나, 정성 평가
결과 의미 있는 문장을 거의 생성하지 못했다. 데이터 규모가 근본적인 원인이라고
판단해, 위키백과와 FineWeb-2 한국어 데이터를 합쳐 13.6GB 코퍼스로 처음부터
다시 구축하고 모델을 재학습시켰다.

**핵심 목표**
- Decoder-only Transformer를 라이브러리 없이 PyTorch로 직접 구현
- 대규모 한국어 코퍼스로 처음부터(from scratch) 학습
- FastAPI로 서빙해 웹에서 사용 가능하도록 구현

## 아키텍처
데이터 수집 (위키백과 + FineWeb-2)
↓
data_preprocess.py  →  corpus.txt (13.6GB)
↓
tokenizer.py         →  tokenizer.model / tokenizer.vocab (BPE, vocab=16,000)
↓
(토큰화, uint16)      →  tokens.bin (5.69GB, 총 30.5억 토큰)
↓
train.py (Colab A100) →  minigpt.pt (54.3M params, 30,000 steps)
↓
inference.py          →  generate() — temperature/top-k 샘플링
↓
main.py (FastAPI)     →  POST /generate — Swagger UI(/docs)로 테스트


데이터 수집, 토큰화, 학습은 Google Colab(A100 GPU)에서 수행했고,
추론 서버(FastAPI)는 로컬 환경(Mac)에서 실행한다.

## 기술 스택

| 영역 | 선택 | 비고 |
|---|---|---|
| 프레임워크 | PyTorch (직접 구현) | 외부 GPT 라이브러리 없이 Attention/Block/Model 전부 직접 작성 |
| 토크나이저 | SentencePiece BPE | vocab_size=16,000, character_coverage=0.9995 |
| 데이터 | 위키백과 + FineWeb-2 | 총 13.6GB, 3,054,800,116개 토큰 |
| 학습 환경 | Google Colab A100 GPU | 로컬(Mac)은 GPU 미보유로 학습 불가, 추론만 가능 |
| 서빙 | FastAPI + Uvicorn | POST /generate, Swagger UI 자동 제공 |

## 모델 구조

| 항목 | 값 |
|---|---|
| n_layer (Transformer Block 수) | 12 |
| n_head (Attention Head 수) | 8 |
| n_embd (임베딩 차원) | 512 |
| block_size (컨텍스트 길이) | 256 |
| vocab_size | 16,000 |
| dropout | 0.1 |
| **총 파라미터 수** | **54,289,408개 (54.3M)** |

**구성 요소** (`model.py`)
- `MultiHeadAttention`: `scaled_dot_product_attention` 기반 Self-Attention (causal mask 적용)
- `FeedForward`: 4배 확장 후 GELU 활성화
- `TransformerBlock`: Attention + FeedForward + Residual Connection, 12개 스택
- `MiniGPT`: 토큰 임베딩 + 위치 임베딩 → 12개 Block → 다음 토큰 예측
- `generate()`: temperature/top-k 샘플링 기반 autoregressive 문장 생성

## 학습 결과

| Step | val_loss |
|---|---|
| 0 | 9.4564 |
| 2,000 | 4.7626 |
| 10,000 | 4.0261 |
| 20,000 | 3.8042 |
| 29,500 (최종) | **3.7147** |

- Optimizer: AdamW (lr=1e-3, cosine decay)
- Batch size: 128, Steps: 30,000
- 학습 토큰: 2,749,320,104개 / 검증 토큰: 305,480,012개

## 실험 결과 (정성 평가)

문법적으로 완결된 한국어 문장은 생성하지만, 질문의 의도를 이해하고 답하는
능력은 없다 — 다음 단어 예측만 학습했기 때문이다.

- 입력: `"인공지능이란"` → 문법적으로 자연스러운 문장 생성 (사실 정확도는 미보장)
- 입력: `"조선의 역사에 대해 설명해줄수 있어?"` (질의응답 형태) → 질문 의도를 반영하지
  못하고 특정 단어를 반복하는 현상 확인

## 트러블슈팅

| 문제 | 원인 | 해결 |
|---|---|---|
| 초기 버전 성능 저조 | 학습 데이터가 문장 100개로 지나치게 소규모 | 위키백과+FineWeb으로 13.6GB까지 데이터 규모 확대 |
| 토큰화 중 반복적 중단 | 30억 개 토큰을 한 번에 메모리에 올려 처리 시도 | 50,000줄 배치 단위로 나눠 처리하고 매번 파일에 flush하는 방식으로 변경 |
| Colab 세션 재시작 시 `MiniGPT is not defined` 등 에러 | 세션이 끊기면 이전에 정의한 변수/클래스가 전부 초기화됨 | 새 세션마다 라이브러리 설치 → 드라이브 마운트 → 모델 클래스 재정의 순서로 재실행 |
| `git push` 시 `File minigpt.pt is 207.14 MB; exceeds GitHub's file size limit` | 학습된 모델 체크포인트(207MB)가 GitHub 100MB 제한 초과 | `.gitignore`에 `05/minigpt.pt` 추가, 커밋 히스토리에서도 제거 후 재커밋 |
| `git push` 시 `rejected (fetch first)` / `non-fast-forward` | 로컬과 원격(origin) 브랜치가 서로 다른 커밋을 가진 상태로 분기됨 | `git pull` 후 merge 방식으로 병합, 충돌 파일은 수동으로 정리 후 재커밋 |
| `CONFLICT (modify/delete): 05/README.md` | 로컬에서는 파일을 삭제, 원격에서는 같은 파일이 수정된 상태로 충돌 | 최신 문서(`MiniGPT.md`)로 대체하기로 하고 `git rm`으로 삭제 확정 |
| 질의응답형 입력에 대해 특정 단어를 반복 생성 | 순수 다음 단어 예측 모델은 질문 의도를 반영하도록 학습된 적이 없음 | 한계점으로 기록. RAG(6주차) 단계에서는 자체 모델 대신 Gemini 2.5 Flash를 답변 생성기로 사용 |

## 파일 구조

\`\`\`
05/
├── data_preprocess.py   # 위키백과 + FineWeb 다운로드/전처리 → corpus.txt
├── tokenizer.py           # SentencePiece BPE 토크나이저 학습
├── model.py               # MiniGPT 모델 정의 (Transformer 구조)
├── train.py                # 학습 루프 (AdamW, cosine decay, 30,000 steps)
├── inference.py           # 문장 생성 (autoregressive generate)
├── main.py                 # FastAPI 서빙 (POST /generate)
├── minigpt.pt              # 학습된 모델 가중치 (용량 문제로 gitignore, 로컬 보관)
├── tokenizer.model         # 학습된 토크나이저
└── MiniGPT.md              # 상세 기술 문서
\`\`\`
## 실행 방법

```bash
# 1. 라이브러리 설치
pip3 install torch fastapi uvicorn sentencepiece numpy

# 2. 모델 구조 확인 (파라미터 수 출력)
python3 model.py

# 3. 서버 실행
python3 main.py

# 4. Swagger UI에서 테스트
# http://localhost:8000/docs
```

## 앞으로 개선할 점

- 질의응답 형태 입력에 대응하기 위한 Q&A 포맷 파인튜닝 (다음 단어 예측 → 지시문 이해)
- 반복 생성(repetition) 완화를 위한 repetition penalty 적용
- 6주차 RAG 파이프라인에 자체 모델을 연동할 경우, "생성형" 대신 "추출형(Span
  Extraction)" 방식(문서에서 정답 구간을 찾아 반환) 도입 검토

## 회고

- 처음에는 한국어 문장 100개 정도의 소규모 데이터로 시작했으나, 정성 평가에서
  의미 있는 문장을 거의 생성하지 못해 데이터 규모를 대폭 늘려 재구축했다.
- 위키백과와 FineWeb-2를 합쳐 13.6GB 코퍼스로 처음부터 다시 학습시킨 결과,
  검증 손실이 9.45 → 3.71까지 감소했고 문법적으로 완결된 문장을 생성하게 됐다.
- 순수 다음 단어 예측 방식은 질의응답이나 RAG 활용에는 한계가 있다는 것을
  실험을 통해 직접 확인했다. 이는 6주차 RAG 작업에서 LLM을 자체 모델이 아닌
  Gemini 2.5 Flash API로 대체한 이유이기도 하다.
- 학습 자체보다 Colab 세션 관리, GitHub 대용량 파일 처리, 브랜치 충돌 해결 등
  주변 인프라 이슈에 예상보다 많은 시간을 썼다. 이 과정에서 겪은 문제들을
  트러블슈팅 표로 남겨 다음 주차 작업 시 참고할 수 있도록 정리했다.

---

상세한 데이터/모델/학습 과정은 [MiniGPT.md](./MiniGPT.md) 참고.
