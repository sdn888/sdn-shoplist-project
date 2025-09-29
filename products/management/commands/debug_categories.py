from django.core.management.base import BaseCommand
from products.models import Product, Category


class Command(BaseCommand):
    help = 'Debug categories assignment'

    def handle(self, *args, **options):
        # Проверяем все товары
        products = Product.objects.all()

        self.stdout.write("=== ТЕКУЩЕЕ СОСТОЯНИЕ ТОВАРОВ ===")
        for product in products:
            category_info = f"{product.category.id}:{product.category.name}" if product.category else "НЕТ"
            self.stdout.write(f"📦 {product.name} → Категория: {category_info}")

        self.stdout.write("\n=== СТАТИСТИКА ===")
        self.stdout.write(f"Всего товаров: {products.count()}")
        self.stdout.write(f"Товаров с категориями: {products.filter(category__isnull=False).count()}")
        self.stdout.write(f"Товаров без категорий: {products.filter(category__isnull=True).count()}")

        self.stdout.write("\n=== ВСЕ КАТЕГОРИИ ===")
        for category in Category.objects.all():
            self.stdout.write(f"{category.id}: {category.name}")