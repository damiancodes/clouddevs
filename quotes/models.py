# from django.db import models
# from django.utils.text import slugify
#
#
# class Service(models.Model):
#     """Services available for quotes/estimates"""
#     name = models.CharField(max_length=100)
#     slug = models.SlugField(max_length=100, unique=True)
#     description = models.TextField()
#     base_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Starting price for this service")
#
#     # Display order in service estimator
#     order = models.PositiveIntegerField(default=0)
#
#     class Meta:
#         ordering = ['order', 'name']
#
#     def __str__(self):
#         return self.name
#
#     def save(self, *args, **kwargs):
#         if not self.slug:
#             self.slug = slugify(self.name)
#         if Service.objects.filter(slug=self.slug).exclude(id=self.id).exists():
#             self.slug = f"{slugify(self.name)}-{Service.objects.count()}"
#         super().save(*args, **kwargs)
#
#
# class ServiceFeature(models.Model):
#     """Features/options for services that affect pricing"""
#     service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='features')
#     name = models.CharField(max_length=100)
#     description = models.TextField(blank=True)
#
#     # Price impact of this feature
#     price_type = models.CharField(max_length=20,
#                                   choices=[
#                                       ('fixed', 'Fixed Amount'),
#                                       ('percentage', 'Percentage of Base'),
#                                   ],
#                                   default='fixed')
#     price_value = models.DecimalField(max_digits=10, decimal_places=2)
#
#     # Is this required or optional?
#     is_required = models.BooleanField(default=False)
#
#     # Display order in the estimator
#     order = models.PositiveIntegerField(default=0)
#
#     class Meta:
#         ordering = ['service', 'order', 'name']
#
#     def __str__(self):
#         return f"{self.service.name} - {self.name}"
#
#
# class QuoteRequest(models.Model):
#     """Customer requests for quotes"""
#     # Contact Information
#     name = models.CharField(max_length=100)
#     email = models.EmailField()
#     phone = models.CharField(max_length=20, blank=True)
#     company = models.CharField(max_length=100, blank=True)
#
#     # Project Information
#     service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name='quote_requests')
#     features = models.ManyToManyField(ServiceFeature, blank=True, related_name='quote_requests')
#
#     # Additional custom requirements
#     requirements = models.TextField(blank=True)
#     budget = models.CharField(max_length=100, blank=True)
#     timeline = models.CharField(max_length=100, blank=True)
#
#     # Admin fields
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
#     status = models.CharField(max_length=20,
#                               choices=[
#                                   ('new', 'New Request'),
#                                   ('reviewing', 'Under Review'),
#                                   ('estimated', 'Estimate Provided'),
#                                   ('accepted', 'Accepted'),
#                                   ('declined', 'Declined'),
#                                   ('completed', 'Project Completed'),
#                               ],
#                               default='new')
#
#     admin_notes = models.TextField(blank=True)
#
#     class Meta:
#         ordering = ['-created_at']
#
#     def __str__(self):
#         return f"Quote Request from {self.name} - {self.service.name}"
#
#     @property
#     def calculated_estimate(self):
#         """Calculate an estimated cost based on selected service and features"""
#         if not self.service:
#             return 0
#
#         total = self.service.base_price
#
#         for feature in self.features.all():
#             if feature.price_type == 'fixed':
#                 total += feature.price_value
#             elif feature.price_type == 'percentage':
#                 total += (self.service.base_price * feature.price_value / 100)
#
#         return total
# quotes/models.py
from django.db import models
from decimal import Decimal
from client_portal.models import Client, Payment, Invoice
from services.models import Service, ServiceFeature


class ExchangeRate(models.Model):
    """Model for storing currency exchange rates."""
    usd_to_ksh = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('145.00'))
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"USD to KSH: {self.usd_to_ksh} (Updated: {self.last_updated})"

    @classmethod
    def get_rate(cls):
        """Get the current exchange rate. Create if it doesn't exist."""
        rate, created = cls.objects.get_or_create(
            pk=1,
            defaults={'usd_to_ksh': Decimal('145.00')}
        )
        return rate.usd_to_ksh


