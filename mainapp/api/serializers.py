from rest_framework import serializers
from ..models import Category, Customer ,Order


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):

    orders = OrderSerializer(many=True)

    class Meta:
        model = Customer
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):

    title = serializers.CharField(required=True)
    slug = serializers.SlugField()

    class Meta:
        model = Category
        fields = [
            'id', 'title', 'slug'
        ]


class BaseProductSerializer():
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects)
    title = serializers.CharField(required=True)
    slug = serializers.SlugField(required=True)
    image = serializers.ImageField(required=True)
    description = serializers.CharField(required=False)
    price = serializers.DecimalField(max_digits=9, decimal_places=2, required=True)



