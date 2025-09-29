from django import forms
from .models import Product, Category, ProductImage

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'image', 'price', 'shop_addresses', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'shop_addresses': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Введите адреса магазинов через точку с запятой (;)'
            }),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': 'Название товара',
            'description': 'Описание',
            'image': 'Изображение',
            'price': 'Цена (руб)',
            'shop_addresses': 'Адреса магазинов',
            'is_active': 'Активный товар',
            'category': 'Категория',
        }

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'order']
