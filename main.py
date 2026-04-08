import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.database import init_db
from routes.auth import router as auth_router
from routes.users import router as users_router
from routes.items import router as items_router

app = FastAPI(
    title="Usha Graphics Backend API",
    description="A FastAPI backend for user authentication, item management, and order processing",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(items_router)

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "FastAPI Backend is running",
        "docs": "/docs",
        "endpoints": {
            "register": "POST /auth/register",
            "login": "POST /auth/login",
            "me": "GET /users/me",
            "get_items": "GET /items/",
            "create_item": "POST /items/",
        }
    }