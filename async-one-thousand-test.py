import aiohttp
import asyncio
import os
import time
import csv
import base64
import json

SEMAPHORE_LIMIT = 7

cabinet_dir = "cabinet_data_samples"
results_dir = "results_100"
url = "http://localhost:8050/get-image-weekly"

semaphore = asyncio.Semaphore(SEMAPHORE_LIMIT)


def get_unique_csv_path(base_dir, base_filename="request_stats.csv"):
    base_path = os.path.join(base_dir, base_filename)
    if not os.path.exists(base_path):
        return base_path

    name, ext = os.path.splitext(base_filename)
    index = 1
    while True:
        new_filename = f"{name}_{index}{ext}"
        new_path = os.path.join(base_dir, new_filename)
        if not os.path.exists(new_path):
            return new_path
        index += 1


request_stats = []


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

                async with session.post(url, data=form) as resp:
                    if resp.status == 200:
                        json_resp = await resp.json()
                        base64_img = json_resp.get("image_base64")
                        if base64_img:
                            img_bytes = base64.b64decode(base64_img)
                            filename = f"{results_dir}/weekly-stat-{index}.png"
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
            os.path.join(cabinet_dir, f)
            for f in os.listdir(cabinet_dir)
            if f.endswith(".csv")
        ]
    )[:100]

    os.makedirs(results_dir, exist_ok=True)

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


asyncio.run(main())
