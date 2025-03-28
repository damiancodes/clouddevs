# chatbot/urls.py
from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chat_interface, name='chat_interface'),
    path('api/send-message/', views.send_message, name='send_message'),
]