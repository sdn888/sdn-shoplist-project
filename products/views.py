from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Product, Category, Cart, CartItem, ProductImage, Shop, Favorite
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from users.decorators import manager_required
from .forms import ProductForm, ProductImageForm, ShopForm
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Q


def product_list(request):
    search_query = request.GET.get('q', '')
    category_filter = request.GET.get('category', '')
    shop_filter = request.GET.get('shop', '')
    price_min = request.GET.get('price_min', '')
    price_max = request.GET.get('price_max', '')
    sort_by = request.GET.get('sort', '-created_at')
    page_number = request.GET.get('page', 1)

    # Базовый запрос
    products = Product.objects.filter(is_active=True)

    # ФИЛЬТРАЦИЯ ПО КАТЕГОРИИ С ИЕРАРХИЕЙ
    if category_filter:
        def get_all_subcategories(category_id):
            subcategories = [category_id]
            children = Category.objects.filter(parent_id=category_id)
            for child in children:
                subcategories.extend(get_all_subcategories(child.id))
            return subcategories

        all_category_ids = get_all_subcategories(int(category_filter))
        products = products.filter(category_id__in=all_category_ids)

    # Фильтрация по магазину
    if shop_filter:
        products = products.filter(shops__id=shop_filter)

    # Фильтрация по цене
    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)

    # ПОИСК С РУССКОЙ ПОДДЕРЖКОЙ
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Сортировка
    products = products.order_by(sort_by)

    # Пагинация
    paginator = Paginator(products, 6)
    page_obj = paginator.get_page(page_number)

    # Данные для фильтров
    categories = Category.objects.filter(parent__isnull=True)
    shops = Shop.objects.all()

    # Избранное
    user_favorite_ids = []
    if request.user.is_authenticated:
        user_favorite_ids = list(Favorite.objects.filter(user=request.user).values_list('product_id', flat=True))

    return render(request, 'products/product_list.html', {
        'products': page_obj,
        'search_query': search_query,
        'page_obj': page_obj,
        'categories': categories,
        'shops': shops,
        'selected_category': category_filter,
        'selected_shop': shop_filter,
        'price_min': price_min,
        'price_max': price_max,
        'sort_by': sort_by,
        'user_favorite_ids': user_favorite_ids,
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)

    # Проверяем, добавлен ли товар в избранное для текущего пользователя
    user_favorites = False
    if request.user.is_authenticated:
        user_favorites = Favorite.objects.filter(user=request.user, product=product).exists()

    return render(request, 'products/product_detail.html', {
        'product': product,
        'user_favorites': user_favorites
    })


@login_required
@manager_required
def product_manage(request):
    """Панель управления товарами для менеджеров"""
    products = Product.objects.filter(created_by=request.user).order_by('-created_at')

    # Статистика для шаблона
    unique_categories = products.values('category').distinct().count()
    total_price = products.aggregate(total=models.Sum('price'))['total'] or 0

    return render(request, 'products/manage.html', {
        'products': products,
        'unique_categories': unique_categories,
        'total_price': total_price
    })


@login_required
@manager_required
def product_add(request):
    """Добавление нового товара с изображениями"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            product = form.save(commit=False)
            product.created_by = request.user
            product.save()  # Это сохранит все, включая M2M связи!

            # Обработка дополнительных изображений
            additional_images = request.FILES.getlist('images')
            for i, image_file in enumerate(additional_images[:6]):
                try:
                    ProductImage.objects.create(
                        product=product,
                        image=image_file,
                        order=i + 1
                    )
                except Exception as e:
                    print(f"Ошибка при создании изображения {i + 1}: {e}")

            messages.success(request, f'Товар "{product.name}" успешно добавлен!')
            return redirect('product_manage')
    else:
        form = ProductForm(user=request.user)

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
        form = ProductForm(request.POST, request.FILES, instance=product, user=request.user)
        if form.is_valid():
            # СОХРАНЯЕМ ОСНОВНЫЕ ДАННЫЕ
            product = form.save()  # Это сохранит все, включая M2M!

            # Обработка дополнительных изображений
            additional_images = request.FILES.getlist('images')
            existing_images_count = product.images.count()

            for i, image_file in enumerate(additional_images):
                if existing_images_count + i < 6:
                    try:
                        ProductImage.objects.create(
                            product=product,
                            image=image_file,
                            order=existing_images_count + i + 1
                        )
                    except Exception as e:
                        messages.warning(request, f'Ошибка при загрузке изображения {i + 1}')

            messages.success(request, f'Товар "{product.name}" успешно обновлен!')
            return redirect('product_manage')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме')
    else:
        form = ProductForm(instance=product, user=request.user)

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

    # Добавляем вычисленные значения в контекст для совместимости
    cart_items = cart.items.all()
    total_items = cart.total_items()
    total_price = cart.total_price()

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_items': total_items,
        'total_price': total_price
    }

    return render(request, 'products/cart.html', context)


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


# Магазины
def shop_list(request):
    """Список магазинов с картой"""
    shops = Shop.objects.all()
    return render(request, 'products/shop_list.html', {'shops': shops})


def nearest_shops(request):
    """Ближайшие магазины"""
    user_lat = request.GET.get('lat')
    user_lng = request.GET.get('lng')

    shops = Shop.objects.all()

    if user_lat and user_lng:
        shops = sorted(shops, key=lambda x: abs(x.latitude - float(user_lat)) + abs(
            x.longitude - float(user_lng)) if x.latitude and x.longitude else float('inf'))

    return render(request, 'products/nearest_shops.html', {'shops': shops})

@login_required
@manager_required
def shop_manage(request):
    """Управление магазинами для менеджеров"""
    shops = Shop.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'products/shop_manage.html', {'shops': shops})


@login_required
@manager_required
def shop_add(request):
    """Добавление магазина - ОТЛАДОЧНАЯ ВЕРСИЯ"""
    print("=== DEBUG SHOP_ADD ===")
    print("Method:", request.method)
    print("User:", request.user)
    print("User role:", getattr(request.user, 'role', 'NO ROLE'))

    if request.method == 'POST':
        print("POST data:", dict(request.POST))

        # Берем данные напрямую
        name = request.POST.get('name', '').strip()
        address = request.POST.get('address', '').strip()
        phone = request.POST.get('phone', '').strip()

        print("Extracted data:", {'name': name, 'address': address, 'phone': phone})

        if name and address:
            try:
                shop = Shop(
                    name=name,
                    address=address,
                    phone=phone,
                    owner=request.user
                )
                shop.save()
                print("SUCCESS: Shop saved with ID:", shop.id)
                messages.success(request, f'Магазин "{name}" успешно добавлен!')
                return redirect('shop_manage')
            except Exception as e:
                print("ERROR:", str(e))
                messages.error(request, f'Ошибка: {str(e)}')
        else:
            messages.error(request, 'Заполните название и адрес')

    # Всегда показываем форму
    return render(request, 'products/shop_form.html', {'title': 'Добавить магазин'})

@login_required
@manager_required
def shop_edit(request, shop_id):
    """Редактирование магазина"""
    shop = get_object_or_404(Shop, id=shop_id, owner=request.user)

    if request.method == 'POST':
        try:
            shop.name = request.POST.get('name', '').strip()
            shop.address = request.POST.get('address', '').strip()
            shop.phone = request.POST.get('phone', '').strip()
            shop.opening_hours = request.POST.get('opening_hours', '').strip()
            shop.save()

            messages.success(request, f'Магазин "{shop.name}" успешно обновлен!')
            return redirect('shop_manage')

        except Exception as e:
            messages.error(request, f'Ошибка при обновлении магазина: {str(e)}')

    # Передаем данные магазина в шаблон для предзаполнения
    context = {
        'title': 'Редактировать магазин',
        'shop': shop
    }
    return render(request, 'products/shop_form.html', context)

@login_required
@manager_required
def shop_delete(request, shop_id):
    """Удаление магазина"""
    shop = get_object_or_404(Shop, id=shop_id, owner=request.user)

    if request.method == 'POST':
        shop_name = shop.name
        shop.delete()
        messages.success(request, f'Магазин "{shop_name}" успешно удален!')
        return redirect('shop_manage')

    return render(request, 'products/shop_confirm_delete.html', {'shop': shop})


# Избранное
@login_required
def favorite_list(request):
    """Список избранных товаров"""
    favorites = Favorite.objects.filter(user=request.user).select_related('product')
    return render(request, 'products/favorite_list.html', {'favorites': favorites})


@login_required
def add_to_favorite(request, product_id):
    """Добавление товара в избранное"""
    product = get_object_or_404(Product, id=product_id, is_active=True)

    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        product=product
    )

    if created:
        messages.success(request, f'Товар "{product.name}" добавлен в избранное! ❤️')
    else:
        messages.info(request, f'Товар "{product.name}" уже в избранном!')

    return redirect('product_detail', product_id=product.id)


@login_required
def remove_from_favorite(request, product_id):
    """Удаление товара из избранного"""
    product = get_object_or_404(Product, id=product_id)

    favorite = get_object_or_404(Favorite, user=request.user, product=product)
    favorite.delete()

    messages.success(request, f'Товар "{product.name}" удален из избранного! 💔')

    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('favorite_list')


@login_required
def toggle_favorite(request, product_id):
    """Переключение состояния избранного (AJAX)"""
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        product = get_object_or_404(Product, id=product_id, is_active=True)

        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            product=product
        )

        if not created:
            favorite.delete()
            return JsonResponse({'status': 'removed', 'message': 'Удалено из избранного'})
        else:
            return JsonResponse({'status': 'added', 'message': 'Добавлено в избранное'})

    return JsonResponse({'error': 'Invalid request'}, status=400)


# Обработчики ошибок
def handler403(request, exception):
    return render(request, '403.html', status=403)


def handler404(request, exception):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)