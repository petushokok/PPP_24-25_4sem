from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.api.auth import router as auth_router
from app.api.lab import router as lab_router
from app.db.db import Base, engine
from pathlib import Path

Base.metadata.create_all(bind=engine)  # Создаём таблицы в SQLite
templates = Jinja2Templates(directory=str("app/templates"))

app = FastAPI()
app.include_router(auth_router)
app.include_router(lab_router)


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})
