from fastapi import FastAPI, Request, Form, APIRouter
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from pathlib import Path
import base64
from io import BytesIO
from PIL import Image
from pydantic import confloat

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter()

class BinaryImagePayload(BaseModel):
    t: confloat(ge=0.0, le=1.0) = 0.5
    image: str  # base64
    algorithm: str


@router.get("/binary_image", response_class=HTMLResponse)
async def get_form(request: Request):
    algorithms = ["Бернсен", "Брэдли и Рота", "Сингх"]
    return templates.TemplateResponse("binary_form.html", {
        "request": request,
        "algorithms": algorithms
    })


@router.post("/binary_image")
async def process_image(payload: BinaryImagePayload):
    try:
        image_data = base64.b64decode(payload.image.split(",")[-1])
        image = Image.open(BytesIO(image_data)).convert("L")

        # Тут вы бы применили выбранный алгоритм бинаризации:
        # result = apply_algorithm(image, payload.algorithm)

        return {"status": "success", "algorithm": payload.algorithm}
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
