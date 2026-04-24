from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import json
from .models import UserProfile
from django.utils.crypto import get_random_string
from django.core.mail import send_mail

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
            
@csrf_exempt
def register_user(request):
    if request.method == "POST":
        data = json.loads(request.body)

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = int(data.get('role'))

        # Validate role
        if role not in [UserProfile.ADMIN, UserProfile.AGENT]:
            return JsonResponse({"error": "Invalid role"}, status=400)

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        profile=UserProfile.objects.create(user=user, role=role)
        profile.generate_otp()
        
        send_mail(
            f'Hello {user.username}',
            f'Your OTP code is: {profile.otp}',
            'moroted16@gmail.com',
            [email]
        )
        # Optional: admin privileges
        if role == UserProfile.ADMIN:
            user.is_staff = True
            user.is_superuser = True
            user.save()

        return JsonResponse({"message": "User created successfully"})