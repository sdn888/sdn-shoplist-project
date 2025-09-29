from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                               verbose_name="Родительская категория", related_name='children')
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']

    def __str__(self):
        if self.parent:
            return f"{self.parent} → {self.name}"
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название товара")
    description = models.TextField(verbose_name="Описание", blank=True)
    image = models.ImageField(
        upload_to='products/',
        verbose_name="Изображение",
        blank=True,
        null=True
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена"
    )
    shop_addresses = models.TextField(
        verbose_name="Адреса магазинов",
        help_text="Перечислите адреса магазинов через точку с запятой (;)",
        blank=True
    )
    category = models.ForeignKey(Category, on_delete=models.SET_NULL,
                                 null=True, blank=True, verbose_name="Категория")
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        verbose_name="Создатель"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name="Активный")

    search_name = models.CharField(max_length=200, blank=True, editable=False)
    search_description = models.TextField(blank=True, editable=False)

    def __str__(self):
        return self.name

    def get_shops_display(self):
        """Возвращает форматированный список адресов"""
        if self.shop_addresses:
            addresses = [addr.strip() for addr in self.shop_addresses.split(';') if addr.strip()]
            return ", ".join(addresses)
        return "Нет в наличии"

    def save(self, *args, **kwargs):
        self.search_name = self.name.lower()
        self.search_description = self.description.lower()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']  # ← ДОБАВИЛ СОРТИРОВКУ

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/', verbose_name="Изображение")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товаров"
        ordering = ['order']

    def __str__(self):
        return f"Изображение {self.id} для {self.product.name}"



class Cart(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return self.product.price * self.quantity

    class Meta:
        unique_together = ['cart', 'product']


@receiver(post_save, sender=get_user_model())
def create_user_cart(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)


# Данные для категорий (оставлю для справки)
CATEGORIES_DATA = {
    "Продукты питания": {
        "Молочные продукты": ["Молоко", "Сыр", "Йогурты", "Творог"],
        "Мясо и птица": ["Говядина", "Свинина", "Курица", "Колбасы"],
        "Бакалея": ["Крупы", "Макароны", "Мука", "Сахар"],
        "Напитки": ["Соки", "Вода", "Газировка", "Чай", "Кофе"]
    },
    "Электроника": {
        "Смартфоны и гаджеты": ["Смартфоны", "Планшеты", "Умные часы"],
        "Компьютеры": ["Ноутбуки", "ПК", "Мониторы", "Комплектующие"],
        "Техника для дома": ["Телевизоры", "Холодильники", "Стиральные машины"],
        "Аудиотехника": ["Наушники", "Колонки", "Саундбары"]
    },
    "Товары для дома": {
        "Мебель": ["Диваны", "Кровати", "Столы", "Стулья"],
        "Текстиль": ["Шторы", "Постельное белье", "Покрывала"],
        "Кухонные принадлежности": ["Посуда", "Столовые приборы", "Кастрюли"]
    },
    "Одежда и обувь": {
        "Мужская одежда": ["Рубашки", "Брюки", "Куртки", "Футболки"],
        "Женская одежда": ["Платья", "Юбки", "Блузки", "Верхняя одежда"],
        "Обувь": ["Кроссовки", "Туфли", "Сапоги", "Ботинки"]
    },
    "Товары для автомобиля": {
        "Запчасти": ["Аккумуляторы", "Шины", "Тормозные колодки"],
        "Автохимия": ["Масла", "Омывайки", "Очистители"],
        "Аксессуары": ["Чехлы", "Коврики", "Ароматизаторы"]
    },
    "Услуги": {
        "Ремонтные работы": ["Сантехника", "Электрика", "Отделочные работы"],
        "Клининговые услуги": ["Уборка", "Химчистка", "Мойка окон"],
        "Доставка": ["Доставка продуктов", "Доставка товаров"]
    },
    "Прочие товары и услуги": {
        "Прочие товары": [],
        "Прочие услуги": []
    }
}