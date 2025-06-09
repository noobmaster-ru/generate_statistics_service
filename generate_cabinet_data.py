import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import csv

# Параметры генерации
num_records = 14_000
records_per_file = 14
num_files = num_records // records_per_file

initial_date = datetime.strptime("2025-04-25", "%Y-%m-%d")  # или любую стартовую

# Сдвигаем initial_date назад до ближайшего понедельника
weekday = initial_date.weekday()  # 0 = понедельник
base_monday = initial_date - timedelta(days=weekday)

# Каждые 13 записей — новая группа, начинающаяся с понедельника
dates = [
    (base_monday + timedelta(days=(i // 13) * 13 + (i % 13))).strftime("%Y-%m-%d")
    for i in range(num_records)
]

# Генерация данных
data = {
    "id": [3] * num_records,
    "date": dates,
    "open_card_count": np.random.randint(4000, 12000, size=num_records),
    "add_to_cart_count": np.random.randint(800, 2000, size=num_records),
    "orders_count": np.random.randint(70, 250, size=num_records),
    "orders_sum_rub": np.random.randint(100000, 4000000, size=num_records),
    "views": np.random.randint(30000, 999999, size=num_records),
    "cliks": np.random.randint(1000, 5000, size=num_records),
    "sum": np.round(np.random.uniform(11000, 26000, size=num_records), 2),
}

df = pd.DataFrame(data)

# Создание директории для файлов
output_dir = "cabinet_data_samples"
os.makedirs(output_dir, exist_ok=True)

# Разделение на 1000 файлов
file_paths = []
for i in range(num_files):
    chunk = df.iloc[i * records_per_file : (i + 1) * records_per_file]
    file_path = f"{output_dir}/chunk_{i+1:04}.csv"
    chunk.to_csv(
        file_path, sep=";", index=False, quoting=csv.QUOTE_NONE, escapechar="\\"
    )
    file_paths.append(file_path)
