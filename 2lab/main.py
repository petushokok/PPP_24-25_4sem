from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from app.api.auth import router as auth_router
from app.api.lab import router as lab_router
from app.db.db import Base, engine

Base.metadata.create_all(bind=engine)  # Создаём таблицы в SQLite

app = FastAPI()
app.include_router(auth_router)
app.include_router(lab_router)


@app.get("/")
def read_root():
    return {"message": "Auth API"}
