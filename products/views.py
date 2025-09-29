from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Category, Cart, CartItem, ProductImage
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.decorators import manager_required
from .forms import ProductForm, ProductImageForm  # ← ИМПОРТИРУЕМ ProductImageForm
from django.core.paginator import Paginator
from django.db import models

def product_list(request):
    search_query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    page_number = request.GET.get('page', 1)

    # Базовый запрос
    products = Product.objects.filter(is_active=True).order_by('-created_at')

    # Фильтрация по категории (ПРОСТОЙ ВАРИАНТ - все уровни)
    if category_filter:
        # Ищем товары, у которых категория ИЛИ любой из родителей равен выбранной категории
        products = products.filter(
            models.Q(category_id=category_filter) |
            models.Q(category__parent_id=category_filter) |
            models.Q(category__parent__parent_id=category_filter)
        )

    # Поиск
    if search_query:
        search_lower = search_query.lower()
        products_list = [
            p for p in products
            if search_lower in p.name.lower() or search_lower in p.description.lower()
        ]
    else:
        products_list = list(products)

    # Пагинация
    paginator = Paginator(products_list, 6)
    page_obj = paginator.get_page(page_number)

    # Категории для фильтра
    categories = Category.objects.filter(parent__isnull=True)

    return render(request, 'products/product_list.html', {
        'products': page_obj,
        'search_query': search_query,
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': category_filter
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    return render(request, 'products/product_detail.html', {'product': product})


@login_required
@manager_required
def product_manage(request):
    """Панель управления товарами для менеджеров"""
    products = Product.objects.filter(created_by=request.user).order_by('-created_at')
    return render(request, 'products/manage.html', {'products': products})


@login_required
@manager_required
def product_add(request):
    """Добавление нового товара с изображениями"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.save()

            # ПРАВИЛЬНАЯ ОБРАБОТКА МНОЖЕСТВЕННЫХ ФАЙЛОВ
            additional_images = request.FILES.getlist('additional_images')
            print(f"DEBUG: Получено файлов: {len(additional_images)}")  # Для отладки

            for i, image_file in enumerate(additional_images[:6]):  # Максимум 6 изображений
                try:
                    ProductImage.objects.create(
                        product=product,
                        image=image_file,
                        order=i + 1
                    )
                    print(f"DEBUG: Создано изображение {i + 1}")  # Для отладки
                except Exception as e:
                    print(f"DEBUG: Ошибка при создании изображения {i + 1}: {e}")

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
    """Редактирование товара с изображениями"""
    try:
        product = get_object_or_404(Product, id=product_id)

        # Проверяем права доступа - менеджер может редактировать только свои товары
        if product.created_by != request.user and request.user.role != 'admin':
            messages.error(request, 'У вас нет прав для редактирования этого товара')
            return redirect('product_list')

    except Product.DoesNotExist:
        messages.error(request, 'Товар не найден')
        return redirect('product_manage')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()

            # ИСПРАВЛЕНИЕ: используем правильное имя поля 'images'
            additional_images = request.FILES.getlist('images')
            existing_images_count = product.images.count()

            print(f"DEBUG: Получено файлов: {len(additional_images)}, существующих: {existing_images_count}")

            # Добавляем новые изображения
            for i, image_file in enumerate(additional_images):
                if existing_images_count + i < 6:  # Максимум 6 изображений всего
                    try:
                        ProductImage.objects.create(
                            product=product,
                            image=image_file,
                            order=existing_images_count + i + 1
                        )
                        print(f"DEBUG: Создано изображение {existing_images_count + i + 1}")
                    except Exception as e:
                        print(f"DEBUG: Ошибка при создании изображения: {e}")
                        messages.warning(request, f'Ошибка при загрузке изображения {i + 1}')

            messages.success(request, f'Товар "{product.name}" успешно обновлен!')
            return redirect('product_manage')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
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

    messages.success(request, f'Товар "{product.name}" удален из корзину!')
    return redirect('cart_view')

def handler403(request, exception):
    return render(request, '403.html', status=403)

def handler404(request, exception):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)