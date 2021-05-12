from collections import OrderedDict

from rest_framework.response import Response
from rest_framework.generics import ListAPIView , RetrieveAPIView , ListCreateAPIView ,RetrieveUpdateAPIView , RetrieveDestroyAPIView
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination

from .serializers import CategorySerializer, SmartphoneSerializer ,NotebookSerializer ,CustomerSerializer
from ..models import Category, Smartphone , Notebook , Customer


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


class SmartphoneListAPIView(ListAPIView):
    serializer_class = SmartphoneSerializer
    pagination_class = ProductPagination
    queryset = Smartphone.objects.all()
    filter_backends = [SearchFilter]
    search_fields = ['title','price']


class NotebookListAPIView(ListAPIView):
    serializer_class = NotebookSerializer
    queryset =  Notebook.objects.all()
    filter_backends = [SearchFilter]
    search_fields = ['title','price']


class SmartphoneDetailAPIView(RetrieveAPIView):
    serializer_class = SmartphoneSerializer
    queryset = Smartphone.objects.all()
    lookup_field = 'id'


class CustomersListAPIView(ListAPIView):

    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()

