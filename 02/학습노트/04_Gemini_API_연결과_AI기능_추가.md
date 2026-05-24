# 04 Gemini API 연결과 AI 기능 추가

## ai.py 구성

현재 코드:

```python
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

genai.configure(
    api_key=os.getenv("GEN_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)
```

---

## 코드 설명

```python
load_dotenv()
```

`.env` 파일 내용을 읽는다.

---

```python
os.getenv("GEN_API_KEY")
```

환경변수에 저장한 API KEY를 가져온다.

코드 안에 직접 API 키를 적지 않기 위해 사용하였다.

---

```python
genai.GenerativeModel(
    "gemini-2.5-flash"
)
```

Gemini 모델 객체 생성

이후:

```python
response = model.generate_content(
    "게시글 요약해줘"
)
```

형태로 사용할 수 있다.

---

## .env를 사용한 이유

API KEY를 코드 안에 직접 적으면 GitHub에 업로드될 수 있다.

그래서:

```text
.env
```

파일로 분리하였다.

또 `.gitignore`에 추가하였다.

```text
.env
```

```text
community.db
```

이렇게 설정하여 중요한 파일이 GitHub에 올라가지 않도록 구성하였다.

---

## 실제 사용한 API

게시글 요약:

```text
GET /posts/{id}/summary
```

댓글 요약:

```text
GET /posts/{post_id}/comments/{comment_index}/summary
```

예:

```text
/posts/1/summary
```

↓

게시글 조회

↓

Gemini 요청

↓

요약 결과 생성

↓

JSON 응답

---

## 전체 흐름

```text
브라우저

↓

FastAPI

↓

게시글 조회

↓

community.db

↓

Gemini API 요청

↓

요약 결과 반환
```

---

## 구현하면서 느낀 점

처음에는 AI 기능이 매우 복잡할 것이라고 생각했다.

하지만 실제로는 FastAPI에서 게시글 내용을 가져온 후, Gemini에 전달하고 결과를 응답하는 구조였다.

CRUD 기능과 AI 기능이 완전히 다른 것이 아니라, 기존 데이터 흐름 위에 AI를 추가하는 방식이라는 점을 이해할 수 있었다.

---

## 정리

이번 단계에서 이해한 내용:

- Gemini API 연결
- .env 환경변수 사용
- API KEY 보안 관리
- FastAPI + AI 기능 연결
- 게시글/댓글 요약 기능 구현