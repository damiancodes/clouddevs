
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count
from services.models import Service, ServiceFeature
from services.forms import ServiceForm, ServiceFeatureForm
# In admin_views.py
from .views import is_admin_user

from .models import Client, Project, Invoice, Payment
from services.models import Service  # Import the Service model


@staff_member_required
def admin_dashboard(request):
    """Admin dashboard view with statistics and service management"""

    # Client statistics
    total_clients = Client.objects.count()
    active_clients = Client.objects.filter(is_active=True).count()

    # Project statistics
    total_projects = Project.objects.count()
    projects_in_progress = Project.objects.filter(status='IN_PROGRESS').count()
    projects_by_status = Project.objects.values('status').annotate(count=Count('id'))

    # Financial statistics
    total_invoiced = Invoice.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_collected = Payment.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    outstanding_amount = total_invoiced - total_collected

    # Payment statistics
    payment_by_method = Payment.objects.values('payment_method').annotate(
        count=Count('id'),
        total=Sum('amount')
    )

    # Recent payments
    recent_payments = Payment.objects.select_related('invoice__client').order_by('-payment_date')[:10]

    # Overdue invoices
    today = timezone.now().date()
    overdue_invoices = Invoice.objects.filter(
        due_date__lt=today,
        balance_due__gt=0
    ).select_related('client').order_by('due_date')[:10]

    # Services for management
    services = Service.objects.all().order_by('category', 'name')


    context = {
        'total_clients': total_clients,
        'active_clients': active_clients,
        'total_projects': total_projects,
        'projects_in_progress': projects_in_progress,
        'projects_by_status': projects_by_status,
        'total_invoiced': total_invoiced,
        'total_collected': total_collected,
        'outstanding_amount': outstanding_amount,
        'payment_by_method': payment_by_method,
        'recent_payments': recent_payments,
        'overdue_invoices': overdue_invoices,
        'services': services,
    }

    return render(request, 'client_portal/admin_dashboard.html', context)


@staff_member_required
def admin_service_action(request):
    print("admin_services view function called")
    """Handle service CRUD operations"""
    if request.method == 'POST':
        action_type = request.POST.get('action_type')

        if action_type == 'add':
            # Create new service
            service = Service.objects.create(
                name=request.POST.get('name'),
                category=request.POST.get('category'),
                description=request.POST.get('description'),
                base_price=request.POST.get('base_price'),
                is_active=request.POST.get('is_active') == 'True',
            )
            messages.success(request, f'Service "{service.name}" has been created successfully.')

        elif action_type == 'edit':
            # Update existing service
            service_id = request.POST.get('service_id')
            service = get_object_or_404(Service, id=service_id)

            service.name = request.POST.get('name')
            service.category = request.POST.get('category')
            service.description = request.POST.get('description')
            service.base_price = request.POST.get('base_price')
            service.is_active = request.POST.get('is_active') == 'True'
            service.save()
            messages.success(request, f'Service "{service.name}" has been updated successfully.')

        elif action_type == 'delete':
            # Delete service
            service_id = request.POST.get('service_id')
            service = get_object_or_404(Service, id=service_id)
            service_name = service.name
            service.delete()
            messages.success(request, f'Service "{service_name}" has been deleted successfully.')

    return redirect('client_portal:admin_dashboard')


