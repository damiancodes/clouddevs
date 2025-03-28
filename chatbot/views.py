from django.shortcuts import render
from django.http import JsonResponse


def chat_interface(request):
    return render(request, 'chatbot/chat_interface.html', {'title': 'Chat with Us'})


def send_message(request):
    # Placeholder for API endpoint
    if request.method == 'POST':
        # Will process chat message here later
        return JsonResponse({'status': 'success', 'message': 'Message received (placeholder)'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


from django.shortcuts import render

# Create your views here.
