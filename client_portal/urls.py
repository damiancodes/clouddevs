# from django.urls import path
# from . import views
# from .admin_views import admin_dashboard
#
# app_name = 'client_portal'
#
# urlpatterns = [
#     # Authentication
#     path('login/', views.client_login, name='login'),
#     path('register/', views.client_register, name='register'),
#     path('logout/', views.client_logout, name='logout'),
#
#     # Dashboard
#     path('', views.dashboard, name='dashboard'),
#     path('profile/', views.profile, name='profile'),
#
#     # Projects
#     path('projects/', views.ProjectListView.as_view(), name='projects'),
#     path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
#
#     # Invoices
#     path('invoices/', views.InvoiceListView.as_view(), name='invoices'),
#     path('invoices/<int:pk>/', views.InvoiceDetailView.as_view(), name='invoice_detail'),
#     path('invoices/<int:invoice_id>/payment/', views.make_payment, name='make_payment'),
#     path('invoices/balance-due/', views.balance_due, name='balance_due'),
#
#     # Payments
#     path('payment/paypal/<int:invoice_id>/<str:amount>/', views.process_paypal, name='process_paypal'),
#     path('payment/credit-card/<int:invoice_id>/<str:amount>/', views.process_credit_card, name='process_credit_card'),
#     path('payment/mpesa/<int:invoice_id>/<str:amount>/', views.process_mpesa, name='process_mpesa'),
#     path('payment/success/<int:invoice_id>/<str:payment_method>/<str:transaction_id>/', views.payment_success,
#          name='payment_success'),
#     path('payment/receipt/<int:payment_id>/', views.print_receipt, name='print_receipt'),
#
#     # Messages
#     path('messages/', views.MessageListView.as_view(), name='messages'),
#     path('messages/send/', views.send_message, name='send_message'),
#     path('messages/read/<int:message_id>/', views.mark_message_read, name='mark_message_read'),
# ]


# from django.urls import path
# from . import views
# from .views import (
#     ProjectListView,
#     ProjectDetailView,
#     InvoiceListView,
#     InvoiceDetailView,
#     MessageListView
# )
#
# app_name = 'client_portal'
#
# urlpatterns = [
#     # Authentication URLs
#     path('login/', views.client_login, name='login'),
#     path('register/', views.client_register, name='register'),
#     path('logout/', views.client_logout, name='logout'),
#
#     # Dashboard
#     path('', views.dashboard, name='dashboard'),
#     path('profile/', views.profile, name='profile'),
#
#     # Projects
#     path('projects/', ProjectListView.as_view(), name='projects'),
#     path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project_detail'),
#
#     # Invoices
#     path('invoices/', InvoiceListView.as_view(), name='invoices'),
#     path('invoices/<int:pk>/', InvoiceDetailView.as_view(), name='invoice_detail'),
#     path('invoices/<int:invoice_id>/payment/', views.make_payment, name='make_payment'),
#     path('invoices/balance-due/', views.balance_due, name='balance_due'),
#
#     # Payments
#     path('payment/paypal/<int:invoice_id>/<str:amount>/', views.process_paypal, name='process_paypal'),
#     path('payment/credit-card/<int:invoice_id>/<str:amount>/', views.process_credit_card, name='process_credit_card'),
#     path('payment/mpesa/<int:invoice_id>/<str:amount>/', views.process_mpesa, name='process_mpesa'),
#     path('payment/success/<int:invoice_id>/<str:payment_method>/<str:transaction_id>/',
#          views.payment_success, name='payment_success'),
#     path('payment/receipt/<int:payment_id>/', views.print_receipt, name='print_receipt'),
#
#     # Messages
#     path('messages/', MessageListView.as_view(), name='messages'),
#     path('messages/send/', views.send_message, name='send_message'),
#     path('messages/read/<int:message_id>/', views.mark_message_read, name='mark_message_read'),
#
#     # Admin-related URLs
#     path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
#     path('admin/clients/', views.admin_clients, name='admin_clients'),
#     path('admin/clients/<int:client_id>/', views.admin_client_detail, name='admin_client_detail'),
#     path('admin/create-project/', views.admin_create_project, name='admin_create_project'),
#     path('admin/create-invoice/', views.admin_create_invoice, name='admin_create_invoice'),
#     path('admin/record-payment/', views.admin_record_payment, name='admin_record_payment'),
#
#    path('admin/financial-summary/', views.admin_financial_summary, name='admin_financial_summary'),
#
#     path('admin/add-client/', views.admin_add_client, name='admin_add_client'),
#     path('admin/clients/', views.admin_clients, name='admin_clients'),
#     path('admin/clients/<int:client_id>/', views.admin_client_detail, name='admin_client_detail'),
#     path('admin/create-invoice/', views.admin_create_invoice, name='admin_create_invoice'),
#     path('admin/record-payment/', views.admin_record_payment, name='admin_record_payment'),
#     path('admin/services/', views.admin_services, name='admin_services'),
#     path('admin/financial-summary/', views.admin_financial_summary, name='admin_financial_summary'),
#
#     # Email receipt URL
#     path('payment/receipt/<int:payment_id>/email/', views.email_receipt, name='email_receipt'),
#
#     # Add the following to your existing URLs if not already present
#     path('payment/receipt/<int:payment_id>/', views.print_receipt, name='print_receipt'),
# ]

