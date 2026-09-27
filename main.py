from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Разрешаем запросы с фронтенда, который открыт как отдельный html-файл
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# "База данных" прямо в памяти — для демо этого достаточно
posts = {
    17: {"id": 17, "text": "Мой первый пост", "likesCount": 3, "likedBy": set()}
}

CURRENT_USER = "demo_user"  # для простоты — один "пользователь" на всех


@app.get("/api/posts")
def get_posts():
    return [
        {
            "id": p["id"],
            "text": p["text"],
            "likesCount": p["likesCount"],
            "isLikedByMe": CURRENT_USER in p["likedBy"],
        }
        for p in posts.values()
    ]


@app.post("/api/posts/{post_id}/like")
def like_post(post_id: int):
    post = posts.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if CURRENT_USER not in post["likedBy"]:
        post["likedBy"].add(CURRENT_USER)
        post["likesCount"] += 1

    return {
        "postId": post_id,
        "likesCount": post["likesCount"],
        "isLikedByMe": True,
    }


@app.delete("/api/posts/{post_id}/like")
def unlike_post(post_id: int):
    post = posts.get(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if CURRENT_USER in post["likedBy"]:
        post["likedBy"].discard(CURRENT_USER)
        post["likesCount"] -= 1

    return {
        "postId": post_id,
        "likesCount": post["likesCount"],
        "isLikedByMe": False,
    }
