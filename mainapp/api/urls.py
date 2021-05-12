from django.urls import path
from .api_views import (
    CategoryAPIView,
    SmartphoneListAPIView,
    NotebookListAPIView,
    SmartphoneDetailAPIView,
    CustomersListAPIView
)

urlpatterns = [
    path('categories/',  CategoryAPIView.as_view(), name='categories_list'),
    path('categories/<str:id>/', CategoryAPIView.as_view(), name='categories_update'),
    path('customers/', CustomersListAPIView.as_view(), name='customers_list'),
    path('notebooks/<str:id>', NotebookListAPIView.as_view(), name='notebooks_list'),
    path('smartphones/', SmartphoneListAPIView.as_view(), name='smartphones_list'),
    path('smartphones/<str:id>', SmartphoneDetailAPIView.as_view(), name='smartphone_detail'),

]
