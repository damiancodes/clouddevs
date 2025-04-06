from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from .models import Service, ServiceFeature, QuoteRequest
from .forms import QuoteRequestForm, ServiceEstimatorForm



def quote_request(request):
    """Display and process the quote request form"""
    if request.method == 'POST':
        form = QuoteRequestForm(request.POST)
        if form.is_valid():
            quote_request = form.save()

            # Send notification email to admins
            subject = f"New Quote Request: {quote_request.service.name}"
            message = f"""
            A new quote request has been submitted:

            Name: {quote_request.name}
            Email: {quote_request.email}
            Phone: {quote_request.phone}
            Company: {quote_request.company}

            Service: {quote_request.service.name}
            Estimated Cost: ${quote_request.calculated_estimate}

            Requirements: {quote_request.requirements}
            Budget: {quote_request.budget}
            Timeline: {quote_request.timeline}

            View in admin: {request.build_absolute_uri('/admin/quotes/quoterequest/')}{quote_request.id}/change/
            """

            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.ADMIN_EMAIL],
                    fail_silently=False,
                )
            except Exception as e:
                # Log the error but don't show to user
                print(f"Error sending email: {e}")

            # Redirect to thank you page
            return redirect('quotes:thank_you')
    else:
        form = QuoteRequestForm()

    return render(request, 'quotes/quote_request.html', {'form': form})


def service_estimator(request):
    """Interactive service estimation tool"""
    services = Service.objects.all()

    if request.method == 'POST':
        form = ServiceEstimatorForm(request.POST)
        if form.is_valid():
            # Save the form data to session for use in quote_request
            request.session['estimator_data'] = {
                'service_id': form.cleaned_data['service'].id,
                'feature_ids': [f.id for f in form.cleaned_data['features']]
            }

            # Redirect to quote request with pre-filled data
            return redirect('quotes:quote_request')
    else:
        form = ServiceEstimatorForm()

    return render(request, 'quotes/service_estimator.html', {
        'services': services,
        'form': form
    })


def get_service_features(request, service_id):
    """AJAX endpoint to get features for a specific service"""
    service = get_object_or_404(Service, id=service_id)
    features = service.features.all()

    # Format data for JSON response
    features_data = [
        {
            'id': feature.id,
            'name': feature.name,
            'description': feature.description,
            'price_type': feature.price_type,
            'price_value': float(feature.price_value),
            'is_required': feature.is_required
        }
        for feature in features
    ]

    return JsonResponse({
        'service': {
            'id': service.id,
            'name': service.name,
            'description': service.description,
            'base_price': float(service.base_price)
        },
        'features': features_data
    })


def thank_you(request):
    """Thank you page after quote submission"""
    return render(request, 'quotes/thank_you.html')