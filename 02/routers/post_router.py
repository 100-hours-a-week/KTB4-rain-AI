from fastapi import APIRouter
from schemas import Post
from database import get_connection

router = APIRouter()


@router.get("/posts")
def get_posts():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM posts")

    rows = cursor.fetchall()

    conn.close()

    result=[]

    for row in rows:
        result.append({
            "id":row["id"],
            "title":row["title"],
            "content":row["content"]
        })

    return result


@router.post("/posts")
def create_post(post:Post):

    conn=get_connection()
    cursor=conn.cursor()

    cursor.execute(
        "INSERT INTO posts (title,content) VALUES (?,?)",
        (post.title,post.content)
    )

    conn.commit()

    post_id=cursor.lastrowid

    conn.close()

    return{
        "id":post_id,
        "title":post.title,
        "content":post.content
    }