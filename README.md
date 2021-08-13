# Online_store
## API для интернет магазина :credit_card:, реализует следующий функционал:
- Регистрация и авторизация по токену
- CRUD адреса пользователя <br/> 
- Просмотр списка категорий, а также просмотр товаров, принадлежащих к конкретной категории <br/>
- Просмотр отдельного товара <br/>
- Поиск по товарам (для улучшения поиска использовался модуль postgres.search)<br/>
- CRUD корзины <br/>
- Просмотр краткой информации о  корзине (общее кол-во и итоговая стоимость) <br/>
- Просмотр и добавление заказа
- Отправка email об успешном заказе
- Система купонов на скидку 
- Система рекомедаций для товаров
- Подключена тестовая платформа для оплаты
- Выгрузка заказов в csv в админке

## Использованные технологии:
- Django, DRF <br/>
- Celery для отправки email об успешном оформлении заказа <br/>
- Redis для хранения и подсчета рекомендаций для товаров и как брокер для Celery <br/>
- PostgreSQL <br/>
- Docker <br/>

## Запуск проекта:
- git clone https://github.com/o-l-e-z-a/online_store.git <br/>
- cd online_store <br/>
- создать .env файл со след константами: DEBUG, SECRET_KEY,DJANGO_ALLOWED_HOSTS,DB_ENGINE,DB_DATABASE,DB_USER,DB_PASSWORD,DB_HOST,DB_PORT,REDIS_HOST,REDIS_PORT,REDIS_DB,EMAIL_HOST_USER,EMAIL_HOST_PASSWORD,BRAINTREE_MERCHANT_ID,BRAINTREE_PUBLIC_KEY,BRAINTREE_PRIVATE_KEY
- docker-compose up --build <br/>
