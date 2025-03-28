from django.db import models
from django.utils.text import slugify


class Service(models.Model):
    SERVICE_TYPES = (
        ('web', 'Web Development'),
        ('app', 'App Development'),
        ('pos', 'POS System'),
    )

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    service_type = models.CharField(max_length=10, choices=SERVICE_TYPES)
    short_description = models.TextField(max_length=200)
    description = models.TextField()
    features = models.TextField()
    icon = models.CharField(max_length=50, help_text="Font Awesome class name")
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['service_type', 'name']


class ServiceFeature(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='service_features')
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Font Awesome class name")

    def __str__(self):
        return f"{self.service.name} - {self.title}"