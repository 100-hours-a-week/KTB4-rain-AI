# 02_FastAPI — 커뮤니티 

FastAPI를 사용하여 커뮤니티 REST API를 구현한 프로젝트입니다.

기본 CRUD 기능부터 SQLite 데이터베이스 연동, Gemini API 기반 AI 요약 기능까지 단계별로 구현하였습니다.

---

# 버전 구성

|기능|설명|상태|
|---|---:|---|
|메모리 기반 구현|리스트 활용 CRUD|✅|
|DB 연동|SQLite 적용|✅|
|AI 기능 추가|Gemini API 게시글 요약|✅|

---

# 공통 기능

- 게시글 생성
- 게시글 조회
- 댓글 작성
- 댓글 조회
- SQLite 저장
- AI 게시글 요약
- Swagger 테스트 지원

---

# 실행 방법

터미널:

```bash
uvicorn main:app --reload
```

실행 주소:

프론트:

```text
http://localhost:8001
```

Swagger:

```text
http://localhost:8001/docs
```

---

# 폴더 구조

```text
02/

├── README.md
├── HTTP내용정리.md
├── index.html

├── 학습노트/
│   ├── 01_프로젝트_시작과_FastAPI_구성.md
│   ├── 02_Router_분리와_API_구조화.md
│   ├── 03_SQLite_연동과_데이터_영구저장.md
│   └── 04_Gemini_API_연결과_AI기능_추가.md

├── routers/
│   ├── ai_router.py
│   ├── comment_router.py
│   └── post_router.py

├── ai.py
├── database.py
├── main.py
├── schemas.py
├── community.db
├── .env
└── .gitignore
```

---

# 설계 원칙

요청 흐름:

```text
사용자 요청

↓

Router

↓

Database 조회

↓

Gemini API 요청

↓

응답 반환
```

각 파일 역할:

- routers → URL 연결
- database.py → SQLite 연결
- ai.py → Gemini API 연결
- schemas.py → 데이터 형식
- main.py → FastAPI 실행

---

# 회고

▶ FastAPI 라우터 구조를 처음 적용

▶ SQLite 직접 연결 경험

▶ .env를 활용한 API KEY 분리

▶ Gemini API 연동 경험

- (솔직히 이번 위클리 챌린지는 AI 도움이 80% 였다. css는 100% ai 였다. 그래서 다시 처음 부터 해볼 예정이다. 내가 얼마나 이해하고 학습했는지 직접 눈으로 확인하고 싶다.
그리고 기능들도 부족한것 같다..시간 관계상 이번 위클리챌린지의 최대 노력이었지만 더 노력해야 함을 느꼈다.)
---


# 구현 과정 기록

- [01_프로젝트_시작과_FastAPI_구성](./학습노트/01_프로젝트_시작과_FastAPI_구성.md)

- [02_Router_분리와_API_구조화](./학습노트/02_Router_분리와_API_구조화.md)

- [03_SQLite_연동과_데이터_영구저장](./학습노트/03_SQLite_연동과_데이터_영구저장.md)

- [04_Gemini_API_연결과_AI기능_추가](./학습노트/04_Gemini_API_연결과_AI기능_추가.md)

---

