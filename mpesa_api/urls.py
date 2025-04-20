from django.urls import path
from . import views

app_name = 'mpesa_api'

urlpatterns = [
    path('initiate/<int:invoice_id>/<str:amount>/', views.initiate_stk_push, name='initiate_stk_push'),
    path('check-status/', views.check_payment_status, name='check_payment_status'),
    path('query-status/', views.query_payment_status, name='query_payment_status'),
    path('callback/', views.mpesa_callback, name='mpesa_callback'),
    path('initiate-direct/<str:amount>/', views.initiate_direct_payment, name='initiate_direct_payment'),
    path('check-direct-status/', views.check_direct_payment_status, name='check_direct_payment_status'),
]