# from django.contrib import admin
# from import_export import resources
# from import_export.admin import ImportExportModelAdmin
# from .models import Client, Project, ProjectTask, ProjectUpdate, ProjectFile, Invoice, InvoiceItem, Payment, Message
# from django.utils.html import format_html
# from django.contrib.admin import AdminSite
#
#
# class CloudLinkAdminSite(AdminSite):
#     site_header = 'CloudLink_Devs Administration'
#     site_title = 'CloudLink_Devs Admin'
#     index_title = 'Administration Dashboard'
#
#     def get_urls(self):
#         from django.urls import path
#         urls = super().get_urls()
#         custom_urls = [
#             path('dashboard/', self.admin_view(admin_dashboard), name='admin_dashboard'),
#         ]
#         return custom_urls + urls
#
#
# # Replace the default admin site
# admin_site = CloudLinkAdminSite(name='cloudlink_admin')
#
# # Register your models with this custom admin site
# admin_site.register(Client, ClientAdmin)
# admin_site.register(Project, ProjectAdmin)
#
#
# # Invoice Resource for Import/Export
# class InvoiceResource(resources.ModelResource):
#     client_name = resources.Field()
#     payment_status = resources.Field()
#
#     class Meta:
#         model = Invoice
#         fields = ('id', 'invoice_number', 'client_name', 'issue_date', 'due_date',
#                   'subtotal', 'tax_amount', 'total', 'payment_status')
#
#     def dehydrate_client_name(self, invoice):
#         return f"{invoice.client.full_name} ({invoice.client.company_name})"
#
#     def dehydrate_payment_status(self, invoice):
#         if invoice.is_fully_paid:
#             return "Paid"
#         elif invoice.status == 'overdue':
#             return f"Overdue (${invoice.balance_due})"
#         else:
#             return f"Pending (${invoice.balance_due})"
#
# # Client Admin
# @admin.register(Client)
# class ClientAdmin(admin.ModelAdmin):
#     list_display = ('user', 'company_name', 'phone', 'is_active', 'created_at')
#     list_filter = ('is_active', 'created_at', 'industry')
#     search_fields = ('user__username', 'user__email', 'company_name', 'phone')
#     date_hierarchy = 'created_at'
#     fieldsets = (
#         ('User Information', {
#             'fields': ('user', 'is_active')
#         }),
#         ('Company Information', {
#             'fields': ('company_name', 'phone', 'address', 'profile_image', 'industry', 'website')
#         }),
#         ('Additional Information', {
#             'fields': ('referred_by', 'created_at', 'updated_at')
#         }),
#     )
#     readonly_fields = ('created_at', 'updated_at')
#
# # Project Inlines
# class ProjectTaskInline(admin.TabularInline):
#     model = ProjectTask
#     extra = 1
#
# class ProjectUpdateInline(admin.TabularInline):
#     model = ProjectUpdate
#     extra = 1
#
# class ProjectFileInline(admin.TabularInline):
#     model = ProjectFile
#     extra = 1
#
# # Project Admin
# @admin.register(Project)
# class ProjectAdmin(admin.ModelAdmin):
#     list_display = ('title', 'client', 'status', 'start_date', 'end_date', 'budget', 'completion_percentage')
#     list_filter = ('status', 'start_date', 'end_date')
#     search_fields = ('title', 'description', 'client__user__username', 'client__company_name')
#     date_hierarchy = 'start_date'
#     inlines = [ProjectTaskInline, ProjectUpdateInline, ProjectFileInline]
#     fieldsets = (
#         ('Project Information', {
#             'fields': ('client', 'title', 'description', 'status')
#         }),
#         ('Dates & Budget', {
#             'fields': ('start_date', 'end_date', 'budget')
#         }),
#         ('Metadata', {
#             'fields': ('created_at', 'updated_at')
#         }),
#     )
#     readonly_fields = ('created_at', 'updated_at')
#
# # ProjectTask Admin
# @admin.register(ProjectTask)
# class ProjectTaskAdmin(admin.ModelAdmin):
#     list_display = ('title', 'project', 'is_completed', 'due_date', 'is_overdue')
#     list_filter = ('is_completed', 'due_date', 'project')
#     search_fields = ('title', 'description', 'project__title')
#     date_hierarchy = 'due_date'
#
# # ProjectUpdate Admin
# @admin.register(ProjectUpdate)
# class ProjectUpdateAdmin(admin.ModelAdmin):
#     list_display = ('title', 'project', 'created_at')
#     list_filter = ('created_at', 'project')
#     search_fields = ('title', 'description', 'project__title')
#     date_hierarchy = 'created_at'
#
# # ProjectFile Admin
# @admin.register(ProjectFile)
# class ProjectFileAdmin(admin.ModelAdmin):
#     list_display = ('title', 'project', 'file', 'uploaded_at')
#     list_filter = ('uploaded_at', 'project')
#     search_fields = ('title', 'description', 'project__title')
#     date_hierarchy = 'uploaded_at'
#
# # Invoice Inlines
# class InvoiceItemInline(admin.TabularInline):
#     model = InvoiceItem
#     extra = 1
#
# class PaymentInline(admin.TabularInline):
#     model = Payment
#     extra = 0
#     readonly_fields = ('payment_date', 'amount', 'payment_method', 'transaction_id')
#     can_delete = False
#
#     def has_add_permission(self, request, obj=None):
#         return False
#
# # Invoice Admin
# @admin.register(Invoice)
# class InvoiceAdmin(ImportExportModelAdmin):
#     resource_class = InvoiceResource
#     list_display = ('invoice_number', 'client', 'project', 'status', 'issue_date', 'due_date', 'total', 'balance_due')
#     list_filter = ('status', 'issue_date', 'due_date')
#     search_fields = ('invoice_number', 'client__user__username', 'client__company_name', 'project__title')
#     date_hierarchy = 'issue_date'
#     inlines = [InvoiceItemInline, PaymentInline]
#     fieldsets = (
#         ('Invoice Information', {
#             'fields': ('client', 'project', 'invoice_number', 'status')
#         }),
#         ('Dates', {
#             'fields': ('issue_date', 'due_date')
#         }),
#         ('Amounts', {
#             'fields': ('subtotal', 'tax_rate', 'discount', 'total')
#         }),
#         ('Notes', {
#             'fields': ('notes',)
#         }),
#         ('Metadata', {
#             'fields': ('created_at', 'updated_at')
#         }),
#     )
#     readonly_fields = ('total', 'created_at', 'updated_at')
#
# # InvoiceItem Admin
# @admin.register(InvoiceItem)
# class InvoiceItemAdmin(admin.ModelAdmin):
#     list_display = ('description', 'invoice', 'quantity', 'unit_price', 'amount')
#     list_filter = ('invoice', 'invoice__status')
#     search_fields = ('description', 'invoice__invoice_number')
#     readonly_fields = ('amount',)
#
# # Payment Admin
# @admin.register(Payment)
# class PaymentAdmin(admin.ModelAdmin):
#     list_display = ('id', 'invoice', 'amount', 'payment_date', 'payment_method_display', 'transaction_id')
#     list_filter = ('payment_method', 'payment_date')
#     search_fields = ('invoice__invoice_number', 'transaction_id')
#     date_hierarchy = 'payment_date'
#
#     def payment_method_display(self, obj):
#         # Get the display value
#         method = obj.get_payment_method_display()
#
#         # Add icons for visual distinction
#         if obj.payment_method == 'credit_card':
#             return format_html('<i class="fas fa-credit-card"></i> {}', method)
#         elif obj.payment_method == 'paypal':
#             return format_html('<i class="fab fa-paypal"></i> {}', method)
#         elif obj.payment_method == 'mpesa':
#             return format_html('<i class="fas fa-mobile-alt"></i> {}', method)
#         else:
#             return method
#
#     payment_method_display.short_description = 'Payment Method'
#
# # Message Admin
# @admin.register(Message)
# class MessageAdmin(admin.ModelAdmin):
#     list_display = ('subject', 'client', 'is_from_client', 'is_read', 'created_at')
#     list_filter = ('is_from_client', 'is_read', 'created_at')
#     search_fields = ('subject', 'content', 'client__user__username', 'client__company_name')
#     date_hierarchy = 'created_at'
#     actions = ['mark_as_read']
#
#     def mark_as_read(self, request, queryset):
#         queryset.update(is_read=True)
#
#     mark_as_read.short_description = "Mark selected messages as read"

