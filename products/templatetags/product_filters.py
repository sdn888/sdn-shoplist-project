from django import template

register = template.Library()

@register.filter
def format_price(value):
    """Форматирует цену с разделителями тысяч"""
    try:
        price = float(value)
        # Форматируем: 89990 → "89 990,00 ₽"
        return "{:,.2f} ₽".format(price).replace(",", " ").replace(".", ",")
    except (ValueError, TypeError):
        return f"{value} ₽"