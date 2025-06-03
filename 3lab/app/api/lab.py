from fastapi import Request, APIRouter, Depends, Cookie, WebSocket
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from pathlib import Path
import base64
import re
import io
from PIL import Image
from pydantic import confloat
from typing import Annotated
from pydantic import Field
from app.services.auth import oauth2_scheme
from app.services.bernsen import bernsen_binarization, singh_binarization, equbal_binarization
from typing import Optional
from uuid import uuid4
from app.tasks import equbal_binarization_task, bernsen_binarization_task, singh_binarization_task

from app.api.websocket import websocket_progress

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter()


class BinaryImagePayload(BaseModel):
    t: Annotated[float, Field(ge=0.0, le=1.0)] = 0.5
    image: str  # base64
    algorithm: str


ALGORITHMS = ["Бернсен", "Эйквил", "Сингх"]


@router.get("/binary_image", response_class=HTMLResponse)
async def get_form(request: Request, access_token: Optional[str] = Cookie(None)):
    if not access_token:
        return RedirectResponse(url="/login")
    algorithms = ALGORITHMS
    return templates.TemplateResponse("binary_form.html", {
        "request": request,
        "algorithms": algorithms
    })


@router.post("/binary_image")
async def process_image(payload: BinaryImagePayload):
    if payload.algorithm not in ALGORITHMS:
        return JSONResponse(
                status_code=400,
                content={"error": "Неподдерживаемый алгоритм"})

    try:
        image_data = re.sub("^data:image/.+;base64,", "", payload.image)
    except Exception as e:
        return JSONResponse(
                status_code=400,
                content={"error": f"Ошибка декодирования изображения: {e}"})

    task_id = str(uuid4())

    if payload.algorithm == "Бернсен":
        bernsen_binarization_task.delay(task_id, image_data, t=payload.t)
    elif payload.algorithm == "Сингх":
        singh_binarization_task.delay(task_id, image_data, k=payload.t)
    elif payload.algorithm == "Эйквил":
        equbal_binarization_task.delay(task_id, image_data, k=payload.t)
    else:
        return {"error": "Неизвестный алгоритм"}

    return {"task_id": task_id}


@router.websocket("/ws/{task_id}")
async def websocket_endpoint(ws: WebSocket, task_id: str):
    await websocket_progress(ws, task_id)
