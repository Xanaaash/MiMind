from pathlib import Path

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app import app as api_app


ROOT_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = ROOT_DIR / "frontend"
USER_DIST = FRONTEND_DIR / "user" / "dist"
ADMIN_DIR = FRONTEND_DIR / "admin"

api_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if ADMIN_DIR.exists():
    api_app.mount(
        "/admin",
        StaticFiles(directory=str(ADMIN_DIR), html=True),
        name="admin-frontend",
    )

if USER_DIST.exists():
    api_app.mount(
        "/",
        StaticFiles(directory=str(USER_DIST), html=True),
        name="user-frontend",
    )
elif FRONTEND_DIR.exists():
    api_app.mount(
        "/",
        StaticFiles(directory=str(FRONTEND_DIR), html=True),
        name="frontend",
    )

app = api_app
