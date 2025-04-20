from django.contrib import admin
from django.utils.html import format_html
from .models import Service, ServiceFeature, ServiceOrder

class ServiceFeatureInline(admin.TabularInline):
    model = ServiceFeature
    extra = 1  # Number of empty forms to display
    fields = ['title', 'description', 'icon', 'price_type', 'price_value', 'is_required']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'service_type', 'base_price', 'is_active', 'display_icon', 'created_at')
    list_filter = ('service_type', 'is_active', 'created_at')
    search_fields = ('name', 'description', 'short_description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ServiceFeatureInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'service_type', 'short_description')
        }),
        ('Pricing', {
            'fields': ('base_price',),
        }),
        ('Details', {
            'fields': ('description', 'features', 'icon', 'image', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def display_icon(self, obj):
        return format_html('<i class="{}"></i> {}', obj.icon, obj.icon)

    display_icon.short_description = 'Icon'

@admin.register(ServiceFeature)
class ServiceFeatureAdmin(admin.ModelAdmin):
    list_display = ('title', 'service', 'price_type', 'price_value', 'is_required', 'display_icon')
    list_filter = ('service', 'price_type', 'is_required')
    search_fields = ('title', 'description')

    def display_icon(self, obj):
        return format_html('<i class="{}"></i> {}', obj.icon, obj.icon)

    display_icon.short_description = 'Icon'

@admin.register(ServiceOrder)
class ServiceOrderAdmin(admin.ModelAdmin):
    list_display = ['service', 'order']
    list_editable = ['order']