from django.urls import path
from . import views
from django.conf.urls import handler403, handler404, handler500

handler403 = 'products.views.handler403'
handler404 = 'products.views.handler404'
handler500 = 'products.views.handler500'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),

    # Управление товарами (для менеджеров)
    path('manage/', views.product_manage, name='product_manage'),
    path('manage/add/', views.product_add, name='product_add'),
    path('manage/edit/<int:product_id>/', views.product_edit, name='product_edit'),
    path('manage/delete/<int:product_id>/', views.product_delete, name='product_delete'),

    # Корзина ← ДОБАВЛЯЕМ ЭТИ СТРОКИ
    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
]


