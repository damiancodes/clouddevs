from django.db import models


class MpesaTransaction(models.Model):
    """
    Model to track M-Pesa transactions
    """
    transaction_type = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100, unique=True)
    phone_number = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # M-Pesa response fields
    merchant_request_id = models.CharField(max_length=100, blank=True)
    checkout_request_id = models.CharField(max_length=100, blank=True)
    response_code = models.CharField(max_length=20, blank=True)
    response_description = models.CharField(max_length=255, blank=True)
    customer_message = models.CharField(max_length=255, blank=True)

    # For tracking purposes
    result_code = models.CharField(max_length=20, blank=True, null=True)
    result_description = models.CharField(max_length=255, blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    is_successful = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.transaction_id} - {self.amount} - {self.phone_number}"