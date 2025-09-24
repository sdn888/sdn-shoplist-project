from django.shortcuts import render, get_object_or_404, redirect
from .models import Product
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.decorators import manager_required
from .forms import ProductForm


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
