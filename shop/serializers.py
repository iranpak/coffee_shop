from rest_framework import serializers

from shop.models import Product, Order


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class OrderListRetrieveSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField('get_products')
    customer = serializers.SerializerMethodField('get_customer')
    total_price = serializers.SerializerMethodField('get_total_price')

    @staticmethod
    def get_products(order):
        products = order.products.all()
        result = []
        for product in products:
            result.append({'id': product.id, 'name': product.name, 'price': product.price})
        return result

    @staticmethod
    def get_customer(order):
        return {'id': order.customer.id, 'username': order.customer.username}

    @staticmethod
    def get_total_price(order):
        products = order.products.all()
        total_price = 0
        for product in products:
            total_price += product.price
        return total_price

    class Meta:
        model = Order
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
