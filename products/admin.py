from django.contrib import admin
from django.contrib.auth import get_user_model
from .models import Product, Category, Cart, CartItem, ProductImage, Shop, Favorite

User = get_user_model()


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'created_at')
    list_filter = ('parent',)
    search_fields = ('name',)
    ordering = ('name',)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'order', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'created_by', 'created_at', 'is_active')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    inlines = [ProductImageInline]

    fieldsets = (
        (None, {
            'fields': ('name', 'category', 'description', 'image', 'price', 'shops')
        }),
        ('Дополнительно', {
            'fields': ('created_by', 'is_active'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image_preview', 'order', 'created_at')
    list_filter = ('created_at',)
    ordering = ('product', 'order')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="height: 50px;" />'
        return "Нет изображения"

    image_preview.allow_tags = True
    image_preview.short_description = 'Превью'


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'phone', 'owner', 'created_at')
    search_fields = ('name', 'address')
    list_filter = ('created_at', 'owner')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'product__name')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'total_items', 'total_price')

    def total_items(self, obj):
        return obj.total_items()

    total_items.short_description = 'Количество товаров'

    def total_price(self, obj):
        return f"{obj.total_price()} ₽"

    total_price.short_description = 'Общая стоимость'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'added_at', 'total_price')
    list_filter = ('added_at',)

    def total_price(self, obj):
        return f"{obj.total_price()} ₽"

    total_price.short_description = 'Стоимость'