import aiohttp
import asyncio
import os
import time
import csv
import base64
import json
from dotenv import load_dotenv


"""send_request(
    session: aiohttp.ClientSession(),
    file_path: chunk_*.csv,
    index: index of chunk_*.csv
"""
async def send_request_weekly(session, file_path, index):
    async with semaphore:
        start = time.perf_counter()
        success = False
        error_message = ""
        try:
            # чтение в бинарном режиме всех файлов chunk_*.csv асинхронно
            with open(file_path, "rb") as f:
                data = {
                    "token_id": "123",
                    "supplier_id": "21341",
                    "cabinet_name": "test_cabinet",
                }
                form_weekly = aiohttp.FormData() # экземляр класса для отправки  HTTP запроса

                # c 57 по 64 строку добавляем  поля к запросу
                form_weekly.add_field(
                    "file",
                    f,
                    filename=os.path.basename(file_path),
                    content_type="text/csv",
                )

                for k, v in data.items():
                    form_weekly.add_field(k, v)

                # отпрявляем запрос POST и получаем ответ от FASTapi нашего 
                async with session.post(URL_WEEKLY, data=form_weekly) as resp:
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
                        print(f"❌ Ошибка в запросе {index},HTTP {resp.status} - {await resp.text()}")

        except Exception as e:
            error_message = str(e)
            print(f"❌ Ошибка в запросе {index}: {error_message}")


        # общая статистика по всем запросам
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
async def send_request_daily(session, file_path,file_path_, index):
    async with semaphore:
        start = time.perf_counter()
        success = False
        error_message = ""
        try:
            # чтение в бинарном режиме всех файлов chunk_*.csv асинхронно
            with open(file_path, "rb") as f1:
                with open(file_path_, "rb") as f2:
                    data = {
                        "token_id": "123",
                        "supplier_id": "21341",
                        "cabinet_name": "test_cabinet",
                    }
                    form_daily = aiohttp.FormData() # экземляр класса для отправки  HTTP запроса

                    # c 57 по 64 строку добавляем  поля к запросу
                    form_daily.add_field(
                        "file1",
                        f1,
                        filename=os.path.basename(file_path),
                        content_type="text/csv",
                    )
                    form_daily.add_field(
                        "file2",
                        f2,
                        filename=os.path.basename(file_path_),
                        content_type="text/csv",
                    )
                    for k, v in data.items():
                        form_daily.add_field(k, v)

                    # отпрявляем запрос POST и получаем ответ от FASTapi нашего 
                    async with session.post(URL_DAILY, data=form_daily) as resp:
                        if resp.status == 200:
                            json_resp = await resp.json()
                            base64_img = json_resp.get("image_base64")
                            if base64_img:
                                img_bytes = base64.b64decode(base64_img)
                                filename = f"{RESULTS_DIR}/daily-stat-{index}.png"
                                with open(filename, "wb") as out:
                                    out.write(img_bytes)
                                print(f"✅ Получено: {filename}")
                                success = True
                            else:
                                error_message = "❌ Нет поля 'image_base64' в ответе"
                        else:
                            error_message = f"HTTP {resp.status}"
                            print(f"❌ Ошибка в запросе {index},HTTP {resp.status} - {await resp.text()}")

        except Exception as e:
            error_message = str(e)
            print(f"❌ Ошибка в запросе {index}: {error_message}")


        # общая статистика по всем запросам
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
    ) # берем все файлы 


    # создает папку с графиками для 100 файлов
    os.makedirs(RESULTS_DIR, exist_ok=True)

    start_time = time.perf_counter()

    tasks = []
    # отправляет запросы по всем файлам из tests/correct_data
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            *[
                coro
                for i in range(0, len(files)-1)
                for coro in (
                    send_request_daily(session, files[i], files[i + 1], i + 1),
                    send_request_weekly(session, files[i], i + 1)
                )
                # send_request_daily(session, files[i], files[i+1], i + 1)
                # for i in range(0, len(files) - 1, 1)
            ]
        )
    end_time = time.perf_counter()
    total_time = end_time - start_time
    success_count = sum(1 for r in request_stats if r["success"])
    fail_count = len(request_stats) - success_count
    speed = success_count / total_time if total_time > 0 else 0
    # speed_2 = total_time / success_count if total_time > 0 else 0

    # Вывод общей статистики
    print("\n📊 Итоговая статистика:")
    print(f"⏱️ Общее время: {total_time:.2f} секунд")
    print(f"✅ Успешных: {success_count}")
    print(f"❌ Ошибок: {fail_count}")
    print(f"⚡ Скорость: {speed:.2f} запросов/сек")
    # print(f"⚡ Скорость: {speed_2:.2f} сек на запрос")

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
