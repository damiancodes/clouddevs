from django import forms
from .models import Service, ServiceFeature


class ServiceForm(forms.ModelForm):
    """Form for managing services"""

    class Meta:
        model = Service
        fields = [
            'name', 'service_type', 'short_description', 'description',
            'features', 'icon', 'image', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter service name'}),
            'short_description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Brief service description (200 char max)'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Detailed service description'}),
            'features': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'List main features of this service'}),
            'icon': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Font Awesome icon class (e.g., fas fa-code)'}),
            'service_type': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'custom-control-input'}),
        }

    def clean_short_description(self):
        """Ensure short description is actually short"""
        short_desc = self.cleaned_data.get('short_description')
        if short_desc and len(short_desc) > 200:
            raise forms.ValidationError("Short description must be 200 characters or less.")
        return short_desc

    def clean_icon(self):
        """Ensure icon class is provided and follows Font Awesome format"""
        icon = self.cleaned_data.get('icon')
        if not icon:
            return 'fas fa-cog'  # Default icon

        # Basic validation for Font Awesome class format
        if not ('fa-' in icon and (icon.startswith('fa ') or icon.startswith('fas ') or
                                   icon.startswith('far ') or icon.startswith('fab '))):
            raise forms.ValidationError("Icon must be a valid Font Awesome class (e.g., fas fa-code)")

        return icon


class ServiceFeatureForm(forms.ModelForm):
    """Form for managing service features"""

    class Meta:
        model = ServiceFeature
        fields = ['title', 'description', 'icon']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Feature title'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Feature description'}),
            'icon': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Font Awesome icon class (e.g., fas fa-check)'}),
        }

    def clean_icon(self):
        """Ensure icon class is provided and follows Font Awesome format"""
        icon = self.cleaned_data.get('icon')
        if not icon:
            return 'fas fa-check'  # Default icon

        # Basic validation for Font Awesome class format
        if not ('fa-' in icon and (icon.startswith('fa ') or icon.startswith('fas ') or
                                   icon.startswith('far ') or icon.startswith('fab '))):
            raise forms.ValidationError("Icon must be a valid Font Awesome class (e.g., fas fa-check)")

        return icon