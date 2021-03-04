from django.contrib.auth.models import Permission, Group
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from users.models import User
from users.serializers import PermissionSerializer, GroupSerializer, UserSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filterset_fields = '__all__'
    ordering_fields = '__all__'


class PermissionListRetrieveViewSet(ReadOnlyModelViewSet):
    queryset = Permission.objects.order_by('id')
    serializer_class = PermissionSerializer


class GroupCRUDViewSet(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
