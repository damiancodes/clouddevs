# # email_utils.py
# # Place this file in your client_portal directory
#
# from django.conf import settings
# from django.core.mail import EmailMultiAlternatives
# from django.template.loader import render_to_string
# from django.utils.html import strip_tags
#
#
# def send_welcome_email(user):
#     """
#     Send a welcome email to newly registered users
#     """
#     subject = 'Welcome to CloudLink_Devs'
#     from_email = settings.DEFAULT_FROM_EMAIL
#     to_email = user.email
#
#     # Context for email template
#     context = {
#         'user': user,
#         'client': getattr(user, 'client_profile', None),
#         'login_url': f"{settings.SITE_URL}/client/login/"
#     }
#
#     # Render email templates
#     html_content = render_to_string('client_portal/emails/welcome_email.html', context)
#     text_content = strip_tags(html_content)  # Plain text version
#
#     # Create and send email
#     email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
#     email.attach_alternative(html_content, "text/html")
#     email.send()
#
#     return True
#
#
# def send_payment_receipt(payment, additional_message=None, to_email=None):
#     """
#     Send a payment receipt via email
#     """
#     invoice = payment.invoice
#     client = invoice.client
#
#     # Use provided email or fall back to client's email
#     recipient_email = to_email or client.user.email
#
#     subject = f'Payment Receipt - Invoice #{invoice.invoice_number}'
#     from_email = settings.DEFAULT_FROM_EMAIL
#
#     # Context for email template
#     context = {
#         'payment': payment,
#         'invoice': invoice,
#         'client': client,
#         'additional_message': additional_message,
#         'view_receipt_url': f"{settings.SITE_URL}/client/payment/receipt/{payment.id}/",
#         'view_invoice_url': f"{settings.SITE_URL}/client/invoices/{invoice.id}/"
#     }
#
#     # Render email templates
#     html_content = render_to_string('client_portal/emails/payment_receipt.html', context)
#     text_content = strip_tags(html_content)  # Plain text version
#
#     # Create and send email
#     email = EmailMultiAlternatives(subject, text_content, from_email, [recipient_email])
#     email.attach_alternative(html_content, "text/html")
#     email.send()
#
#     return True
#
#
# def send_invoice_created_notification(invoice):
#     """
#     Send an email notification when a new invoice is created
#     """
#     client = invoice.client
#
#     subject = f'New Invoice #{invoice.invoice_number} - CloudLink_Devs'
#     from_email = settings.DEFAULT_FROM_EMAIL
#     to_email = client.user.email
#
#     # Context for email template
#     context = {
#         'invoice': invoice,
#         'client': client,
#         'view_invoice_url': f"{settings.SITE_URL}/client/invoices/{invoice.id}/"
#     }
#
#     # Render email templates
#     html_content = render_to_string('client_portal/emails/invoice_created.html', context)
#     text_content = strip_tags(html_content)  # Plain text version
#
#     # Create and send email
#     email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
#     email.attach_alternative(html_content, "text/html")
#     email.send()
#
#     return True
#
#
# def send_payment_reminder(invoice):
#     """
#     Send a payment reminder for upcoming or overdue invoices
#     """
#     client = invoice.client
#
#     if invoice.status == 'overdue':
#         subject = f'OVERDUE: Invoice #{invoice.invoice_number} - Payment Required'
#     else:
#         subject = f'Reminder: Invoice #{invoice.invoice_number} Due Soon'
#
#     from_email = settings.DEFAULT_FROM_EMAIL
#     to_email = client.user.email
#
#     # Context for email template
#     context = {
#         'invoice': invoice,
#         'client': client,
#         'is_overdue': invoice.status == 'overdue',
#         'view_invoice_url': f"{settings.SITE_URL}/client/invoices/{invoice.id}/",
#         'payment_url': f"{settings.SITE_URL}/client/invoices/{invoice.id}/payment/"
#     }
#
#     # Render email templates
#     html_content = render_to_string('client_portal/emails/payment_reminder.html', context)
#     text_content = strip_tags(html_content)  # Plain text version
#
#     # Create and send email
#     email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
#     email.attach_alternative(html_content, "text/html")
#     email.send()
#
#     return True
#
# def is_admin_user(user):
#     """Helper function to check if user is admin"""
#     return user.is_staff or user.is_superuser









