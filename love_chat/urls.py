"""
URL configuration for love_chat project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger/OpenAPI schema
schema_view = get_schema_view(
    openapi.Info(
        title="Love Chat API",
        default_version='v1',
        description="REST API for Love Chat application with chat, games, farm, and wallet features",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="admin@lovechat.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Authentication
    path('accounts/', include('django.contrib.auth.urls')),
    
    # API Documentation
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API Endpoints
    path('', include('auth_urls')),
    path('', include('chat.api_urls')),
    path('', include('caro_game.api_urls')),
    path('', include('user_wallet.api_urls')),
    path('', include('happy_farm.api_urls')),
    
    # Legacy template-based URLs (optional, can be removed for pure API)
    path('legacy/', include('chat.urls')),
    path('legacy/caro/', include('caro_game.urls')),
    path('legacy/farm/', include('happy_farm.urls')),
    path('legacy/wallet/', include('user_wallet.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)