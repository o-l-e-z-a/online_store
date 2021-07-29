import redis

from django.conf import settings

from .models import Product

# подключение к redis
r = redis.StrictRedis(host=settings.REDIS_HOST,
                      port=settings.REDIS_PORT,
                      db=settings.REDIS_DB)


class Recommender(object):
    """
    Класс для реализации системы рекомендаций для товаров
    """

    def get_product_key(self, id):
        """ возвращает ключ продукта для записи в redis """
        return 'product:{}:purchased_with'.format(id)

    def products_bought(self, products):
        """ доавление купленных продуктов """
        product_ids = [p.id for p in products]
        for product_id in product_ids:
            for with_id in product_ids:
                # get the other products bought with each product
                if product_id != with_id:
                    # increment score for product purchased together
                    name = self.get_product_key(product_id)
                    r.zincrby(name=name, value=with_id, amount=1)

    def suggest_products_for(self, products, max_results=6):
        product_ids = [p.id for p in products]
        if len(products) == 0:
            return []
        elif len(products) == 1:
            # Передан только один товар.
            suggestions = r.zrange(
                self.get_product_key(product_ids[0]),
                0, -1, desc=True)[:max_results]
        else:
            # Формируем временный ключ хранилища.
            flat_ids = ''.join([str(id) for id in product_ids])
            tmp_key = 'tmp_{}'.format(flat_ids)
            print()
            print(tmp_key)
            # Передано несколько товаров, суммируем рейтинги их рекомендаций.
            # Сохраняем суммы во временном ключе.
            keys = [self.get_product_key(id) for id in product_ids]
            print(keys)
            r.zunionstore(tmp_key, keys)
            # Удаляем ID товаров, которые были переданы всписке.
            r.zrem(tmp_key, *product_ids)
            # Получаем товары, отсортированные по рейтингу.
            suggestions = r.zrange(tmp_key, 0, -1,
                                   desc=True)[:max_results]
            # Удаляем временный ключ.
            r.delete(tmp_key)
        suggested_products_ids = [int(id) for id in suggestions]
        suggested_products = Product.objects.filter(id__in=suggested_products_ids)

        return suggested_products

    def clear_purchases(self):
        """
        удаление рекомендаций для продуктов
        """
        for id in Product.objects.values_list('id', flat=True):
            r.delete(self.get_product_key(id))