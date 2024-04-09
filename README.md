![Static Badge](https://img.shields.io/badge/Python-blue?logo=python&logoColor=%23F7DF1E)
![Static Badge](https://img.shields.io/badge/Django-%23092E20?logo=django)
![Static Badge](https://img.shields.io/badge/Django%20rest%20framework-red?logo=django&labelColor=%23092E20)
![Static Badge](https://img.shields.io/badge/GitHub-%23181717?logo=github)
![Static Badge](https://img.shields.io/badge/nginx-%23009639?logo=nginx)
![Static Badge](https://img.shields.io/badge/JavaScript-%23F7DF1E?logo=javascript&labelColor=%23181717)
![Static Badge](https://img.shields.io/badge/PostgreSQL-%234169E1?logo=postgresql&logoColor=white)
![Static Badge](https://img.shields.io/badge/Docker-%232496ED?logo=docker&logoColor=white)
![Static Badge](https://img.shields.io/badge/GitHub%20Actions-%232088FF?logo=githubactions&logoColor=white)

### Описание:

Продуктовый помощник Foodgram.

Посетить веб-сайт проекта: http://foodgram-project.ddns.net

«Продуктовый помощник»: приложение, в котором пользователи публикуют рецепты, есть возможность подписаться на публикации других авторов и добавлять рецепты в избранное. В приложении есть сервис «Список покупок» который позволяет пользователю создавать список продуктов, которые нужно купить для приготовления выбранных блюд, так же есть возможость скачать этот список в текстовом виде перед походом в магазин.

Реализован workflow c автодеплоем на удаленный сервер и отправкой сообщения в Telegram

### Как запустить проект:

## Локальный запуск проекта:
```
Клонируйте репозиторий с проектом на свой компьютер. В терминале из рабочей директории выполните команду:

git clone https://github.com/FrolovAlex22/foodgram-project-react

```
Cоздать и активировать виртуальное окружение:

Команда для установки виртуального окружения на Mac или Linux:

python3 -m venv env
source env/bin/activate

Команда для Windows:

python -m venv venv
source venv/Scripts/activate

```
Перейти в директорию infra:

cd infra

Создать файл .env по образцу:

.env.example

```
Установить зависимости из файла requirements.txt

cd ..
cd backend/foodgram
pip install -r requirements.txt

```
Выполните миграции:

python manage.py migrate

```
Создание нового супер пользователя:

python manage.py createsuperuser

```
Заполните базу тестовыми данными:

python manage.py add_tags
python manage.py add_ingidients 

```
Запустить локальный сервер:

python manage.py runserver

## Установка на удалённом сервере:
```
Выполнить вход на удаленный сервер

Установить docker:

sudo apt install docker.io

```
Установить docker-compose:

sudo apt install docker-compose    

```
Находясь локально в директории infra/, скопировать файлы docker-compose.yml и nginx.conf на удаленный сервер:

scp docker-compose.yml <username>@<host>:/home/<username>/
scp nginx.conf <username>@<host>:/home/<username>/

```
Выполните команду:

docker compose up 

```
Создайте и выполните миграции:

docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate

```
Создайте суперпользователя:

docker-compose exec backend python manage.py createsuperuser

```
Загрузите статику:

docker-compose exec backend python manage.py collectstatic

```
Заполните базу тестовыми данными:

docker-compose exec backend python manage.py add_tags
docker-compose exec backend python manage.py add_ingidients 

### Основные адреса:

```
Регистрация пользователя:

/api/users/

```
Получение данных своей учетной записи:

/api/users/me/ 

```
Добавление подписки:

/api/users/id/subscribe/

```
Обновление рецепта:

/api/recipes/id/

```
Удаление рецепта из избранного:

/api/recipes/id/favorite/

```
Получение списка ингредиентов:

/api/ingredients/

```
Скачать список покупок:

/api/recipes/download_shopping_cart/

```
Полный список запросов API находятся в документации

### Автор:

Фролов Александр
email: frolov.bsk@yandex.ru
github: https://github.com/FrolovAlex22
