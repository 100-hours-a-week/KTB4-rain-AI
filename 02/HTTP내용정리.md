# HTTP

## 🚀 개념 정리

| 단어 | 뜻 | 사용 이유 |
|---|---|---|
| HTTP | 웹에서 클라이언트와 서버가 데이터를 주고받기 위한 통신 규약 | 서버와 클라이언트가 정해진 규칙에 따라 데이터를 주고받기 위해 |
| HTTP Message | HTTP에서 데이터를 주고받을 때 사용하는 메시지 형식 | 요청과 응답 데이터를 구조화하기 위해 |
| HTTP Method | 서버에게 어떤 작업을 수행할지 알려주는 요청 방식 | 조회, 생성, 수정, 삭제 작업을 구분하기 위해 |
| HTTP Status Code | 요청 처리 결과를 나타내는 코드 | 요청 성공 여부나 오류 상태를 명확히 전달하기 위해 |
| URL | 웹 자원의 위치를 나타내는 주소 | 특정 서버와 리소스에 접근하기 위해 |

---

## 📝 설명

# 1. HTTP

> HTTP(HyperText Transfer Protocol)는 웹에서 클라이언트와 서버가 데이터를 주고받기 위한 통신 규약이다.

> HTML, CSS, JS, 이미지 파일, JSON 등 구조화된 데이터를 전송할 때 사용한다.

### 사용 이유

- 웹 서버와 클라이언트가 동일한 규칙으로 통신하기 위해
- 다양한 시스템 간 통신 방식을 표준화하기 위해
- 데이터를 효율적으로 요청하고 응답하기 위해

```text
클라이언트(Request) ←————————→ 서버(Response)
```

예시:

사용자가 브라우저에서 네이버를 접속하면

```text
브라우저 → "메인 페이지 주세요"
서버 → "여기 HTML 파일입니다"
```

이 과정이 HTTP 통신이다.

---

## 1-1. HTTP Message

> HTTP에서 데이터를 주고받는 기본 단위

HTTP Message는 다음 구조를 가진다.

| 순서 | 이름 | 설명 |
|---|---|---|
| 1 | Start Line | 요청 또는 응답의 첫 줄 |
| 2 | Header | 부가 정보 |
| 3 | Empty Line | Header와 Body를 구분 |
| 4 | Body | 실제 데이터 |

구조 예시

```text
POST /posts HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
 "title":"HTTP 공부",
 "content":"열심히..."
}
```

### Start Line

요청 방식과 URL 정보가 들어간다.

예시

```text
GET /posts HTTP/1.1
```

구성:

- GET → 요청 메소드
- /posts → 요청 주소
- HTTP/1.1 → HTTP 버전

---

## 1-2. HTTP Header

> 요청 또는 응답에 필요한 추가 정보

대표 Header

| 헤더 | 설명 |
|---|---|
| Host | 서버 주소 |
| User-Agent | 브라우저 정보 |
| Content-Type | 데이터 형식 |
| Content-Length | 데이터 크기 |
| Authorization | 로그인 인증 정보 |

예시

```text
Content-Type: application/json
```

의미:

```text
"보내는 데이터는 JSON 형식입니다."
```

---

## 1-3. HTTP Body

> 실제 데이터를 담는 공간

GET 요청은 일반적으로 Body를 사용하지 않는다.

POST 요청 예시

```json
{
    "title":"제목",
    "content":"내용"
}
```

FastAPI에서는 Body 데이터를 Pydantic으로 자동 검증 가능

```python
from pydantic import BaseModel

class PostCreate(BaseModel):
    title:str
    content:str
```

자동 검증 내용:

- title 존재 여부
- content 존재 여부
- 데이터 타입 일치 여부

검증 실패 시:

```text
422 Unprocessable Entity
```

반환

---

## 1-4. HTTP Method

> 서버에게 어떤 작업을 수행할지 알려주는 규칙

| Method | 의미 | Body |
|---|---:|---|
| GET | 데이터 조회 | ❌ |
| POST | 데이터 생성 | ⭕ |
| PUT | 전체 수정 | ⭕ |
| PATCH | 일부 수정 | ⭕ |
| DELETE | 삭제 | 🔺 |

예시

게시글 조회

```text
GET /posts
```

게시글 생성

```text
POST /posts
```

게시글 삭제

```text
DELETE /posts/3
```

FastAPI 예시

```python
@app.get("/posts")
def get_posts():
    return posts


@app.post("/posts")
def create_post(post:PostCreate):
    return post
```

---

## 1-5. HTTP Status Code

> 서버가 요청 결과를 알려주는 코드

| 코드 | 설명 |
|---|---|
| 1xx | 정보 |
| 2xx | 성공 |
| 3xx | 리다이렉트 |
| 4xx | 클라이언트 오류 |
| 5xx | 서버 오류 |

자주 사용하는 코드

| 코드 | 의미 | 예시 |
|---|---|---|
| 200 | 요청 성공 | 조회 성공 |
| 201 | 생성 성공 | 게시글 생성 |
| 204 | 응답 없음 | 삭제 완료 |
| 400 | 잘못된 요청 | 데이터 누락 |
| 401 | 인증 필요 | 로그인 필요 |
| 403 | 권한 없음 | 관리자 접근 |
| 404 | 없음 | 게시글 없음 |
| 422 | 데이터 검증 실패 | 필수값 누락 |
| 500 | 서버 오류 | 코드 문제 |

---

## 1-6. URL

> 웹 자원의 위치를 나타내는 주소

예시

```text
https://example.com:443/posts/1?sort=latest
```

구조

```text
https://example.com:443/posts/1?sort=latest
   ↓          ↓          ↓
scheme    domain      path
```

| 구성요소 | 설명 |
|---|---|
| Scheme | http, https |
| Domain | 서버 주소 |
| Port | 포트 번호 |
| Path | 리소스 위치 |
| Query | 추가 정보 |

예시

```text
/posts?sort=latest
```

latest 기준 정렬 요청

---

## 2. FastAPI에서 HTTP

FastAPI는 HTTP 요청을 받아 처리하고 응답한다.

실행 과정:

```text
브라우저

↓

GET /posts 요청

↓

FastAPI 서버

↓

JSON 응답
```

예시 코드

```python
from fastapi import FastAPI
from pydantic import BaseModel

app=FastAPI()

posts=[]

class PostCreate(BaseModel):
    title:str
    content:str

@app.get("/posts")
def get_posts():
    return posts


@app.post("/posts")
def create_post(post:PostCreate):

    posts.append(post)

    return {
        "message":"생성 완료",
        "post":post
    }
```

---

## 📌 정리

HTTP는 웹에서 데이터를 주고받기 위한 통신 규약이다.

클라이언트는 URL과 Method를 이용해 서버에 요청(Request)을 보내고 서버는 Status Code와 데이터를 포함한 Response를 반환한다.

FastAPI는 이러한 HTTP 요청과 응답을 쉽게 구현할 수 있도록 도와주는 프레임워크이다.

