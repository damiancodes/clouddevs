from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.overview, name='overview'),
    path('web-development/', views.web_development, name='web_development'),
    path('app-development/', views.app_development, name='app_development'),
    path('pos-systems/', views.pos_systems, name='pos_systems'),


]