from django import forms
from .models import QuoteRequest, Service, ServiceFeature


class QuoteRequestForm(forms.ModelForm):
    """Form for client quote requests"""

    class Meta:
        model = QuoteRequest
        fields = [
            'name', 'email', 'phone', 'company',
            'service', 'features', 'requirements',
            'budget', 'timeline'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Phone Number'}),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Company (optional)'}),
            'service': forms.Select(attrs={'class': 'form-control'}),
            'features': forms.CheckboxSelectMultiple(),
            'requirements': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your project requirements'}),
            'budget': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your budget range (optional)'}),
            'timeline': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Your preferred timeline (optional)'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make some fields optional
        self.fields['features'].required = False
        self.fields['requirements'].required = False
        self.fields['budget'].required = False
        self.fields['timeline'].required = False
        self.fields['phone'].required = False
        self.fields['company'].required = False

        # Add help texts
        self.fields['service'].help_text = "Select the service you're interested in"
        self.fields['features'].help_text = "Select the features you need for your project"
        self.fields['budget'].help_text = "e.g., $5,000-$10,000 or 'Flexible'"
        self.fields['timeline'].help_text = "e.g., 'Within 3 months' or 'Flexible'"

        # If there's session data from the estimator, pre-select service and features
        if 'request' in kwargs and hasattr(kwargs['request'], 'session'):
            session = kwargs['request'].session
            if 'estimator_data' in session:
                data = session['estimator_data']
                if 'service_id' in data:
                    self.fields['service'].initial = data['service_id']
                if 'feature_ids' in data:
                    self.fields['features'].initial = data['feature_ids']

    def clean(self):
        cleaned_data = super().clean()
        service = cleaned_data.get('service')
        features = cleaned_data.get('features', [])

        # Ensure that all required features for the selected service are included
        if service:
            required_features = service.features.filter(is_required=True)
            for feature in required_features:
                if feature not in features:
                    self.add_error('features', f"The feature '{feature.name}' is required for {service.name}")

        return cleaned_data


class ServiceEstimatorForm(forms.Form):
    """Form for interactive service estimator"""
    service = forms.ModelChoiceField(
        queryset=Service.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'service-selector'}),
        empty_label="Select a service"
    )

    features = forms.ModelMultipleChoiceField(
        queryset=ServiceFeature.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'feature-checkbox'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If a service is selected, filter features by that service
        if 'service' in self.data:
            try:
                service_id = int(self.data.get('service'))
                self.fields['features'].queryset = ServiceFeature.objects.filter(service_id=service_id)
            except (ValueError, TypeError):
                pass
        elif self.initial.get('service'):
            self.fields['features'].queryset = ServiceFeature.objects.filter(service=self.initial['service'])