from django import template
from products.models import Category

register = template.Library()

@register.filter
def get_category(categories, category_id):
    """Получает название категории по ID"""
    try:
        category = Category.objects.get(id=category_id)
        return category.name
    except Category.DoesNotExist:
        return "Неизвестная категория"