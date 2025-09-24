from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Cart, CartItem
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.decorators import manager_required
from .forms import ProductForm
from django.core.paginator import Paginator


def product_list(request):
    search_query = request.GET.get('q', '')
    page_number = request.GET.get('page', 1)

    if search_query:
        search_lower = search_query.lower()
        all_products = Product.objects.filter(is_active=True)
        products_list = [
            p for p in all_products
            if search_lower in p.name.lower() or search_lower in p.description.lower()
        ]
    else:
        products_list = Product.objects.filter(is_active=True)

    # Пагинация - 6 товаров на страницу
    paginator = Paginator(products_list, 6)
    page_obj = paginator.get_page(page_number)

    return render(request, 'products/product_list.html', {
        'products': page_obj,
        'search_query': search_query,
        'page_obj': page_obj
    })

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    return render(request, 'products/product_detail.html', {'product': product})


@login_required
@manager_required
def product_manage(request):
    """Панель управления товарами для менеджеров"""
    products = Product.objects.filter(created_by=request.user)
    return render(request, 'products/manage.html', {'products': products})


@login_required
@manager_required
def product_add(request):
    """Добавление нового товара"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.save()
            messages.success(request, f'Товар "{product.name}" успешно добавлен!')
            return redirect('product_manage')
    else:
        form = ProductForm()

    return render(request, 'products/product_form.html', {
        'form': form,
        'title': 'Добавить товар'
    })


@login_required
@manager_required
def product_edit(request, product_id):
    """Редактирование товара"""
    product = get_object_or_404(Product, id=product_id, created_by=request.user)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Товар "{product.name}" успешно обновлен!')
            return redirect('product_manage')
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/product_form.html', {
        'form': form,
        'title': 'Редактировать товар',
        'product': product
    })


@login_required
@manager_required
def product_delete(request, product_id):
    """Удаление товара"""
    product = get_object_or_404(Product, id=product_id, created_by=request.user)

    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Товар "{product_name}" успешно удален!')
        return redirect('product_manage')

    return render(request, 'products/product_confirm_delete.html', {'product': product})


@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'products/cart.html', {'cart': cart})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f'Товар "{product.name}" добавлен в корзину!')
    return redirect('product_detail', product_id=product.id)


@login_required
def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_object_or_404(Cart, user=request.user)

    cart_item = get_object_or_404(CartItem, cart=cart, product=product)
    cart_item.delete()

    messages.success(request, f'Товар "{product.name}" удален из корзины!')
    return redirect('cart_view')
