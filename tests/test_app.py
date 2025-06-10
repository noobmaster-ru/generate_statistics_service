import pytest
from fastapi.testclient import TestClient
from io import BytesIO
import pandas as pd
import glob
import random
import os
import sys
from PIL import Image
import base64


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import app
client = TestClient(app.app)

# cписок всех CSV-файлов в папке tests
current_dir = os.path.dirname(__file__)  # папка с test_app.py (tests)


# что если данные внутри файла не интеджер 

# что если данные неопределелены 

# что если не будет хватать одного дня (структура данных)

# что если не все данные типа float/int

# что если 




# Тест на ошибку (неверный формат файла)
# def test_invalid_file_format_weekly():
#     #  не-CSV файл
#     invalid_file = BytesIO(b"not a csv file")
#     files = {
#         "file":  ("file1.csv",  invalid_file, "text/csv")
#     }
#     data = {
#         "token_id": "test123",
#         "supplier_id": "supplier456",
#         "cabinet_name": "test_cabinet",
#     }

#     response = client.post("/get-image-weekly", files=files, data=data)
#     print(response.json())
#     assert response.status_code == 500


# # Тесты на отсутствие обязательных полей  data=(token,supplier,cabinet) - прошёл
# def test_missing_required_fields_daily(sample_csv_file):
#     files = {
#         "file1": sample_csv_file,
#         "file2": sample_csv_file
#     }
#     # Не передаем обязательные поля data=(token,supplier,cabinet)
#     response = client.post("/get-image-daily", files=files)
#     assert response.status_code == 422 # Ошибка - Ok
# def test_missing_required_fields_weekly(sample_csv_file):
#     files = {
#         "file": ("test.csv", sample_csv_file, "text/csv"),
#     }
#     # Не передаем обязательные поля data=(token,supplier,cabinet)
#     response = client.post("/get-image-weekly", files=files)
#     assert response.status_code == 422 # Ошибка - Ok



pattern_success = os.path.join(current_dir, "tests_success/*.csv")
csv_file_paths_success = glob.glob(pattern_success) # все имена файлов .csv

# фикстура для всех правильных csv файлов 
@pytest.fixture(params=csv_file_paths_success, ids=lambda path: path.split("/")[-1])
def sample_success_csv_file(request):
    with open(request.param, "rb") as f:
        csv_bytes = BytesIO(f.read())
        csv_bytes.seek(0)
        return csv_bytes

def test_image_compression_weekly_success(sample_success_csv_file):
    files = {
        "file": ("test.csv", sample_success_csv_file, "text/csv"),
    }
    data = {
        "token_id": "test123",
        "supplier_id": "supplier456",
        "cabinet_name": "test_cabinet",
    }

    response = client.post("/get-image-weekly", files=files, data=data)
    assert response.status_code == 200, f"Unexpected status: {response.status_code}, Detail: {response.text}"

    json_response = response.json()
    image_data = json_response["image_base64"]

    assert 5000 < len(image_data) < 120000

    decoded_image = base64.b64decode(image_data)
    img = Image.open(BytesIO(decoded_image))
    assert img.format in ['JPEG', 'WEBP', 'PNG']

    if img.format == 'JPEG':
        assert img.info.get('quality', 100) < 90


pattern_failure = os.path.join(current_dir, "tests_failure/*.csv")
csv_file_paths_failure = glob.glob(pattern_failure) # все имена ошибочных файлов .csv

# фикстура для всех правильных csv файлов 
@pytest.fixture(params=csv_file_paths_failure, ids=lambda path: path.split("/")[-1])
def sample_failure_csv_file(request):
    with open(request.param, "rb") as f:
        csv_bytes = BytesIO(f.read())
        csv_bytes.seek(0)
        return csv_bytes

def test_image_compression_weekly_failure(sample_failure_csv_file):
    files = {
        "file": ("test.csv", sample_failure_csv_file, "text/csv"),
    }
    data = {
        "token_id": "test123",
        "supplier_id": "supplier456",
        "cabinet_name": "test_cabinet",
    }

    response = client.post("/get-image-weekly", files=files, data=data)

    # Мы ожидаем, что API вернёт 500 или 400 (если ты явно выставляешь 400)
    assert response.status_code in (400, 500), f"Expected error, got {response.status_code}"

