from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from schemas import Post, Comment
from database import create_tables, get_connection
from ai import model
from routers.post_router import router as post_router
from routers.comment_router import router as comment_router


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_tables()

app.include_router(post_router)
app.include_router(comment_router)


@app.get("/")
def home():
    return FileResponse("/Users/gimdayeon/KTB4-rain-AI/02/index.html")


@app.get("/posts/{id}")
def get_post(id:int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM posts WHERE id=?",
        (id,)
    )

    row = cursor.fetchone()

    conn.close()

    if row is None:
        return {"message":"게시글 없음"}

    return {
        "id": row["id"],
        "title": row["title"],
        "content": row["content"]
    }

@app.delete("/posts/{id}")
def delete_post(id:int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM posts WHERE id=?",
        (id,)
    )

    row = cursor.fetchone()

    if row is None:
        conn.close()
        return {"message":"게시글 없음"}

    cursor.execute(
        "DELETE FROM posts WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return {"message":"삭제 완료"}

@app.put("/posts/{id}")
def update_post(id:int, post:Post):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM posts WHERE id=?",
        (id,)
    )

    row = cursor.fetchone()

    if row is None:
        conn.close()
        return {"message":"게시글 없음"}

    cursor.execute(
        "UPDATE posts SET title=?, content=? WHERE id=?",
        (post.title, post.content, id)
    )

    conn.commit()
    conn.close()

    return {
        "id": id,
        "title": post.title,
        "content": post.content
    }


@app.get("/posts/{id}/summary")
def summarize_post(id:int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM posts WHERE id=?",
        (id,)
    )

    row = cursor.fetchone()

    conn.close()

    if row is None:
        return {"message":"게시글 없음"}

    response = model.generate_content(
        f"다음 게시글을 한 문장으로 요약해줘: {row['content']}"
    )

    return {
        "post_id": id,
        "summary": response.text
    }


@app.get("/posts/{post_id}/comments/{comment_index}/summary")
def summarize_comment(post_id:int, comment_index:int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM comments WHERE post_id=?",
        (post_id,)
    )

    rows = cursor.fetchall()

    conn.close()

    if comment_index < 1 or comment_index > len(rows):
        return {"message":"댓글 없음"}

    comment = rows[comment_index-1]

    response = model.generate_content(
        f"다음 댓글을 한 문장으로 요약해줘: {comment['content']}"
    )

    return {
        "post_id": post_id,
        "comment_index": comment_index,
        "summary": response.text
    }