from rest_framework import serializers
from .models import Product, ProductImage,Collection,Order, OrderItem, Cart,CartItem, Customer
from django.db import transaction
# pylint: disable=no-member

        
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']
        
    def create(self, validated_data):
        product_id = self.context['product_id']
        return ProductImage.objects.create(product_id=product_id, **validated_data)
    
class CollectionSerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField()
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']
        
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title',  'description','unit_price', 'inventory', 'collection', 'images']
        
    
    collection = serializers.StringRelatedField()    
    images = ProductImageSerializer(many=True, read_only=True)
    
class SimpleProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True) 
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price', 'images']
    
        
class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']
    
    quantity = serializers.IntegerField(read_only=True)
    product = SimpleProductSerializer(read_only=True)
    total_price = serializers.SerializerMethodField(method_name='get_total_price')
    
    def get_total_price(self, cartItem:CartItem):
        return cartItem.quantity * cartItem.product.unit_price
        

class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'items','total_price']
    
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(method_name='get_total_price')
    
    def get_total_price(self, cart:Cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])
    
class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']
        
    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError("No product with the given ID was found.")
        return value
        
    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']

        try:
            # Update existing item
            cart_item = CartItem.objects.get(
                cart_id=cart_id,
                product_id=product_id
            )
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            # Create new item
            self.instance = CartItem.objects.create(
                cart_id=cart_id,
                product_id=product_id,
                quantity=quantity
            )
            
        return self.instance
    
    
class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']
        

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'birth_date']

    user_id = serializers.IntegerField(read_only=True)
    
    
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'unit_price', 'quantity']
        
    product = SimpleProductSerializer(read_only=True)
    
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'customer', 'placed_at', 'payment_status', 'items']
        
    items = OrderItemSerializer(many=True, read_only=True)
    
# 🧩 Class Purpose
# This class handles creating an order from a cart in a Django REST API. It:

# Takes a cart_id as input.

# Finds the customer based on the user making the request.

# Creates a new order.

# Transfers all items from the cart into the order.

# Deletes the cart afterward.


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
    
    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            user_id = self.context['user_id']
            
            (customer, created) = Customer.objects.get_or_create(user_id=user_id)
            order = Order.objects.create(customer=customer)
            
            cart_items = CartItem.objects.select_related('product').filter(cart_id=cart_id)
            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    unit_price=item.product.unit_price,
                    quantity=item.quantity
                ) for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)
            Cart.objects.filter(pk=cart_id).delete()
            
            return order