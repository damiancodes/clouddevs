from django.urls import path
from . import views
from .admin_views import admin_dashboard

app_name = 'client_portal'

urlpatterns = [
    # Authentication
    path('login/', views.client_login, name='login'),
    path('register/', views.client_register, name='register'),
    path('logout/', views.client_logout, name='logout'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),

    # Projects
    path('projects/', views.ProjectListView.as_view(), name='projects'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),

    # Invoices
    path('invoices/', views.InvoiceListView.as_view(), name='invoices'),
    path('invoices/<int:pk>/', views.InvoiceDetailView.as_view(), name='invoice_detail'),
    path('invoices/<int:invoice_id>/payment/', views.make_payment, name='make_payment'),
    path('invoices/balance-due/', views.balance_due, name='balance_due'),

    # Payments
    path('payment/paypal/<int:invoice_id>/<str:amount>/', views.process_paypal, name='process_paypal'),
    path('payment/credit-card/<int:invoice_id>/<str:amount>/', views.process_credit_card, name='process_credit_card'),
    path('payment/mpesa/<int:invoice_id>/<str:amount>/', views.process_mpesa, name='process_mpesa'),
    path('payment/success/<int:invoice_id>/<str:payment_method>/<str:transaction_id>/', views.payment_success,
         name='payment_success'),
    path('payment/receipt/<int:payment_id>/', views.print_receipt, name='print_receipt'),

    # Messages
    path('messages/', views.MessageListView.as_view(), name='messages'),
    path('messages/send/', views.send_message, name='send_message'),
    path('messages/read/<int:message_id>/', views.mark_message_read, name='mark_message_read'),
]