from django import template
from products.models import Category

register = template.Library()

@register.filter
def get_category(categories, category_id):
    """Возвращает название категории по ID"""
    try:
        return categories.get(id=int(category_id)).name
    except (Category.DoesNotExist, ValueError, AttributeError):
        return "Неизвестная категория"