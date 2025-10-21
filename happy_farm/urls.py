"""
URL Configuration for Happy Farm App
"""
from django.urls import path
from . import views

app_name = 'happy_farm'

urlpatterns = [
    # Farm main page
    path('', views.farm_view, name='farm'),
    
    # Farm API endpoints
    path('api/plant/', views.plant_crop_api, name='plant_crop_api'),
    path('api/harvest/', views.harvest_crop_api, name='harvest_crop_api'),
    path('api/clear/', views.clear_plot_api, name='clear_plot_api'),
    path('api/status/', views.farm_status_api, name='farm_status_api'),
    path('api/status/', views.farm_status_api, name='status'),
    path('api/plant/', views.plant_crop_api, name='plant'),
    path('api/harvest/', views.harvest_crop_api, name='harvest'),
]
