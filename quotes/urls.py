from django.urls import path
from . import views

app_name = 'quotes'

urlpatterns = [
    path('request/', views.quote_request, name='quote_request'),
    path('estimator/', views.service_estimator, name='service_estimator'),
    path('thank-you/', views.thank_you, name='thank_you'),
    path('api/service-features/<int:service_id>/', views.get_service_features, name='get_service_features'),
]