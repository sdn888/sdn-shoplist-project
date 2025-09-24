from django.db import models
from django.contrib.auth import get_user_model


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
        help_text="Перечислите адреса магазинов через запятую"
    )
    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        verbose_name="Создатель"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name="Активный")

    def __str__(self):
        return self.name

    def get_shops_display(self):
        """Возвращает форматированный список адресов"""
        if self.shop_addresses:
            return self.shop_addresses
        return "Нет в наличии"

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"