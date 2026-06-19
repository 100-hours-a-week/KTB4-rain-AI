# 🤖 MiniGPT-Korean

> GPT 스타일 Decoder Transformer를 **처음부터 직접 구현**한 한국어 챗봇입니다.
> 사전학습 모델 없이 From Scratch로 설계·구현했으며, FastAPI로 서빙까지 완성했습니다.

---

## 📌 프로젝트 개요

한국어 문장을 입력받아 다음 토큰을 예측하고, 이를 반복 생성하여 완전한 문장을 만드는 챗봇입니다.

- **과제 5-1**: 입력 문장을 받아 다음 글자 1개를 예측
- **과제 5-2**: 예측을 재귀적으로 반복하여 완전한 문장 생성 (Autoregressive)
- KoGPT2 같은 사전학습 모델을 쓰지 않고, **모델 구조를 직접 이해하고 구현**하는 것을 목표로 했습니다

---

## 🏗️ 아키텍처

```
사용자 입력 (브라우저)
        │
        ▼
  [FastAPI 서버]
  POST /api/next-word  →  다음 글자 1개 반환 (과제 5-1)
  POST /api/chat       →  완전한 문장 반환  (과제 5-2)
        │
        ▼
  [MiniGPT 모델]
  입력 토큰 ID 시퀀스
        │
        ▼
  토큰 임베딩 + 위치 임베딩 (N_EMBD=128)
        │
        ▼
  ┌─────────────────────────┐
  │  Masked Self-Attention  │
  │  Add & LayerNorm        │  × 4 layers
  │  Feed-Forward (GELU)    │
  │  Add & LayerNorm        │
  └─────────────────────────┘
        │
        ▼
  Linear + Softmax → vocab(251)에 대한 확률 분포
        │
        ▼
  Temperature / Top-k 샘플링 → 다음 토큰 선택 → 반복(Autoregressive)
```

---

## 📁 프로젝트 구조

```
MiniGPT-Korean/
├── app/
│   └── chat.py         # FastAPI 라우터 (/api/next-word, /api/chat)
├── model/
│   └── generator.py    # MiniGPT 모델 구조 + 학습 + 생성 함수
├── static/
│   ├── index.html      # 챗봇 웹 UI
│   ├── style.css       # 디자인
│   └── script.js       # fetch API 호출
├── state.py            # 전역 model, device 공유 (순환 임포트 방지)
├── main.py             # FastAPI 앱 시작점
├── data.txt            # 한국어 학습 데이터 (100문장)
└── requirements.txt    # 의존성 패키지
```

---

## ⚙️ 모델 구조 (GPT-style Decoder Transformer)

| 항목 | 값 |
|---|---|
| 모델 타입 | GPT-style Decoder Transformer |
| BLOCK_SIZE | 16 (한 번에 볼 수 있는 최대 글자 수) |
| N_EMBD | 128 (임베딩 차원) |
| N_HEAD | 4 (멀티헤드 어텐션) |
| N_LAYER | 4 (트랜스포머 블록 수) |
| DROPOUT | 0.1 |
| 토크나이저 | 글자 단위 (Character-level) |
| vocab 크기 | 251개 |
| 파라미터 수 | 855,040개 |
| 옵티마이저 | AdamW (lr=3e-4, weight_decay=0.1) |

---

## 🔁 Autoregressive 생성 방식

```python
# 과제 5-1: 다음 글자 1개 예측
def predict_next_token(model, text, device, temperature=0.8, top_k=50):
    ids = tokenizer.encode(text)[-BLOCK_SIZE:]
    logits = model(idx)                  # 모델에 넣기
    logits = logits / temperature        # temperature로 창의성 조절
    probs = softmax(top_k_filter(logits))  # top-k 필터 후 확률 계산
    next_id = multinomial(probs)         # 확률 비례 샘플링
    return tokenizer.decode(next_id)     # 글자로 변환

# 과제 5-2: 반복 생성 (Autoregressive)
def generate(model, text, device, max_new_tokens=100):
    result = text
    for _ in range(max_new_tokens):
        next_char = predict_next_token(model, result, ...)
        if next_char == EOS: break       # 문장 끝나면 멈춤
        result += next_char              # 글자 붙이기 반복!
    return result
```

---

## 🚀 실행 방법

```bash
# 1. 가상환경 설정
python3 -m venv venv
source venv/bin/activate

# 2. 패키지 설치
pip install -r requirements.txt

# 3. 모델 학습
python3 -c "
import torch
from model.generator import train
device = torch.device('cpu')
train('data.txt', device, steps=3000)
"

# 4. 서버 실행
python3 main.py

# 5. 브라우저에서 접속
# http://localhost:8000
```

---

## 🌐 API 엔드포인트

| 엔드포인트 | 메서드 | 설명 |
|---|---|---|
| `/api/next-word` | POST | 다음 글자 1개 반환 (과제 5-1) |
| `/api/chat` | POST | 완전한 문장 반환 (과제 5-2) |
| `/` | GET | 챗봇 웹 UI |
| `/docs` | GET | Swagger UI (API 문서) |

---

## 🐛 트러블슈팅

