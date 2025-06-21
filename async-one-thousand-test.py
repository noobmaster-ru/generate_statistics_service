import aiohttp
import asyncio
import os
import time
import csv
import base64
import json
from dotenv import load_dotenv



async def send_request(session, file_path, index):
    async with semaphore:
        start = time.perf_counter()
        success = False
        error_message = ""
        try:
            with open(file_path, "rb") as f:
                data = {
                    "token_id": "123",
                    "supplier_id": "21341",
                    "cabinet_name": "test_cabinet",
                }
                form = aiohttp.FormData()
                form.add_field(
                    "file",
                    f,
                    filename=os.path.basename(file_path),
                    content_type="text/csv",
                )
                for k, v in data.items():
                    form.add_field(k, v)

                async with session.post(URL_WEEKLY, data=form) as resp:
                    if resp.status == 200:
                        json_resp = await resp.json()
                        base64_img = json_resp.get("image_base64")
                        if base64_img:
                            img_bytes = base64.b64decode(base64_img)
                            filename = f"{RESULTS_DIR}/weekly-stat-{index}.png"
                            with open(filename, "wb") as out:
                                out.write(img_bytes)
                            print(f"✅ Получено: {filename}")
                            success = True
                        else:
                            error_message = "❌ Нет поля 'image_base64' в ответе"
                    else:
                        error_message = f"HTTP {resp.status}"
        except Exception as e:
            error_message = str(e)
            print(f"❌ Ошибка в запросе {index}: {e}")

        duration = time.perf_counter() - start
        request_stats.append(
            {
                "index": index,
                "file": os.path.basename(file_path),
                "success": success,
                "duration_sec": round(duration, 4),
                "error": error_message,
            }
        )


async def main():
    files = sorted(
        [
            os.path.join(CORRECT_DATA, f)
            for f in os.listdir(CORRECT_DATA)
            if f.endswith(".csv")
        ]
    )

    os.makedirs(RESULTS_DIR, exist_ok=True)

    start_time = time.perf_counter()

    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            *[
                send_request(session, file_path, idx + 1)
                for idx, file_path in enumerate(files)
            ]
        )

    end_time = time.perf_counter()
    total_time = end_time - start_time
    success_count = sum(1 for r in request_stats if r["success"])
    fail_count = len(request_stats) - success_count
    speed = success_count / total_time if total_time > 0 else 0

    # Вывод общей статистики
    print("\n📊 Итоговая статистика:")
    print(f"⏱️ Общее время: {total_time:.2f} секунд")
    print(f"✅ Успешных: {success_count}")
    print(f"❌ Ошибок: {fail_count}")
    print(f"⚡ Скорость: {speed:.2f} запросов/сек")

if __name__ == "__main__":
    load_dotenv()
    SEMAPHORE_LIMIT = int(os.getenv("SEMAPHORE_LIMIT"))
    CORRECT_DATA = os.getenv("CORRECT_DATA") 
    RESULTS_DIR = os.getenv("RESULTS_DIR")
    URL_WEEKLY = os.getenv("URL_WEEKLY")
    URL_DAILY = os.getenv("URL_DAILY")

    request_stats = []
    semaphore = asyncio.Semaphore(SEMAPHORE_LIMIT)
    asyncio.run(main())