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

from .models import Client, Project, ProjectTask, ProjectUpdate, ProjectFile, Invoice, InvoiceItem, Payment, Message
from .forms import (
    ClientRegistrationForm, ClientLoginForm, ClientProfileForm,
    ProjectForm, TaskForm, MessageForm, PaymentForm
)

import datetime
import json
import uuid


def client_login(request):
    """Handle client login"""
    if request.user.is_authenticated:
        return redirect('client_portal:dashboard')

    if request.method == 'POST':
        form = ClientLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                # Check if user has a client profile
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
    """Client dashboard view"""
    try:
        client = request.user.client_profile
    except:
        messages.error(request, 'You do not have a client profile.')
        logout(request)
        return redirect('client_portal:login')

    # Get recent projects
    recent_projects = client.projects.all().order_by('-updated_at')[:5]

    # Get recent invoices
    recent_invoices = client.invoices.all().order_by('-issue_date')[:5]

    # Get unread messages
    unread_messages = client.messages.filter(is_read=False, is_from_client=False).count()

    # Get financial summary
    total_invoiced = client.invoices.aggregate(Sum('total'))['total__sum'] or 0
    total_paid = Payment.objects.filter(invoice__client=client).aggregate(Sum('amount'))['amount__sum'] or 0

    # Calculate project statistics
    total_projects = client.projects.count()
    active_projects = client.projects.filter(status__in=['planning', 'in_progress']).count()
    completed_projects = client.projects.filter(status='completed').count()

    context = {
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
    try:
        client = request.user.client_profile
    except:
        messages.error(request, 'You do not have a client profile.')
        logout(request)
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

    return render(request, 'client_portal/profile.html', {'form': form, 'client': client})


class ProjectListView(LoginRequiredMixin, ListView):
    """List all client projects"""
    model = Project
    template_name = 'client_portal/projects.html'
    context_object_name = 'projects'

    def get_queryset(self):
        try:
            client = self.request.user.client_profile
            return Project.objects.filter(client=client).order_by('-updated_at')
        except:
            return Project.objects.none()


class ProjectDetailView(LoginRequiredMixin, DetailView):
    """Show project details"""
    model = Project
    template_name = 'client_portal/project_detail.html'
    context_object_name = 'project'

    def get_queryset(self):
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

        return context


class InvoiceListView(LoginRequiredMixin, ListView):
    """List all client invoices"""
    model = Invoice
    template_name = 'client_portal/invoices.html'
    context_object_name = 'invoices'

    def get_queryset(self):
        try:
            client = self.request.user.client_profile
            return Invoice.objects.filter(client=client).order_by('-issue_date')
        except:
            return Invoice.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Calculate totals
        client = self.request.user.client_profile
        total_invoiced = client.invoices.aggregate(Sum('total'))['total__sum'] or 0
        total_paid = Payment.objects.filter(invoice__client=client).aggregate(Sum('amount'))['amount__sum'] or 0
        pending_invoices_count = client.invoices.filter(status__in=['sent', 'overdue']).count()

        context['pending_invoices_count'] = pending_invoices_count

        context['total_invoiced'] = total_invoiced
        context['total_paid'] = total_paid
        context['balance_due'] = total_invoiced - total_paid

        return context


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    """Show invoice details"""
    model = Invoice
    template_name = 'client_portal/invoice_detail.html'
    context_object_name = 'invoice'

    def get_queryset(self):
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

        # Add payment form if invoice is not fully paid
        if not self.object.is_fully_paid and self.object.status != 'cancelled':
            context['payment_form'] = PaymentForm(initial={'amount': self.object.balance_due})

        return context


@login_required
def make_payment(request, invoice_id):
    """Handle invoice payment"""
    invoice = get_object_or_404(Invoice, id=invoice_id, client=request.user.client_profile)

    if invoice.is_fully_paid or invoice.status == 'cancelled':
        messages.error(request, 'This invoice is already paid or cancelled.')
        return redirect('client_portal:invoice_detail', pk=invoice.id)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data['payment_method']
            amount = form.cleaned_data['amount']

            # Process different payment methods
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
        'invoice': invoice
    })


