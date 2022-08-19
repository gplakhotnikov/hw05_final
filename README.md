# Социальная сеть YaTube

Социальная сеть с авторизацией, возможностью публикации постов с изображениями, персональной лентой для каждого пользователя, комментариями к записям, возможностью подписываться друг на друга, индивидуальными страницами с профилем. Выполнена в качестве одного из финальных заданий для bootcamp Yandex.Practicum.

## Особенности / Features

- Все действия, начиная от регистрации и заканчивая добавлением постов, производятся через пользовательский интерфейс
- Хранение информации в базе данных реализовано через Django ORM
- Добавление публикаций с изображениями или без них, создание комментариев к записям, подписки на пользователей
- Большинство страниц генерируется автоматически 

## Стек технологий / Tech

- [Python](https://www.python.org/)
- [Django](https://www.djangoproject.com/)
- [Django REST framework](https://www.django-rest-framework.org/)
- [requests 2.26.0](https://pypi.org/project/requests/2.6.0/) - an Apache2 Licensed HTTP library, written in Python, that allows you to send HTTP/1.1 requests easily
- Unittest, Pytest, SQLite, CSS, JS, HTML

## Как запустить проект / Installation
Клонировать репозиторий на свой компьютер
```
git clone git@github.com:gplakhotnikov/PROJECT_NAME.git
```
Cоздать и активировать виртуальное окружение
```
python3 -m venv venv
source venv/bin/activate
```
Установить зависимости из файла requirements.txt
```
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```
Выполнить миграции
```
python3 manage.py migrate
```
Запустить проект
```
python3 manage.py runserver
```

## О разработчике / Development
Grigory Plakhotnikov
