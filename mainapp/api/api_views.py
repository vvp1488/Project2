from collections import OrderedDict

from rest_framework.response import Response
from rest_framework.generics import ListAPIView  , ListCreateAPIView ,RetrieveUpdateAPIView , RetrieveDestroyAPIView

from rest_framework.pagination import PageNumberPagination

from .serializers import CategorySerializer,CustomerSerializer
from ..models import Category, Customer


class CategoryPagination(PageNumberPagination):
    page_size = 2
    page_query_param = 'page'
    max_page_size = 10

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('К-ство категорий', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('Результат', data)
        ]))


class ProductPagination(PageNumberPagination):
    page_size = 2
    page_query_param = 'page'
    max_page_size = 10

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('К-ство категорий', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('Результат', data)
        ]))


class CategoryAPIView(ListCreateAPIView, RetrieveUpdateAPIView, RetrieveDestroyAPIView):

    serializer_class = CategorySerializer
    pagination_class = CategoryPagination
    queryset = Category.objects.all()
    lookup_field = 'id'




class CustomersListAPIView(ListAPIView):

    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()

