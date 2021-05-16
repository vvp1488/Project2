import sys
from PIL import Image

from django.db import models
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.urls import reverse
from django.utils import timezone

from io import BytesIO

User = get_user_model()


def get_models_for_count(*model_names):
    return [models.Count(model_name) for model_name in model_names]




class MinResolutionErrorException(Exception):
    pass


class MaxResolutionErrorException(Exception):
    pass


class Category(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название категории')
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Product(models.Model):
    MIN_RESOLUTION = (400, 400)
    MAX_RESOLUTION = (800, 800)
    MAX_IMAGE_SIZE = 3145728

    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE,related_name='products_for_category')
    title = models.CharField(max_length=255, verbose_name='Наименование')
    slug = models.SlugField(unique=True)
    image = models.ImageField(verbose_name='Изображения')
    description = models.TextField(verbose_name='Описание', null=True)
    price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Цена')

    def __str__(self):
        return self.title

    def get_model_name(self):
        return self.__class__.__name__.lower()

    def save(self, *args, **kwargs):
        # image=self.image
        # img = Image.open(image)
        # min_width, min_height = self.MIN_RESOLUTION
        # max_width, max_height = self.MAX_RESOLUTION
        # if img.width < min_width or img.height < min_height:
        #     raise MinResolutionErrorException('Изображения меньше минимального разрешения')
        # elif img.width > max_width or img.height > max_height:
        #     raise MaxResolutionErrorException('Изображения больше максимального разрешения')
        image = self.image
        img = Image.open(image)
        new_img = img.convert('RGB')
        resized_new_img = new_img.resize((200, 200), Image.ANTIALIAS)
        file_stream = BytesIO()
        resized_new_img.save(file_stream, 'JPEG', quality=90)
        file_stream.seek(0)
        name = '{}.{}'.format(*self.image.name.split('.'))
        self.image = InMemoryUploadedFile(
            file_stream, 'ImageField', name, 'jpeg/image', sys.getsizeof(file_stream), None
        )
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug':self.slug})


class CartProduct(models.Model):
    user = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE, related_name='related_product')
    product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(verbose_name='К-ство', default=1)
    final_price = models.DecimalField(max_digits=9, decimal_places=2, verbose_name='Общаяя цена')

    def __str__(self):
        return "Cart Product: {} (для корзины) ".format(self.product.title)

    def save(self, *args, **kwargs):
        self.final_price = self.qty * self.product.price
        super().save(*args, **kwargs)


class Cart(models.Model):
    owner = models.ForeignKey('Customer', null=True, verbose_name='Владелец', on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField(default=0)
    final_price = models.DecimalField(max_digits=9, default=0, decimal_places=2, verbose_name='Общаяя цена')
    in_order = models.BooleanField(default=False)
    for_anonymous_user = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class Customer(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, verbose_name='Номер телефона', blank=True, null=True)
    address = models.CharField(max_length=255, verbose_name='Адрес', blank=True, null=True)
    orders = models.ManyToManyField('Order', verbose_name='Заказы покупателя', related_name='related_customer')

    def __str__(self):
        return 'Покупатель :  {}'.format(self.user)


class Order(models.Model):
    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_READY = 'is_ready'
    STATUS_COMPLETED = 'completed'

    BUYING_TYPE_SELF = 'self'
    BUYING_TYPE_DELIVERY = 'delivery'

    STATUS_CHOICES = (
        (STATUS_NEW, 'Новый заказ'),
        (STATUS_IN_PROGRESS, 'Заказ в обработке'),
        (STATUS_READY, 'Заказ готов'),
        (STATUS_COMPLETED, 'Заказ выполнен')
    )

    BUYING_TYPE_CHOICES = (
        (BUYING_TYPE_SELF, 'Самовывоз'),
        (BUYING_TYPE_DELIVERY, 'Доставка')

    )
    customer = models.ForeignKey(Customer, verbose_name='Покупатель', on_delete=models.CASCADE,
                                 related_name='related_orders')
    first_name = models.CharField(max_length=255, verbose_name='Имя')
    last_name = models.CharField(max_length=255, verbose_name='Фамилия')
    cart = models.ForeignKey(Cart, verbose_name='Корзина', on_delete=models.CASCADE, null=True, blank=True)
    phone = models.CharField(max_length=25, verbose_name='Телефон')
    address = models.CharField(max_length=1024, verbose_name='Адрес', null=True, blank=True)
    status = models.CharField(max_length=255, verbose_name='Статус заказа', choices=STATUS_CHOICES, default=STATUS_NEW)
    buying_type = models.CharField(
        max_length=255,
        verbose_name='Тип заказа',
        choices=BUYING_TYPE_CHOICES,
        default=BUYING_TYPE_SELF)
    comment = models.TextField(verbose_name='Коментарий к заказу', null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True, verbose_name='Дата создания заказа')
    order_date = models.DateField(verbose_name='Дата получения заказа', default=timezone.now)

    def __str__(self):
        return (f'Заказ номер {self.id} на сумму : {self.cart.final_price} грн')
