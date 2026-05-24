from fastapi import APIRouter
from schemas import Comment
from database import get_connection

router = APIRouter()


@router.post("/posts/{post_id}/comments")
def create_comment(post_id:int, comment:Comment):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO comments (post_id, content) VALUES (?, ?)",
        (post_id, comment.content)
    )

    conn.commit()

    comment_id = cursor.lastrowid

    conn.close()

    return {
        "id": comment_id,
        "post_id": post_id,
        "content": comment.content,
        "message":"댓글 등록 완료"
    }


@router.get("/posts/{post_id}/comments")
def get_comments(post_id:int):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM comments WHERE post_id=?",
        (post_id,)
    )

    rows = cursor.fetchall()

    conn.close()

    result=[]

    for row in rows:
        result.append({
            "id": row["id"],
            "post_id": row["post_id"],
            "content": row["content"]
        })

    return result