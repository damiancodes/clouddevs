import requests
import json
import base64
import datetime
from requests.auth import HTTPBasicAuth
from django.conf import settings


class MpesaAPI:
    """
    Class for handling M-Pesa API integration
    """

    def __init__(self):
        # Get configurations from settings
        self.config = settings.MPESA_CONFIG

        # API URLs
        if self.config['ENVIRONMENT'] == 'production':
            self.base_url = 'https://api.safaricom.co.ke'
        else:
            self.base_url = 'https://sandbox.safaricom.co.ke'

        self.auth_url = f'{self.base_url}/oauth/v1/generate?grant_type=client_credentials'
        self.stk_push_url = f'{self.base_url}/mpesa/stkpush/v1/processrequest'
        self.query_url = f'{self.base_url}/mpesa/stkpushquery/v1/query'

    def get_access_token(self):
        """
        Get OAuth access token from Safaricom
        """
        response = requests.get(
            self.auth_url,
            auth=HTTPBasicAuth(
                self.config['CONSUMER_KEY'],
                self.config['CONSUMER_SECRET']
            )
        )

        if response.status_code == 200:
            result = response.json()
            return result['access_token']
        else:
            raise Exception(f"Authentication failed with status code {response.status_code}")

    def generate_password(self, timestamp):
        """
        Generate the LipaNaMpesa Online password
        """
        shortcode = self.config['SHORTCODE']
        passkey = self.config['PASS_KEY']
        password_str = shortcode + passkey + timestamp
        password_bytes = password_str.encode('utf-8')
        return base64.b64encode(password_bytes).decode('utf-8')

    def initiate_stk_push(self, phone_number, amount, reference, description=None):
        """
        Initiate an STK push request to customer's phone
        """
        # Format timestamp
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

        # Format phone number (remove leading 0 or +)
        if phone_number.startswith('+'):
            phone_number = phone_number[1:]
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]

        # Generate the password
        password = self.generate_password(timestamp)

        # Get access token
        token = self.get_access_token()

        # Prepare headers
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        # Prepare the request data
        request_data = {
            'BusinessShortCode': self.config['SHORTCODE'],
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': int(amount),
            'PartyA': phone_number,
            'PartyB': self.config['SHORTCODE'],
            'PhoneNumber': phone_number,
            'CallBackURL': self.config['CALLBACK_URL'],
            'AccountReference': reference[:12] if len(reference) > 12 else reference,
            'TransactionDesc': description or self.config['TRANSACTION_DESC']
        }

        # Make the request
        response = requests.post(
            self.stk_push_url,
            json=request_data,
            headers=headers
        )

        # Return the response
        return response.json()

    def query_stk_status(self, checkout_request_id):
        """
        Check the status of an STK push request
        """
        # Format timestamp
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

        # Generate the password
        password = self.generate_password(timestamp)

        # Get access token
        token = self.get_access_token()

        # Prepare headers
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        # Prepare the request data
        request_data = {
            'BusinessShortCode': self.config['SHORTCODE'],
            'Password': password,
            'Timestamp': timestamp,
            'CheckoutRequestID': checkout_request_id
        }

        # Make the request
        response = requests.post(
            self.query_url,
            json=request_data,
            headers=headers
        )

        # Return the response
        return response.json()