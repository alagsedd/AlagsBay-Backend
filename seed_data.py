# seed_data.py
# pylint: disable=no-member

import django
import os

# Replace with your actual project settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alagsbay.settings")
django.setup()

from store.models import Collection, Product

# Optional: Reset data
Product.objects.all().delete()
Collection.objects.all().delete()

# Step 1: Create Collections
collection_titles = [
    "Electronics",
    "Clothing",
    "Home & Living",
    "Beauty",
    "Sports",
    "Books"
]

collections = {}
for title in collection_titles:
    collections[title] = Collection.objects.create(title=title)

# Step 2: Create Products (under Electronics)
electronics_products = [
    {
        "title": "Samsung Galaxy S24 Ultra",
        "description": "Flagship phone with 200MP camera and Snapdragon 8 Gen 3.",
        "unit_price": 1199.99,
        "inventory": 25
    },
    {
        "title": "Apple MacBook Pro M3",
        "description": "14-inch Liquid Retina XDR display with M3 chip.",
        "unit_price": 1799.99,
        "inventory": 15
    },
    {
        "title": "Nike Jordan Hoodie",
        "description": "Comfortable fleece hoodie with iconic Jordan logo.",
        "unit_price": 89.99,
        "inventory": 40
    },
    {
        "title": "Apple AirPods Pro 2",
        "description": "Noise cancelling earbuds with spatial audio.",
        "unit_price": 249.99,
        "inventory": 30
    },
    {
        "title": "JBL Flip 6 Bluetooth Speaker",
        "description": "Portable waterproof speaker with punchy bass.",
        "unit_price": 129.99,
        "inventory": 50
    },
    {
        "title": "Dyson V15 Vacuum Cleaner",
        "description": "Cordless vacuum with intelligent cleaning modes.",
        "unit_price": 699.99,
        "inventory": 10
    },
    {
        "title": "Xbox Series X Console",
        "description": "Next-gen gaming console with 1TB SSD.",
        "unit_price": 499.99,
        "inventory": 12
    },
    {
        "title": "Beanless Lounge Chair",
        "description": "Inflatable beanless lounge chair for relaxing.",
        "unit_price": 39.99,
        "inventory": 60
    },
    {
        "title": "Sony WH-1000XM5 Headphones",
        "description": "Industry-leading noise cancelling headphones.",
        "unit_price": 349.99,
        "inventory": 20
    },
    {
        "title": "Canon EOS R50 Camera",
        "description": "Compact mirrorless camera with 4K video.",
        "unit_price": 999.99,
        "inventory": 8
    }
]

for product in electronics_products:
    Product.objects.create(
        title=product["title"],
        description=product["description"],
        unit_price=product["unit_price"],
        inventory=product["inventory"],
        collection=collections["Electronics"]
    )

print("✅ Seeded collections and products successfully.")
