from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'price', 'image')
        }),
        ('Дополнительно', {
            'fields': ('shop_addresses', 'created_by', 'is_active'),
            'classes': ('collapse',)
        }),
    )