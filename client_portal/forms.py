# from django import forms
# from django.contrib.auth.models import User
# from django.contrib.auth.forms import UserCreationForm
# from .models import Client, Project, ProjectTask, Message, Payment
#
#
# class ClientRegistrationForm(UserCreationForm):
#     """Form for client registration"""
#     first_name = forms.CharField(max_length=30, required=True)
#     last_name = forms.CharField(max_length=30, required=True)
#     email = forms.EmailField(max_length=254, required=True)
#     company_name = forms.CharField(max_length=100, required=False)
#     phone = forms.CharField(max_length=20, required=False)
#     address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
#
#     class Meta:
#         model = User
#         fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2',
#                   'company_name', 'phone', 'address']
#
#     def __init__(self, *args, **kwargs):
#         super(ClientRegistrationForm, self).__init__(*args, **kwargs)
#         for field_name in self.fields:
#             self.fields[field_name].widget.attrs.update({'class': 'form-control'})
#
#
# class ClientLoginForm(forms.Form):
#     """Form for client login"""
#     username = forms.CharField(max_length=150)
#     password = forms.CharField(widget=forms.PasswordInput)
#
#     def __init__(self, *args, **kwargs):
#         super(ClientLoginForm, self).__init__(*args, **kwargs)
#         for field_name in self.fields:
#             self.fields[field_name].widget.attrs.update({'class': 'form-control'})
#
#
# class ClientProfileForm(forms.ModelForm):
#     """Form for editing client profile"""
#     first_name = forms.CharField(max_length=30, required=True)
#     last_name = forms.CharField(max_length=30, required=True)
#     email = forms.EmailField(max_length=254, required=True)
#
#     class Meta:
#         model = Client
#         fields = ['company_name', 'phone', 'address', 'profile_image', 'industry', 'website']
#         widgets = {
#             'address': forms.Textarea(attrs={'rows': 3}),
#         }
#
#     def __init__(self, *args, **kwargs):
#         super(ClientProfileForm, self).__init__(*args, **kwargs)
#         for field_name in self.fields:
#             self.fields[field_name].widget.attrs.update({'class': 'form-control'})
#
#         self.fields['profile_image'].widget.attrs.update({'class': 'form-control-file'})
#
#
# class ProjectForm(forms.ModelForm):
#     """Form for projects (primarily for staff use)"""
#
#     class Meta:
#         model = Project
#         fields = ['title', 'description', 'status', 'start_date', 'end_date', 'budget']
#         widgets = {
#             'description': forms.Textarea(attrs={'rows': 5}),
#             'start_date': forms.DateInput(attrs={'type': 'date'}),
#             'end_date': forms.DateInput(attrs={'type': 'date'}),
#         }
#
#     def __init__(self, *args, **kwargs):
#         super(ProjectForm, self).__init__(*args, **kwargs)
#         for field_name in self.fields:
#             self.fields[field_name].widget.attrs.update({'class': 'form-control'})
#
#
# class TaskForm(forms.ModelForm):
#     """Form for project tasks (primarily for staff use)"""
#
#     class Meta:
#         model = ProjectTask
#         fields = ['title', 'description', 'is_completed', 'due_date']
#         widgets = {
#             'description': forms.Textarea(attrs={'rows': 3}),
#             'due_date': forms.DateInput(attrs={'type': 'date'}),
#         }
#
#     def __init__(self, *args, **kwargs):
#         super(TaskForm, self).__init__(*args, **kwargs)
#         for field_name in self.fields:
#             if field_name != 'is_completed':
#                 self.fields[field_name].widget.attrs.update({'class': 'form-control'})
#
#
# class MessageForm(forms.ModelForm):
#     """Form for sending messages"""
#
#     class Meta:
#         model = Message
#         fields = ['subject', 'content']
#         widgets = {
#             'content': forms.Textarea(attrs={'rows': 5}),
#         }
#
#     def __init__(self, *args, **kwargs):
#         super(MessageForm, self).__init__(*args, **kwargs)
#         for field_name in self.fields:
#             self.fields[field_name].widget.attrs.update({'class': 'form-control'})
#
#
# class PaymentForm(forms.Form):
#     """Form for processing payments"""
#     PAYMENT_METHOD_CHOICES = (
#         ('credit_card', 'Credit Card'),
#         ('bank_transfer', 'Bank Transfer'),
#         ('paypal', 'PayPal'),
#         ('mpesa', 'M-Pesa'),
#         ('cash', 'Cash'),
#         ('other', 'Other'),
#     )
#
#     amount = forms.DecimalField(max_digits=10, decimal_places=2)
#     payment_method = forms.ChoiceField(choices=PAYMENT_METHOD_CHOICES)
#     notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
#
#     def __init__(self, *args, **kwargs):
#         super(PaymentForm, self).__init__(*args, **kwargs)
#         for field_name in self.fields:
#             self.fields[field_name].widget.attrs.update({'class': 'form-control'})
# from django import forms
# from django.contrib.auth.models import User
# from django.contrib.auth.forms import UserCreationForm
# from .models import (
#     Client, Project, ProjectTask, Message, Payment,
# )
# # Import Service models from the correct app
# from services.models import Service, ServiceFeature
#
# class ClientRegistrationForm(UserCreationForm):
#     """Form for client registration"""
#     first_name = forms.CharField(max_length=30, required=True)
#     last_name = forms.CharField(max_length=30, required=True)
#     email = forms.EmailField(max_length=254, required=True)
#     company_name = forms.CharField(max_length=100, required=False)
#     phone = forms.CharField(max_length=20, required=False)
#     address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
#
#     class Meta:
#         model = User
#         fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2',
#                   'company_name', 'phone', 'address']
#
#     def __init__(self, *args, **kwargs):
#         super(ClientRegistrationForm, self).__init__(*args, **kwargs)
#         for field_name in self.fields:
#             self.fields[field_name].widget.attrs.update({'class': 'form-control'})
#
# class ClientLoginForm(forms.Form):
#     """Form for client login"""
#     username = forms.CharField(max_length=150)
#     password = forms.CharField(widget=forms.PasswordInput)
#
#     def __init__(self, *args, **kwargs):
#         super(ClientLoginForm, self).__init__(*args, **kwargs)
#         for field_name in self.fields:
#             self.fields[field_name].widget.attrs.update({'class': 'form-control'})
#
# class ClientProfileForm(forms.ModelForm):
#     """Form for editing client profile"""
#     first_name = forms.CharField(max_length=30, required=True)
#     last_name = forms.CharField(max_length=30, required=True)
#     email = forms.EmailField(max_length=254, required=True)
#
#     class Meta:
#         model = Client
#         fields = ['company_name', 'phone', 'address', 'profile_image', 'industry', 'website']
#         widgets = {
#             'address': forms.Textarea(attrs={'rows': 3}),
#         }
#
#     def __init__(self, *args, **kwargs):
#         super(ClientProfileForm, self).__init__(*args, **kwargs)
#         for field_name in self.fields:
#             self.fields[field_name].widget.attrs.update({'class': 'form-control'})
#
#         self.fields['profile_image'].widget.attrs.update({'class': 'form-control-file'})
#
# class ProjectForm(forms.ModelForm):
#     """Form for projects (primarily for staff use)"""
#
#     class Meta:
#         model = Project
#         fields = ['title', 'description', 'status', 'start_date', 'end_date', 'budget']
#         widgets = {
#             'description': forms.Textarea(attrs={'rows': 5}),
#             'start_date': forms.DateInput(attrs={'type': 'date'}),
#             'end_date': forms.DateInput(attrs={'type': 'date'}),
#         }
#
#     def __init__(self, *args, **kwargs):
#         super(ProjectForm, self).__init__(*args, **kwargs)
#         for field_name in self.fields:
#             self.fields[field_name].widget.attrs.update({'class': 'form-control'})
#
# class TaskForm(forms.ModelForm):
#     """Form for project tasks (primarily for staff use)"""
#
#     class Meta:
#         model = ProjectTask
#         fields = ['title', 'description', 'is_completed', 'due_date']
#         widgets = {
#             'description': forms.Textarea(attrs={'rows': 3}),
#             'due_date': forms.DateInput(attrs={'type': 'date'}),
#         }
#
#     def __init__(self, *args, **kwargs):
#         super(TaskForm, self).__init__(*args, **kwargs)
#         for field_name in self.fields:
#             if field_name != 'is_completed':
#                 self.fields[field_name].widget.attrs.update({'class': 'form-control'})
#
# class MessageForm(forms.ModelForm):
#     """Form for sending messages"""
#
#     class Meta:
#         model = Message
#         fields = ['subject', 'content']
#         widgets = {
#             'content': forms.Textarea(attrs={'rows': 5}),
#         }
#
#     def __init__(self, *args, **kwargs):
#         super(MessageForm, self).__init__(*args, **kwargs)
#         for field_name in self.fields:
#             self.fields[field_name].widget.attrs.update({'class': 'form-control'})
#
# class PaymentForm(forms.Form):
#     """Form for processing payments"""
#     PAYMENT_METHOD_CHOICES = (
#         ('credit_card', 'Credit Card'),
#         ('bank_transfer', 'Bank Transfer'),
#         ('paypal', 'PayPal'),
#         ('mpesa', 'M-Pesa'),
#         ('cash', 'Cash'),
#         ('other', 'Other'),
#     )
#
#     amount = forms.DecimalField(max_digits=10, decimal_places=2)
#     payment_method = forms.ChoiceField(choices=PAYMENT_METHOD_CHOICES)
#     notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)
#
#     def __init__(self, *args, **kwargs):
#         super(PaymentForm, self).__init__(*args, **kwargs)
#         for field_name in self.fields:
#             self.fields[field_name].widget.attrs.update({'class': 'form-control'})
#
# # Service management forms should be in the services app, not client_portal
# # Moving these forms to services/forms.py would be a better approach
# # But if you need them here, use the proper import from the services app as shown above
# class ServiceForm(forms.ModelForm):
#     """Form for managing services"""
#     class Meta:
#         model = Service
#         fields = [
#             'name', 'service_type', 'short_description', 'description',
#             'features', 'icon', 'image', 'is_active'
#         ]
#         widgets = {
#             'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
#             'short_description': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
#             'features': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
#             'name': forms.TextInput(attrs={'class': 'form-control'}),
#             'icon': forms.TextInput(attrs={'class': 'form-control'}),
#             'service_type': forms.Select(attrs={'class': 'form-control'}),
#         }
#
# class ServiceFeatureForm(forms.ModelForm):
#     """Form for managing service features"""
#     class Meta:
#         model = ServiceFeature
#         fields = ['service', 'title', 'description', 'icon']
#         widgets = {
#             'service': forms.Select(attrs={'class': 'form-control'}),
#             'title': forms.TextInput(attrs={'class': 'form-control'}),
#             'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
#             'icon': forms.TextInput(attrs={'class': 'form-control'}),
#         }

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import (
    Client, Project, ProjectTask, Message, Payment,
)
# Import Service models from the services app
from services.models import Service, ServiceFeature

