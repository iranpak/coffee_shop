from django.conf.urls import url
from django.urls import include
from rest_framework import routers

from shop.views import ProductViewSet, OrderViewSet

router = routers.DefaultRouter()
router.register(r'products', ProductViewSet, basename='products')
router.register(r'orders', OrderViewSet, basename='orders')

urlpatterns = router.urls
