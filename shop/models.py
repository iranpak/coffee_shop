from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords

from users.models import User


class BaseModel(models.Model):
    create_date = models.DateTimeField(default=timezone.now)
    history = HistoricalRecords(inherit=True)

    class Meta:
        abstract = True


class Product(BaseModel):
    name = models.CharField(max_length=128, unique=True, null=False)
    price = models.IntegerField(null=False)
    options = models.JSONField(null=True)


class OrderStatus(models.TextChoices):
    WAITING = 'waiting'
    PREPARATION = 'preparation'
    READY = 'ready'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'


class Order(BaseModel):
    products = models.ManyToManyField(Product, related_name='orders')
    customer = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='orders', null=False)
    status = models.CharField(max_length=16, choices=OrderStatus.choices, default=OrderStatus.WAITING, null=False)
    options = models.JSONField(null=True)
