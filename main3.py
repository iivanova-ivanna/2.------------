from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# "База данных" прямо в памяти — несколько постов
posts = {
    17: {"id": 17, "text": "Мой первый пост", "imageUrl": "https://images.pexels.com/photos/39315274/pexels-photo-39315274.jpeg", "likesCount": 3, "likedBy": set(), "comments": []},
    18: {"id": 18, "text": "Изучаю FastAPI, это интересно!", "imageUrl": "https://images.pexels.com/photos/19227922/pexels-photo-19227922.jpeg", "likesCount": 0, "likedBy": set(), "comments": []},
    19: {"id": 19, "text": "Сегодня разбирали клиент-серверную архитектуру", "imageUrl": "https://images.pexels.com/photos/39226797/pexels-photo-39226797.jpeg", "likesCount": 1, "likedBy": set(), "comments": []},
}

next_comment_id = 1


class CommentCreate(BaseModel):
    text: str
    author: str


@app.get("/api/posts")
def get_posts(username: str = "anonymous"):
    return [
        {
            "id": p["id"],
            "text": p["text"],
            "imageUrl": p["imageUrl"],   # ← новая строка
            "likesCount": p["likesCount"],
            "isLikedByMe": username in p["likedBy"],
            "commentsCount": len(p["comments"]),
        }
        for p in posts.values()
    ]


@app.post("/api/posts/{post_id}/like")
def like_post(post_id: int, username: str = "anonymous"):
    post = posts.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if username not in post["likedBy"]:
        post["likedBy"].add(username)
        post["likesCount"] += 1

    return {
        "postId": post_id,
        "likesCount": post["likesCount"],
        "isLikedByMe": True,
    }


@app.delete("/api/posts/{post_id}/like")
def unlike_post(post_id: int, username: str = "anonymous"):
    post = posts.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if username in post["likedBy"]:
        post["likedBy"].discard(username)
        post["likesCount"] -= 1

    return {
        "postId": post_id,
        "likesCount": post["likesCount"],
        "isLikedByMe": False,
    }


@app.get("/api/posts/{post_id}/comments")
def get_comments(post_id: int):
    post = posts.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return post["comments"]


@app.post("/api/posts/{post_id}/comments", status_code=201)
def create_comment(post_id: int, comment: CommentCreate):
    global next_comment_id

    post = posts.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if not comment.text.strip():
        raise HTTPException(status_code=422, detail="Comment text cannot be empty")
    if not comment.author.strip():
        raise HTTPException(status_code=422, detail="Author cannot be empty")

    new_comment = {
        "id": next_comment_id,
        "postId": post_id,
        "author": comment.author,
        "text": comment.text,
    }
    post["comments"].append(new_comment)
    next_comment_id += 1

    return new_comment
