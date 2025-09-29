from django.core.management.base import BaseCommand
from products.models import Product, Category


class Command(BaseCommand):
    help = 'Assign categories to existing products based on keywords'

    def handle(self, *args, **options):
        # Словарь для автоматического назначения категорий
        category_keywords = {
            'Электроника': ['iphone', 'samsung', 'ноутбук', 'macbook', 'наушники', 'смартфон', 'планшет', 'galaxy'],
            'Одежда и обувь': ['рубашка', 'брюки', 'платье', 'куртка', 'обувь', 'футболка'],
            'Продукты питания': ['молоко', 'сыр', 'йогурт', 'мясо', 'курица', 'напиток'],
            'Товары для дома': ['диван', 'кровать', 'стол', 'стул', 'шторы', 'посуда'],
            'Товары для автомобиля': ['аккумулятор', 'шины', 'масло', 'чехол', 'ароматизатор'],
        }

        products = Product.objects.filter(category__isnull=True)
        assigned_count = 0

        for product in products:
            product_name_lower = product.name.lower()

            # Ищем подходящую категорию по ключевым словам
            for category_name, keywords in category_keywords.items():
                if any(keyword in product_name_lower for keyword in keywords):
                    try:
                        category = Category.objects.get(name=category_name)
                        product.category = category
                        product.save()
                        assigned_count += 1
                        self.stdout.write(f'✅ Товару "{product.name}" назначена категория "{category_name}"')
                        break
                    except Category.DoesNotExist:
                        continue

        # Назначаем оставшимся товарам категорию "Прочие товары"
        other_category, created = Category.objects.get_or_create(name="Прочие товары")
        remaining_products = Product.objects.filter(category__isnull=True)

        if remaining_products.exists():
            remaining_products.update(category=other_category)
            self.stdout.write(f'✅ {remaining_products.count()} товаров назначена категория "Прочие товары"')

        self.stdout.write(
            self.style.SUCCESS(f'✅ Всего назначено категорий: {assigned_count + remaining_products.count()} товарам'))