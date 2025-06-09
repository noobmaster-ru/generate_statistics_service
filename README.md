## FastAPI, Docker
```
docker build -t fastapi-stat-app .
docker run -d -p 8050:8050 --name stat_server fastapi-stat-app
```
## Сгенерировать тестовые данные
```
python generate_cabinet_data.py
```
## Тест на производительность
```
python async-one-thousand-test.py
```

----------------------------------------
# старт без docker
uvicorn app:app --host 0.0.0.0 --port 8050 