# email_utils.py
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.exceptions import ObjectDoesNotExist

def is_admin_user(user):
    """Helper function to check if user is admin"""
    return user.is_staff or user.is_superuser

def send_welcome_email(user):
    """
    Send a welcome email to newly registered users
    """
    try:
        subject = 'Welcome to CloudLink_Devs'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = user.email

        # Context for email template
        context = {
            'user': user,
            'client': getattr(user, 'client_profile', None),
            'login_url': f"{settings.SITE_URL}/client/login/"
        }

        # Render email templates
        html_content = render_to_string('client_portal/emails/welcome_email.html', context)
        text_content = strip_tags(html_content)  # Plain text version

        # Create and send email
        email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        email.attach_alternative(html_content, "text/html")
        email.send()

        return True
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        return False

def send_payment_receipt(payment, additional_message=None, to_email=None):
    """
    Send a payment receipt via email
    """
    try:
        invoice = payment.invoice
        client = invoice.client

        # Use provided email or fall back to client's email
        recipient_email = to_email or client.user.email

        subject = f'Payment Receipt - Invoice #{invoice.invoice_number}'
        from_email = settings.DEFAULT_FROM_EMAIL

        # Context for email template
        context = {
            'payment': payment,
            'invoice': invoice,
            'client': client,
            'additional_message': additional_message,
            'view_receipt_url': f"{settings.SITE_URL}/client/payment/receipt/{payment.id}/",
            'view_invoice_url': f"{settings.SITE_URL}/client/invoices/{invoice.id}/"
        }

        # Render email templates
        html_content = render_to_string('client_portal/emails/payment_receipt.html', context)
        text_content = strip_tags(html_content)  # Plain text version

        # Create and send email
        email = EmailMultiAlternatives(subject, text_content, from_email, [recipient_email])
        email.attach_alternative(html_content, "text/html")
        email.send()

        return True
    except Exception as e:
        print(f"Error sending payment receipt: {e}")
        return False

def send_invoice_created_notification(invoice):
    """
    Send an email notification when a new invoice is created
    """
    try:
        client = invoice.client

        subject = f'New Invoice #{invoice.invoice_number} - CloudLink_Devs'
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = client.user.email

        # Context for email template
        context = {
            'invoice': invoice,
            'client': client,
            'view_invoice_url': f"{settings.SITE_URL}/client/invoices/{invoice.id}/"
        }

        # Render email templates
        html_content = render_to_string('client_portal/emails/invoice_created.html', context)
        text_content = strip_tags(html_content)  # Plain text version

        # Create and send email
        email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        email.attach_alternative(html_content, "text/html")
        email.send()

        return True
    except Exception as e:
        print(f"Error sending invoice created notification: {e}")
        return False

def send_payment_reminder(invoice):
    """
    Send a payment reminder for upcoming or overdue invoices
    """
    try:
        client = invoice.client

        if invoice.status == 'overdue':
            subject = f'OVERDUE: Invoice #{invoice.invoice_number} - Payment Required'
        else:
            subject = f'Reminder: Invoice #{invoice.invoice_number} Due Soon'

        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = client.user.email

        # Context for email template
        context = {
            'invoice': invoice,
            'client': client,
            'is_overdue': invoice.status == 'overdue',
            'view_invoice_url': f"{settings.SITE_URL}/client/invoices/{invoice.id}/",
            'payment_url': f"{settings.SITE_URL}/client/invoices/{invoice.id}/payment/"
        }

        # Render email templates
        html_content = render_to_string('client_portal/emails/payment_reminder.html', context)
        text_content = strip_tags(html_content)  # Plain text version

        # Create and send email
        email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        email.attach_alternative(html_content, "text/html")
        email.send()

        return True
    except Exception as e:
        print(f"Error sending payment reminder: {e}")
        return False

# Optional: Error Logging Function
def log_email_error(function_name, error):
    """
    Log email-related errors
    """
    print(f"Email Error in {function_name}: {error}")