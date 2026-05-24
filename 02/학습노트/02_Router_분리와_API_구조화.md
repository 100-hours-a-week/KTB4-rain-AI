# 02 Router 분리와 API 구조화

## 목표

처음에는 `main.py` 안에 모든 API 코드를 작성하였다.

하지만 게시글, 댓글, AI 기능이 늘어나면서 코드가 길어졌고, 기능별로 파일을 나누는 구조가 필요했다.

그래서 `routers` 폴더를 만들고 기능별 라우터 파일을 분리하였다.

---

## 현재 라우터 구조

```text
02/
├── routers/
│   ├── post_router.py
│   ├── comment_router.py
│   └── ai_router.py
```

각 파일 역할:

|파일|역할|
|---|---|
|post_router.py|게시글 작성, 목록 조회 기능|
|comment_router.py|댓글 작성, 댓글 목록 조회 기능|
|ai_router.py|AI 요약 기능 분리용 파일|

---

## APIRouter 사용

FastAPI에서는 `APIRouter`를 사용해 API 기능을 파일별로 나눌 수 있다.

예시:

```python
from fastapi import APIRouter

router = APIRouter()
```

기존에는 `main.py`에서 바로 작성했던 코드를:

```python
@app.get("/posts")
def get_posts():
    ...
```

라우터 파일에서는 아래처럼 작성한다.

```python
@router.get("/posts")
def get_posts():
    ...
```

---

## main.py에서 라우터 연결

분리한 라우터는 `main.py`에서 다시 연결해준다.

```python
from routers.post_router import router as post_router
from routers.comment_router import router as comment_router

app.include_router(post_router)
app.include_router(comment_router)
```

이렇게 하면 실제 API 주소는 그대로 유지하면서, 코드만 기능별 파일로 나눌 수 있다.

---

## API 흐름

```text
사용자 요청
↓
main.py
↓
include_router()
↓
post_router.py 또는 comment_router.py
↓
DB 처리
↓
JSON 응답
```

---

## 구현하면서 이해한 점

라우터를 나눈다고 해서 API 주소가 바뀌는 것은 아니었다.

예를 들어 `GET /posts`는 그대로 유지되지만, 코드 위치만 `main.py`에서 `post_router.py`로 이동한다.

즉, 라우터 분리는 기능을 바꾸는 것이 아니라 **코드 구조를 정리하는 작업**이었다.

---

## 정리

이번 단계에서 이해한 내용:

- `main.py`에 모든 코드를 넣으면 관리가 어려워진다.
- `APIRouter`를 사용하면 기능별로 파일을 분리할 수 있다.
- `include_router()`를 통해 분리된 라우터를 FastAPI 앱에 연결한다.
- 구조를 나누면 README에서 프로젝트 구조를 더 명확하게 설명할 수 있다.
- (너무 많은데 기억이 안난다.. 앞으로는 바로바로 기록하자)