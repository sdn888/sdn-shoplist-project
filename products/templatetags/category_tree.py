from django import template
from products.models import Category

register = template.Library()


@register.inclusion_tag('products/category_tree.html')
def render_category_tree(selected_category=None):
    def get_categories_with_children(parent=None):
        categories = Category.objects.filter(parent=parent).order_by('name')
        result = []
        for category in categories:
            result.append({
                'category': category,
                'children': get_categories_with_children(category)
            })
        return result

    return {
        'categories_tree': get_categories_with_children(),
        'selected_category': selected_category
    }