from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import Client, Project, ProjectTask, ProjectUpdate, ProjectFile, Invoice, InvoiceItem, Payment, Message
from django.utils.html import format_html
from django.contrib.admin import AdminSite
from django.http import HttpResponse
from openpyxl import Workbook
from django.db.models import Sum, Count
from datetime import datetime
import csv

# First, import the admin_dashboard view or define it inline
try:
    from .admin_views import admin_dashboard
except ImportError:
    # Fallback if the view hasn't been created yet
    from django.shortcuts import render


    def admin_dashboard(request):
        # Client statistics
        total_clients = Client.objects.count()
        active_clients = Client.objects.filter(is_active=True).count()

        # Project statistics
        projects_by_status = Project.objects.values('status').annotate(count=Count('id'))

        # Financial summary
        total_invoiced = Invoice.objects.aggregate(Sum('total'))['total__sum'] or 0
        total_paid = Payment.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        balance_due = total_invoiced - total_paid

        # Payment method breakdown
        payment_by_method = Payment.objects.values('payment_method').annotate(
            count=Count('id'),
            total=Sum('amount')
        ).order_by('-total')

        # Recent payments
        recent_payments = Payment.objects.select_related('invoice', 'invoice__client').order_by('-payment_date')[:10]

        # Overdue invoices
        overdue_invoices = Invoice.objects.filter(status='overdue').select_related('client')

        return render(request, 'admin/dashboard.html', {
            'total_clients': total_clients,
            'active_clients': active_clients,
            'projects_by_status': projects_by_status,
            'total_invoiced': total_invoiced,
            'total_paid': total_paid,
            'balance_due': balance_due,
            'payment_by_method': payment_by_method,
            'recent_payments': recent_payments,
            'overdue_invoices': overdue_invoices,
        })


