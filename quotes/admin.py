from django.contrib import admin
from .models import Service, ServiceFeature, QuoteRequest


class ServiceFeatureInline(admin.TabularInline):
    model = ServiceFeature
    extra = 1
    fields = ['name', 'description', 'price_type', 'price_value', 'is_required', 'order']


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_price', 'order', 'feature_count']
    list_editable = ['order', 'base_price']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ServiceFeatureInline]

    def feature_count(self, obj):
        return obj.features.count()

    feature_count.short_description = 'Features'


@admin.register(ServiceFeature)
class ServiceFeatureAdmin(admin.ModelAdmin):
    list_display = ['name', 'service', 'price_type', 'price_value', 'is_required', 'order']
    list_filter = ['service', 'price_type', 'is_required']
    list_editable = ['order', 'price_value', 'is_required']
    search_fields = ['name', 'description', 'service__name']


@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'service', 'status', 'created_at', 'estimated_cost']
    list_filter = ['status', 'service', 'created_at']
    search_fields = ['name', 'email', 'company', 'requirements']
    readonly_fields = ['created_at', 'updated_at', 'calculated_estimate']
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone', 'company')
        }),
        ('Project Details', {
            'fields': ('service', 'features', 'requirements', 'budget', 'timeline')
        }),
        ('Administrative', {
            'fields': ('status', 'estimated_cost', 'admin_notes', 'created_at', 'updated_at', 'calculated_estimate')
        }),
    )
    filter_horizontal = ['features']

    def calculated_estimate(self, obj):
        """Display the calculated estimate based on selected service and features"""
        return f"${obj.calculated_estimate:.2f}"

    calculated_estimate.short_description = 'Calculated Estimate'