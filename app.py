from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from loguru import logger
from io import BytesIO
from PIL import Image
import pandas as pd
from pandas.errors import ParserError
import numpy as np

# найти способ, как можно с опенсорсом сжать фото
# варианты: Pillow, pngquant, OpenCV
from PIL import Image
import io
# import tinify 
import io
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
from fastapi import HTTPException, UploadFile
from datetime import datetime

# tinify.key = "Vc1ZzMhvsvNSkbVSzdD7ntP4mqHZV1vP"  # Заменить API ключ

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
    img_bytes = fig.to_image(format="png") # Convert a figure to a static image bytes string

    # Compress with TinyPNG
    # source = tinify.from_buffer(img_bytes)
    # compressed_img_bytes = source.to_buffer()
    
    # Pillow compress
    img = Image.open(io.BytesIO(img_bytes))
    buffer = io.BytesIO()

    # img.save(buffer, format="JPEG" ,quality=70)  # выдает ошибку:  {"error":"cannot write mode RGBA as JPEG"}
    img.save(buffer, format="WEBP", quality=70)  # Можно понизить quality для сильнее сжатия

    compressed_img_bytes = buffer.getvalue()

    # Encode image to base64
    encoded_image = base64.b64encode(compressed_img_bytes).decode("utf-8")

    # Add image to payload
    json_payload["image_base64"] = encoded_image

    return JSONResponse(content=json_payload)

# convert data to expected types in all dataframe
def cast_columns(df: pd.DataFrame, expected_columns: dict) -> pd.DataFrame:
    df = df.copy()

    for col, dtype in expected_columns.items():
        if col not in df.columns:
            raise HTTPException(status_code=400, detail = f"Column '{col}' is missing")

        if dtype == "datetime":
            df[col] = pd.to_datetime(df[col], errors="coerce")
        else:
            df[col] = pd.to_numeric(df[col], errors="coerce", downcast=None if dtype == float else "integer")

    return df

# 400 error - data error
def read_csv_safe(file: UploadFile) -> pd.DataFrame:
    try:
        # Читаем всё как строки, без автоматической подстановки NaN
        df = pd.read_csv(file, sep=";", dtype=str, keep_default_na=False)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка чтения CSV: {str(e)}")

    expected_columns = {
        "id": int,
        "date": "datetime",
        "open_card_count": int,
        "add_to_cart_count": int,
        "orders_count": int,
        "orders_sum_rub": int,
        "median_orders_sum_per_user": int,
        "median_drr": float,
        "avg_orders_sum_per_user": int,
        "drr": float,
        "views": int,
        "cliks": int,
        "sum": float,
    }
    # convert all data from df to expected types
    df = cast_columns(df, expected_columns)
    if len(df) < 14:
        raise HTTPException(status_code=400, detail=f"Ожидалось минимум 14 строк данных (без заголовка), получено: {len(df)}")

    if list(df.columns) != list(expected_columns.keys()):
        raise HTTPException(status_code=400, detail="Неверные или отсутствующие названия столбцов")

    # Проверка и преобразование значений
    for col, expected_type in expected_columns.items():
        for i, val in enumerate(df[col], start=2):  # +2 потому что первая строка — заголовки
            try:
                if expected_type == "datetime":
                    try:
                        pd.to_datetime(val, format="%Y-%m-%d")
                    except Exception as e:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Столбец '{col}', строка {i}: значение '{val}' не соответствует типу {expected_type} — {e}"
                        )
                elif expected_type == int:
                    try:
                        int(val)
                    except Exception as e:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Столбец '{col}', строка {i}: значение '{val}' не соответствует типу {expected_type} — {e}"
                        )
                elif expected_type == float:
                    try:
                        float(val)
                    except Exception as e:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Столбец '{col}', строка {i}: значение '{val}' не соответствует типу {expected_type} — {e}"
                        )
                else:
                    raise HTTPException(
                            status_code=400,
                            detail=f"Столбец '{col}', строка {i}: значение '{val}' не соответствует типу {expected_type} — {e}"
                        )
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Столбец '{col}', строка {i}: значение '{val}' не соответствует типу {expected_type} — {e}"
                )
    return df



@app.post("/get-image-daily")
async def daily_statistics(
    file1: UploadFile = File(...), # ("имя_файла", файловый_объект, "MIME-тип") - кортеж из 3 частей!
    file2: UploadFile = File(...),
    token_id: str = Form(...),
    supplier_id: str = Form(...),
    cabinet_name: str = Form(...),
):
    try:
        logger.info(f"Received files: {file1.filename}, {file2.filename}")

        # считываем csv с учетом возможных ошибок - если будет ошибка чтения, то сработает exception 
        df1 = read_csv_safe(file1.file) # read_csv_safe(file1.file)
        df2 = read_csv_safe(file2.file) # read_csv_safe(file2.file)

        fig = generate_daily_statistics(df1, df2) # делает фотографию типа Figure

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
        df = read_csv_safe(file.file) # pd.read_csv(file.file, sep=";")

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
