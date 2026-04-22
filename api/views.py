from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def login_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        username = data.get('username')
        password = data.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            return JsonResponse({
                "status": "success",
                "message": "Login successful",
                "user_id": user.id,
                "username": user.username
            })
        else:
            return JsonResponse({
                "status": "error",
                "message": "Invalid credentials"
            }, status=401)