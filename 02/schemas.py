from pydantic import BaseModel

class Post(BaseModel):
    title: str
    content: str

class Comment(BaseModel):
    content: str