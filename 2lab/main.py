from fastapi import FastAPI
from app.api import auth
from app.db.db import Base, engine

Base.metadata.create_all(bind=engine)  # Создаём таблицы в SQLite

app = FastAPI()
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "Auth API"}