# Define the custom admin site
class CloudLinkAdminSite(AdminSite):
    site_header = 'CloudLink_Devs Administration'
    site_title = 'CloudLink_Devs Admin'
    index_title = 'Administration Dashboard'

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(admin_dashboard), name='admin_dashboard'),
        ]
        return custom_urls + urls


# Create the admin site instance
admin_site = CloudLinkAdminSite(name='cloudlink_admin')


# Invoice Resource for Import/Export
class InvoiceResource(resources.ModelResource):
    client_name = resources.Field()
    payment_status = resources.Field()

    class Meta:
        model = Invoice
        fields = ('id', 'invoice_number', 'client_name', 'issue_date', 'due_date',
                  'subtotal', 'tax_amount', 'total', 'payment_status')

    def dehydrate_client_name(self, invoice):
        return f"{invoice.client.full_name} ({invoice.client.company_name})"

    def dehydrate_payment_status(self, invoice):
        if invoice.is_fully_paid:
            return "Paid"
        elif invoice.status == 'overdue':
            return f"Overdue (${invoice.balance_due})"
        else:
            return f"Pending (${invoice.balance_due})"


# Define all admin classes first
# Client Admin
class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name', 'phone', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'industry')
    search_fields = ('user__username', 'user__email', 'company_name', 'phone')
    date_hierarchy = 'created_at'
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'is_active')
        }),
        ('Company Information', {
            'fields': ('company_name', 'phone', 'address', 'profile_image', 'industry', 'website')
        }),
        ('Additional Information', {
            'fields': ('referred_by', 'created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


# Project Inlines
class ProjectTaskInline(admin.TabularInline):
    model = ProjectTask
    extra = 1


class ProjectUpdateInline(admin.TabularInline):
    model = ProjectUpdate
    extra = 1


class ProjectFileInline(admin.TabularInline):
    model = ProjectFile
    extra = 1


# Project Admin
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'status', 'start_date', 'end_date', 'budget', 'completion_percentage')
    list_filter = ('status', 'start_date', 'end_date')
    search_fields = ('title', 'description', 'client__user__username', 'client__company_name')
    date_hierarchy = 'start_date'
    inlines = [ProjectTaskInline, ProjectUpdateInline, ProjectFileInline]
    fieldsets = (
        ('Project Information', {
            'fields': ('client', 'title', 'description', 'status')
        }),
        ('Dates & Budget', {
            'fields': ('start_date', 'end_date', 'budget')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


# ProjectTask Admin
class ProjectTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'is_completed', 'due_date', 'is_overdue')
    list_filter = ('is_completed', 'due_date', 'project')
    search_fields = ('title', 'description', 'project__title')
    date_hierarchy = 'due_date'


# ProjectUpdate Admin
class ProjectUpdateAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'created_at')
    list_filter = ('created_at', 'project')
    search_fields = ('title', 'description', 'project__title')
    date_hierarchy = 'created_at'


# ProjectFile Admin
class ProjectFileAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'file', 'uploaded_at')
    list_filter = ('uploaded_at', 'project')
    search_fields = ('title', 'description', 'project__title')
    date_hierarchy = 'uploaded_at'


# Invoice Inlines
class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ('payment_date', 'amount', 'payment_method', 'transaction_id')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


# Invoice Admin
class InvoiceAdmin(ImportExportModelAdmin):
    resource_class = InvoiceResource
    list_display = ('invoice_number', 'client', 'project', 'status', 'issue_date', 'due_date', 'total', 'balance_due')
    list_filter = ('status', 'issue_date', 'due_date')
    search_fields = ('invoice_number', 'client__user__username', 'client__company_name', 'project__title')
    date_hierarchy = 'issue_date'
    inlines = [InvoiceItemInline, PaymentInline]
    actions = ['export_as_csv', 'export_as_excel']
    fieldsets = (
        ('Invoice Information', {
            'fields': ('client', 'project', 'invoice_number', 'status')
        }),
        ('Dates', {
            'fields': ('issue_date', 'due_date')
        }),
        ('Amounts', {
            'fields': ('subtotal', 'tax_rate', 'discount', 'total')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    readonly_fields = ('total', 'created_at', 'updated_at')

    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response[
            'Content-Disposition'] = f'attachment; filename=invoices_export_{datetime.now().strftime("%Y-%m-%d")}.csv'

        writer = csv.writer(response)
        writer.writerow(['Invoice #', 'Client', 'Status', 'Issue Date', 'Due Date', 'Total', 'Balance Due'])

        for invoice in queryset:
            writer.writerow([
                invoice.invoice_number,
                invoice.client.full_name,
                invoice.get_status_display(),
                invoice.issue_date,
                invoice.due_date,
                invoice.total,
                invoice.balance_due
            ])

        return response

    export_as_csv.short_description = "Export selected invoices as CSV"

    def export_as_excel(self, request, queryset):
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response[
            'Content-Disposition'] = f'attachment; filename=invoices_export_{datetime.now().strftime("%Y-%m-%d")}.xlsx'

        wb = Workbook()
        ws = wb.active
        ws.title = "Invoices"

        # Header row
        columns = ['Invoice #', 'Client', 'Status', 'Issue Date', 'Due Date', 'Total', 'Balance Due']
        ws.append(columns)

        # Data rows
        for invoice in queryset:
            ws.append([
                invoice.invoice_number,
                invoice.client.full_name,
                invoice.get_status_display(),
                invoice.issue_date,
                invoice.due_date,
                invoice.total,
                invoice.balance_due
            ])

        wb.save(response)
        return response

    export_as_excel.short_description = "Export selected invoices as Excel"


# InvoiceItem Admin
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ('description', 'invoice', 'quantity', 'unit_price', 'amount')
    list_filter = ('invoice', 'invoice__status')
    search_fields = ('description', 'invoice__invoice_number')
    readonly_fields = ('amount',)


# Payment Admin
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'invoice', 'amount', 'payment_date', 'payment_method_display', 'transaction_id')
    list_filter = ('payment_method', 'payment_date')
    search_fields = ('invoice__invoice_number', 'transaction_id')
    date_hierarchy = 'payment_date'

    def payment_method_display(self, obj):
        # Get the display value
        method = obj.get_payment_method_display()

        # Add icons for visual distinction
        if obj.payment_method == 'credit_card':
            return format_html('<i class="fas fa-credit-card"></i> {}', method)
        elif obj.payment_method == 'paypal':
            return format_html('<i class="fab fa-paypal"></i> {}', method)
        elif obj.payment_method == 'mpesa':
            return format_html('<i class="fas fa-mobile-alt"></i> {}', method)
        else:
            return method

    payment_method_display.short_description = 'Payment Method'


# Message Admin
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'client', 'is_from_client', 'is_read', 'created_at')
    list_filter = ('is_from_client', 'is_read', 'created_at')
    search_fields = ('subject', 'content', 'client__user__username', 'client__company_name')
    date_hierarchy = 'created_at'
    actions = ['mark_as_read']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)

    mark_as_read.short_description = "Mark selected messages as read"


# Finally register all models with the custom admin site
admin_site.register(Client, ClientAdmin)
admin_site.register(Project, ProjectAdmin)
admin_site.register(ProjectTask, ProjectTaskAdmin)
admin_site.register(ProjectUpdate, ProjectUpdateAdmin)
admin_site.register(ProjectFile, ProjectFileAdmin)
admin_site.register(Invoice, InvoiceAdmin)
admin_site.register(InvoiceItem, InvoiceItemAdmin)
admin_site.register(Payment, PaymentAdmin)
admin_site.register(Message, MessageAdmin)