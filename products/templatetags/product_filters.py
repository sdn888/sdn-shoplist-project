from django import template

register = template.Library()

@register.filter
def format_price(value):
    """Форматирует цену в читаемый вид"""
    try:
        if value is None:
            return "0 ₽"
        return f"{float(value):,.2f} ₽".replace(',', ' ').replace('.', ',')
    except (ValueError, TypeError):
        return "0 ₽"