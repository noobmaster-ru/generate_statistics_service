import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import csv
import random
from dotenv import load_dotenv
load_dotenv()

# Константы
NUM_RECORDS = int(os.getenv("NUM_RECORDS")) 
RECORDS_PER_FILE = int(os.getenv("RECORDS_PER_FILE"))
NUM_FILES = NUM_RECORDS // RECORDS_PER_FILE
OUTPUT_DIR = "tests/failure_data"

# Генерация базовых данных
today_str = datetime.today().strftime("%Y-%m-%d")
initial_date = datetime.strptime(today_str, "%Y-%m-%d")
weekday = initial_date.weekday()
base_monday = initial_date - timedelta(days=weekday)

dates = [
    (base_monday + timedelta(days=(i // 13) * 13 + (i % 13))).strftime("%Y-%m-%d")
    for i in range(NUM_RECORDS)
]

data = {
    "id": [3] * NUM_RECORDS,
    "date": dates,
    "open_card_count": np.random.randint(4000, 12000, size=NUM_RECORDS),
    "add_to_cart_count": np.random.randint(800, 2000, size=NUM_RECORDS),
    "orders_count": np.random.randint(70, 250, size=NUM_RECORDS),
    "orders_sum_rub": np.random.randint(100000, 4000000, size=NUM_RECORDS),
    "median_orders_sum_per_user": np.random.randint(1000, 3000, size=NUM_RECORDS),
    "median_drr": np.round(np.random.uniform(0, 100, size=NUM_RECORDS), 2),
    "avg_orders_sum_per_user": np.random.randint(0, 10000, size=NUM_RECORDS),
    "drr": np.round(np.random.uniform(0, 100, size=NUM_RECORDS), 2),
    "views": np.random.randint(30000, 999999, size=NUM_RECORDS),
    "cliks": np.random.randint(1000, 5000, size=NUM_RECORDS),
    "sum": np.round(np.random.uniform(11000, 26000, size=NUM_RECORDS), 2),
}

df = pd.DataFrame(data)

# Создание директории
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Типы ошибок
def drop_random_row(chunk):
    return chunk.drop(chunk.sample(1).index)

def drop_random_column(chunk):
    return chunk.drop(columns=[random.choice(chunk.columns)])

def inject_nan(chunk):
    i = random.randint(0, len(chunk) - 1)
    col = random.choice(chunk.columns)
    chunk.loc[chunk.index[i], col] = np.nan
    return chunk

def change_dtype_to_str(chunk):
    col = random.choice(chunk.select_dtypes(include=[np.number]).columns)
    chunk[col] = chunk[col].astype(str)
    return chunk

error_functions = [
    drop_random_row, 
    drop_random_column, 
    inject_nan, 
    change_dtype_to_str
]

# Генерация файлов
for i in range(NUM_FILES):
    chunk = df.iloc[i * RECORDS_PER_FILE : (i + 1) * RECORDS_PER_FILE].copy()
    error_func = random.choice(error_functions)
    corrupted_chunk = error_func(chunk)
    
    file_path = f"{OUTPUT_DIR}/failure_data_{error_func.__name__}_{i+1:02}.csv"
    corrupted_chunk.to_csv(
        file_path, sep=";", index=False, quoting=csv.QUOTE_NONE, escapechar="\\"
    )

print("Генерация ошибочных данных завершена.")