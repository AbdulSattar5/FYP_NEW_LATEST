"""
Django Management Command: Convert All Available CSV Files to Website Format
Usage: python manage.py convert_all_csv_to_website
"""

from django.core.management.base import BaseCommand
from store.models import Category, Product
import csv
import os
from decimal import Decimal
from django.utils.text import slugify
import random


class Command(BaseCommand):
    help = 'Convert all available Amazon CSV files to website database format'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv-file',
            type=str,
            default='auto',
            help='Specify CSV file: cleaned, products, uk, categories, or auto (default: auto detects all)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of products to import (default: all)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing products before import'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        limit = options['limit']
        clear_existing = options['clear']

        if clear_existing:
            self.stdout.write(self.style.WARNING('Clearing existing products...'))
            Product.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Products cleared'))

        # Auto-detect and process all available CSV files
        if csv_file == 'auto':
            self.stdout.write(self.style.SUCCESS('🔍 Auto-detecting CSV files...'))
            self.process_all_csv_files(limit)
        else:
            self.process_specific_csv(csv_file, limit)

        self.stdout.write(self.style.SUCCESS(f'\n✅ Import completed!'))
        self.stdout.write(f'Total Categories: {Category.objects.count()}')
        self.stdout.write(f'Total Products: {Product.objects.count()}')

    def process_all_csv_files(self, limit):
        """Process all available CSV files"""
        csv_files = {
            'amazon_products_sales_data_cleaned.csv': self.import_cleaned_csv,
            'amazon_products.csv': self.import_products_csv,
            'amz_uk_processed_data.csv': self.import_uk_csv,
            'amazon_categories.csv': self.import_categories_csv,
        }

        for filename, import_func in csv_files.items():
            if os.path.exists(filename):
                self.stdout.write(self.style.SUCCESS(f'\n📁 Found: {filename}'))
                import_func(filename, limit)
            else:
                self.stdout.write(self.style.WARNING(f'⚠ Not found: {filename}'))

    def process_specific_csv(self, csv_type, limit):
        """Process a specific CSV file"""
        csv_map = {
            'cleaned': ('amazon_products_sales_data_cleaned.csv', self.import_cleaned_csv),
            'products': ('amazon_products.csv', self.import_products_csv),
            'uk': ('amz_uk_processed_data.csv', self.import_uk_csv),
            'categories': ('amazon_categories.csv', self.import_categories_csv),
        }

        if csv_type in csv_map:
            filename, import_func = csv_map[csv_type]
            if os.path.exists(filename):
                self.stdout.write(self.style.SUCCESS(f'📁 Processing: {filename}'))
                import_func(filename, limit)
            else:
                self.stdout.write(self.style.ERROR(f'❌ File not found: {filename}'))
        else:
            self.stdout.write(self.style.ERROR(f'❌ Invalid CSV type: {csv_type}'))

    def import_cleaned_csv(self, filename, limit):
        """Import from amazon_products_sales_data_cleaned.csv"""
        self.stdout.write('Importing from cleaned sales data...')
        
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            count = 0
            
            for row in reader:
                if limit and count >= limit:
                    break
                
                try:
                    # Extract category
                    category_name = row.get('product_category', 'Electronics').strip()
                    category = self.get_or_create_category(category_name)
                    
                    # Extract pricing
                    discounted_price = self.parse_price(row.get('discounted_price', '0'))
                    original_price = self.parse_price(row.get('original_price', '0'))
                    discount_pct = self.parse_decimal(row.get('discount_percentage', '0'))
                    
                    # Calculate prices
                    if discounted_price > 0:
                        price = discounted_price
                    else:
                        price = original_price
                    
                    if original_price == 0:
                        original_price = price
                    
                    # Extract other fields
                    product_name = row.get('product_title', 'Unknown Product')[:200]
                    rating = self.parse_decimal(row.get('product_rating', '0'))
                    reviews = self.parse_int(row.get('total_reviews', '0'))
                    purchased = self.parse_int(row.get('purchased_last_month', '0'))
                    is_best_seller = row.get('is_best_seller', '').lower() == 'best seller'
                    
                    # Create product
                    product = Product.objects.create(
                        name=product_name,
                        category=category,
                        description=f"{product_name}\n\nRating: {rating}/5 ({reviews} reviews)\nPurchased last month: {purchased}",
                        price=price,
                        original_price=original_price if original_price > price else None,
                        is_on_discount=discount_pct > 0,
                        discount_percentage=discount_pct,
                        stock_level=random.randint(10, 200),
                        is_available=True,
                        is_featured=is_best_seller,
                        rating=rating,
                        image=self.download_or_assign_image(row.get('product_image_url', ''), count),
                        attributes={
                            'reviews': reviews,
                            'purchased_last_month': purchased,
                            'is_sponsored': row.get('is_sponsored', ''),
                            'has_coupon': row.get('has_coupon', ''),
                        }
                    )
                    
                    count += 1
                    if count % 10 == 0:
                        self.stdout.write(f'  Imported {count} products...')
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  Error: {str(e)}'))
                    continue
        
        self.stdout.write(self.style.SUCCESS(f'✓ Imported {count} products from cleaned CSV'))

    def import_products_csv(self, filename, limit):
        """Import from amazon_products.csv"""
        self.stdout.write('Importing from amazon_products.csv...')
        
        # This file might have different structure, adjust as needed
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            count = 0
            
            for row in reader:
                if limit and count >= limit:
                    break
                
                try:
                    # Adjust field names based on actual CSV structure
                    product_name = row.get('product_name', row.get('title', 'Unknown'))[:200]
                    category_name = row.get('category', 'General').strip()
                    category = self.get_or_create_category(category_name)
                    
                    price = self.parse_price(row.get('price', '0'))
                    
                    Product.objects.create(
                        name=product_name,
                        category=category,
                        description=row.get('description', product_name),
                        price=price,
                        stock_level=random.randint(10, 200),
                        is_available=True,
                        rating=self.parse_decimal(row.get('rating', '4.0')),
                    )
                    
                    count += 1
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  Error: {str(e)}'))
                    continue
        
        self.stdout.write(self.style.SUCCESS(f'✓ Imported {count} products from products CSV'))

    def import_uk_csv(self, filename, limit):
        """Import from amz_uk_processed_data.csv"""
        self.stdout.write('Importing from UK processed data...')
        
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            count = 0
            
            for row in reader:
                if limit and count >= limit:
                    break
                
                try:
                    category_name = row.get('categoryName', 'Electronics').strip()
                    category = self.get_or_create_category(category_name)
                    
                    product_name = row.get('title', 'Unknown Product')[:200]
                    price = self.parse_price(row.get('price', '0'))
                    rating = self.parse_decimal(row.get('stars', '0'))
                    reviews = self.parse_int(row.get('reviews', '0'))
                    is_best_seller = row.get('isBestSeller', 'False').lower() == 'true'
                    bought_last_month = self.parse_int(row.get('boughtInLastMonth', '0'))
                    
                    Product.objects.create(
                        name=product_name,
                        category=category,
                        description=f"{product_name}\n\nRating: {rating}/5 ({reviews} reviews)\nBought last month: {bought_last_month}",
                        price=price,
                        stock_level=random.randint(10, 200),
                        is_available=True,
                        is_featured=is_best_seller,
                        rating=rating,
                        image=self.download_or_assign_image(row.get('imgUrl', ''), count),
                        attributes={
                            'asin': row.get('asin', ''),
                            'reviews': reviews,
                            'bought_last_month': bought_last_month,
                        }
                    )
                    
                    count += 1
                    if count % 10 == 0:
                        self.stdout.write(f'  Imported {count} products...')
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  Error: {str(e)}'))
                    continue
        
        self.stdout.write(self.style.SUCCESS(f'✓ Imported {count} products from UK CSV'))

    def import_categories_csv(self, filename, limit):
        """Import from amazon_categories.csv"""
        self.stdout.write('Importing categories...')
        
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            count = 0
            
            for row in reader:
                try:
                    category_name = row.get('category_name', '').strip()
                    if category_name:
                        self.get_or_create_category(category_name)
                        count += 1
                
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  Error: {str(e)}'))
                    continue
        
        self.stdout.write(self.style.SUCCESS(f'✓ Imported {count} categories'))

    def get_or_create_category(self, category_name):
        """Get or create category with proper formatting"""
        if not category_name:
            category_name = 'General'
        
        # Map common categories to icons and colors
        category_config = {
            'Electronics': {'icon': 'fa-laptop', 'color': '#6C63FF'},
            'Phones': {'icon': 'fa-mobile-alt', 'color': '#3F8EFC'},
            'Laptops': {'icon': 'fa-laptop', 'color': '#6C63FF'},
            'Clothing': {'icon': 'fa-tshirt', 'color': '#FF6584'},
            'Books': {'icon': 'fa-book', 'color': '#43AA8B'},
            'Food': {'icon': 'fa-utensils', 'color': '#F8961E'},
            'Home & Kitchen': {'icon': 'fa-home', 'color': '#9B59B6'},
            'Sports': {'icon': 'fa-football-ball', 'color': '#E74C3C'},
            'Toys': {'icon': 'fa-gamepad', 'color': '#F39C12'},
            'Beauty': {'icon': 'fa-spa', 'color': '#E91E63'},
            'Hi-Fi Speakers': {'icon': 'fa-volume-up', 'color': '#00BCD4'},
            'Other Electronics': {'icon': 'fa-plug', 'color': '#607D8B'},
        }
        
        config = category_config.get(category_name, {'icon': 'fa-tag', 'color': '#95A5A6'})
        
        category, created = Category.objects.get_or_create(
            name=category_name,
            defaults={
                'description': f'Browse our collection of {category_name}',
                'icon': config['icon'],
                'color': config['color'],
            }
        )
        
        return category

    def download_or_assign_image(self, image_url, index):
        """Assign existing product images or return None"""
        # Use existing images from media/products/
        image_files = [f'products/product_{i}.jpg' for i in range(201, 320)]
        
        if image_files:
            # Cycle through available images
            return image_files[index % len(image_files)]
        
        return None

    def parse_price(self, value):
        """Parse price from string"""
        try:
            # Remove currency symbols and commas
            cleaned = str(value).replace('$', '').replace('£', '').replace(',', '').strip()
            return Decimal(cleaned) if cleaned else Decimal('0')
        except:
            return Decimal('0')

    def parse_decimal(self, value):
        """Parse decimal from string"""
        try:
            return Decimal(str(value).strip())
        except:
            return Decimal('0')

    def parse_int(self, value):
        """Parse integer from string"""
        try:
            # Remove commas and convert
            cleaned = str(value).replace(',', '').strip()
            return int(float(cleaned)) if cleaned else 0
        except:
            return 0
