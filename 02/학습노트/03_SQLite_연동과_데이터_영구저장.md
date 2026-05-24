# 03 SQLite 연동과 데이터 영구 저장

## SQLite를 선택한 이유

이번 과제에서는 복잡한 ORM보다 데이터베이스의 기본 흐름을 이해하는 것이 더 중요하다고 생각했다.

그래서 SQLModel 대신 Python에 기본 내장된 `sqlite3`를 사용하였다.

SQLite의 장점:

- Python에 기본 포함되어 별도 설치 부담이 적다.
- 작은 프로젝트에서 사용하기 쉽다.
- SQL을 직접 작성하면서 DB 동작 흐름을 이해할 수 있다.
- `community.db` 파일 하나로 데이터가 저장된다.

---

## database.py 구조

```python
import sqlite3

DB_NAME = "community.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn
```

## 코드 설명

```python
sqlite3.connect(DB_NAME)
```

`community.db` 파일에 연결한다.

파일이 없으면 새로 생성된다.

```python
conn.row_factory = sqlite3.Row
```

DB에서 가져온 데이터를 딕셔너리처럼 사용할 수 있게 한다.

예를 들어:

```python
row["title"]
row["content"]
```

처럼 컬럼 이름으로 접근할 수 있다.

---

## 테이블 생성

```python
def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        content TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()
```

---

## posts 테이블

게시글 데이터를 저장하는 테이블이다.

|컬럼|설명|
|---|---|
|id|게시글 번호|
|title|게시글 제목|
|content|게시글 내용|

---

## comments 테이블

댓글 데이터를 저장하는 테이블이다.

|컬럼|설명|
|---|---|
|id|댓글 번호|
|post_id|댓글이 달린 게시글 번호|
|content|댓글 내용|

`post_id`를 사용해서 특정 게시글에 달린 댓글을 구분한다.

예를 들어:

```text
1번 게시글
 ├── 댓글 1
 └── 댓글 2
```

이런 관계를 만들 수 있다.

---

## 댓글 조회 흐름

```python
cursor.execute(
    "SELECT * FROM comments WHERE post_id=?",
    (post_id,)
)
```

이 SQL은 특정 게시글 번호에 해당하는 댓글만 가져온다.

예:

```text
/posts/1/comments
```

요청이 들어오면 `post_id`가 1인 댓글만 조회한다.

---

## commit()과 close()

```python
conn.commit()
```

DB에 변경사항을 실제로 저장한다.

```python
conn.close()
```

DB 연결을 닫는다.

INSERT, UPDATE, DELETE처럼 데이터가 바뀌는 작업에서는 `commit()`이 필요하다.

---

## 구현하면서 이해한 점

처음에는 DB가 따로 복잡하게 동작하는 것으로 느껴졌지만, 실제 흐름은 단순했다.

```text
FastAPI 요청
↓
get_connection()
↓
cursor.execute()
↓
SQLite 조회 또는 저장
↓
JSON 응답
```

즉, FastAPI가 요청을 받고 SQLite에 SQL을 실행한 뒤 결과를 다시 응답으로 보내는 구조였다.

---

## 정리

이번 단계에서 이해한 내용:

- SQLite는 Python에 내장된 가벼운 데이터베이스이다.
- `community.db` 파일에 데이터가 저장된다.
- `cursor.execute()`로 SQL을 실행한다.
- `post_id`를 통해 게시글과 댓글을 연결할 수 있다.