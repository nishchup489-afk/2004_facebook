import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.router import routers


load_dotenv()

FRONTEND_API_URL = os.getenv("FRONTEND_API_URL")


app = FastAPI()


allowed_origins = [
    "http://127.0.0.1:3000",
    "http://localhost:3000",
]

if FRONTEND_API_URL:
    allowed_origins.append(
        FRONTEND_API_URL.rstrip("/")
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "2004 Facebook API"
    }

for router in routers:
    app.include_router(router)

