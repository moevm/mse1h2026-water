# mse-template

## Установка и запуск
Инструкции по установке и запуску проекта.
Скачать проект на устройство
```
git clone https://github.com/moevm/mse1h2026-water.git
```

1. Создать ключ может каждый участник проекта (текущая обстановка такая) - https://console.cloud.google.com/iam-admin/serviceaccounts/details (IAM-admin -> service accounts -> Add account; keys -> add key -> JSON)
3. Json-ключ поместить в папку back/credentials
4. сделать соответствующие правки в .env файле (в .gitignore исключено случайное попадание .env в репо, если только его не запушить самостоятельно)
.env менять из-за смены ключа не нужно
5. если не получилось создать ключ можете запросить его у разработчиков

#### ! Note: you have to start your Docker Desktop Engine before work with containers

Запуск docker-compose файла

```
docker compose up --build
```

## Проверка работоспособности
после запуска на устройстве

1. перейти на страницу http://localhost:8000 - для проверки работоспособности api

готовые запросы:
GET /water-info - получение информации о водоеме
GET / - документация
GET /methods/get_satellite_image - получение изображения
Результат можно напрямую передать в следующий метод
POST /methods/cv_integrated_water_classifier - Классификации водоемов через OpenCV
GET /methods/water_detector - получение данных их overpass api
GET /methods/get_eutrophication_stats - получение данных из gee api

2. перейти на страницу http://localhost:8501 - для проверки front
   можно вводить данные координат, ответ возвращается от сервера

## Проверка работоспособности тесты
1. запустить приложение по инструкции выше
2. установка зависимостей из папки tests
```
pip install -r requirements.txt
```
3. Запуск всех тестов
```
pytest
```
3. Запуск одного теста
```
pytest tests/test_selenium.py
```
Также можно проверить работоспособность по следующим ссылкам
* https://fairly-supportive-skimmer.cloudpub.ru/ - front
* https://ghostly-direct-gerbil.cloudpub.ru/ - api
## Дополнительная информация

