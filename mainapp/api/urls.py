from django.urls import path
from .api_views import (
    CategoryAPIView,

    CustomersListAPIView
)

urlpatterns = [
    path('categories/',  CategoryAPIView.as_view(), name='categories_list'),
    path('categories/<str:id>/', CategoryAPIView.as_view(), name='categories_update'),
    path('customers/', CustomersListAPIView.as_view(), name='customers_list'),

]
