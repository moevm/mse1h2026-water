## О проекте
### Постановка задачи
Основная проблема:  
получение типа водоема и его экологического статуса по координатам (широта и долгота)  
Категория пользователей:  
Экологи и люди интересующиеся экологией, для которых важно получение информации о водоемах
### Требования
1. веб-страница для ввода данных
2. обязательно использовать NDWI для сегментации
3. результат один из 4 типов водоемов (озеро, река, болото, пруд) и 2 экологических статуса (ИЗВ, эвтрофикация)
4. классифицировать водоем по открытым данным и/или обученной модели

### Требования к запросам :
* GET [/water-info](http://127.0.0.1:8000/docs#/default/get_water_info_water_info_get) - получение информации о водоеме
* GET [/](http://127.0.0.1:8000/docs#/default/redirect_to_docs__get)  - документация
* GET [/methods/get_satellite_image](http://127.0.0.1:8000/docs#/default/get_satellite_image_methods_get_satellite_image_get) - получение изображения  
Результат можно напрямую передать в следующий метод  
* POST [/methods/cv_integrated_water_classifier](http://127.0.0.1:8000/docs#/default/cv_integrated_water_classifier_methods_cv_integrated_water_classifier_post) - Классификации водоемов через OpenCV
* GET [/methods/water_detector](http://127.0.0.1:8000/docs#/default/water_detector_endpoint_methods_water_detector_get) - получение данных их overpass api
* GET [/methods/get_eutrophication_stats](http://127.0.0.1:8000/docs#/default/get_eutrophication_stats_methods_get_eutrophication_stats_get) - получение данных из gee api


Технологии: Python, scikit-learn / TensorFlow, Google Earth Engine API, FastAPI.
### Сценарии использования
Основной сценарий использования:
1. Пользователь вводит координаты и нажимает на кнопку проверки
2. Система отображает тип и экологический статус

Основной сценарий обращения к API:
1. Пользователь обращается по пути [water-info](http://127.0.0.1:8000/docs#/default/get_water_info_water_info_get)
2. Система возвращает информация о водоеме

Альтернативный сценарий обращения к API:
1. Пользователь обращается по пути /
2. Система отображает докуменацию

Альтернативный сценарий обращения к API:
1. Пользователь обращается по пути [/methods/get_satellite_image](http://127.0.0.1:8000/docs#/default/get_satellite_image_methods_get_satellite_image_get) 
2. Система возвращает изображение

Альтернативный сценарий обращения к API:
1. Пользователь обращается по пути [/methods/](http://127.0.0.1:8000/docs#/default/get_satellite_image_methods_get_satellite_image_get)[cv_integrated_water_classifier](http://127.0.0.1:8000/docs#/default/cv_integrated_water_classifier_methods_cv_integrated_water_classifier_post) и передает данные об изображении
2. Система возвращает информацию о водоеме

Альтернативный сценарий обращения к API:
1. Пользователь обращается по пути [/methods/](http://127.0.0.1:8000/docs#/default/get_satellite_image_methods_get_satellite_image_get)[water_detector](http://127.0.0.1:8000/docs#/default/water_detector_endpoint_methods_water_detector_get) 
2. Система возвращает данные о водоеме из overpass api

Альтернативный сценарий обращения к API:
1. Пользователь обращается по пути [/methods/](http://127.0.0.1:8000/docs#/default/get_satellite_image_methods_get_satellite_image_get)[get_eutrophication_stats](http://127.0.0.1:8000/docs#/default/get_eutrophication_stats_methods_get_eutrophication_stats_get)
2. Система возвращает данные о водоеме из gee api

Макет
![Макет](docs/ui.png)

### Инструкция по запуску
* [северной части](https://github.com/moevm/mse1h2026-water/wiki/Endpoint-для-запроса)
* [веб-страницы](https://github.com/moevm/mse1h2026-water/wiki/UI-demo-wiki)
* [пример работы с OSM](https://github.com/moevm/mse1h2026-water/wiki/Open-Data-Integration)
* [пример работы с GEE API](https://github.com/moevm/mse1h2026-water/wiki/Использование-GEE-API)
* [модель](https://github.com/moevm/mse1h2026-water/wiki/Классификатор-типов-водоемов-с-помощью-CV) 

Инструкции по установке и запуску проекта.
Скачать проект на устройство
```
git clone https://github.com/moevm/mse1h2026-water.git
```

1. Создать ключ может каждый участник проекта (текущая обстановка такая) - https://console.cloud.google.com/iam-admin/serviceaccounts/details (IAM-admin -> service accounts -> Add account; keys -> add key -> JSON)
3. Json-ключ поместить в папку back/credentials
4. сделать соответствующие правки в .env файле (в .gitignore исключено случайное попадание .env в репо, если только его не запушить самостоятельно)
.env менять из-за смены ключа не нужно

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

Также можно проверить работоспособность по следующим ссылкам  

https://fairly-supportive-skimmer.cloudpub.ru/ - front  
https://ghostly-direct-gerbil.cloudpub.ru/ - api

## Итерация №1
### Презентация
[Презентация 1](https://github.com/moevm/mse1h2026-water/blob/reports/docs/Итерация%201.pdf)
### Запланированные задачи
1. получить доступ в репозиторий и общим чатам
2. правильно указать имена на github
3. провести встречи с командой и заказчиком
4. создать шаблон для демо страницы
5. создать один endpoint для запроса
6. создать пример использования готовой модели (может не быть некоторых типов водоемов)
7. создать пример использования открытых данных (GEE API, OSM API)

### Выполненные задачи
1. получен доступ в репозиторий и общим чатам
2. указаны имена на github
3. проведена встреча с командой и заказчиком
4. создан шаблон для демо страницы [wiki](https://github.com/moevm/mse1h2026-water/wiki/UI-demo-wiki)
5. создан один endpoint для запроса [wiki](https://github.com/moevm/mse1h2026-water/wiki/Endpoint-для-запроса)
6. пример использования готовой модели [wiki](https://github.com/moevm/mse1h2026-water/wiki/Классификатор-типов-водоемов-с-помощью-CV)
7. пример использования открытых данных ([GEE API](https://github.com/moevm/mse1h2026-water/wiki/Использование-GEE-API), [OSM API](https://github.com/moevm/mse1h2026-water/wiki/Open-Data-Integration))

### Задачи на следующую итерацию
1. связать компоненты
2. улучшение работы модели

## Итерация №2
### Презентация
[Презентация 2](https://github.com/moevm/mse1h2026-water/blob/reports/docs/Итерация%202.pdf)
### Видео демострация
[скринкаст](https://github.com/moevm/mse1h2026-water/blob/reports/docs/iter2.mp4)
### Запланированные задачи
1. Автоматизировать запуск
2. Написать Dockerfile для front
3. Написать Dockerfile для back
4. Написать docker compose файл
5. Улучшение работы модели
6. Связать отдельные компоненты (back и front, добавить в back модель)

### Выполненные задачи
1. Автоматизирован запуск
2. Написан Dockerfile для front
3. Написан Dockerfile для back
4. Написан docker compose файл
5. Улучшена работа модели (ускорение работы, определение оптимального радиуса 6 км)
6. Связаны отдельные компоненты (back и front, модель добавлена в back)

Front - https://fairly-supportive-skimmer.cloudpub.ru/  
Api - https://ghostly-direct-gerbil.cloudpub.ru/

### Задачи на следующую итерацию
1. Написать тесты
2. улучшение работы модели распознавание болот

## Итерация №3
### Презентация
[Презентация 3](https://github.com/moevm/mse1h2026-water/blob/reports/docs/Итерация%203.pdf)
### Видео демострация
[скринкаст](https://github.com/moevm/mse1h2026-water/blob/reports/docs/iter3.mp4)
### Запланированные задачи
1. Добавить тестирование
2. Улучшение работы модели распознавание болот
   
### Выполненные задачи
1. Тесты
   * water-detection
   * get_satellite_image
   * water-info
   * cv_integrated_water_classifier
   * get_eutrophication_stats
2. Реализован автоматический запуск тестов в github actions
3. Selenium тест
4. в визуал добавлен вывод маски

### Задачи на следующую итерацию
1. улучшение работы модели распознавание болот
2. Добавить ООП
3. Интерпритация риска
4. Расширение selenium тестов ( не правильный ввод коордианат, загрузка бэка, ошибка подгрузки изображения)

## Итерация №4
### Презентация
[Презентация 4](https://github.com/moevm/mse1h2026-water/blob/reports/docs/Итерация%204.pdf)
### Видео демострация
[скринкаст](https://github.com/moevm/mse1h2026-water/blob/reports/docs/iter4.mp4)
### Запланированные задачи
1. Улучшение работы модели распознавание болот
2. Добавить ООП
3. Интерпритация риска
4. Расширение selenium тестов ( не правильный ввод
координат, загрузка бэка, ошибка подгрузки изображения)
   
### Выполненные задачи
1. Добавлена интерпритация риска
2. Описано дальнейшее внедрение ООП и созданы базовые классы - [wiki](https://github.com/moevm/mse1h2026-water/wiki/Заготовка-под-ООП)
3. Результат болото - [wiki]( https://github.com/moevm/mse1h2026-water/wiki/%D0%A3%D0%BB%D1%83%D1%87%D1%88%D0%B5%D0%BD%D0%B8%D0%B5-%D1%80%D0%B0%D1%81%D0%BF%D0%BE%D0%B7%D0%BD%D0%B0%D0%BD%D0%B8%D1%8F-%D0%B1%D0%BE%D0%BB%D0%BE%D1%82)
4. Добавлена информационная сводка и ввод дат
5. Selenium тест
   * не правильный ввод координат
   * загрузка бэка
   * ошибка подгрузки изображения (проверка ограничения по радиусу)
