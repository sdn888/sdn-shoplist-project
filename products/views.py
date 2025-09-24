from django.shortcuts import render, get_object_or_404
from .models import Product


def product_list(request):
    search_query = request.GET.get('q', '')

    if search_query:
        # Простой и надежный поиск
        search_lower = search_query.lower()
        all_products = Product.objects.filter(is_active=True)

        products = [
            p for p in all_products
            if search_lower in p.name.lower() or search_lower in p.description.lower()
        ]
    else:
        products = Product.objects.filter(is_active=True)

    return render(request, 'products/product_list.html', {
        'products': products,
        'search_query': search_query
    })

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    return render(request, 'products/product_detail.html', {'product': product})
