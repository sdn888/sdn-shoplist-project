from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
import os
from uuid import uuid4


def product_main_image_path(instance, filename):
    """Путь для основного изображения товара"""
    ext = filename.split('.')[-1]
    filename = f"{uuid4().hex}.{ext}"
    return os.path.join('products', 'main', filename)


def product_gallery_image_path(instance, filename):
    """Путь для изображений галереи товара"""
    ext = filename.split('.')[-1]
    filename = f"{uuid4().hex}.{ext}"
    return os.path.join('products', 'gallery', filename)


class CategoryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by('parent_id', 'name')


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название категории')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                               verbose_name='Родительская категория')
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CategoryManager()  # ← ДОБАВИТЬ ЭТУ СТРОКУ

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        # ordering можно убрать если используем менеджер

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} → {self.name}"
        return self.name


class Shop(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название магазина')
    address = models.TextField(verbose_name='Адрес')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    opening_hours = models.CharField(max_length=100, blank=True, verbose_name='Часы работы')
    latitude = models.FloatField(null=True, blank=True, verbose_name='Широта')
    longitude = models.FloatField(null=True, blank=True, verbose_name='Долгота')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Владелец',
                              related_name='shops')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'

    def __str__(self):
        return f"{self.name} - {self.address}"


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название товара')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Категория')
    description = models.TextField(blank=True, verbose_name='Описание')
    image = models.ImageField(upload_to=product_main_image_path, blank=True, null=True,
                              verbose_name='Основное изображение')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name='Цена')
    shops = models.ManyToManyField(Shop, blank=True, verbose_name='Магазины')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Добавил')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name='Активный')

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def shop_addresses(self):
        return "\n".join([shop.address for shop in self.shops.all()])


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=product_gallery_image_path)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображения товаров'

    def __str__(self):
        return f"Изображение {self.order} для {self.product.name}"


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_items_property(self):
        return self.total_items()

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

    @property
    def total_price_property(self):
        return self.total_price()

    def __str__(self):
        return f"Корзина {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return self.product.price * self.quantity

    @property
    def total_price_property(self):
        return self.total_price()

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Пользователь')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные товары'
        unique_together = ['user', 'product']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"