from django.urls import path
from . import views
from .views import (
    ProjectListView,
    ProjectDetailView,
    InvoiceListView,
    InvoiceDetailView,
    MessageListView
)

app_name = 'client_portal'
#
# urlpatterns = [
#     path('admin/services/', views.admin_services, name='admin_services'),
#     path('admin/services/add/', views.admin_add_service, name='admin_add_service'),
#     path('admin/services/edit/<int:service_id>/', views.admin_edit_service, name='admin_edit_service'),
#     path('admin/services/delete/<int:service_id>/', views.admin_delete_service, name='admin_delete_service'),
#     # Authentication URLs
#     path('login/', views.client_login, name='login'),
#     path('register/', views.client_register, name='register'),
#     path('logout/', views.client_logout, name='logout'),
#
#     # Dashboard
#     path('', views.dashboard, name='dashboard'),
#     path('profile/', views.profile, name='profile'),
#
#     # Projects
#     path('projects/', ProjectListView.as_view(), name='projects'),
#     path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project_detail'),
#
#     # Invoices
#     path('invoices/', InvoiceListView.as_view(), name='invoices'),
#     path('invoices/<int:pk>/', InvoiceDetailView.as_view(), name='invoice_detail'),
#     path('invoices/<int:invoice_id>/payment/', views.make_payment, name='make_payment'),
#     path('invoices/balance-due/', views.balance_due, name='balance_due'),
#
#     # Payments
#     path('payment/paypal/<int:invoice_id>/<str:amount>/', views.process_paypal, name='process_paypal'),
#     path('payment/credit-card/<int:invoice_id>/<str:amount>/', views.process_credit_card, name='process_credit_card'),
#     path('payment/mpesa/<int:invoice_id>/<str:amount>/', views.process_mpesa, name='process_mpesa'),
#     path('payment/success/<int:invoice_id>/<str:payment_method>/<str:transaction_id>/',
#          views.payment_success, name='payment_success'),
#     path('payment/receipt/<int:payment_id>/', views.print_receipt, name='print_receipt'),
#
#     # Messages
#     path('messages/', MessageListView.as_view(), name='messages'),
#     path('messages/send/', views.send_message, name='send_message'),
#     path('messages/read/<int:message_id>/', views.mark_message_read, name='mark_message_read'),
#
#     # Admin-related URLs
#     path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
#     path('admin/clients/', views.admin_clients, name='admin_clients'),
#     path('admin/clients/<int:client_id>/', views.admin_client_detail, name='admin_client_detail'),
#     path('admin/create-project/', views.admin_create_project, name='admin_create_project'),
#     path('admin/create-invoice/', views.admin_create_invoice, name='admin_create_invoice'),
#     path('admin/record-payment/', views.admin_record_payment, name='admin_record_payment'),
#     path('admin/financial-summary/', views.admin_financial_summary, name='admin_financial_summary'),
#     path('admin/add-client/', views.admin_add_client, name='admin_add_client'),
#     path('admin/services/', views.admin_services, name='admin_services'),
#
#     # Email receipt URL
#     path('payment/receipt/<int:payment_id>/email/', views.email_receipt, name='email_receipt'),
# ]


# from django.urls import path
# from . import views
# from .views import ProjectListView, ProjectDetailView, InvoiceListView, InvoiceDetailView, MessageListView
#
# app_name = 'client_portal'
#
# urlpatterns = [
#     # Authentication URLs
#     path('login/', views.client_login, name='login'),
#     path('register/', views.client_register, name='register'),
#     path('logout/', views.client_logout, name='logout'),
#
#     # Dashboard
#     path('', views.dashboard, name='dashboard'),
#     path('profile/', views.profile, name='profile'),
#
#     # Projects
#     path('projects/', ProjectListView.as_view(), name='projects'),
#     path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project_detail'),
#
#     # Invoices
#     path('invoices/', InvoiceListView.as_view(), name='invoices'),
#     path('invoices/<int:pk>/', InvoiceDetailView.as_view(), name='invoice_detail'),
#     path('invoices/<int:invoice_id>/payment/', views.make_payment, name='make_payment'),
#     path('invoices/balance-due/', views.balance_due, name='balance_due'),
#
#     # Payments
#     path('payment/paypal/<int:invoice_id>/<str:amount>/', views.process_paypal, name='process_paypal'),
#     path('payment/credit-card/<int:invoice_id>/<str:amount>/', views.process_credit_card, name='process_credit_card'),
#     path('payment/mpesa/<int:invoice_id>/<str:amount>/', views.process_mpesa, name='process_mpesa'),
#     path('payment/success/<int:invoice_id>/<str:payment_method>/<str:transaction_id>/',
#          views.payment_success, name='payment_success'),
#     path('payment/receipt/<int:payment_id>/', views.print_receipt, name='print_receipt'),
#
#     # Messages
#     path('messages/', MessageListView.as_view(), name='messages'),
#     path('messages/send/', views.send_message, name='send_message'),
#     path('messages/read/<int:message_id>/', views.mark_message_read, name='mark_message_read'),
#
#     # Admin-related URLs
#     path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
#     path('admin/clients/', views.admin_clients, name='admin_clients'),
#     path('admin/clients/<int:client_id>/', views.admin_client_detail, name='admin_client_detail'),
#     path('admin/create-project/', views.admin_create_project, name='admin_create_project'),
#     path('admin/create-invoice/', views.admin_create_invoice, name='admin_create_invoice'),
#     path('admin/record-payment/', views.admin_record_payment, name='admin_record_payment'),
#     path('admin/financial-summary/', views.admin_financial_summary, name='admin_financial_summary'),
#     path('admin/add-client/', views.admin_add_client, name='admin_add_client'),
#
#     # Admin Service Management URLs
#     path('admin/services/', views.admin_services, name='admin_services'),
#     path('admin/services/add/', views.admin_add_service, name='admin_add_service'),
#     path('admin/services/edit/<int:service_id>/', views.admin_edit_service, name='admin_edit_service'),
#     path('admin/services/delete/<int:service_id>/', views.admin_delete_service, name='admin_delete_service'),
#     path('admin/services/<int:service_id>/add-feature/', views.admin_add_feature, name='admin_add_feature'),
#     path('admin/features/edit/<int:feature_id>/', views.admin_edit_feature, name='admin_edit_feature'),
#     path('admin/features/delete/<int:feature_id>/', views.admin_delete_feature, name='admin_delete_feature'),
#
#     # Email receipt URL
#     path('payment/receipt/<int:payment_id>/email/', views.email_receipt, name='email_receipt'),
# ]

