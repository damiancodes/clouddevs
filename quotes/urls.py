# from django.urls import path
# from . import views
#
# app_name = 'quotes'
#
# urlpatterns = [
#     path('request/', views.quote_request, name='quote_request'),
#     path('estimator/', views.service_estimator, name='service_estimator'),
#     path('thank-you/', views.thank_you, name='thank_you'),
#     path('api/service-features/<int:service_id>/', views.get_service_features, name='get_service_features'),
# ]


# from django.urls import path
# from . import views
#
# app_name = 'quotes'
#
# urlpatterns = [
#     # Existing URLs
#     path('solution-builder/', views.solution_builder, name='solution_builder'),
#     path('request/', views.quote_request, name='quote_request'),
#     path('estimator/', views.service_estimator, name='service_estimator'),
#     path('thank-you/', views.thank_you, name='thank_you'),
#     path('api/service-features/<int:service_id>/', views.get_service_features, name='get_service_features'),
#
#     # New solution builder URLs
#     path('api/exchange-rate/', views.get_exchange_rate, name='get_exchange_rate'),
#     path('create-order/', views.create_order, name='create_order'),
#     path('payment-choice/<int:order_id>/', views.payment_choice, name='payment_choice'),
#     path('process-mpesa/<int:order_id>/', views.process_mpesa, name='process_mpesa'),
#     path('mpesa-stk-push/', views.mpesa_stk_push, name='mpesa_stk_push'),
#     path('mpesa-check-status/', views.mpesa_check_status, name='mpesa_check_status'),
#     path('process-paypal/<int:order_id>/', views.process_paypal, name='process_paypal'),
#     path('process-crypto/<int:order_id>/', views.process_crypto, name='process_crypto'),
#     path('skip-payment/<int:order_id>/', views.skip_payment, name='skip_payment'),
#     path('payment-callback/<int:order_id>/<str:payment_method>/', views.payment_callback, name='payment_callback'),
#     path('confirmation/<int:order_id>/', views.confirmation, name='confirmation'),
#
#
# ]


# quotes/urls.py
from django.urls import path
from . import views

app_name = 'quotes'

urlpatterns = [
    # Service estimator flow
    path('estimator/', views.service_estimator, name='service_estimator'),
    path('api/service-features/<int:service_id>/', views.get_service_features, name='get_service_features'),
    path('request/', views.quote_request, name='quote_request'),

    # Solution builder flow
    path('solution-builder/', views.solution_builder, name='solution_builder'),
    path('api/exchange-rate/', views.get_exchange_rate, name='get_exchange_rate'),
    path('create-order/', views.create_order, name='create_order'),

    # Payment flow
    path('payment-choice/<int:order_id>/', views.payment_choice, name='payment_choice'),
    path('process-mpesa/<int:order_id>/', views.process_mpesa, name='process_mpesa'),
    path('mpesa-stk-push/', views.mpesa_stk_push, name='mpesa_stk_push'),
    path('mpesa-check-status/', views.mpesa_check_status, name='mpesa_check_status'),
    path('process-paypal/<int:order_id>/', views.process_paypal, name='process_paypal'),
    path('process-crypto/<int:order_id>/', views.process_crypto, name='process_crypto'),
    path('skip-payment/<int:order_id>/', views.skip_payment, name='skip_payment'),

    # Confirmation and callback
    path('payment-callback/<int:order_id>/<str:payment_method>/', views.payment_callback, name='payment_callback'),
    path('confirmation/<int:order_id>/', views.confirmation, name='confirmation'),
    path('thank-you/', views.thank_you, name='thank_you'),
]