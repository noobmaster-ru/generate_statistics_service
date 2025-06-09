import pytest
from fastapi.testclient import TestClient
from io import BytesIO
import pandas as pd
import glob
import random
import os
from app import app  
from PIL import Image
import base64

client = TestClient(app)


# Получаем список всех CSV-файлов в папке
csv_file_paths = glob.glob("cabinet_data_samples/*.csv")

# фикстура для всех csv файлов изи cabinet_data_samples 
@pytest.fixture(params=csv_file_paths, ids=lambda path: path.split("/")[-1])
def sample_csv_file(request):
    with open(request.param, "rb") as f:
        csv_bytes = BytesIO(f.read())
        csv_bytes.seek(0)
        return csv_bytes

# Тест на ошибку (неверный формат файла)
def test_invalid_file_format_weekly(sample_csv_file):
    #  не-CSV файл
    invalid_file = BytesIO(b"not a csv file")
    files = {
        "file": invalid_file
    }
    data = {
        "token_id": "test123",
        "supplier_id": "supplier456",
        "cabinet_name": "test_cabinet",
    }

    response = client.post("/get-image-weekly", files=files, data=data)
    assert response.status_code == 422


# Тесты на отсутствие обязательных полей  data=(token,supplier,cabinet) - прошёл
def test_missing_required_fields_daily(sample_csv_file):
    files = {
        "file1": sample_csv_file,
        "file2": sample_csv_file
    }
    # Не передаем обязательные поля data=(token,supplier,cabinet)
    response = client.post("/get-image-daily", files=files)
    assert response.status_code == 422 # Ошибка - Ok
def test_missing_required_fields_weekly(sample_csv_file):
    files = {
        "file": ("test.csv", sample_csv_file, "text/csv"),
    }
    # Не передаем обязательные поля data=(token,supplier,cabinet)
    response = client.post("/get-image-weekly", files=files)
    assert response.status_code == 422 # Ошибка - Ok


# Проверка сжатия изображения
def test_image_compression_weekly(sample_csv_file):
    files = {
        "file": ("test.csv", sample_csv_file, "text/csv"),
    }
    data = {
        "token_id": "test123",
        "supplier_id": "supplier456",
        "cabinet_name": "test_cabinet",
    }

    response = client.post("/get-image-weekly", files=files, data=data)
    assert response.status_code == 200, "not success"
    json_response = response.json()
    image_data = json_response["image_base64"]

    # Проверяем, что изображение не пустое и не слишком большое
    assert 5000 < len(image_data) < 120000

    # Декодируем и проверяем формат (JPEG или WEBP)
    decoded_image = base64.b64decode(image_data)
    img = Image.open(BytesIO(decoded_image))
    assert img.format in ['JPEG', 'WEBP', 'PNG']  # Добавьте нужные форматы

    # Если JPEG, проверяем качество
    if img.format == 'JPEG':
        assert img.info.get('quality', 100) < 90  # Качество меньше 90%