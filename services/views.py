from django.shortcuts import render

def overview(request):
    """Render the services overview page"""
    return render(request, 'services/overview.html')

def web_development(request):
    """Render the web development services page"""
    return render(request, 'services/web_development.html')

def app_development(request):
    """Render the app development services page"""
    return render(request, 'services/app_development.html')

def pos_systems(request):
    """Render the POS systems services page"""
    return render(request, 'services/pos_system.html')