import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required

from client_portal.models import Invoice, Payment
from .models import MpesaTransaction
from .api import MpesaAPI


@login_required
def initiate_stk_push(request, invoice_id, amount):
    """
    Initiate an STK push request to the user's phone
    """
    # Get the invoice - handle both admin and client access
    if request.user.is_staff:
        invoice = get_object_or_404(Invoice, id=invoice_id)
    else:
        invoice = get_object_or_404(Invoice, id=invoice_id, client__user=request.user)

    # Check the amount
    if float(amount) <= 0:
        messages.error(request, "The payment amount must be greater than zero.")
        return redirect('client_portal:make_payment', invoice_id=invoice.id)

    # Get the phone number from the POST request
    phone_number = request.POST.get('phone_number', '').strip()

    if not phone_number:
        messages.error(request, "Please provide a phone number.")
        return redirect('client_portal:make_payment', invoice_id=invoice.id)

    # Create reference from invoice number
    reference = f"INV-{invoice.invoice_number}"

    # Description
    description = f"Payment for invoice {invoice.invoice_number}"

    try:
        # Initialize the M-Pesa API
        mpesa_api = MpesaAPI()

        # Send STK push
        response = mpesa_api.initiate_stk_push(
            phone_number=phone_number,
            amount=float(amount),
            reference=reference,
            description=description
        )

        # Check if successful
        if 'ResponseCode' in response and response['ResponseCode'] == '0':
            # Create MpesaTransaction record
            transaction = MpesaTransaction.objects.create(
                transaction_type='stk_push',
                transaction_id=f"STK-{timezone.now().strftime('%Y%m%d%H%M%S')}",
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

            # Store transaction ID in session for checking status later
            request.session['mpesa_checkout_request_id'] = response.get('CheckoutRequestID', '')
            request.session['mpesa_amount'] = float(amount)
            request.session['mpesa_invoice_id'] = invoice.id

            # Redirect to a status checking page
            return redirect('mpesa_api:check_payment_status')
        else:
            # If failed, show error message
            error_message = response.get('errorMessage', 'Failed to initiate M-Pesa payment')
            messages.error(request, error_message)
            return redirect('client_portal:make_payment', invoice_id=invoice.id)

    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('client_portal:make_payment', invoice_id=invoice.id)


@login_required
def check_payment_status(request):
    """
    Check the status of an STK push payment
    """
    # Get the checkout request ID from session
    checkout_request_id = request.session.get('mpesa_checkout_request_id', None)
    amount = request.session.get('mpesa_amount', 0)
    invoice_id = request.session.get('mpesa_invoice_id', None)

    if not checkout_request_id or not invoice_id:
        messages.error(request, "Payment session expired or invalid.")
        return redirect('client_portal:invoices')

    # Get the invoice
    if request.user.is_staff:
        invoice = get_object_or_404(Invoice, id=invoice_id)
    else:
        invoice = get_object_or_404(Invoice, id=invoice_id, client__user=request.user)

    # Get the transaction
    transaction = get_object_or_404(
        MpesaTransaction,
        checkout_request_id=checkout_request_id
    )

    context = {
        'invoice': invoice,
        'transaction': transaction,
        'amount': amount,
    }

    # If the transaction is completed, show the result
    if transaction.is_completed:
        if transaction.is_successful:
            # Clear session data
            request.session.pop('mpesa_checkout_request_id', None)
            request.session.pop('mpesa_amount', None)
            request.session.pop('mpesa_invoice_id', None)

            # Show success message
            messages.success(request, "Payment completed successfully!")

            # Redirect to success page
            return redirect(
                'client_portal:payment_success',
                invoice_id=invoice.id,
                payment_method='mpesa',
                transaction_id=transaction.transaction_id
            )
        else:
            # Show failure message
            messages.error(request, f"Payment failed: {transaction.result_description}")

            # Clear session data
            request.session.pop('mpesa_checkout_request_id', None)
            request.session.pop('mpesa_amount', None)
            request.session.pop('mpesa_invoice_id', None)

            return redirect('client_portal:make_payment', invoice_id=invoice.id)

    return render(request, 'mpesa_api/check_status.html', context)


@login_required
def query_payment_status(request):
    """
    AJAX endpoint to query the status of an STK push payment
    """
    # Get the checkout request ID from session
    checkout_request_id = request.session.get('mpesa_checkout_request_id', None)

    if not checkout_request_id:
        return JsonResponse({'status': 'error', 'message': 'Invalid session'})

    try:
        # Get the transaction
        transaction = MpesaTransaction.objects.get(checkout_request_id=checkout_request_id)

        # If already completed, return the status
        if transaction.is_completed:
            return JsonResponse({
                'status': 'completed',
                'success': transaction.is_successful,
                'message': transaction.result_description
            })

        # Otherwise, query the status from M-Pesa
        mpesa_api = MpesaAPI()
        response = mpesa_api.query_stk_status(checkout_request_id)

        # Check the response
        if 'ResultCode' in response:
            # Update the transaction
            transaction.result_code = response.get('ResultCode', '')
            transaction.result_description = response.get('ResultDesc', '')
            transaction.is_completed = True
            transaction.is_successful = response.get('ResultCode', '') == '0'
            transaction.save()

            return JsonResponse({
                'status': 'completed',
                'success': transaction.is_successful,
                'message': transaction.result_description
            })
        else:
            # If still pending
            return JsonResponse({'status': 'pending', 'message': 'Payment is being processed'})

    except MpesaTransaction.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Transaction not found'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@csrf_exempt
def mpesa_callback(request):
    """
    Callback endpoint for M-Pesa to send payment results
    """
    if request.method == 'POST':
        try:
            # Parse the JSON response
            response_data = json.loads(request.body)

            # Get the body
            body = response_data.get('Body', {})
            stkCallback = body.get('stkCallback', {})

            # Get checkout request ID
            checkout_request_id = stkCallback.get('CheckoutRequestID')

            # Get result code
            result_code = stkCallback.get('ResultCode')
            result_desc = stkCallback.get('ResultDesc')

            # Find the transaction
            try:
                transaction = MpesaTransaction.objects.get(checkout_request_id=checkout_request_id)

                # Update the transaction
                transaction.result_code = result_code
                transaction.result_description = result_desc
                transaction.is_completed = True
                transaction.is_successful = result_code == '0'

                # If successful, get the payment details
                if result_code == '0':
                    # Get the callback metadata
                    callback_metadata = stkCallback.get('CallbackMetadata', {})
                    item_list = callback_metadata.get('Item', [])

                    # Extract metadata
                    metadata = {}
                    for item in item_list:
                        name = item.get('Name')
                        value = item.get('Value')
                        metadata[name] = value

                    # Update transaction with M-Pesa receipt number
                    mpesa_receipt = metadata.get('MpesaReceiptNumber', '')
                    if mpesa_receipt:
                        transaction.transaction_id = mpesa_receipt

                transaction.save()

                # If payment successful, create a Payment record
                if transaction.is_successful:
                    # Get the invoice
                    try:
                        invoice_id = transaction.reference.replace('INV-', '')
                        invoice = Invoice.objects.get(invoice_number=invoice_id)

                        # Create payment record
                        Payment.objects.create(
                            invoice=invoice,
                            amount=transaction.amount,
                            payment_date=timezone.now().date(),
                            payment_method='mpesa',
                            transaction_id=transaction.transaction_id,
                            notes=f"M-Pesa payment via phone {transaction.phone_number}"
                        )

                        # Update invoice status if fully paid
                        if invoice.balance_due <= 0:
                            invoice.status = 'paid'
                            invoice.save()

                    except Invoice.DoesNotExist:
                        # Log the error but don't disrupt the callback
                        pass

                return HttpResponse(status=200)

            except MpesaTransaction.DoesNotExist:
                # Transaction not found, log but don't disrupt callback
                return HttpResponse(status=200)

        except Exception as e:
            # Log the error but don't disrupt the callback
            return HttpResponse(status=200)

    return HttpResponse(status=405)  # Method not allowed


# Add this function to mpesa_api/views.py

@login_required
def initiate_direct_payment(request, amount):
    """
    Initiate an STK push request for direct payment without invoice
    """
    # Get the phone number from the URL query parameter first, then from session as fallback
    phone_number = request.GET.get('phone', '') or request.session.get('mpesa_phone_number', '')

    if not phone_number:
        messages.error(request, "Please provide a phone number.")
        return redirect('client_portal:direct_payment')

    # Get the payment purpose from session
    purpose = request.session.get('direct_payment_purpose', 'Direct payment')

    # Create reference from client username and timestamp
    client = request.user.client_profile
    reference = f"DIR-{client.user.username}-{timezone.now().strftime('%Y%m%d%H%M%S')}"

    # Description
    description = f"Direct payment: {purpose}"

    try:
        # Initialize the M-Pesa API
        mpesa_api = MpesaAPI()

        # Send STK push
        response = mpesa_api.initiate_stk_push(
            phone_number=phone_number,
            amount=float(amount),
            reference=reference,
            description=description
        )

        # Check if successful
        if 'ResponseCode' in response and response['ResponseCode'] == '0':
            # Create MpesaTransaction record
            transaction = MpesaTransaction.objects.create(
                transaction_type='direct_payment',
                transaction_id=f"DIR-{timezone.now().strftime('%Y%m%d%H%M%S')}",
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

            # Store transaction ID in session for checking status later
            request.session['mpesa_checkout_request_id'] = response.get('CheckoutRequestID', '')
            request.session['mpesa_direct_payment'] = True
            request.session['direct_payment_amount'] = float(amount)
            request.session.modified = True

            # Redirect to a status checking page
            return redirect('mpesa_api:check_direct_payment_status')
        else:
            # If failed, show error message
            error_message = response.get('errorMessage', 'Failed to initiate M-Pesa payment')
            messages.error(request, error_message)
            return redirect('client_portal:direct_payment')

    except Exception as e:
        import traceback
        traceback.print_exc()
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('client_portal:direct_payment')


@login_required
def initiate_direct_payment(request, amount):
    """
    Initiate an STK push request for direct payment without invoice
    """
    print("DEBUG - Starting initiate_direct_payment function")

    # Get the phone number from the URL query parameter first, then from session as fallback
    phone_number = request.GET.get('phone', '') or request.session.get('mpesa_phone_number', '')
    print(f"DEBUG - Initial phone number: {phone_number}")

    # Ensure the phone number is properly formatted
    phone_number = ''.join(filter(str.isdigit, phone_number))
    print(f"DEBUG - Cleaned phone number (digits only): {phone_number}")

    if phone_number.startswith('0'):
        phone_number = '254' + phone_number[1:]
    if not phone_number.startswith('254'):
        phone_number = '254' + phone_number

    print(f"DEBUG - Final formatted phone: {phone_number} for amount: {amount}")

    if not phone_number:
        print("DEBUG - No phone number provided")
        messages.error(request, "Please provide a phone number.")
        return redirect('client_portal:direct_payment')

    # Get the payment purpose from session
    purpose = request.session.get('direct_payment_purpose', 'Direct payment')
    print(f"DEBUG - Payment purpose: {purpose}")

    try:
        print("DEBUG - Attempting to get client")
        # Create reference from client username and timestamp
        client = request.user.client_profile
        reference = f"DIR-{client.user.username}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        print(f"DEBUG - Reference: {reference}")

        # Description
        description = f"Direct payment: {purpose}"
        print(f"DEBUG - Description: {description}")

        print("DEBUG - Initializing MpesaAPI")
        # Initialize the M-Pesa API
        mpesa_api = MpesaAPI()

        # Log the API call parameters
        print(
            f"DEBUG - Making API call with: phone={phone_number}, amount={amount}, reference={reference}, description={description}")

        # Send STK push
        try:
            response = mpesa_api.initiate_stk_push(
                phone_number=phone_number,
                amount=float(amount),
                reference=reference,
                description=description
            )
            print(f"DEBUG - API Response received: {response}")
        except Exception as api_error:
            print(f"DEBUG - API call failed with error: {str(api_error)}")
            import traceback
            traceback.print_exc()
            messages.error(request, f"M-Pesa API error: {str(api_error)}")
            return redirect('client_portal:direct_payment')

        # Check if successful
        if 'ResponseCode' in response and response['ResponseCode'] == '0':
            print("DEBUG - STK push successful")
            # Create MpesaTransaction record
            transaction = MpesaTransaction.objects.create(
                transaction_type='direct_payment',
                transaction_id=f"DIR-{timezone.now().strftime('%Y%m%d%H%M%S')}",
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

            print(f"DEBUG - Created transaction record: {transaction.id}")

            # Store transaction ID in session for checking status later
            request.session['mpesa_checkout_request_id'] = response.get('CheckoutRequestID', '')
            request.session['mpesa_direct_payment'] = True
            request.session['direct_payment_amount'] = float(amount)
            request.session.modified = True

            print(f"DEBUG - Updated session with checkout_request_id: {response.get('CheckoutRequestID', '')}")
            print(f"DEBUG - Redirecting to check_direct_payment_status")

            # Redirect to a status checking page
            return redirect('mpesa_api:check_direct_payment_status')
        else:
            # If failed, show error message
            error_message = response.get('errorMessage',
                                         response.get('responseDescription', 'Failed to initiate M-Pesa payment'))
            print(f"DEBUG - STK push failed: {error_message}")
            messages.error(request, f"M-Pesa error: {error_message}")
            return redirect('client_portal:direct_payment')

    except Exception as e:
        print(f"DEBUG - Exception in initiate_direct_payment: {str(e)}")
        import traceback
        traceback.print_exc()
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('client_portal:direct_payment')


@login_required
def check_direct_payment_status(request):
    """
    Check the status of a direct payment STK push
    """
    # Get the checkout request ID from session
    checkout_request_id = request.session.get('mpesa_checkout_request_id', None)
    amount = request.session.get('direct_payment_amount', 0)

    if not checkout_request_id:
        messages.error(request, "Payment session expired or invalid.")
        return redirect('client_portal:direct_payment')

    # Get the transaction
    transaction = get_object_or_404(
        MpesaTransaction,
        checkout_request_id=checkout_request_id
    )

    context = {
        'transaction': transaction,
        'amount': amount,
        'purpose': request.session.get('direct_payment_purpose', 'Direct payment')
    }

    # If the transaction is completed, show the result
    if transaction.is_completed:
        if transaction.is_successful:
            # Create a direct payment record
            try:
                # Create payment without invoice
                payment = Payment.objects.create(
                    invoice=None,  # Direct payment has no invoice
                    amount=transaction.amount,
                    payment_date=timezone.now().date(),
                    payment_method='mpesa',
                    transaction_id=transaction.transaction_id,
                    notes=f"Direct M-Pesa payment: {transaction.description}"
                )

                # Clear session data
                request.session.pop('mpesa_checkout_request_id', None)
                request.session.pop('direct_payment_amount', None)
                request.session.pop('direct_payment_purpose', None)
                request.session.pop('mpesa_phone_number', None)
                request.session.pop('mpesa_direct_payment', None)

                # Show success message
                messages.success(request, "Payment completed successfully!")

                # Redirect to receipt page
                return redirect('client_portal:print_receipt', payment_id=payment.id)

            except Exception as e:
                messages.error(request, f"Payment was successful but there was an error recording it: {str(e)}")
                return redirect('client_portal:dashboard')
        else:
            # Show failure message
            messages.error(request, f"Payment failed: {transaction.result_description}")

            # Clear session data
            request.session.pop('mpesa_checkout_request_id', None)
            request.session.pop('direct_payment_amount', None)
            request.session.pop('direct_payment_purpose', None)
            request.session.pop('mpesa_phone_number', None)
            request.session.pop('mpesa_direct_payment', None)

            return redirect('client_portal:direct_payment')

    # Render the check status template
    return render(request, 'mpesa_api/check_direct_status.html', context)


def process_paypal(request, order_id):
    """Handle PayPal payment."""
    try:
        solution = get_object_or_404(SolutionBuilder, id=order_id)

        # Make sure you have these values in your settings
        client_id = getattr(settings, 'PAYPAL_CLIENT_ID', 'your-client-id-here')

        context = {
            'order': solution,
            'client_id': client_id,
            'return_url': request.build_absolute_uri(
                reverse('quotes:payment_callback', kwargs={
                    'order_id': solution.id,
                    'payment_method': 'paypal'
                })
            ),
            'cancel_url': request.build_absolute_uri(
                reverse('quotes:payment_choice', kwargs={'order_id': solution.id})
            )
        }
        return render(request, 'quotes/paypal_payment.html', context)
    except Exception as e:
        logger.error(f"Error processing PayPal payment: {e}")
        messages.error(request, "An error occurred while setting up PayPal payment. Please try again.")
        return redirect('quotes:payment_choice', order_id=order_id)