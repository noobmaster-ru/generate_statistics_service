from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import  JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import pandas as pd
import matplotlib.pyplot as plt
import io
from generate_statistics import generate_weekly_statistics, generate_daily_statistics
import psutil
import time
import base64
from fastapi.responses import JSONResponse
from fastapi import HTTPException, UploadFile
import asyncio
import matplotlib
matplotlib.use('Agg')  


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def build_base64_json_response(fig, json_payload):
    try:
        img_bytes = await asyncio.to_thread(_matplotlib_figure_to_png_bytes, fig)
        img_base64 = base64.b64encode(img_bytes).decode()
        plt.close(fig)
        return {"image_base64": img_base64, **json_payload}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rendering graph: {str(e)}")

def _matplotlib_figure_to_png_bytes(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight') # dpi = 80 maybe
    buf.seek(0)
    plt.close(fig) 
    return buf.getvalue()


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
        df = pd.read_csv(file, sep=";", dtype=str, keep_default_na=False)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading CSV: {str(e)}")

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
        raise HTTPException(status_code=400, detail=f"Expected minimum 14 rows of data (no header), received: {len(df)}")

    if list(df.columns) != list(expected_columns.keys()):
        raise HTTPException(status_code=400, detail="Incorrect or missing column names")


    for col, expected_type in expected_columns.items():
        for i, val in enumerate(df[col], start=2):  
            try:
                if expected_type == "datetime":
                    try:
                        pd.to_datetime(val, format="%Y-%m-%d")
                    except Exception as e:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Column '{col}', row {i}: value '{val}' does not match the type {expected_type} — {e}"
                        )
                elif expected_type == int:
                    try:
                        int(val)
                    except Exception as e:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Column '{col}', row {i}: value '{val}' does not match the type {expected_type} — {e}"
                        )
                elif expected_type == float:
                    try:
                        float(val)
                    except Exception as e:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Column '{col}', row {i}: value '{val}' does not match the type {expected_type} — {e}"
                        )
                else:
                    raise HTTPException(
                            status_code=400,
                            detail=f"Column '{col}', row {i}: value '{val}' does not match the type {expected_type} — {e}"
                        )
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=f"Column '{col}', row {i}: value'{val}' does not match the type {expected_type} — {e}"
                )
    return df



@app.post("/get-image-daily")
async def daily_statistics(
    file1: UploadFile = File(...), 
    file2: UploadFile = File(...),
    token_id: str = Form(...),
    supplier_id: str = Form(...),
    cabinet_name: str = Form(...),
):
    try:
        df1 = read_csv_safe(file1.file) 
        df2 = read_csv_safe(file2.file) 
         
        start = time.perf_counter()
        fig = generate_daily_statistics(df1, df2)
        duration = time.perf_counter() - start

        mem = psutil.Process().memory_info().rss / 1024**2
        logger.info(f"PLot making time = {duration:.2f}s, memory: {mem:.1f} MB")

        json_payload = {
            "token_id": token_id,
            "supplier_id": supplier_id,
            "cabinet_name": cabinet_name,
        }

        plt.close(fig)
        return await build_base64_json_response(fig, json_payload)
    
    except HTTPException as e:
        # data error 
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    except Exception as e:
        # server error
        return JSONResponse(status_code=500, content={"Error": str(e)})


@app.post("/get-image-weekly")
async def weekly_statistics(
    file: UploadFile = File(...),
    token_id: str = Form(...),
    supplier_id: str = Form(...),
    cabinet_name: str = Form(...),
):
    try:
        df = read_csv_safe(file.file) 

        start = time.perf_counter()
        fig = generate_weekly_statistics(df)
        duration = time.perf_counter() - start

        mem = psutil.Process().memory_info().rss / 1024**2
        logger.info(f"PLot making time =  {duration:.2f}s, memore: {mem:.1f} MB")

        json_payload = {
            "token_id": token_id,
            "supplier_id": supplier_id,
            "cabinet_name": cabinet_name,
        }
        plt.close(fig)
        return await build_base64_json_response(fig, json_payload)
    except HTTPException as e:
        # data error
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    except Exception as e:
        # server error
        return JSONResponse(status_code=500, content={"Error": str(e)})

