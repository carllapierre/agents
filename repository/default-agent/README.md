docker build -t fastapi-docker .
docker run -dp 8004:8004 --env-file .env -v $(pwd):/app fastapi-docker
