from fastapi import Request, APIRouter, Depends, Cookie
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
from app.services.bernsen import bernsen_binarization
from typing import Optional

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
        img_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(img_bytes)).convert("L")
    except Exception as e:
        return JSONResponse(
                status_code=400,
                content={"error": f"Ошибка декодирования изображения: {e}"})

    if payload.algorithm == "Бернсен":
        result_image = bernsen_binarization(image, t=payload.t)
#    elif payload.algorhtm == "Сингх":
#        result_image = binarize_singh(image, t=payload.t)
    else:
        # простая бинаризация как заглушка
        threshold = 128
        result_image = image.point(lambda p: 255 if p > threshold else 0)

    buffered = io.BytesIO()
    result_image.save(buffered, format="PNG")
    result_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    result_data_url = f"data:image/png;base64,{result_base64}"

    return {"image_result": result_data_url}