@login_required
def process_paypal(request, invoice_id, amount):
    """Process PayPal payment"""
    invoice = get_object_or_404(Invoice, id=invoice_id, client=request.user.client_profile)

    # In a real implementation, this would integrate with PayPal API
    # For now, we'll just simulate the payment process

    return render(request, 'client_portal/payment_paypal.html', {
        'invoice': invoice,
        'amount': amount
    })


@login_required
def process_credit_card(request, invoice_id, amount):
    """Process credit card payment"""
    invoice = get_object_or_404(Invoice, id=invoice_id, client=request.user.client_profile)

    # In a real implementation, this would integrate with a payment gateway API
    # For now, we'll just simulate the payment process

    return render(request, 'client_portal/payment_credit_card.html', {
        'invoice': invoice,
        'amount': amount
    })


@login_required
def process_mpesa(request, invoice_id, amount):
    """Process M-Pesa payment"""
    invoice = get_object_or_404(Invoice, id=invoice_id, client=request.user.client_profile)

    # In a real implementation, this would integrate with M-Pesa API
    # For now, we'll just simulate the payment process

    return render(request, 'client_portal/payment_mpesa.html', {
        'invoice': invoice,
        'amount': amount
    })


@login_required
def payment_success(request, invoice_id, payment_method, transaction_id):
    """Handle successful payment"""
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
        notes=f"Online payment via {payment_method}"
    )

    # Update invoice status if fully paid
    if invoice.balance_due <= 0:
        invoice.status = 'paid'
        invoice.save()

    messages.success(request, f'Payment of ${amount} processed successfully! Thank you for your payment.')

    return redirect('client_portal:invoice_detail', pk=invoice.id)


@login_required
def print_receipt(request, payment_id):
    """Generate a printable receipt for a payment"""
    try:
        client = request.user.client_profile
        payment = Payment.objects.get(id=payment_id, invoice__client=client)
    except:
        messages.error(request, 'Payment not found.')
        return redirect('client_portal:invoices')

    return render(request, 'client_portal/print_receipt.html', {
        'payment': payment,
        'invoice': payment.invoice,
        'client': client
    })


@login_required
def balance_due(request):
    """Show client balance and payment options"""
    try:
        client = request.user.client_profile
    except:
        messages.error(request, 'You do not have a client profile.')
        logout(request)
        return redirect('client_portal:login')

    # Get unpaid invoices
    unpaid_invoices = client.invoices.filter(status__in=['sent', 'overdue']).order_by('due_date')

    # Check if any overdue invoices exist
    has_overdue_invoices = client.invoices.filter(status='overdue').exists()

    # Calculate totals
    total_invoiced = client.invoices.aggregate(Sum('total'))['total__sum'] or 0
    total_paid = Payment.objects.filter(invoice__client=client).aggregate(Sum('amount'))['amount__sum'] or 0
    balance_due = total_invoiced - total_paid

    return render(request, 'client_portal/balance_due.html', {
        'client': client,
        'unpaid_invoices': unpaid_invoices,
        'has_overdue_invoices': has_overdue_invoices,
        'total_invoiced': total_invoiced,
        'total_paid': total_paid,
        'balance_due': balance_due
    })


class MessageListView(LoginRequiredMixin, ListView):
    """List all client messages"""
    model = Message
    template_name = 'client_portal/messages.html'
    context_object_name = 'messages_list'

    def get_queryset(self):
        try:
            client = self.request.user.client_profile
            return Message.objects.filter(client=client).order_by('-created_at')
        except:
            return Message.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = MessageForm()
        return context


@login_required
def send_message(request):
    """Send a message from the client"""
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
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


# In views.py
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


@login_required
@user_passes_test(lambda u: u.is_staff)
def export_payments(request):
    # Create workbook and active sheet
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


# In views.py
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

    return render(request, 'admin/financial_summary.html', {
        'start_date': start_date,
        'end_date': end_date,
        'total_received': payments.aggregate(Sum('amount'))['amount__sum'] or 0,
        'payment_by_method': payment_by_method,
        'export_url': export_url,
    })