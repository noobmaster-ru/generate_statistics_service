from locust import HttpUser, task, between
import random
from pathlib import Path


CSV_DIR = Path("correct_data")
CSV_FILES = list(CSV_DIR.glob("*.csv"))  

# http://localhost:8080/
class MyUser(HttpUser):
    wait_time = between(0,0) 

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

            with self.client.post("/get-image-daily", files=files_daily, data=data, catch_response=True) as response:
                if response.status_code != 200:
                    response.failure(f"Unexpected status: {response.status_code}")
                
        # weekly 
        with open(csv_path, "rb") as f:
            files_weekly = {
                "file": (csv_path.name, f, "text/csv")
            }

            with self.client.post("/get-image-weekly", files=files_weekly, data=data, catch_response=True) as response:
                if response.status_code != 200:
                    response.failure(f"Unexpected status: {response.status_code}")