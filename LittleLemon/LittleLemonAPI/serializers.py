from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, MenuItem, Cart, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']


class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'category_id']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class CartSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'menuitem', 'menuitem_id', 'quantity', 'unit_price', 'price']
        read_only_fields = ['unit_price', 'price']

    def validate_menuitem_id(self, value):
        try:
            MenuItem.objects.get(id=value)
        except MenuItem.DoesNotExist:
            raise serializers.ValidationError("Menu item not found.")
        return value

    def create(self, validated_data):
        menuitem = MenuItem.objects.get(id=validated_data['menuitem_id'])
        quantity = validated_data['quantity']
        validated_data['unit_price'] = menuitem.price
        validated_data['price'] = menuitem.price * quantity
        validated_data['menuitem'] = menuitem
        validated_data.pop('menuitem_id')
        return super().create(validated_data)


class OrderItemSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'menuitem', 'quantity', 'unit_price', 'price']


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    delivery_crew = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date', 'order_items']
