
import invoice
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views import View
from django.http import HttpResponse
from openpyxl import Workbook
from datetime import datetime
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.db.models import Sum, Q, Count
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST

from services.models import Service
from . import models
from .models import Payment
from .email_utils import send_payment_receipt
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test

from .models import Client, Project, ProjectTask, ProjectUpdate, ProjectFile, Invoice, InvoiceItem, Payment, Message
from .forms import (
    ClientRegistrationForm, ClientLoginForm, ClientProfileForm,
    ProjectForm, TaskForm, MessageForm, PaymentForm
)

import datetime
import json
import uuid
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from services.forms import ServiceForm, ServiceFeatureForm
from services.models import ServiceFeature
from services.forms import ServiceFeatureForm


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
        'services_by_type': services.values('service_type').annotate(count=models.Count('id'))
    }
    return render(request, 'admin/admin_services.html', context)


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


# Helper function to check if user is admin
def is_admin_user(user):
    return user.is_staff or user.is_superuser


# Helper function to safely get client or handle admin
def get_client_or_none(user):
    """Safely get client profile or return None"""
    if is_admin_user(user):
        return None

    try:
        return user.client_profile
    except:
        return None


def client_login(request):
    """Handle client login"""
    if request.user.is_authenticated:
        # If user is already logged in, redirect to dashboard
        # Admins can access the dashboard too
        return redirect('client_portal:dashboard')

    if request.method == 'POST':
        form = ClientLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                # If user is admin, allow login directly
                if is_admin_user(user):
                    login(request, user)
                    return redirect('client_portal:dashboard')

                # For regular users, check if they have a client profile
                try:
                    client = user.client_profile
                    if client.is_active:
                        login(request, user)
                        return redirect('client_portal:dashboard')
                    else:
                        messages.error(request, 'Your account is inactive. Please contact support.')
                except:
                    messages.error(request, 'You do not have a client profile. Please register or contact support.')
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = ClientLoginForm()

    return render(request, 'client_portal/login.html', {'form': form})


def client_register(request):
    """Handle client registration"""
    if request.user.is_authenticated:
        return redirect('client_portal:dashboard')

    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            # Create user account
            user = form.save()

            # Create client profile
            client = Client.objects.create(
                user=user,
                company_name=form.cleaned_data.get('company_name', ''),
                phone=form.cleaned_data.get('phone', ''),
                address=form.cleaned_data.get('address', '')
            )

            # Log user in
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to the client portal.')
            return redirect('client_portal:dashboard')
    else:
        form = ClientRegistrationForm()

    return render(request, 'client_portal/register.html', {'form': form})


