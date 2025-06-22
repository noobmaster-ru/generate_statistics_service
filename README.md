## Docker
```
docker build -t market-api .
docker run -d -p 8050:8050 --name market_api market-api
docker exec market_api python async-one-thousand-test.py
```
## Тест gunicorn (локально у себя)
```
gunicorn app:app -k uvicorn.workers.UvicornWorker -w 8 --bind 0.0.0.0:8050 --timeout 180
python async-one-thousand-test.py
``` 
## Тест locust (локально у себя, 100 пользователей по 10 в секунду)
```
locust -u 100 -r 10 --host http://localhost:8050 
```