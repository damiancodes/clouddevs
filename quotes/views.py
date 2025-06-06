








# quotes/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .forms import QuoteRequestForm, ServiceEstimatorForm
from django.contrib import messages
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from decimal import Decimal
from .forms import QuoteRequestForm, ServiceEstimatorForm
import json
import requests
import uuid
import logging

# Import your models
from .models import ExchangeRate, SolutionBuilder, SolutionFeature
from services.models import Service, ServiceFeature
from client_portal.models import Client, Payment, Invoice

# Set up logging
logger = logging.getLogger(__name__)

# Original views for quote request and service estimator
def quote_request(request):
    """Display and process the quote request form"""
    if request.method == 'POST':
        form = QuoteRequestForm(request.POST, request=request)
        if form.is_valid():
            # Instead of saving to the database, get the cleaned data
            quote_data = form.save()

            # Send notification email to admins
            service = quote_data['service']

            subject = f"New Quote Request: {service.name}"
            message = f"""
            A new quote request has been submitted:

            Name: {quote_data['name']}
            Email: {quote_data['email']}
            Phone: {quote_data.get('phone', 'Not provided')}
            Company: {quote_data.get('company', 'Not provided')}

            Service: {service.name}

            Requirements: {quote_data.get('requirements', 'Not provided')}
            Budget: {quote_data.get('budget', 'Not specified')}
            Timeline: {quote_data.get('timeline', 'Not specified')}
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
        form = QuoteRequestForm(request=request)

    return render(request, 'quotes/quote_request.html', {'form': form})



def service_estimator(request):
    """Interactive service estimation tool"""
    # Try to import the form directly here if it's not imported at the top of your file
    try:
        from .forms import ServiceEstimatorForm
    except ImportError:
        # Fallback to just rendering the template without the form
        services = Service.objects.all()
        return render(request, 'quotes/service_estimator.html', {
            'services': services,
        })

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


# def get_service_features(request, service_id):
#     """AJAX endpoint to get features for a specific service"""
#     try:
#         # Make sure to get the actual Service object
#         service = get_object_or_404(Service, id=service_id)
#
#         # Try accessing features - this might be service.features or service.service_features
#         try:
#             features = service.features.all()
#         except AttributeError:
#             # If 'features' relationship isn't available, try service_features
#             features = service.service_features.all()
#
#         # Format data for JSON response
#         features_data = [
#             {
#                 'id': feature.id,
#                 'name': feature.name,
#                 'description': feature.description,
#                 'price_type': feature.price_type,
#                 'price_value': float(feature.price_value),
#                 'is_required': feature.is_required
#             }
#             for feature in features
#         ]
#
#         return JsonResponse({
#             'service': {
#                 'id': service.id,
#                 'name': service.name,
#                 'description': service.description,
#                 'base_price': float(service.base_price)
#             },
#             'features': features_data
#         })
#     except Exception as e:
#         print(f"Error in get_service_features: {e}")
#         return JsonResponse({
#             'error': str(e)
#         }, status=500)

def get_service_features(request, service_id):
    """AJAX endpoint to get features for a specific service"""
    try:
        service = get_object_or_404(Service, id=service_id)

        # Try to get features through the correct related name
        try:
            features = service.service_features.all()  # Use the correct related_name
            print(f"Found {features.count()} features for service {service.name}")
        except Exception as e:
            print(f"Error accessing features: {e}")
            features = []

        # Format data for JSON response
        features_data = []
        for feature in features:
            feature_data = {
                'id': feature.id,
                'name': feature.title,  # Note: Using 'title' from your model
                'description': feature.description,
                'price_type': getattr(feature, 'price_type', 'fixed'),
                'price_value': float(getattr(feature, 'price_value', 0)),
                'is_required': getattr(feature, 'is_required', False)
            }
            features_data.append(feature_data)

        # Use base_price field
        base_price = getattr(service, 'base_price', 0.0)

        return JsonResponse({
            'service': {
                'id': service.id,
                'name': service.name,
                'description': service.description,
                'base_price': float(base_price)
            },
            'features': features_data
        })
    except Exception as e:
        logger.error(f"Error in get_service_features: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def thank_you(request):
    """Thank you page after quote submission"""
    return render(request, 'quotes/thank_you.html')


# Solution Builder views
def solution_builder(request):
    """Main view for the solution builder."""
    services = Service.objects.all().order_by('name')
    context = {
        'services': services,
    }
    return render(request, 'quotes/templates/quotes/solution_builder.html', context)
def get_exchange_rate(request):
    """API endpoint to get current USD to KSH exchange rate."""
    rate = ExchangeRate.get_rate()
    return JsonResponse({'rate': float(rate)})


@require_POST
def create_order(request):
    """Process the form submission and create an order."""
    try:
        # Extract form data
        service_id = request.POST.get('service')
        feature_ids = request.POST.getlist('features')
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        appointment_date = request.POST.get('appointment_date')
        notes = request.POST.get('notes', '')
        total_price_usd = Decimal(request.POST.get('total_price_usd', '0.00'))
        total_price_ksh = Decimal(request.POST.get('total_price_ksh', '0.00'))

        # Get objects
        service = Service.objects.get(id=service_id)
        features = ServiceFeature.objects.filter(id__in=feature_ids)

        # Check if there's a logged in user with client profile
        client = None
        if request.user.is_authenticated:
            try:
                client = request.user.client_profile
            except:
                pass

        # Create order
        solution = SolutionBuilder.objects.create(
            client=client,
            name=name,
            email=email,
            phone=phone,
            service=service,
            appointment_date=appointment_date,
            notes=notes,
            total_price_usd=total_price_usd,
            total_price_ksh=total_price_ksh
        )

        # Add features to solution
        for feature in features:
            price_at_order = 0
            if feature.price_type == 'fixed':
                price_at_order = feature.price_value
            else:  # percentage
                price_at_order = service.base_price * feature.price_value / 100

            SolutionFeature.objects.create(
                solution=solution,
                feature=feature,
                price_at_order=price_at_order,
                price_type=feature.price_type
            )

        # Check if skip payment
        if request.POST.get('skip_payment') == 'true':
            solution.payment_method = 'none'
            solution.save()
            # Send email notification
            send_order_confirmation(solution, payment_skipped=True)
            return redirect('quotes:confirmation', order_id=solution.id)

        # Redirect to payment choice page
        return redirect('quotes:payment_choice', order_id=solution.id)

    except Exception as e:
        logger.error(f"Error creating order: {e}")
        messages.error(request, "An error occurred while processing your order. Please try again.")
        return redirect('quotes:solution_builder')


def payment_choice(request, order_id):
    """Display payment choices."""
    try:
        solution = get_object_or_404(SolutionBuilder, id=order_id)
        context = {
            'order': solution,
        }
        # Make sure this template exists at quotes/templates/quotes/payment_choice.html
        return render(request, 'quotes/payment_choice.html', context)
    except Exception as e:
        logger.error(f"Error in payment choice: {e}")
        messages.error(request, "An error occurred while loading payment options. Please try again.")
        return redirect('quotes:solution_builder')


def process_mpesa(request, order_id):
    """Handle M-Pesa STK push payment."""
    try:
        # Get the solution
        solution = get_object_or_404(SolutionBuilder, id=order_id)

        # Pass the solution to the template
        context = {'order': solution}

        # Use the correct template path
        return render(request, 'quotes/mpesa_payment.html', context)
    except Exception as e:
        logger.error(f"Error processing M-Pesa payment: {e}")
        messages.error(request, "An error occurred while setting up M-Pesa payment. Please try again.")
        return redirect('quotes:payment_choice', order_id=order_id)


@require_POST
# @require_POST
# def mpesa_stk_push(request):
#     """API endpoint to initiate M-Pesa STK push."""
#     try:
#         data = json.loads(request.body)
#         phone_number = data.get('phone_number')
#         order_id = data.get('order_id')
#         amount = data.get('amount')
#
#         # Get the order
#         solution = get_object_or_404(SolutionBuilder, id=order_id)
#
#         # Import your existing M-Pesa API function, or use direct API
#         # This depends on how your mpesa_api app is structured
#         try:
#             from mpesa_api.api import stk_push
#             response = stk_push(phone_number, float(amount))
#
#             if response and response.get('ResponseCode') == '0':
#                 return JsonResponse({
#                     'success': True,
#                     'checkout_request_id': response.get('CheckoutRequestID'),
#                     'message': 'STK push sent successfully.'
#                 })
#             else:
#                 return JsonResponse({
#                     'success': False,
#                     'message': response.get('ResponseDescription', 'Failed to send STK push. Please try again.')
#                 })
#         except ImportError:
#             # Fallback if M-Pesa API import fails - simulate success for testing
#             return JsonResponse({
#                 'success': True,
#                 'checkout_request_id': str(uuid.uuid4()),
#                 'message': 'STK push simulation successful (test mode).'
#             })
#
#     except Exception as e:
#         logger.error(f"Error in M-Pesa STK push: {e}")
#         return JsonResponse({
#             'success': False,
#             'message': f'Failed to send STK push. Error: {str(e)}'
#         })
@require_POST
def mpesa_stk_push(request):
    """API endpoint to initiate M-Pesa STK push."""
    try:
        data = json.loads(request.body)
        phone_number = data.get('phone_number')
        order_id = data.get('order_id')
        amount = data.get('amount')

        # Format phone number consistently
        phone_number = ''.join(filter(str.isdigit, phone_number))
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        if not phone_number.startswith('254'):
            phone_number = '254' + phone_number

        # Get the order
        solution = get_object_or_404(SolutionBuilder, id=order_id)

        # Create reference and description
        reference = f"SOL-{solution.id}"
        description = f"Payment for {solution.service.name} service"

        # Import the MpesaAPI class from mpesa_api
        from mpesa_api.api import MpesaAPI

        # Initialize and use the M-Pesa API
        mpesa_api = MpesaAPI()

        # Send STK push
        response = mpesa_api.initiate_stk_push(
            phone_number=phone_number,
            amount=float(amount),
            reference=reference,
            description=description
        )

        # Check if successful
        if response and response.get('ResponseCode') == '0':
            # Create transaction record in the mpesa_api app
            from mpesa_api.models import MpesaTransaction
            from django.utils import timezone

            transaction = MpesaTransaction.objects.create(
                transaction_type='solution_payment',
                transaction_id=f"SOL-{timezone.now().strftime('%Y%m%d%H%M%S')}",
                phone_number=phone_number,
                amount=float(amount),
                reference=reference,
                description=description,
                merchant_request_id=response.get('MerchantRequestID', ''),
                checkout_request_id=response.get('CheckoutRequestID', ''),
                response_code=response.get('ResponseCode', ''),
                response_description=response.get('ResponseDescription', ''),
                customer_message=response.get('CustomerMessage', '')
            )

            # Store checkout request ID for status checking
            request.session['mpesa_checkout_request_id'] = response.get('CheckoutRequestID')
            request.session['mpesa_solution_id'] = solution.id

            return JsonResponse({
                'success': True,
                'checkout_request_id': response.get('CheckoutRequestID'),
                'message': 'STK push sent successfully.'
            })
        else:
            # Response exists but has an error
            error_message = response.get('errorMessage', response.get('ResponseDescription',
                                                                      'Failed to send STK push. Please try again.'))
            return JsonResponse({
                'success': False,
                'message': error_message
            })

    except Exception as e:
        logger.error(f"Error in M-Pesa STK push: {e}")
        import traceback
        traceback.print_exc()  # Print full stack trace to console
        return JsonResponse({
            'success': False,
            'message': f'Failed to send STK push. Error: {str(e)}'
        })


@require_POST
def mpesa_check_status(request):
    """API endpoint to check M-Pesa payment status."""
    try:
        data = json.loads(request.body)
        checkout_request_id = data.get('checkout_request_id')
        order_id = data.get('order_id')

        # Import necessary modules from mpesa_api
        from mpesa_api.api import MpesaAPI
        from mpesa_api.models import MpesaTransaction

        # Get the transaction
        try:
            transaction = MpesaTransaction.objects.get(checkout_request_id=checkout_request_id)

            # If already completed, return the status
            if transaction.is_completed:
                return JsonResponse({
                    'success': transaction.is_successful,
                    'status': 'completed',
                    'transaction_id': transaction.transaction_id,
                    'message': transaction.result_description or 'Payment processed successfully.'
                })

            # Query status from M-Pesa API
            mpesa_api = MpesaAPI()
            response = mpesa_api.query_stk_status(checkout_request_id)

            # Check response
            if 'ResultCode' in response:
                # Update transaction
                transaction.result_code = response.get('ResultCode', '')
                transaction.result_description = response.get('ResultDesc', '')
                transaction.is_completed = True
                transaction.is_successful = response.get('ResultCode', '') == '0'

                # If successful, update transaction ID
                if transaction.is_successful and 'MpesaReceiptNumber' in response:
                    transaction.transaction_id = response.get('MpesaReceiptNumber')

                transaction.save()

                return JsonResponse({
                    'success': transaction.is_successful,
                    'status': 'completed',
                    'transaction_id': transaction.transaction_id,
                    'message': transaction.result_description or 'Payment processed successfully.'
                })
            else:
                # Still pending
                return JsonResponse({
                    'status': 'pending',
                    'message': 'Payment is being processed'
                })

        except MpesaTransaction.DoesNotExist:
            return JsonResponse({
                'success': False,
                'status': 'failed',
                'message': 'Transaction not found.'
            })

    except Exception as e:
        logger.error(f"Error checking M-Pesa status: {e}")
        import traceback
        traceback.print_exc()  # Print full stack trace to console
        return JsonResponse({
            'success': False,
            'status': 'failed',
            'message': f'Failed to verify payment status. Error: {str(e)}'
        })




def process_crypto(request, order_id):
    """Handle Crypto payment."""
    try:
        solution = get_object_or_404(SolutionBuilder, id=order_id)
        context = {
            'order': solution,
            'crypto_address': settings.CRYPTO_ADDRESS
        }
        return render(request, 'quotes/crypto_payment.html', context)
    except Exception as e:
        logger.error(f"Error processing Crypto payment: {e}")
        messages.error(request, "An error occurred while setting up cryptocurrency payment. Please try again.")
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(f'/quotes/payment-choice/{order_id}/')




def skip_payment(request, order_id):
    """Skip payment and show confirmation."""
    try:
        solution = get_object_or_404(SolutionBuilder, id=order_id)
        solution.payment_method = 'none'
        solution.save()

        # Send email notification
        send_order_confirmation(solution, payment_skipped=True)

        return redirect('quotes:confirmation', order_id=solution.id)
    except Exception as e:
        logger.error(f"Error skipping payment: {e}")
        messages.error(request, "An error occurred while processing your request. Please try again.")
        return redirect('quotes:payment_choice', order_id=order_id)


def payment_callback(request, order_id, payment_method):
    """Handle payment callbacks from various methods."""
    try:
        solution = get_object_or_404(SolutionBuilder, id=order_id)
        transaction_id = request.GET.get('transaction_id', '')

        # Update solution
        solution.is_paid = True
        solution.payment_method = payment_method
        solution.transaction_id = transaction_id
        solution.save()

        # Create invoice if needed
        if solution.client and not solution.invoice:
            invoice = solution.create_invoice()

            # Record payment for the invoice
            payment_amount = solution.total_price_usd

            # Create payment record
            Payment.objects.create(
                invoice=invoice,
                amount=payment_amount,
                payment_date=timezone.now().date(),
                payment_method=payment_method,
                transaction_id=transaction_id,
                notes=f"Payment from solution builder order #{solution.id}"
            )

            # Update invoice status
            invoice.status = 'paid'
            invoice.save()

        # Send email confirmation
        send_order_confirmation(solution)

        return redirect('quotes:confirmation', order_id=solution.id)
    except Exception as e:
        logger.error(f"Error in payment callback: {e}")
        messages.error(request, "An error occurred while processing payment confirmation. Please contact support.")
        return redirect('quotes:solution_builder')


def confirmation(request, order_id):
    """Display confirmation page after order creation/payment."""
    try:
        solution = get_object_or_404(SolutionBuilder, id=order_id)
        context = {
            'order': solution,
            'payment_skipped': solution.payment_method == 'none',
        }
        return render(request, 'quotes/confirmation.html', context)
    except Exception as e:
        logger.error(f"Error showing confirmation: {e}")
        messages.error(request, "An error occurred while loading the confirmation page. Please contact support.")
        return redirect('quotes:solution_builder')


def send_order_confirmation(solution, payment_skipped=False):
    """Send order confirmation email to customer and admin."""
    try:
        # Customer email
        customer_subject = f"Your CloudLink_Devs Order: {solution.service.name}"
        customer_html = render_to_string('quotes/emails/customer_confirmation.html', {
            'order': solution,
            'payment_skipped': payment_skipped,
        })
        customer_text = strip_tags(customer_html)

        customer_email = EmailMultiAlternatives(
            customer_subject,
            customer_text,
            settings.DEFAULT_FROM_EMAIL,
            [solution.email]
        )
        customer_email.attach_alternative(customer_html, "text/html")
        customer_email.send()

        # Admin email
        admin_subject = f"New Order: {solution.service.name} by {solution.name}"
        admin_html = render_to_string('quotes/emails/admin_notification.html', {
            'order': solution,
            'payment_skipped': payment_skipped,
            'admin_url': f"{settings.SITE_URL}/admin/quotes/solutionbuilder/{solution.id}/change/"
        })
        admin_text = strip_tags(admin_html)

        admin_email = EmailMultiAlternatives(
            admin_subject,
            admin_text,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL]  # Make sure this is defined in settings.py
        )
        admin_email.attach_alternative(admin_html, "text/html")
        admin_email.send()

        return True
    except Exception as e:
        logger.error(f"Error sending confirmation email: {e}")
        return False


def process_paypal(request, order_id):
    """Handle PayPal payment."""
    try:
        solution = get_object_or_404(SolutionBuilder, id=order_id)

        # Make sure you have these values in your settings
        client_id = getattr(settings, 'PAYPAL_CLIENT_ID', 'your-client-id-here')

        # Get the client_id if the user is authenticated
        client_id = None
        if request.user.is_authenticated:
            try:
                client_id = request.user.client_profile.id
            except:
                pass

        # Properly use reverse to generate URLs
        return_url = request.build_absolute_uri(
            reverse('quotes:payment_callback',
                    kwargs={'order_id': solution.id, 'payment_method': 'paypal'})
        )

        cancel_url = request.build_absolute_uri(
            reverse('quotes:payment_choice',
                    kwargs={'order_id': solution.id})
        )

        context = {
            'order': solution,
            'client_id': client_id,
            'return_url': return_url,
            'cancel_url': cancel_url
        }

        return render(request, 'quotes/paypal_payment.html', context)

    except Exception as e:
        logger.error(f"Error processing PayPal payment: {e}")
        messages.error(request, "An error occurred while setting up PayPal payment. Please try again.")
        return redirect('quotes:payment_choice', order_id=order_id)