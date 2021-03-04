from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from coffee_shop import settings

from shop.models import Product, Order, OrderStatus
from shop.serializers import ProductSerializer, OrderSerializer, OrderListRetrieveSerializer


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_fields = ['price']
    ordering_fields = ['name', 'price']


def send_email(subject, message, receiver):
    send_mail(subject, message, settings.EMAIL_HOST_USER, [receiver], fail_silently=False)


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filterset_fields = ['customer', 'status']
    ordering_fields = ['status']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OrderListRetrieveSerializer
        return OrderSerializer

    @action(methods=['patch'], detail=True, permission_classes=[IsAuthenticated])
    def change(self, request, pk=None, *args, **kwargs):
        order = get_object_or_404(Order, id=pk, customer=request.user.id)
        if order.status != OrderStatus.WAITING:
            return Response(data='Your order is not waiting and can not be changed!')
        serializer = self.get_serializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, permission_classes=[IsAuthenticated])
    def cancel(self, request, pk=None):
        order = get_object_or_404(Order, id=pk, customer=request.user.id)
        if order.status != OrderStatus.WAITING:
            return Response(data='Your order is not waiting and can not be cancelled!')
        order.status = OrderStatus.CANCELLED
        order.save()
        return Response(status=status.HTTP_200_OK, data=OrderListRetrieveSerializer(order).data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        old_status = instance.status
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        new_status = instance.status

        if old_status != new_status:
            send_email('Order Update!', 'your order status has changed to {0}'.format(new_status), instance.customer.email)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)
