from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),

    # Управление товарами
    path('manage/', views.product_manage, name='product_manage'),
    path('add/', views.product_add, name='product_add'),
    path('edit/<int:product_id>/', views.product_edit, name='product_edit'),
    path('delete/<int:product_id>/', views.product_delete, name='product_delete'),

    # Корзина
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Магазины
    path('shops/', views.shop_list, name='shop_list'),
    path('nearest-shops/', views.nearest_shops, name='nearest_shops'),

    # Управление магазинами для менеджеров
    path('shops/manage/', views.shop_manage, name='shop_manage'),
    path('shops/add/', views.shop_add, name='shop_add'),
    path('shops/edit/<int:shop_id>/', views.shop_edit, name='shop_edit'),
    path('shops/delete/<int:shop_id>/', views.shop_delete, name='shop_delete'),

    # Избранное
    path('favorites/', views.favorite_list, name='favorite_list'),
    path('favorites/add/<int:product_id>/', views.add_to_favorite, name='add_to_favorite'),
    path('favorites/remove/<int:product_id>/', views.remove_from_favorite, name='remove_from_favorite'),
    path('favorites/toggle/<int:product_id>/', views.toggle_favorite, name='toggle_favorite'),
]