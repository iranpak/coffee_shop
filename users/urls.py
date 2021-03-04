from django.conf.urls import url
from django.urls import include
from rest_framework import routers

from users.views import UserViewSet, PermissionListRetrieveViewSet, GroupCRUDViewSet

router = routers.DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('permissions', PermissionListRetrieveViewSet, basename='permissions')
router.register('groups', GroupCRUDViewSet, basename='groups')

urlpatterns = router.urls