class ClientRegistrationForm(UserCreationForm):
    """Form for client registration"""
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)
    company_name = forms.CharField(max_length=100, required=False)
    phone = forms.CharField(max_length=20, required=False)
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2',
                  'company_name', 'phone', 'address']

    def __init__(self, *args, **kwargs):
        super(ClientRegistrationForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})

class ClientLoginForm(forms.Form):
    """Form for client login"""
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super(ClientLoginForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})

class ClientProfileForm(forms.ModelForm):
    """Form for editing client profile"""
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)

    class Meta:
        model = Client
        fields = ['company_name', 'phone', 'address', 'profile_image', 'industry', 'website']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super(ClientProfileForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})

        self.fields['profile_image'].widget.attrs.update({'class': 'form-control-file'})

class ProjectForm(forms.ModelForm):
    """Form for projects (primarily for staff use)"""

    class Meta:
        model = Project
        fields = ['title', 'description', 'status', 'start_date', 'end_date', 'budget']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})

class TaskForm(forms.ModelForm):
    """Form for project tasks (primarily for staff use)"""

    class Meta:
        model = ProjectTask
        fields = ['title', 'description', 'is_completed', 'due_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            if field_name != 'is_completed':
                self.fields[field_name].widget.attrs.update({'class': 'form-control'})

class MessageForm(forms.ModelForm):
    """Form for sending messages"""

    class Meta:
        model = Message
        fields = ['subject', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})

class PaymentForm(forms.Form):
    """Form for processing payments"""
    PAYMENT_METHOD_CHOICES = (
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('paypal', 'PayPal'),
        ('mpesa', 'M-Pesa'),
        ('cash', 'Cash'),
        ('other', 'Other'),
    )

    amount = forms.DecimalField(max_digits=10, decimal_places=2)
    payment_method = forms.ChoiceField(choices=PAYMENT_METHOD_CHOICES)
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False)

    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].widget.attrs.update({'class': 'form-control'})

# Note: Service management forms have been moved to services/forms.py