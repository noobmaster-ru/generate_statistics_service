from locust import HttpUser, task, between
import io
import random
import string
from pathlib import Path


CSV_DIR = Path("correct_data")
CSV_FILES = list(CSV_DIR.glob("*.csv"))  #  all csv in correct data

# RPS — сколько запросов в секунду выдерживает сервер
# http://localhost:8089/
class MyUser(HttpUser):
    wait_time = between(0.1, 0.3)  # Пауза между запросами

    @task
    def send_request(self):
        csv_path = random.choice(CSV_FILES)

        # daily
        with open(csv_path, "rb") as f1, open(csv_path, "rb") as f2:
            files_daily = {
                "file1": (csv_path.name, f1, "text/csv"),
                "file2": (csv_path.name, f2, "text/csv")
            }

            data = {
                "token_id": "locust_token",
                "supplier_id": "123",
                "cabinet_name": "locust_cabinet"
            }

            self.client.post("/get-image-daily", files=files_daily, data=data)
    
        # weekly 
        with open(csv_path, "rb") as f:
            files_weekly = {
                "file": (csv_path.name, f, "text/csv")
            }

            self.client.post("/get-image-weekly", files=files_weekly, data=data)