from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

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
    # ИСПРАВЛЯЕМ: используем TextField для адресов вместо ManyToMany
    shop_addresses = models.TextField(
        verbose_name="Адреса магазинов",
        help_text="Перечислите адреса магазинов через точку с запятой (;)",
        blank = True
    )
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
            # Разделяем по точке с запятой
            addresses = [addr.strip() for addr in self.shop_addresses.split(';') if addr.strip()]
            return ", ".join(addresses)
        return "Нет в наличии"

    def save(self, *args, **kwargs):
        # При сохранении создаем поле для поиска в нижнем регистре
        self.search_name = self.name.lower()
        self.search_description = self.description.lower()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"


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
