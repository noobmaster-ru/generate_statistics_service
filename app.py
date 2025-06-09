from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from loguru import logger
from io import BytesIO
from PIL import Image
import pandas as pd
import tinify 
# найти способ, как можно с опенсорсом сжать фото
import json
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

from generate_daily_statistics import generate_daily_statistics
from generate_weekly_statistics import generate_weekly_statistics
import psutil
import time
import base64
from fastapi.responses import JSONResponse

tinify.key = "Vc1ZzMhvsvNSkbVSzdD7ntP4mqHZV1vP"  # Заменить API ключ

app = FastAPI()

# Optional: CORS settings if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def build_base64_json_response(fig, json_payload: dict) -> JSONResponse:
    # Convert figure to PNG bytes
    img_bytes = fig.to_image(format="png")

    # Compress with TinyPNG
    source = tinify.from_buffer(img_bytes)
    compressed_img_bytes = source.to_buffer()

    # Encode image to base64
    encoded_image = base64.b64encode(compressed_img_bytes).decode("utf-8")

    # Add image to payload
    json_payload["image_base64"] = encoded_image

    return JSONResponse(content=json_payload)


@app.post("/get-image-daily")
async def daily_statistics(
    file1: UploadFile = File(...),
    file2: UploadFile = File(...),
    token_id: str = Form(...),
    supplier_id: str = Form(...),
    cabinet_name: str = Form(...),
):
    try:
        logger.info(f"Received files: {file1.filename}, {file2.filename}")
        df1 = pd.read_csv(file1.file, sep=";")
        df2 = pd.read_csv(file2.file, sep=";")

        fig = generate_daily_statistics(df1, df2)

        json_payload = {
            "token_id": token_id,
            "supplier_id": supplier_id,
            "cabinet_name": cabinet_name,
        }

        return build_base64_json_response(fig, json_payload)

    except Exception as e:
        logger.exception("Error generating daily stats")
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/get-image-weekly")
async def weekly_statistics(
    file: UploadFile = File(...),
    token_id: str = Form(...),
    supplier_id: str = Form(...),
    cabinet_name: str = Form(...),
):
    try:
        logger.info(f"Received file: {file.filename}")
        df = pd.read_csv(file.file, sep=";")

        start = time.perf_counter()
        fig = generate_weekly_statistics(df)
        duration = time.perf_counter() - start

        mem = psutil.Process().memory_info().rss / 1024**2
        logger.info(f"📊 График построен за {duration:.2f}s, память: {mem:.1f} MB")

        json_payload = {
            "token_id": token_id,
            "supplier_id": supplier_id,
            "cabinet_name": cabinet_name,
        }

        return build_base64_json_response(fig, json_payload)

    except Exception as e:
        logger.exception("Error generating weekly stats")
        return JSONResponse(status_code=500, content={"error": str(e)})
