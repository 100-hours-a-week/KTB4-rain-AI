# 01 프로젝트 시작과 FastAPI 구성

## 목표

FastAPI를 활용하여 커뮤니티 REST API 프로젝트를 구성하였다.

초기에는 게시글 CRUD 기능을 중심으로 구현하고, 이후 데이터베이스 연동과 AI 기능까지 확장하는 것을 목표로 하였다.

---

## 프로젝트 구조 설계

처음부터 기능이 많아질 것을 고려하여 Router 기반 구조를 적용하였다.

구성:

```text
02/
├── routers/
├── main.py
├── schemas.py
├── index.html
└── README.md
```

각 파일 역할:

- main.py → FastAPI 앱 실행
- routers → API 기능 분리
- schemas.py → 데이터 형식 관리
- index.html → 간단한 프론트 화면
- README.md → 프로젝트 문서

---

## FastAPI 실행

실행 명령:

```bash
uvicorn main:app --reload
```

실행 후 확인:

```text
http://localhost:8001
```

Swagger 문서:

```text
http://localhost:8001/docs
```

FastAPI는 자동으로 API 문서를 생성해주기 때문에 테스트가 편리했다.

---

## 느낀 점

프로젝트가 커질수록 구조 설계가 중요하다는 것을 느꼈다.