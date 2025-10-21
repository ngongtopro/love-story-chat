from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import FarmViewSet, CropTypeViewSet, FarmTransactionViewSet

router = DefaultRouter()
router.register('farms', FarmViewSet, basename='farms')
router.register('crops', CropTypeViewSet, basename='crop-types')
router.register('transactions', FarmTransactionViewSet, basename='farm-transactions')

urlpatterns = [
    path('api/farm/', include(router.urls)),
]
