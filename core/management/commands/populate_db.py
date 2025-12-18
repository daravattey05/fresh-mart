from django.core.management.base import BaseCommand
from django.utils.text import slugify
from core.models import Category, Product, Blog, Order, OrderItem
from django.contrib.auth.models import User
import random

class Command(BaseCommand):
    help = 'Populate database with dummy data'

    def handle(self, *args, **options):
        self.stdout.write('Populating database with realistic data...')

        # Clear existing data to avoid duplicates
        Product.objects.all().delete()
        Category.objects.all().delete()
        Blog.objects.all().delete()
        self.stdout.write(self.style.WARNING('Existing data cleared.'))

        # Ensure admin user exists for author assignment
        user, _ = User.objects.get_or_create(username='admin')

        # Define Categories and their Products
        data = {
            'Fresh Meat': [
                ('Beef Steak', 50.00), ('Chicken Wings', 15.00), ('Pork Chops', 25.00),
                ('Lamb Chops', 45.00), ('Ground Beef', 18.00)
            ],
            'Vegetables': [
                ('Broccoli', 5.00), ('Carrots', 3.00), ('Spinach', 4.00),
                ('Bell Peppers', 6.00), ('Tomatoes', 4.50), ('Potatoes', 2.00)
            ],
            'Fruits': [
                ('Organic Bananas', 12.00), ('Red Apples', 8.00), ('Fresh Oranges', 10.00),
                ('Grapes', 14.00), ('Mangoes', 15.00), ('Strawberries', 10.00)
            ],
            'Dried Fruit & Nuts': [
                ('Raisins', 25.00), ('Almonds', 35.00), ('Cashews', 40.00),
                ('Dried Apricots', 30.00)
            ],
            'Ocean Foods': [
                ('Salmon Fillet', 45.00), ('Tuna Steak', 55.00), ('Shrimp', 40.00),
                ('Lobster Tail', 85.00)
            ],
            'Fastfood': [
                ('Hamburger', 12.00), ('Cheeseburger', 14.00), ('Fried Chicken', 10.00)
            ]
        }

        # Create Categories and Products
        for cat_name, products in data.items():
            category, _ = Category.objects.get_or_create(
                slug=slugify(cat_name),
                defaults={'name': cat_name}
            )
            self.stdout.write(f'Category: {cat_name}')
            
            for prod_name, price in products:
                # Construct image path based on convention: "Beef Steak" -> "products/Beef_Steak.jpg"
                image_filename = f"products/{prod_name.replace(' ', '_')}.jpg"
                
                Product.objects.create(
                    name=prod_name,
                    slug=slugify(prod_name),
                    category=category,
                    price=price,
                    stock=random.randint(50, 200),
                    description=f'Fresh and high quality {prod_name} sourced directly from organic farms.',
                    is_featured=random.choice([True, False]),
                    image=image_filename
                )
                self.stdout.write(f' - Product: {prod_name} (Image: {image_filename})')

        # Blogs
        blogs_data = [
            'Cooking tips make cooking simple',
            '6 ways to prepare breakfast for 30',
            'Visit the clean farm in the US',
            'Best vegetables for your garden',
            'Healthy benefits of fresh meat'
        ]
        
        for title in blogs_data:
            Blog.objects.create(
                slug=slugify(title),
                title=title,
                author=user,
                content='Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.',
            )
            self.stdout.write(f'Created Blog: {title}')
        
        self.stdout.write(self.style.SUCCESS('Database populated successfully with realistic data!'))
