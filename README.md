# Online_store
## API для интернет магазина :credit_card:, реализует след функционал:
- Просмотр списка новостей, а также детальный просмотр конкретной новости <br/> 
- Просмотр списка лицензий, а также детальный просмотр конкретной лицензии <br/>
- Просмотр списка категорий <br/>
- Просмотр услуг, принадлежащих к конкретной категории <br/>
- Просмотр компаний, принадлежащих к конретному типу компании <br/>
- Реализация поиска по услугам <br/>

## Использованные технологии:
- Django, DRF <br/>
- Celery для отправки email об успешном оформлении заказа <br/>
- Redis для хранения и подсчета рекомендаций для товаров и как брокер для Celery <br/>
- PostgreSQL <br/>
- Docker <br/>

## Запуск проекта:
- git clone <br/>
- cd online_store <br/>
- создать .env файл со след константами: DEBUG, SECRET_KEY,DJANGO_ALLOWED_HOSTS,DB_ENGINE,DB_DATABASE,DB_USER,DB_PASSWORD,DB_HOST,DB_PORT
- docker-compose build <br/>
- docker-compose up <br/>