class SolutionBuilder(models.Model):
    """Model for solution builder orders with service selection and features."""
    # Client info (we'll link to Client model if user is logged in)
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True, related_name='solution_orders')
    # For non-logged in users or initial collection
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)

    # Service and appointment info
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    appointment_date = models.DateTimeField()
    notes = models.TextField(blank=True, null=True)

    # Pricing
    total_price_usd = models.DecimalField(max_digits=10, decimal_places=2)
    total_price_ksh = models.DecimalField(max_digits=10, decimal_places=2)

    # Payment status
    is_paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=20, blank=True, null=True,
                                      choices=[
                                          ('mpesa', 'M-Pesa'),
                                          ('paypal', 'PayPal'),
                                          ('crypto', 'Cryptocurrency'),
                                          ('none', 'No Payment')
                                      ])
    transaction_id = models.CharField(max_length=100, blank=True, null=True)

    # Link to the created invoice if any
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='solution_order')

    # Link to the project that may be created from this order
    project = models.ForeignKey('client_portal.Project', on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='from_solution')

    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending',
                              choices=[
                                  ('pending', 'Pending'),
                                  ('confirmed', 'Confirmed'),
                                  ('cancelled', 'Cancelled'),
                                  ('completed', 'Completed')
                              ])

    def __str__(self):
        return f"Solution Order by {self.name} - {self.service.name}"

    class Meta:
        ordering = ['-created_at']

    @property
    def get_total_usd(self):
        """Calculate total in USD based on selected features."""
        if hasattr(self, '_total_usd'):
            return self._total_usd

        base = self.service.base_price
        for feature in self.selected_features.all():
            if feature.price_type == 'fixed':
                base += feature.price_at_order
            else:  # percentage
                base += self.service.base_price * (feature.feature.price_value / 100)

        self._total_usd = base
        return base

    @property
    def get_total_ksh(self):
        """Get total in KSH."""
        usd = self.get_total_usd
        rate = ExchangeRate.get_rate()
        return usd * rate

    def create_invoice(self):
        """Create an invoice from this solution order."""
        from django.utils import timezone

        if self.invoice:
            return self.invoice

        # Create a new invoice
        invoice = Invoice.objects.create(
            client=self.client,
            invoice_number=f"SOL-{self.id}",
            status='sent',
            issue_date=timezone.now().date(),
            due_date=timezone.now().date() + timezone.timedelta(days=14),
            subtotal=self.total_price_usd,
            tax_rate=0,  # Set your default tax rate
            discount=0,
            total=self.total_price_usd,
            notes=f"Invoice for solution order: {self.service.name}"
        )

        # Create invoice items
        from client_portal.models import InvoiceItem

        # Base service
        InvoiceItem.objects.create(
            invoice=invoice,
            description=f"Base Service: {self.service.name}",
            quantity=1,
            unit_price=self.service.base_price,
            amount=self.service.base_price
        )

        # Features
        for feature in self.selected_features.all():
            feature_price = feature.price_at_order
            InvoiceItem.objects.create(
                invoice=invoice,
                description=f"Feature: {feature.feature.name}",
                quantity=1,
                unit_price=feature_price,
                amount=feature_price
            )

        # Update the invoice link
        self.invoice = invoice
        self.save()

        return invoice


class SolutionFeature(models.Model):
    """Model for features selected in a solution order."""
    solution = models.ForeignKey(SolutionBuilder, related_name='selected_features', on_delete=models.CASCADE)
    feature = models.ForeignKey(ServiceFeature, on_delete=models.CASCADE)
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2)
    price_type = models.CharField(max_length=10, choices=[('fixed', 'Fixed'), ('percentage', 'Percentage')])

    def __str__(self):
        return f"{self.feature.name} for {self.solution}"


# You might want to add this to services/models.py instead of this file
# class ServiceOrder(models.Model):
#     """Model for storing the display order of services."""
#     service = models.OneToOneField(Service, on_delete=models.CASCADE, related_name='display_order')
#     order = models.IntegerField(default=0)
#
#     class Meta:
#         ordering = ['order']
#
#     def __str__(self):
#         return f"{self.service.name} (Order: {self.order})"