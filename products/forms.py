from django import forms
from .models import Product, Category, ProductImage, Shop

class ShopForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = ['name', 'address', 'phone', 'opening_hours', 'latitude', 'longitude']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'opening_hours': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
        }

class ProductForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ProductForm, self).__init__(*args, **kwargs)

        # Фильтруем магазины
        if user and not user.is_superuser:
            self.fields['shops'].queryset = Shop.objects.filter(owner=user)
        else:
            self.fields['shops'].queryset = Shop.objects.all()

        # Иерархия категорий
        def get_category_choices():
            choices = [('', '---------')]

            def add_categories(categories, level=0):
                for category in categories:
                    indent = "--- " * level
                    choices.append((category.id, f"{indent}{category.name}"))
                    children = Category.objects.filter(parent=category)
                    add_categories(children, level + 1)

            root_categories = Category.objects.filter(parent__isnull=True)
            add_categories(root_categories)
            return choices

        self.fields['category'].choices = get_category_choices()

    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'image', 'price', 'shops', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'shops': forms.SelectMultiple(attrs={'class': 'form-control', 'style': 'height: 120px;'}),
        }

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'order']