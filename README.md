## FastAPI, Docker
```
docker build -t fastapi-stat-app .
docker run -d -p 8050:8050 --name stat_server fastapi-stat-app
```
## Сгенерировать тестовые данные
```
python generate_cabinet_data.py
```
## Тест на производительность(в разных терминалах запускать; 8 процессов всего на сервере)
```
export DYLD_LIBRARY_PATH=/opt/homebrew/lib:$DYLD_LIBRARY_PATH        
lsof -i :8050  // просмотр процессов ,которые  gunicorn занял
gunicorn app:app -k uvicorn.workers.UvicornWorker -w 8 --bind 0.0.0.0:8050 
python async-one-thousand-test.py
```

----------------------------------------
# старт без docker
uvicorn app:app --host 0.0.0.0 --port 8050 