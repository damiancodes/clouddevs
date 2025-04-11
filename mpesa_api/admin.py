# mpesa_api/admin.py
from django.contrib import admin
from .models import MpesaTransaction

@admin.register(MpesaTransaction)
class MpesaTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'phone_number', 'amount', 'is_completed', 'is_successful', 'created_at')
    list_filter = ('is_completed', 'is_successful', 'created_at')
    search_fields = ('transaction_id', 'phone_number', 'reference')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Transaction Details', {
            'fields': ('transaction_type', 'transaction_id', 'phone_number', 'amount', 'reference', 'description')
        }),
        ('M-Pesa Response', {
            'fields': ('merchant_request_id', 'checkout_request_id', 'response_code', 'response_description', 'customer_message')
        }),
        ('Status', {
            'fields': ('result_code', 'result_description', 'is_completed', 'is_successful')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

# mpesa_api/apps.py
from django.apps import AppConfig

class MpesaApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mpesa_api'
    verbose_name = 'M-Pesa Integration'