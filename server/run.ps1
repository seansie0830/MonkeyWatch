docker build -t django-new -f web.dockerfile .
docker build -t mysql -f db.dockerfile .
docker-compose up -d
