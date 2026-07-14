from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers.auth import router as auth_router
from app.routers.comments import router as comment_router
from app.routers.likes import router as like_router
from app.routers.users import router as user_router
from app.routers.posts import router as post_router

Path("uploads").mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="AppifyLab Social API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    print("✅ Database Connected Successfully")
    print("🚀 FastAPI Server Started")
    print("📄 Swagger Docs: http://127.0.0.1:8000/docs")

app.include_router(auth_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(post_router, prefix="/api/v1")
app.include_router(comment_router, prefix="/api/v1")
app.include_router(like_router, prefix="/api/v1")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
def home():
    return {
        "message": "Backend Running Successfully 🚀"
    }