### 1. `<UNK>` 출력 문제
**증상**: 모델이 모든 입력에 대해 `<UNK>`만 출력함

**원인**: 토크나이저를 수동으로 글자 목록을 하드코딩해서 만들었는데, 실제 data.txt의 글자와 불일치

**해결**: `data.txt`를 읽어서 글자를 **자동으로 vocab 구성**하도록 수정
```python
class Tokenizer:
    def __init__(self, text=''):
        unique_chars = sorted(set(text))  # data.txt 글자로 자동 구성!
        self.stoi = {c: i for i, c in enumerate(all_chars)}
```

---

### 2. size mismatch 에러
**증상**: 모델 불러올 때 `RuntimeError: size mismatch` 에러 발생

**원인**: 기존 `minigpt.pt`가 이전 vocab 크기로 저장되어 있어서 새 모델과 크기가 안 맞음

**해결**: `rm model/minigpt.pt` 후 재학습

---

### 3. 순환 임포트 (Circular Import)
**증상**: 서버 실행 시 `ImportError` 또는 `model`이 `None`으로 들어옴

**원인**: `main.py` → `chat.py` → `main.py` 순환 참조
```
main.py가 chat.py를 import
  └→ chat.py가 main.py에서 model을 import
       └→ 💥 무한루프!
```

**해결**: `state.py` 파일을 분리해서 model과 device를 중립적인 공간에서 관리
```python
# state.py - 누구든 꺼내 쓸 수 있는 "공유 냉장고"
import torch
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = None
```

---

### 4. 한글 IME 중복 전송 버그
**증상**: "안녕" 입력 후 Enter를 누르면 채팅창에 "안녕"과 "녕"이 따로따로 두 번 전송됨

**원인**: 한글은 타이핑할 때 글자가 **조합되는 과정(IME Composition)**을 거침
Enter를 누르면 조합 확정 신호와 `keydown` 이벤트가 겹쳐서 마지막 글자가 두 번 처리됨

**해결**: `e.isComposing`으로 조합 중일 때는 이벤트 무시
```javascript
document.getElementById('userInput').addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.isComposing) {  // ✨ 핵심!
        sendMessage();
    }
});
```

---

## 🎯 설계 결정과 이유

| 결정 | 선택 | 이유 |
|---|---|---|
| 모델 | From Scratch 직접 구현 | 구조를 이해하고 설명할 수 있어야 포트폴리오 가치가 있음 |
| 토크나이저 | 글자 단위 (Character-level) | 한국어 형태소 분석 없이도 동작, 구조 이해에 집중 |
| 서빙 | FastAPI | 비동기 처리, 자동 API 문서(/docs), 실제 개발 환경과 동일 |
| 상태 관리 | state.py 분리 | 순환 임포트 방지, 어디서든 model에 접근 가능 |
| 프론트엔드 | Vanilla JS | 프레임워크 없이 fetch API로 직접 구현, 의존성 최소화 |

---

## 📚 이 프로젝트에서 배운 것들

### 딥러닝 개념
- **Self-Attention**: Q, K, V 행렬로 각 글자가 다른 글자들과 얼마나 관련있는지 계산
- **Masked Attention**: GPT처럼 미래 글자를 보지 못하게 막는 인과적 마스킹
- **잔차 연결 (Residual Connection)**: `x = x + attention(x)` — 깊은 네트워크에서 기울기 소실 방지
- **LayerNorm**: 각 레이어 출력을 정규화해서 학습 안정화
- **Temperature**: 높을수록 창의적, 낮을수록 보수적인 텍스트 생성
- **Top-k Sampling**: 확률 상위 k개 중에서만 다음 글자를 뽑아 품질 향상
- **Autoregressive 생성**: 글자를 하나씩 붙여가며 문장을 만드는 방식
- **Overfitting**: train loss는 낮은데 val loss가 높으면 데이터를 "외운" 상태

### 개발 개념
- **순환 임포트**: A가 B를 부르고 B가 A를 부르는 무한루프, `state.py`로 해결
- **IME Composition**: 한글 조합 입력 시 발생하는 브라우저 이벤트 특성
- **FastAPI 라우터**: `APIRouter`로 엔드포인트를 파일별로 분리 관리
- **전역 상태 관리**: 여러 모듈에서 공유해야 하는 변수는 별도 파일로 분리
- **AdamW**: Adam + Weight Decay, 과적합 방지에 효과적인 옵티마이저

---

## 📦 사용 라이브러리

| 라이브러리 | 버전 | 용도 |
|---|---|---|
| torch | 2.8.0 | MiniGPT 모델 구현 및 학습 |
| fastapi | 0.128.8 | API 서버 |
| uvicorn | 0.39.0 | ASGI 서버 |
| pydantic | 2.13.4 | 요청/응답 데이터 검증 |

---

## 📈 학습 결과

| 데이터 | steps | train loss | val loss |
|---|---|---|---|
| 24문장 | 3000 | 0.1483 | 5.3468 |
| 100문장 | 3000 | 0.2818 | 3.1299 ✅ |

> 데이터를 24문장 → 100문장으로 늘리자 val loss가 5.33 → 3.12로 크게 개선됐습니다.
