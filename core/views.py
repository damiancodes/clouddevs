from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_POST


# Import ContactSubmission if you've created it in a contact or core app
# from contact.models import ContactSubmission

def home(request):
    """Render the home page"""
    return render(request, 'core/home.html')  # Changed from 'home.html'

def about(request):
    """Render the about page"""
    return render(request, 'core/about.html')  # This one is already correct

def contact(request):
    """Render the contact page"""
    return render(request, 'core/contact.html')  # Changed from 'contact.html'

def pricing(request):
    """Render the pricing page"""
    return render(request, 'core/pricing.html')  # Changed from 'pricing.html'


@require_POST
def contact_submit(request):
    """Handle contact form submission"""
    name = request.POST.get('name', '')
    email = request.POST.get('email', '')
    subject = request.POST.get('subject', '')
    message = request.POST.get('message', '')

    # Form validation
    if not all([name, email, subject, message]):
        messages.error(request, 'Please fill out all fields.')
        return redirect('core:contact')

    # Create email message
    email_subject = f"CloudLink_Devs Contact Form: {subject}"
    email_message = f"""
    Contact Form Submission:

    Name: {name}
    Email: {email}
    Subject: {subject}

    Message:
    {message}
    """

    # Save to database if ContactSubmission model exists
    try:
        # Uncomment if you've created the ContactSubmission model
        # ContactSubmission.objects.create(
        #     name=name,
        #     email=email,
        #     subject=subject,
        #     message=message,
        #     ip_address=request.META.get('REMOTE_ADDR')
        # )

        # Send email
        send_mail(
            email_subject,
            email_message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.CONTACT_EMAIL or 'info@cloudlinkdevs.com'],  # Use configured email or fallback
            fail_silently=False,
        )
        messages.success(request, 'Your message has been sent successfully. We will contact you soon!')
    except Exception as e:
        # Log the error in production
        print(f"Error processing contact form: {str(e)}")
        messages.error(request, 'There was an error sending your message. Please try again later.')

    return redirect('core:contact')