from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import CaroGameViewSet

router = DefaultRouter()
router.register('games', CaroGameViewSet, basename='caro-games')

urlpatterns = [
    path('api/caro/', include(router.urls)),
]