@staff_member_required
def get_service_data(request, service_id):
    """API endpoint to get service data for editing"""
    service = get_object_or_404(Service, id=service_id)

    data = {
        'name': service.name,
        'category': service.category,
        'description': service.description,
        'base_price': float(service.base_price),
        'is_active': service.is_active,
    }

    return JsonResponse(data)

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_services(request):
    """
    Admin view for managing services
    """
    services = Service.objects.all()

    context = {
        'is_admin': True,
        'services': services,
        'total_services': services.count(),
        'active_services': services.filter(is_active=True).count(),
        'services_by_type': services.values('service_type').annotate(count=Count('id'))
    }
    print("Admin services view called")  # Debug print
    return render(request, 'admin/admin_services.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_add_feature(request, service_id):
    """
    Add a feature to a service
    """
    service = get_object_or_404(Service, id=service_id)

    if request.method == 'POST':
        form = ServiceFeatureForm(request.POST)
        if form.is_valid():
            feature = form.save(commit=False)
            feature.service = service
            feature.save()
            messages.success(request, f'Feature "{feature.title}" added successfully to "{service.name}".')
            return redirect('client_portal:admin_edit_service', service_id=service.id)
    else:
        form = ServiceFeatureForm(initial={'service': service})

    return render(request, 'admin/admin_add_feature.html', {
        'form': form,
        'service': service,
        'is_admin': True
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_edit_feature(request, feature_id):
    """
    Edit a service feature
    """
    feature = get_object_or_404(ServiceFeature, id=feature_id)
    service = feature.service

    if request.method == 'POST':
        form = ServiceFeatureForm(request.POST, instance=feature)
        if form.is_valid():
            form.save()
            messages.success(request, f'Feature "{feature.title}" updated successfully.')
            return redirect('client_portal:admin_edit_service', service_id=service.id)
    else:
        form = ServiceFeatureForm(instance=feature)

    return render(request, 'admin/admin_edit_feature.html', {
        'form': form,
        'feature': feature,
        'service': service,
        'is_admin': True
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_delete_feature(request, feature_id):
    """
    Delete a service feature
    """
    feature = get_object_or_404(ServiceFeature, id=feature_id)
    service = feature.service

    if request.method == 'POST':
        feature_title = feature.title
        feature.delete()
        messages.success(request, f'Feature "{feature_title}" deleted successfully.')
        return redirect('client_portal:admin_edit_service', service_id=service.id)

    return render(request, 'admin/admin_delete_feature.html', {
        'feature': feature,
        'service': service,
        'is_admin': True
    })
@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_add_service(request):
    """
    Add a new service
    """
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save()
            messages.success(request, f'Service "{service.name}" created successfully.')
            return redirect('client_portal:admin_services')
    else:
        form = ServiceForm()

    return render(request, 'admin/admin_add_service.html', {
        'form': form,
        'is_admin': True
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_edit_service(request, service_id):
    """
    Edit an existing service
    """
    service = get_object_or_404(Service, id=service_id)

    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, f'Service "{service.name}" updated successfully.')
            return redirect('client_portal:admin_services')
    else:
        form = ServiceForm(instance=service)

    return render(request, 'admin/admin_edit_service.html', {
        'form': form,
        'service': service,
        'is_admin': True
    })


@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_delete_service(request, service_id):
    """
    Delete a service
    """
    service = get_object_or_404(Service, id=service_id)

    if request.method == 'POST':
        service_name = service.name
        service.delete()
        messages.success(request, f'Service "{service_name}" deleted successfully.')
        return redirect('client_portal:admin_services')

    return render(request, 'admin/admin_delete_service.html', {
        'service': service,
        'is_admin': True
    })

# Admin dashboard view - using the default admin site now
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    # Summary counts
    client_count = Client.objects.count()
    active_clients = Client.objects.filter(is_active=True).count()
    total_projects = Project.objects.count()

    # Financial data
    total_invoiced = Invoice.objects.aggregate(Sum('total'))['total__sum'] or 0
    total_paid = Payment.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    total_due = total_invoiced - total_paid

    # Recent activity
    recent_payments = Payment.objects.order_by('-payment_date')[:10]
    recent_invoices = Invoice.objects.order_by('-issue_date')[:10]

    # Projects by status
    projects_by_status = Project.objects.values('status').annotate(count=Count('id'))

    # Overdue invoices
    overdue_invoices = Invoice.objects.filter(status='overdue')

    return render(request, 'admin/dashboard.html', {
        'client_count': client_count,
        'active_clients': active_clients,
        'total_projects': total_projects,
        'total_invoiced': total_invoiced,
        'total_paid': total_paid,
        'total_due': total_due,
        'recent_payments': recent_payments,
        'recent_invoices': recent_invoices,
        'projects_by_status': projects_by_status,
        'overdue_invoices': overdue_invoices,
    })
def is_admin_user(user):
    return user.is_staff or user.is_superuser