from django.urls import path
from . import views, admin_views
from .views import ProjectListView, ProjectDetailView, InvoiceListView, InvoiceDetailView, MessageListView

app_name = 'client_portal'

urlpatterns = [
    # Authentication URLs
    path('login/', views.client_login, name='login'),
    path('register/', views.client_register, name='register'),

    # Add logout URL (ensure it uses the existing logout view from views.py)
    path('logout/', views.client_logout, name='logout'),

    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),

    # Projects
    path('projects/', ProjectListView.as_view(), name='projects'),
    path('projects/<int:pk>/', ProjectDetailView.as_view(), name='project_detail'),

    # Invoices
    path('invoices/', InvoiceListView.as_view(), name='invoices'),
    path('invoices/<int:pk>/', InvoiceDetailView.as_view(), name='invoice_detail'),
    path('invoices/<int:invoice_id>/payment/', views.make_payment, name='make_payment'),
    path('invoices/balance-due/', views.balance_due, name='balance_due'),

    # Payments
    path('payment/paypal/<int:invoice_id>/<str:amount>/', views.process_paypal, name='process_paypal'),
    path('payment/credit-card/<int:invoice_id>/<str:amount>/', views.process_credit_card, name='process_credit_card'),
    path('payment/mpesa/<int:invoice_id>/<str:amount>/', views.process_mpesa, name='process_mpesa'),
    path('payment/success/<int:invoice_id>/<str:payment_method>/<str:transaction_id>/',
         views.payment_success, name='payment_success'),
    path('payment/receipt/<int:payment_id>/', views.print_receipt, name='print_receipt'),

    # Messages
    path('messages/', MessageListView.as_view(), name='messages'),
    path('messages/send/', views.send_message, name='send_message'),
    path('messages/read/<int:message_id>/', views.mark_message_read, name='mark_message_read'),

    # Admin-related URLs - now pointing to admin_views
    path('admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin/clients/', views.admin_clients, name='admin_clients'),
    path('admin/clients/<int:client_id>/', views.admin_client_detail, name='admin_client_detail'),
    path('admin/create-project/', views.admin_create_project, name='admin_create_project'),
    path('admin/create-invoice/', views.admin_create_invoice, name='admin_create_invoice'),
    path('admin/record-payment/', views.admin_record_payment, name='admin_record_payment'),
    path('admin/financial-summary/', views.admin_financial_summary, name='admin_financial_summary'),
    path('admin/add-client/', views.admin_add_client, name='admin_add_client'),

    # Admin Service Management URLs - now pointing to admin_views
    path('admin/services/', admin_views.admin_services, name='admin_services'),
    path('admin/services/add/', admin_views.admin_add_service, name='admin_add_service'),
    path('admin/services/edit/<int:service_id>/', admin_views.admin_edit_service, name='admin_edit_service'),
    path('admin/services/delete/<int:service_id>/', admin_views.admin_delete_service, name='admin_delete_service'),
    path('admin/services/<int:service_id>/add-feature/', admin_views.admin_add_feature, name='admin_add_feature'),
    path('admin/features/edit/<int:feature_id>/', admin_views.admin_edit_feature, name='admin_edit_feature'),
    path('admin/features/delete/<int:feature_id>/', admin_views.admin_delete_feature, name='admin_delete_feature'),

    # Email receipt URL
    path('payment/receipt/<int:payment_id>/email/', views.email_receipt, name='email_receipt'),
]