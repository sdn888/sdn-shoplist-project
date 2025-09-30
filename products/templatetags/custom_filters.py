from django import template
from products.models import Category, Shop

register = template.Library()

@register.filter
def get_category(categories, category_id):
    """Получает название категории по ID"""
    try:
        category = Category.objects.get(id=category_id)
        return category.name
    except Category.DoesNotExist:
        return "Неизвестная категория"

@register.filter
def get_shop(shops, shop_id):
    """Получает название магазина по ID"""
    try:
        shop = Shop.objects.get(id=shop_id)
        return shop.name
    except Shop.DoesNotExist:
        return "Неизвестный магазин"

@register.filter
def format_price(value):
    """Форматирует цену с разделителями тысяч"""
    try:
        return f"{float(value):,.2f} ₽".replace(',', ' ').replace('.', ',')
    except (ValueError, TypeError):
        return f"{value} ₽"