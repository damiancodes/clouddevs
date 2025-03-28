from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count
from .models import Client, Project, Invoice, Payment


@staff_member_required
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