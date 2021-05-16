from django.db import transaction
from django.shortcuts import render
from django.contrib.auth import authenticate, login

from django.http import HttpResponseRedirect
from django.views.generic import DetailView, View
from .models import Category, Customer, Cart, CartProduct, Product, Order
from .mixins import CartMixin
from django.contrib import messages
from .forms import OrderForm, LoginForm, RegistrationForm
from .utils import recalc_cart


class BaseView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        products = Product.objects.all()

        context = {
            'categories': categories,
            'products': products,
            'cart': self.cart
        }
        return render(request, 'base.html', context)


class CategoryDetailView(CartMixin, DetailView):
    model = Category
    queryset = Category.objects.all()
    context_object_name = 'category'
    template_name = 'category_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = self.cart
        return context


class ProductDetailView(CartMixin, DetailView):
    queryset = Product.objects.all()

    context_object_name = 'product'
    template_name = 'product_detail.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = self.cart
        return context


class AddToCartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        product_slug = kwargs.get('slug')

        product = Product.objects.get(slug=product_slug)
        user = request.user
        if user.is_authenticated:
            cart_product, created = CartProduct.objects.get_or_create(
                user=self.cart.owner, cart=self.cart, product=product)
            if created:
                self.cart.products.add(cart_product)
            recalc_cart(self.cart)
            messages.add_message(request, messages.INFO, 'Товар успешно добавлен в корзину')
        else:
            messages.add_message(request, messages.INFO, 'Сначало нужно войти в систему')
            return HttpResponseRedirect('/login/')
        return HttpResponseRedirect('/cart/')


class DeleteFromCartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        product_slug = kwargs.get('slug')
        product = Product.objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart,
            product=product)
        self.cart.products.remove(cart_product)
        cart_product.delete()
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, 'Товар успешно удален из корзины')
        return HttpResponseRedirect('/cart/')


class CartView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        context = {
            'cart': self.cart,
            'categories': categories
        }
        return render(request, 'cart.html', context)


class CheckoutView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        form = OrderForm(request.POST or None)
        context = {
            'form': form,
            'cart': self.cart,
            'categories': categories
        }
        return render(request, 'checkout.html', context)


class ChangeQTYView(CartMixin, View):

    def post(self, request, *args, **kwargs):
        product_slug = kwargs.get('slug')
        product = Product.objects.get(slug=product_slug)
        cart_product = CartProduct.objects.get(
            user=self.cart.owner, cart=self.cart, product=product)
        qty = int(request.POST.get('qty'))
        cart_product.qty = qty
        cart_product.save()
        recalc_cart(self.cart)
        messages.add_message(request, messages.INFO, 'К-ство успешно изменено')
        return HttpResponseRedirect('/cart/')


class MakeOrderView(CartMixin, View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = OrderForm(request.POST or None)
        customer = Customer.objects.get(user=request.user)
        if form.is_valid():
            new_order = form.save(commit=False)
            new_order.customer = customer
            new_order.first_name = form.cleaned_data['first_name']
            new_order.last_name = form.cleaned_data['last_name']
            new_order.phone = form.cleaned_data['phone']
            new_order.address = form.cleaned_data['address']
            new_order.buying_type = form.cleaned_data['buying_type']
            new_order.order_date = form.cleaned_data['order_date']
            new_order.comment = form.cleaned_data['comment']
            new_order.save()
            self.cart.in_order = True
            self.cart.save()
            new_order.cart = self.cart
            new_order.save()
            customer.orders.add(new_order)
            messages.add_message(request, messages.SUCCESS, 'Спасибо за заказ! Менеджер с вами свяжеться!')
            return HttpResponseRedirect('/')
        messages.add_message(request, messages.WARNING, 'Форма заполнена некоректно')
        return HttpResponseRedirect('/checkout/')


class LoginView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        categories = Category.objects.all()
        context = {
            'form': form,
            'categories': categories,
            'cart': self.cart
        }
        return render(request, 'login.html', context)

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return HttpResponseRedirect('/')
        return render(request, 'login.html', {'form': form, 'cart': self.cart})

    def logoutuser(self, request, *args, **kwargs):
        username = request.user
        print(username)


class RegistrationView(CartMixin, View):

    def get(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST or None)
        categories = Category.objects.all()
        context = {'form':form, 'categories':categories, 'cart':self.cart}
        return render(request,'registration.html',context)

    def post(self,request,*args, **kwargs):
        form = RegistrationForm(request.POST or None)
        categories = Category.objects.all()
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.username = form.cleaned_data['username']
            new_user.phone = form.cleaned_data['phone']
            new_user.first_name = form.cleaned_data['first_name']
            new_user.last_name = form.cleaned_data['last_name']
            new_user.address = form.cleaned_data['address']
            new_user.save()
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            Customer.objects.create(
                user = new_user,
                phone = form.cleaned_data['phone'],
                address = form.cleaned_data['address']

            )
            user = authenticate(username = form.cleaned_data['username'], password = form.cleaned_data['password'])
            login(request, user)
            messages.add_message(request, messages.INFO, 'Пользователь успешно зарегистрирован')
            return HttpResponseRedirect('/')
        return render(request,'registration.html',{'form':form,'categories':categories,'cart':self.cart})


class ProfileView(CartMixin,View):

    def get(self,request,*args,**kwargs):
        customer = Customer.objects.get(user=request.user)
        orders = Order.objects.filter(customer=customer)
        categories = Category.objects.all()
        context = {
            'cart': self.cart,
            'orders' : orders,
            'categories' : categories
        }
        return render(request,'profile.html',context)