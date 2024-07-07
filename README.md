
# Aether-Car

![GitHub top language](https://img.shields.io/github/languages/top/bezhan2009/Aether-Car)
![GitHub language count](https://img.shields.io/github/languages/count/bezhan2009/Aether-Car)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/bezhan2009/Aether-Car)
![GitHub repo size](https://img.shields.io/github/repo-size/bezhan2009/Aether-Car)
![GitHub](https://img.shields.io/github/license/bezhan2009/Aether-Car)
![GitHub last commit](https://img.shields.io/github/last-commit/bezhan2009/Aether-Car)
![GitHub User's stars](https://img.shields.io/github/stars/bezhan2009?style=social)
<br>
<br>
![Python](https://img.shields.io/badge/python-3.12-blue)
![Django](https://img.shields.io/badge/django-latest-brightgreen)

Aether-Car - это веб-приложение для размещения и управления объявлениями о продаже автомобилей. Этот проект является развитием платформы для интернет-магазина, теперь он специализируется на объявлениях о продаже машин, аналогично auto.ru.

## Описание проекта

Aether-Car включает в себя следующие основные функции:

- Регистрация и аутентификация пользователей.
- Просмотр списка объявлений с возможностью фильтрации и поиска.
- Добавление, редактирование и удаление объявлений о продаже автомобилей.
- Интегрированная документация API с помощью Swagger.

## Структура проекта

Проект разделен на несколько подприложений:

1. **userapp**: Регистрация, аутентификация и управление профилями пользователей.
2. **carapp**: Управление объявлениями о продаже автомобилей.
3. **addressapp**: Управление местоположениями и интерактивной картой.
4. **featured_productapp**: Управления избранными автомабилями.

## Технологии
- **Python**: Мощный и универсальный язык программирования, широко используемый для веб-разработки, научных вычислений, анализа данных и многого другого.
- **Django**: Высокоуровневый веб-фреймворк на Python, предоставляющий инструменты для быстрой разработки веб-приложений.
- **Django REST Framework (DRF)**: Набор инструментов для создания веб-API на основе Django.
- **drf-yasg**: Библиотека для генерации интерактивной документации к вашему веб-API.
- **PostgreSQL**: Надежная и производительная реляционная база данных с открытым исходным кодом.
- **simple_jwt**: Библиотека для аутентификации JSON Web Token (JWT) в приложениях Django.

Эти технологии вместе обеспечивают создание мощного и функционального веб-приложения на основе Django, которое обладает RESTful API, внушительной документацией и безопасной аутентификацией.

## Установка и запуск

Чтобы запустить проект локально, выполните следующие шаги:

1. Склонируйте репозиторий на локальную машину.
   ```bash
   git clone https://github.com/bezhan2009/Aether-Car.git
   ```
2. Перейдите в каталог проекта.
   ```bash
   cd Aether-Car
   ```
3. Установите зависимости.
   ```bash
   pip install -r requirements.txt
   ```
4. Примените миграции базы данных.
   ```bash
   python manage.py migrate
   ```
5. Создайте суперпользователя.
   ```bash
   python manage.py createsuperuser
   ```
6. Запустите сервер.
   ```bash
   python manage.py runserver
   ```
7. Перейдите по адресу [http://127.0.0.1:8000/](http://127.0.0.1:8000/) в вашем браузере.