@login_required
def client_logout(request):
    """Handle client logout"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('client_portal:login')


@login_required
def dashboard(request):
    """Client dashboard view - Modified to handle admins"""
    # Set default admin flag
    is_admin = is_admin_user(request.user)

    # For admin users, show all data
    if is_admin:
        # Get all recent projects
        recent_projects = Project.objects.all().order_by('-updated_at')[:5]

        # Get all recent invoices
        recent_invoices = Invoice.objects.all().order_by('-issue_date')[:5]

        # Get all unread messages from clients
        unread_messages = Message.objects.filter(is_read=False, is_from_client=True).count()

        # Get financial summary for all clients
        total_invoiced = Invoice.objects.aggregate(Sum('total'))['total__sum'] or 0
        total_paid = Payment.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        balance_due = total_invoiced - total_paid

        # Calculate project statistics for all
        total_projects = Project.objects.count()
        active_projects = Project.objects.filter(status__in=['planning', 'in_progress']).count()
        completed_projects = Project.objects.filter(status='completed').count()

        # Count of clients
        total_clients = Client.objects.count()
        active_clients = Client.objects.filter(is_active=True).count()

        context = {
            'is_admin': True,
            'recent_projects': recent_projects,
            'recent_invoices': recent_invoices,
            'unread_messages': unread_messages,
            'total_invoiced': total_invoiced,
            'total_paid': total_paid,
            'balance_due': balance_due,
            'total_projects': total_projects,
            'active_projects': active_projects,
            'completed_projects': completed_projects,
            'total_clients': total_clients,
            'active_clients': active_clients,
        }

        return render(request, 'client_portal/dashboard.html', context)

    # Regular client user - get specific client data
    try:
        client = request.user.client_profile
    except:
        messages.error(request, 'You do not have a client profile.')
        logout(request)
        return redirect('client_portal:login')

    # Get client-specific data (original logic)
    recent_projects = client.projects.all().order_by('-updated_at')[:5]
    recent_invoices = client.invoices.all().order_by('-issue_date')[:5]
    unread_messages = client.messages.filter(is_read=False, is_from_client=False).count()
    total_invoiced = client.invoices.aggregate(Sum('total'))['total__sum'] or 0
    total_paid = Payment.objects.filter(invoice__client=client).aggregate(Sum('amount'))['amount__sum'] or 0
    total_projects = client.projects.count()
    active_projects = client.projects.filter(status__in=['planning', 'in_progress']).count()
    completed_projects = client.projects.filter(status='completed').count()

    context = {
        'is_admin': False,
        'client': client,
        'recent_projects': recent_projects,
        'recent_invoices': recent_invoices,
        'unread_messages': unread_messages,
        'total_invoiced': total_invoiced,
        'total_paid': total_paid,
        'balance_due': total_invoiced - total_paid,
        'total_projects': total_projects,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
    }

    return render(request, 'client_portal/dashboard.html', context)
@login_required
def profile(request):
    """Client profile view and edit"""
    # For admin users, redirect to the admin site
    if is_admin_user(request.user):
        messages.info(request, 'Admins use the Django admin interface to manage profiles.')
        return redirect('/admin/client_portal/client/')

    # Try to get or create a client profile
    try:
        client, created = Client.objects.get_or_create(
            user=request.user,
            defaults={
                'company_name': '',
                'phone': '',
                'address': ''
            }
        )
    except Exception as e:
        messages.error(request, f'Error accessing profile: {str(e)}')
        return redirect('client_portal:login')

    if request.method == 'POST':
        form = ClientProfileForm(request.POST, request.FILES, instance=client)
        if form.is_valid():
            # Update user information
            user = client.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']
            user.save()

            # Update client profile
            form.save()

            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('client_portal:profile')
    else:
        initial_data = {
            'first_name': client.user.first_name,
            'last_name': client.user.last_name,
            'email': client.user.email,
        }
        form = ClientProfileForm(instance=client, initial=initial_data)

    return render(request, 'client_portal/client_profile.html', {'form': form, 'client': client})




# Update class-based views to handle admin users
class AdminAwareLoginRequiredMixin(LoginRequiredMixin):
    """Mixin that allows admin users to access views that normally check for client profile"""

    def dispatch(self, request, *args, **kwargs):
        if is_admin_user(request.user):
            return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)


class ProjectListView(AdminAwareLoginRequiredMixin, ListView):
    """List all client projects"""
    model = Project
    template_name = 'client_portal/projects.html'
    context_object_name = 'projects'

    def get_queryset(self):
        # For admin users, show all projects
        if is_admin_user(self.request.user):
            return Project.objects.all().order_by('-updated_at')

        # For regular users, show only their projects
        try:
            client = self.request.user.client_profile
            return Project.objects.filter(client=client).order_by('-updated_at')
        except:
            return Project.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin'] = is_admin_user(self.request.user)
        return context


class ProjectDetailView(AdminAwareLoginRequiredMixin, DetailView):
    """Show project details"""
    model = Project
    template_name = 'client_portal/project_detail.html'
    context_object_name = 'project'

    def get_queryset(self):
        # For admin users, show all projects
        if is_admin_user(self.request.user):
            return Project.objects.all()

        # For regular users, show only their projects
        try:
            client = self.request.user.client_profile
            return Project.objects.filter(client=client)
        except:
            return Project.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add tasks, updates, and files
        context['tasks'] = self.object.tasks.all()
        context['updates'] = self.object.updates.all()
        context['files'] = self.object.files.all()

        # Add invoices related to the project
        context['invoices'] = self.object.invoices.all()

        # Add admin flag
        context['is_admin'] = is_admin_user(self.request.user)

        return context


class InvoiceListView(AdminAwareLoginRequiredMixin, ListView):
    """List all client invoices"""
    model = Invoice
    template_name = 'client_portal/invoices.html'
    context_object_name = 'invoices'

    def get_queryset(self):
        # For admin users, show all invoices
        if is_admin_user(self.request.user):
            return Invoice.objects.all().order_by('-issue_date')

        # For regular users, show only their invoices
        try:
            client = self.request.user.client_profile
            return Invoice.objects.filter(client=client).order_by('-issue_date')
        except:
            return Invoice.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin'] = is_admin_user(self.request.user)

        # For admin users, calculate totals for all clients
        if is_admin_user(self.request.user):
            total_invoiced = Invoice.objects.aggregate(Sum('total'))['total__sum'] or 0
            total_paid = Payment.objects.aggregate(Sum('amount'))['amount__sum'] or 0
            pending_invoices_count = Invoice.objects.filter(status__in=['sent', 'overdue']).count()
        else:
            # For regular users, calculate totals for just their invoices
            try:
                client = self.request.user.client_profile
                total_invoiced = client.invoices.aggregate(Sum('total'))['total__sum'] or 0
                total_paid = Payment.objects.filter(invoice__client=client).aggregate(Sum('amount'))['amount__sum'] or 0
                pending_invoices_count = client.invoices.filter(status__in=['sent', 'overdue']).count()
            except:
                total_invoiced = 0
                total_paid = 0
                pending_invoices_count = 0

        context['pending_invoices_count'] = pending_invoices_count
        context['total_invoiced'] = total_invoiced
        context['total_paid'] = total_paid
        context['balance_due'] = total_invoiced - total_paid

        return context


class InvoiceDetailView(AdminAwareLoginRequiredMixin, DetailView):
    """Show invoice details"""
    model = Invoice
    template_name = 'client_portal/invoice_detail.html'
    context_object_name = 'invoice'

    def get_queryset(self):
        # For admin users, show all invoices
        if is_admin_user(self.request.user):
            return Invoice.objects.all()

        # For regular users, show only their invoices
        try:
            client = self.request.user.client_profile
            return Invoice.objects.filter(client=client)
        except:
            return Invoice.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add invoice items and payments
        context['items'] = self.object.items.all()
        context['payments'] = self.object.payments.all()

        # Add admin flag
        context['is_admin'] = is_admin_user(self.request.user)

        # Add payment form if invoice is not fully paid
        if not self.object.is_fully_paid and self.object.status != 'cancelled':
            context['payment_form'] = PaymentForm(initial={'amount': self.object.balance_due})

        return context


@login_required
def make_payment(request, invoice_id):
    """Handle invoice payment"""
    # For admin users, get any invoice
    if is_admin_user(request.user):
        invoice = get_object_or_404(Invoice, id=invoice_id)
    else:
        # For regular clients, get only their invoice
        invoice = get_object_or_404(Invoice, id=invoice_id, client=request.user.client_profile)

    if invoice.is_fully_paid or invoice.status == 'cancelled':
        messages.error(request, 'This invoice is already paid or cancelled.')
        return redirect('client_portal:invoice_detail', pk=invoice.id)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']
            amount = form.cleaned_data['amount']

            # For admin users, process payment directly
            if is_admin_user(request.user):
                transaction_id = f"ADMIN-{uuid.uuid4().hex[:8].upper()}"
                payment = Payment.objects.create(
                    invoice=invoice,
                    amount=amount,
                    payment_date=timezone.now().date(),
                    payment_method=payment_method,
                    transaction_id=transaction_id,
                    notes=f"Payment recorded by admin user"
                )

                messages.success(request, f'Payment of ${amount} recorded successfully.')

                # If this payment completes the invoice, update status
                if invoice.balance_due <= 0:
                    invoice.status = 'paid'
                    invoice.save()

                return redirect('client_portal:invoice_detail', pk=invoice.id)

            # Regular client payment process
            if payment_method == 'paypal':
                # Redirect to PayPal processing
                return redirect('client_portal:process_paypal', invoice_id=invoice.id, amount=amount)
            elif payment_method == 'credit_card':
                # Redirect to credit card processing
                return redirect('client_portal:process_credit_card', invoice_id=invoice.id, amount=amount)
            elif payment_method == 'mpesa':
                # Redirect to M-Pesa processing
                return redirect('client_portal:process_mpesa', invoice_id=invoice.id, amount=amount)
            else:
                # For other methods, create payment record and mark as pending
                transaction_id = f"MANUAL-{uuid.uuid4().hex[:8].upper()}"
                payment = Payment.objects.create(
                    invoice=invoice,
                    amount=amount,
                    payment_date=timezone.now().date(),
                    payment_method=payment_method,
                    transaction_id=transaction_id,
                    notes=f"Manual payment via {payment_method}"
                )

                messages.success(request,
                                 f'Payment of ${amount} recorded successfully. It will be reviewed by our team.')

                # If this payment completes the invoice, update status
                if invoice.balance_due <= 0:
                    invoice.status = 'paid'
                    invoice.save()

                return redirect('client_portal:invoice_detail', pk=invoice.id)
    else:
        form = PaymentForm(initial={'amount': invoice.balance_due})

    return render(request, 'client_portal/make_payment.html', {
        'form': form,
        'invoice': invoice,
        'is_admin': is_admin_user(request.user)
    })


@login_required
def process_paypal(request, invoice_id, amount):
    """Process PayPal payment"""
    # For admin users, get any invoice
    if is_admin_user(request.user):
        invoice = get_object_or_404(Invoice, id=invoice_id)
    else:
        # For regular clients, get only their invoice
        invoice = get_object_or_404(Invoice, id=invoice_id, client=request.user.client_profile)

    # In a real implementation, this would integrate with PayPal API
    # For now, we'll just simulate the payment process

    return render(request, 'client_portal/payment_paypal.html', {
        'invoice': invoice,
        'amount': amount,
        'is_admin': is_admin_user(request.user)
    })


@login_required
def process_credit_card(request, invoice_id, amount):
    """Process credit card payment"""
    # For admin users, get any invoice
    if is_admin_user(request.user):
        invoice = get_object_or_404(Invoice, id=invoice_id)
    else:
        # For regular clients, get only their invoice
        invoice = get_object_or_404(Invoice, id=invoice_id, client=request.user.client_profile)

    # In a real implementation, this would integrate with a payment gateway API
    # For now, we'll just simulate the payment process

    return render(request, 'client_portal/payment_credit_card.html', {
        'invoice': invoice,
        'amount': amount,
        'is_admin': is_admin_user(request.user)
    })


@login_required
def process_mpesa(request, invoice_id, amount):
    """Process M-Pesa payment"""
    # For admin users, get any invoice
    if is_admin_user(request.user):
        invoice = get_object_or_404(Invoice, id=invoice_id)
    else:
        # For regular clients, get only their invoice
        invoice = get_object_or_404(Invoice, id=invoice_id, client=request.user.client_profile)

    # In a real implementation, this would integrate with M-Pesa API
    # For now, we'll just simulate the payment process

    return render(request, 'client_portal/payment_mpesa.html', {
        'invoice': invoice,
        'amount': amount,
        'is_admin': is_admin_user(request.user)
    })


@login_required
def payment_success(request, invoice_id, payment_method, transaction_id):
    """Handle successful payment"""
    # For admin users, get any invoice
    if is_admin_user(request.user):
        invoice = get_object_or_404(Invoice, id=invoice_id)
    else:
        # For regular clients, get only their invoice
        invoice = get_object_or_404(Invoice, id=invoice_id, client=request.user.client_profile)

    # Get amount from request or session
    amount = request.GET.get('amount', 0)

    # Create payment record
    payment = Payment.objects.create(
        invoice=invoice,
        amount=amount,
        payment_date=timezone.now().date(),
        payment_method=payment_method,
        transaction_id=transaction_id,
        notes=f"Online payment via {payment_method}" +
              (" (recorded by admin)" if is_admin_user(request.user) else "")
    )

    # Update invoice status if fully paid
    if invoice.balance_due <= 0:
        invoice.status = 'paid'
        invoice.save()

    messages.success(request, f'Payment of ${amount} processed successfully!')

    return redirect('client_portal:invoice_detail', pk=invoice.id)


@login_required
def print_receipt(request, payment_id):
    """Generate a printable receipt for a payment"""
    # For admin users, get any payment
    if is_admin_user(request.user):
        payment = get_object_or_404(Payment, id=payment_id)
        client = payment.invoice.client
    else:
        # For regular clients, get only their payment
        try:
            client = request.user.client_profile
            payment = Payment.objects.get(id=payment_id, invoice__client=client)
        except:
            messages.error(request, 'Payment not found.')
            return redirect('client_portal:invoices')

    return render(request, 'client_portal/print_receipt.html', {
        'payment': payment,
        'invoice': payment.invoice,
        'client': client,
        'is_admin': is_admin_user(request.user)
    })


@login_required
def balance_due(request):
    """Show client balance and payment options"""
    # For admin users, show overall balance
    if is_admin_user(request.user):
        # Get all unpaid invoices
        unpaid_invoices = Invoice.objects.filter(status__in=['sent', 'overdue']).order_by('due_date')

        # Check if any overdue invoices exist
        has_overdue_invoices = Invoice.objects.filter(status='overdue').exists()

        # Calculate totals for all clients
        total_invoiced = Invoice.objects.aggregate(Sum('total'))['total__sum'] or 0
        total_paid = Payment.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        balance_due = total_invoiced - total_paid

        # Get client balances
        client_balances = []
        for client in Client.objects.filter(is_active=True):
            client_invoiced = client.invoices.aggregate(Sum('total'))['total__sum'] or 0
            client_paid = Payment.objects.filter(invoice__client=client).aggregate(Sum('amount'))['amount__sum'] or 0
            client_balance = client_invoiced - client_paid

            if client_balance > 0:
                client_balances.append({
                    'client': client,
                    'balance': client_balance,
                    'has_overdue': client.invoices.filter(status='overdue').exists()
                })

        return render(request, 'client_portal/balance_due.html', {
            'is_admin': True,
            'unpaid_invoices': unpaid_invoices,
            'has_overdue_invoices': has_overdue_invoices,
            'total_invoiced': total_invoiced,
            'total_paid': total_paid,
            'balance_due': balance_due,
            'client_balances': client_balances
        })

    # Regular client view
    try:
        client = request.user.client_profile
    except:
        messages.error(request, 'You do not have a client profile.')
        logout(request)
        return redirect('client_portal:login')

    # Get unpaid invoices for this client
    unpaid_invoices = client.invoices.filter(status__in=['sent', 'overdue']).order_by('due_date')

    # Check if any overdue invoices exist
    has_overdue_invoices = client.invoices.filter(status='overdue').exists()

    # Calculate totals
    total_invoiced = client.invoices.aggregate(Sum('total'))['total__sum'] or 0
    total_paid = Payment.objects.filter(invoice__client=client).aggregate(Sum('amount'))['amount__sum'] or 0
    balance_due = total_invoiced - total_paid

    return render(request, 'client_portal/balance_due.html', {
        'is_admin': False,
        'client': client,
        'unpaid_invoices': unpaid_invoices,
        'has_overdue_invoices': has_overdue_invoices,
        'total_invoiced': total_invoiced,
        'total_paid': total_paid,
        'balance_due': balance_due
    })


class MessageListView(AdminAwareLoginRequiredMixin, ListView):
    """List all client messages"""
    model = Message
    template_name = 'client_portal/messages.html'
    context_object_name = 'messages_list'

    def get_queryset(self):
        # For admin users, show all messages
        if is_admin_user(self.request.user):
            return Message.objects.all().order_by('-created_at')

        # For regular users, show only their messages
        try:
            client = self.request.user.client_profile
            return Message.objects.filter(client=client).order_by('-created_at')
        except:
            return Message.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = MessageForm()
        context['is_admin'] = is_admin_user(self.request.user)

        # For admin users, add list of clients for messaging
        if is_admin_user(self.request.user):
            context['clients'] = Client.objects.filter(is_active=True)

        return context


@login_required
def send_message(request):
    """Send a message from the client or admin"""
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            # For admin users, allow specifying a client
            if is_admin_user(request.user):
                client_id = request.POST.get('client_id')
                if client_id:
                    try:
                        client = Client.objects.get(id=client_id)
                        message = form.save(commit=False)
                        message.client = client
                        message.is_from_client = False  # Message from admin to client
                        message.is_read = False
                        message.save()
                        messages.success(request, f'Your message has been sent to {client.full_name}.')
                    except Client.DoesNotExist:
                        messages.error(request, 'Client not found. Please try again.')
                else:
                    messages.error(request, 'Please select a client to send a message to.')
            else:
                # Regular client sending a message
                try:
                    client = request.user.client_profile
                    message = form.save(commit=False)
                    message.client = client
                    message.is_from_client = True
                    message.is_read = False
                    message.save()
                    messages.success(request, 'Your message has been sent successfully.')
                except:
                    messages.error(request, 'Failed to send message. Please try again.')
        else:
            messages.error(request, 'Please correct the errors in the form.')

    return redirect('client_portal:messages')




@login_required
def mark_message_read(request, message_id):
    """Mark a message as read"""
    # For admin users, can mark any message
    if is_admin_user(request.user):
        message = get_object_or_404(Message, id=message_id)
        if message.is_from_client:  # Only mark messages from clients as read
            message.is_read = True
            message.save()
    else:
        # Regular client marking a message
        try:
            client = request.user.client_profile
            message = Message.objects.get(id=message_id, client=client)
            if not message.is_from_client:  # Only mark messages from staff as read
                message.is_read = True
                message.save()
        except:
            pass

    if request.is_ajax():
        return JsonResponse({'status': 'success'})
    else:
        return redirect('client_portal:messages')





@login_required
def payment_success(request, invoice_id, payment_method, transaction_id):
    """Handle successful payment and send email receipt"""
    # Original code for creating the payment
    if request.user.is_staff or request.user.is_superuser:
        invoice = get_object_or_404(Invoice, id=invoice_id)
    else:
        invoice = get_object_or_404(Invoice, id=invoice_id, client__user=request.user)

    # Get amount from request or session
    amount = request.GET.get('amount', 0)

    # Create payment record
    payment = Payment.objects.create(
        invoice=invoice,
        amount=amount,
        payment_date=timezone.now().date(),
        payment_method=payment_method,
        transaction_id=transaction_id,
        notes=f"Online payment via {payment_method}"
    )

    # Update invoice status if fully paid
    if invoice.balance_due <= 0:
        invoice.status = 'paid'
        invoice.save()

    # Send payment receipt via email
    try:
        send_payment_receipt(payment)
    except Exception as e:
        # Log the error but don't disrupt user experience
        print(f"Failed to send payment receipt email: {str(e)}")

    messages.success(request, f'Payment of ${amount} processed successfully! Thank you for your payment.')

    return redirect('client_portal:invoice_detail', pk=invoice.id)




def client_register(request):
    """Handle client registration and send welcome email"""
    if request.user.is_authenticated:
        return redirect('client_portal:dashboard')

    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            # Create user account
            user = form.save()

            # Create client profile
            client = Client.objects.create(
                user=user,
                company_name=form.cleaned_data.get('company_name', ''),
                phone=form.cleaned_data.get('phone', ''),
                address=form.cleaned_data.get('address', '')
            )

            # Send welcome email
            try:
                from .email_utils import send_welcome_email
                send_welcome_email(user)
            except Exception as e:
                # Log the error but don't disrupt user experience
                print(f"Failed to send welcome email: {str(e)}")

            # Log user in
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to the client portal. Check your email for more information.')
            return redirect('client_portal:dashboard')
    else:
        form = ClientRegistrationForm()

    return render(request, 'client_portal/register.html', {'form': form})


@login_required
@user_passes_test(lambda u: u.is_staff)
def export_payments(request):
    # Create workbook and active sheet
    wb = Workbook()
    wb = Workbook()
    ws = wb.active
    ws.title = "Payment Records"

    # Add headers
    headers = ["Date", "Invoice #", "Client", "Amount", "Payment Method", "Transaction ID"]
    ws.append(headers)

    # Get all payments
    payments = Payment.objects.all().order_by('-payment_date')

    # Add data rows
    for payment in payments:
        ws.append([
            payment.payment_date,
            payment.invoice.invoice_number,
            payment.invoice.client.full_name,
            payment.amount,
            payment.get_payment_method_display(),
            payment.transaction_id or "N/A"
        ])

    # Prepare response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=payments_report_{datetime.now().strftime("%Y-%m-%d")}.xlsx'

    # Save workbook to response
    wb.save(response)
    return response


@login_required
@user_passes_test(lambda u: u.is_staff)
def financial_summary(request):
    # Date filtering
    end_date = datetime.now().date()
    start_date = end_date.replace(day=1)  # First day of current month

    if request.GET.get('start_date'):
        try:
            start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
        except ValueError:
            pass

    if request.GET.get('end_date'):
        try:
            end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
        except ValueError:
            pass

    # Get payments in date range
    payments = Payment.objects.filter(payment_date__range=[start_date, end_date])

    # Aggregate by payment method
    payment_by_method = payments.values('payment_method').annotate(
        total=Sum('amount')
    ).order_by('-total')

    # Prepare data for export
    export_url = f'{reverse("admin:export_financial_summary")}?start_date={start_date}&end_date={end_date}'

    return render(request, 'admin_financial_summary.html', {
        'start_date': start_date,
        'end_date': end_date,
        'total_received': payments.aggregate(Sum('amount'))['amount__sum'] or 0,
        'payment_by_method': payment_by_method,
        'export_url': export_url,
    })


# New admin functions for client portal

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_clients(request):
    """View all clients for admin"""
    clients = Client.objects.all().order_by('-created_at')
    active_clients_count = Client.objects.filter(is_active=True).count()

    # Calculate client statistics
    for client in clients:
        client.active_projects = client.projects.filter(status__in=['planning', 'in_progress']).count()
        client.total_invoiced = client.invoices.aggregate(Sum('total'))['total__sum'] or 0
        client.total_paid = Payment.objects.filter(invoice__client=client).aggregate(Sum('amount'))['amount__sum'] or 0
        client.balance = client.total_invoiced - client.total_paid

    return render(request, 'admin_clients.html', {
        'clients': clients,
        'active_clients_count': active_clients_count,
        'is_admin': True
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_client_detail(request, client_id):
    """View client details for admin"""
    client = get_object_or_404(Client, id=client_id)

    # Get client projects
    projects = client.projects.all().order_by('-updated_at')

    # Get client invoices
    invoices = client.invoices.all().order_by('-issue_date')

    # Get financial summary
    total_invoiced = client.invoices.aggregate(Sum('total'))['total__sum'] or 0
    total_paid = Payment.objects.filter(invoice__client=client).aggregate(Sum('amount'))['amount__sum'] or 0
    balance_due = total_invoiced - total_paid

    # Get client messages
    messages_list = client.messages.all().order_by('-created_at')

    return render(request, 'admin_client_detail.html', {
        'client': client,
        'projects': projects,
        'invoices': invoices,
        'total_invoiced': total_invoiced,
        'total_paid': total_paid,
        'balance_due': balance_due,
        'messages': messages_list,
        'is_admin': True
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_create_invoice(request):
    """Create a new invoice as admin"""
    if request.method == 'POST':
        # Process form submission
        client_id = request.POST.get('client')
        try:
            client = Client.objects.get(id=client_id)

            # Create invoice
            invoice = Invoice.objects.create(
                client=client,
                project_id=request.POST.get('project') or None,
                invoice_number=request.POST.get('invoice_number'),
                status='draft',
                issue_date=datetime.strptime(request.POST.get('issue_date'), '%Y-%m-%d').date(),
                due_date=datetime.strptime(request.POST.get('due_date'), '%Y-%m-%d').date(),
                subtotal=float(request.POST.get('subtotal', 0)),
                tax_rate=float(request.POST.get('tax_rate', 0)),
                discount=float(request.POST.get('discount', 0)),
                notes=request.POST.get('notes', '')
            )

            # Calculate total
            tax_amount = (invoice.subtotal * invoice.tax_rate) / 100
            invoice.total = invoice.subtotal + tax_amount - invoice.discount
            invoice.save()

            # Create invoice items if provided
            item_descriptions = request.POST.getlist('item_description')
            item_quantities = request.POST.getlist('item_quantity')
            item_prices = request.POST.getlist('item_price')

            for i in range(len(item_descriptions)):
                if item_descriptions[i] and item_quantities[i] and item_prices[i]:
                    InvoiceItem.objects.create(
                        invoice=invoice,
                        description=item_descriptions[i],
                        quantity=float(item_quantities[i]),
                        unit_price=float(item_prices[i]),
                        amount=float(item_quantities[i]) * float(item_prices[i])
                    )

            messages.success(request, f'Invoice {invoice.invoice_number} created successfully.')
            return redirect('client_portal:invoice_detail', pk=invoice.id)

        except (Client.DoesNotExist, ValueError) as e:
            messages.error(request, f'Error creating invoice: {str(e)}')

    # Display the form
    clients = Client.objects.filter(is_active=True)
    projects = Project.objects.filter(status__in=['planning', 'in_progress'])

    # Generate next invoice number
    last_invoice = Invoice.objects.order_by('-id').first()
    next_number = "INV-001"
    if last_invoice:
        last_num = last_invoice.invoice_number
        if last_num.startswith("INV-"):
            num = int(last_num.split("-")[1])
            next_number = f"INV-{num + 1:03d}"

    return render(request, 'admin_create_invoice.html', {
        'clients': clients,
        'projects': projects,
        'next_invoice_number': next_number,
        'today': datetime.now().date(),
        'due_date': (datetime.now() + datetime.timedelta(days=30)).date(),
        'is_admin': True
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_create_project(request):
    """Create a new project as admin"""
    if request.method == 'POST':
        # Process form submission
        client_id = request.POST.get('client')
        try:
            client = Client.objects.get(id=client_id)

            # Create project
            project = Project.objects.create(
                client=client,
                title=request.POST.get('title'),
                description=request.POST.get('description'),
                status=request.POST.get('status', 'planning'),
                start_date=datetime.strptime(request.POST.get('start_date'), '%Y-%m-%d').date(),
                budget=float(request.POST.get('budget', 0))
            )

            # Set end date if provided
            end_date = request.POST.get('end_date')
            if end_date:
                project.end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                project.save()

            messages.success(request, f'Project "{project.title}" created successfully.')
            return redirect('client_portal:project_detail', pk=project.id)

        except (Client.DoesNotExist, ValueError) as e:
            messages.error(request, f'Error creating project: {str(e)}')

    # Display the form
    clients = Client.objects.filter(is_active=True)

    return render(request, 'admin/admin_create_project.html', {
        'clients': clients,
        'statuses': Project.STATUS_CHOICES,
        'today': datetime.now().date(),
        'is_admin': True
    })


@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_record_payment(request):
    """Record a payment for any invoice as admin"""
    if request.method == 'POST':
        invoice_id = request.POST.get('invoice')
        try:
            invoice = Invoice.objects.get(id=invoice_id)

            # Create payment
            amount = float(request.POST.get('amount', 0))
            payment_method = request.POST.get('payment_method')
            payment_date = datetime.strptime(request.POST.get('payment_date'), '%Y-%m-%d').date()
            transaction_id = request.POST.get('transaction_id', f"ADMIN-{uuid.uuid4().hex[:8].upper()}")
            notes = request.POST.get('notes', 'Payment recorded by admin')

            payment = Payment.objects.create(
                invoice=invoice,
                amount=amount,
                payment_date=payment_date,
                payment_method=payment_method,
                transaction_id=transaction_id,
                notes=notes
            )

            # Update invoice status if fully paid
            if invoice.balance_due <= 0:
                invoice.status = 'paid'
                invoice.save()

            messages.success(request,
                             f'Payment of ${amount} recorded successfully for invoice {invoice.invoice_number}.')
            return redirect('client_portal:invoice_detail', pk=invoice.id)

        except (Invoice.DoesNotExist, ValueError) as e:
            messages.error(request, f'Error recording payment: {str(e)}')

    # Display the form
    invoices = Invoice.objects.filter(status__in=['sent', 'overdue']).order_by('-issue_date')

    return render(request, 'admin_record_payment.html', {
        'invoices': invoices,
        'payment_methods': Payment.PAYMENT_METHOD_CHOICES,
        'today': datetime.now().date(),
        'is_admin': True
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_financial_summary(request):
    """
    Provide a detailed financial summary for admin
    """
    # Calculate total financial metrics
    total_invoiced = Invoice.objects.aggregate(Sum('total'))['total__sum'] or 0
    total_paid = Payment.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    balance_due = total_invoiced - total_paid

    # Breakdown by payment method
    payment_methods = Payment.objects.values('payment_method').annotate(
        total_amount=Sum('amount'),
        transaction_count=Count('id')
    ).order_by('-total_amount')

    # Invoices by status
    invoice_status = Invoice.objects.values('status').annotate(
        total_amount=Sum('total'),
        count=Count('id')
    ).order_by('-total_amount')

    # Recent financial activities
    recent_payments = Payment.objects.order_by('-payment_date')[:10]
    recent_invoices = Invoice.objects.order_by('-issue_date')[:10]

    context = {
        'is_admin': True,
        'total_invoiced': total_invoiced,
        'total_paid': total_paid,
        'balance_due': balance_due,
        'payment_methods': payment_methods,
        'invoice_status': invoice_status,
        'recent_payments': recent_payments,
        'recent_invoices': recent_invoices,
    }

    return render(request, 'admin_financial_summary.html', context)


@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_add_client(request):
    """Add a new client from admin interface"""
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            # Create user account
            user = form.save()

            # Create client profile
            client = Client.objects.create(
                user=user,
                company_name=form.cleaned_data.get('company_name', ''),
                phone=form.cleaned_data.get('phone', ''),
                address=form.cleaned_data.get('address', '')
            )

            messages.success(request, f'Client {client.full_name} added successfully.')
            return redirect('client_portal:admin_clients')
    else:
        form = ClientRegistrationForm()

    return render(request, 'admin_add_client.html', {
        'form': form,
        'is_admin': True
    })

@login_required
def email_receipt(request, payment_id):
    """
    Email a receipt to the client or specified email
    """
    # Get the payment (either as admin or as the client who owns it)
    if request.user.is_staff or request.user.is_superuser:
        payment = get_object_or_404(Payment, id=payment_id)
    else:
        # Regular user can only access their own payments
        payment = get_object_or_404(Payment, id=payment_id, invoice__client__user=request.user)

    # If it's a POST request, user is submitting the email form
    if request.method == 'POST':
        email = request.POST.get('email')
        additional_message = request.POST.get('message', None)

        try:
            # Send the receipt
            send_payment_receipt(payment, additional_message, email)

            # Return JSON response for AJAX or redirect for normal POST
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': f'Receipt sent to {email}'})
            else:
                messages.success(request, f'Receipt has been sent to {email}')
                return redirect('client_portal:print_receipt', payment_id=payment.id)

        except Exception as e:
            # Handle error
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            else:
                messages.error(request, f'Failed to send receipt: {str(e)}')
                return redirect('client_portal:print_receipt', payment_id=payment.id)

    # If it's not a POST request, redirect to the receipt page
    return redirect('client_portal:print_receipt', payment_id=payment.id)


def client_logout(request):
    """Handle logout for both client and admin users"""
    if request.user.is_staff:
        # Staff/Admin logout redirects to admin login
        logout(request)
        messages.success(request, 'Admin logged out successfully.')
        return redirect('admin:login')
    else:
        # Regular client logout
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('client_portal:login')
