import pytest
from httpx import AsyncClient
from httpx import ASGITransport
import sys
import os
from io import BytesIO
import glob

# set the kernel directory == marke_statistics
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import app

# Получаем список всех CSV-файлов в папке
csv_file_paths = glob.glob("tests/correct_data/*.csv")
@pytest.fixture(params=csv_file_paths, ids=lambda path: path.split("/")[-1])
def success_csv_file(request):
    with open(request.param, "rb") as f:
        csv_bytes = BytesIO(f.read())
        csv_bytes.seek(0)
        return csv_bytes

# Получаем список всех CSV-файлов в папке
csv_file_paths = glob.glob("tests/failure_data/*.csv")
@pytest.fixture(params=csv_file_paths, ids=lambda path: path.split("/")[-1])
def failure_csv_file(request):
    with open(request.param, "rb") as f:
        csv_bytes = BytesIO(f.read())
        csv_bytes.seek(0)
        return csv_bytes
    



class TestSuccess:
    @pytest.mark.asyncio
    async def test_get_image_daily_success(self,success_csv_file):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/get-image-daily",
                files={
                    "file1": ("file1.csv", success_csv_file, "text/csv"),
                    "file2": ("file2.csv", success_csv_file, "text/csv"),
                },
                data={
                    "token_id": "abc",
                    "supplier_id": "123",
                    "cabinet_name": "test",
                },
            )
            assert response.status_code == 200, f"Unexpected status: {response.status_code}, Detail: {response.text}"
            json_resp = response.json()
            assert "image_base64" in json_resp


    @pytest.mark.asyncio
    async def test_get_image_weekly_success(self,success_csv_file):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/get-image-weekly",
                files={"file": ("file.csv", success_csv_file, "text/csv")},
                data={
                    "token_id": "abc",
                    "supplier_id": "123",
                    "cabinet_name": "test",
                },
            )
            assert response.status_code == 200, f"Unexpected status: {response.status_code}, Detail: {response.text}"
            json_resp = response.json()
            assert "image_base64" in json_resp


class TestFailure:
    @pytest.mark.asyncio
    async def test_weekly_fail_on_broken_columns(failure_csv_file):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/get-image-weekly",
                files={"file": ("file.csv", failure_csv_file, "text/csv")},
                data={
                    "token_id": "abc",
                    "supplier_id": "123",
                    "cabinet_name": "test",
                },
            )
            assert response.status_code == 400


    @pytest.mark.asyncio
    async def test_weekly_fail_on_too_few_rows(failure_csv_file):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/get-image-weekly",
                files={"file": ("file.csv", failure_csv_file, "text/csv")},
                data={
                    "token_id": "abc",
                    "supplier_id": "123",
                    "cabinet_name": "test",
                },
            )
            assert response.status_code == 400


    @pytest.mark.asyncio
    async def test_weekly_fail_on_wrong_types(failure_csv_file):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/get-image-weekly",
                files={"file": ("file.csv", failure_csv_file, "text/csv")},
                data={
                    "token_id": "abc",
                    "supplier_id": "123",
                    "cabinet_name": "test",
                },
            )
            assert response.status_code == 400


    @pytest.mark.asyncio
    async def test_daily_fail_if_one_file_missing(failure_csv_file):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/get-image-daily",
                files={"file1": ("file.csv", failure_csv_file, "text/csv")},  # file2 отсутствует
                data={
                    "token_id": "abc",
                    "supplier_id": "123",
                    "cabinet_name": "test",
                },
            )
            assert response.status_code == 400
