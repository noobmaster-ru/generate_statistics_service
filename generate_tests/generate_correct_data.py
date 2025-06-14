# генерирует данные от апи и сохраняет в cabinet_data_samples 1000 файлов по 14 дней в каждом
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import csv
from dotenv import load_dotenv
load_dotenv()
# Параметры генерации
NUM_RECORDS = int(os.getenv("NUM_RECORDS")) 
RECORDS_PER_FILE = int(os.getenv("RECORDS_PER_FILE"))
NUM_FILES = NUM_RECORDS // RECORDS_PER_FILE
OUTPUT_DIR = "tests/correct_data"


today_str = datetime.today().strftime("%Y-%m-%d")
initial_date = datetime.strptime(today_str, "%Y-%m-%d")  # или любую стартовую

# Сдвигаем initial_date назад до ближайшего понедельника
weekday = initial_date.weekday()  # 0 = понедельник, 6 - воскресенье
base_monday = initial_date - timedelta(days=weekday)

# Каждые 13 записей — новая группа, начинающаяся с понедельника
dates = [
    (base_monday + timedelta(days=(i // 13) * 13 + (i % 13))).strftime("%Y-%m-%d")
    for i in range(NUM_RECORDS)
]

# Генерация данных
data = {
    "id": [3] * NUM_RECORDS,
    "date": dates,
    "open_card_count": np.random.randint(4000, 12000, size=NUM_RECORDS),
    "add_to_cart_count": np.random.randint(800, 2000, size=NUM_RECORDS),
    "orders_count": np.random.randint(70, 250, size=NUM_RECORDS),
    "orders_sum_rub": np.random.randint(100000, 4000000, size=NUM_RECORDS),

    "median_orders_sum_per_user": np.random.randint(1000,3000,size=NUM_RECORDS),
    "median_drr": np.round(np.random.uniform(0, 100, size=NUM_RECORDS), 2),
    "avg_orders_sum_per_user": np.random.randint(0, 10000, size=NUM_RECORDS),
    "drr": np.round(np.random.uniform(0, 100, size=NUM_RECORDS), 2),
    
    "views": np.random.randint(30000, 999999, size=NUM_RECORDS),
    "cliks": np.random.randint(1000, 5000, size=NUM_RECORDS),
    "sum": np.round(np.random.uniform(11000, 26000, size=NUM_RECORDS), 2),
}

df = pd.DataFrame(data)

# Создание директории для файлов
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Разделение на 1000 файлов
file_paths = []
for i in range(NUM_FILES):
    chunk = df.iloc[i * RECORDS_PER_FILE : (i + 1) * RECORDS_PER_FILE]
    file_path = f"{OUTPUT_DIR}/correct_data_{i+1:04}.csv"
    chunk.to_csv(
        file_path, sep=";", index=False, quoting=csv.QUOTE_NONE, escapechar="\\"
    )
    file_paths.append(file_path)


print("Генерация корретных данных завершена.")