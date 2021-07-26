from django.db.models import ExpressionWrapper, F, DecimalField, Sum
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from django.contrib.postgres.search import SearchVector, SearchRank, SearchQuery

from .models import Product, Cart


class Pagination(PageNumberPagination):
    """ Пагинатор"""
    page_size = 20
    max_page_size = 200
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'data': data
        })


class PaginationProductForCategory(Pagination):
    pass


class PaginationSearch(Pagination):
    pass


def product_search(query_params):
    """ Улучшенный поиск с помощью расширения postgres"""
    if query_params:
        search_vector = SearchVector('name', weight='A') +\
                        SearchVector('brand__name', weight='B') +\
                        SearchVector('category__name', weight='B') + \
                        SearchVector('category__parent__name', weight='C')
        search_query = SearchQuery(query_params)
        results = Product.objects.select_related('brand').prefetch_related('category').annotate(
            rank=SearchRank(search_vector, search_query)
        ).filter(rank__gte=0.1).order_by('-rank')
    else:
        results = Product.objects.select_related('brand').prefetch_related('category').all()
    return results


def get_product_sum(user):
    return Cart.objects.filter(customer=user, order__isnull=True).select_related('product').annotate(
        sum=ExpressionWrapper(F('product__price') * F('quantity'), output_field=DecimalField()))


def get_products_total_sum(user):
    return get_product_sum(user).aggregate(
        final_cost=Sum('sum', output_field=DecimalField()), count=Sum('quantity')
    )
