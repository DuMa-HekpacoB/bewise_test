##Инструкция:
```bash
docker-compose up -d

curl -X POST -H "Content-Type: application/json"     -d '{"questions_num": 5}'    http://127.0.0.1:7070/bewise

```