"""
URL configuration for cloudlink_devs project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# cloudlink_devs/urls.py
from django.contrib import admin  # Keep this import for the default admin site
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# urlpatterns = [
#     path('admin/', admin.site.urls),  # Keep just one admin path
#     path('accounts/', include('django.contrib.auth.urls')),  # Django auth views
#     path('', include('core.urls')),  # Core app handles the main pages
#     path('services/', include('services.urls')),
#     path('portfolio/', include('portfolio.urls')),
#
#    path('mpesa/', include('mpesa_api.urls')),
#     path('blog/', include('blog.urls')),
#     path('quotes/', include('quotes.urls')),
#     path('chat/', include('chatbot.urls')),
#     path('client/', include('client_portal.urls')),  # Keep just one client path
#
# # path('direct-payment/crypto/<str:amount>/', views.process_direct_crypto, name='process_direct_crypto'),
# ]
#
# # Serve media files in development
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# cloudlink_devs/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('core.urls')),
    path('services/', include('services.urls')),
    path('portfolio/', include('portfolio.urls')),
    path('mpesa/', include('mpesa_api.urls')),
    path('blog/', include('blog.urls')),


    path('quotes/', include('quotes.urls')),
    path('chat/', include('chatbot.urls')),
    path('client/', include('client_portal.urls')),

#      path('crypto/', include('crypto_api.urls')),  # If you have a separate crypto app

]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)