from django.db import models
from django.utils.text import slugify


class Service(models.Model):
    """Services available for quotes/estimates"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Starting price for this service")

    # Display order in service estimator
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if Service.objects.filter(slug=self.slug).exclude(id=self.id).exists():
            self.slug = f"{slugify(self.name)}-{Service.objects.count()}"
        super().save(*args, **kwargs)


class ServiceFeature(models.Model):
    """Features/options for services that affect pricing"""
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='features')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    # Price impact of this feature
    price_type = models.CharField(max_length=20,
                                  choices=[
                                      ('fixed', 'Fixed Amount'),
                                      ('percentage', 'Percentage of Base'),
                                  ],
                                  default='fixed')
    price_value = models.DecimalField(max_digits=10, decimal_places=2)

    # Is this required or optional?
    is_required = models.BooleanField(default=False)

    # Display order in the estimator
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['service', 'order', 'name']

    def __str__(self):
        return f"{self.service.name} - {self.name}"


class QuoteRequest(models.Model):
    """Customer requests for quotes"""
    # Contact Information
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=100, blank=True)

    # Project Information
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name='quote_requests')
    features = models.ManyToManyField(ServiceFeature, blank=True, related_name='quote_requests')

    # Additional custom requirements
    requirements = models.TextField(blank=True)
    budget = models.CharField(max_length=100, blank=True)
    timeline = models.CharField(max_length=100, blank=True)

    # Admin fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    estimated_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20,
                              choices=[
                                  ('new', 'New Request'),
                                  ('reviewing', 'Under Review'),
                                  ('estimated', 'Estimate Provided'),
                                  ('accepted', 'Accepted'),
                                  ('declined', 'Declined'),
                                  ('completed', 'Project Completed'),
                              ],
                              default='new')

    admin_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Quote Request from {self.name} - {self.service.name}"

    @property
    def calculated_estimate(self):
        """Calculate an estimated cost based on selected service and features"""
        if not self.service:
            return 0

        total = self.service.base_price

        for feature in self.features.all():
            if feature.price_type == 'fixed':
                total += feature.price_value
            elif feature.price_type == 'percentage':
                total += (self.service.base_price * feature.price_value / 100)

        return total