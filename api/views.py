from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import json
from .models import UserProfile,Field
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.db.models import Count, Case, When, IntegerField

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
                "username": user.username,
                "role":user.userprofile.role
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
    
@csrf_exempt
def create_fields(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            name = data.get("field_name")
            crop_type = data.get("crop_type")
            planting_date = data.get("planting_date")
            stage = int(data.get("stage", 1))
            notes = data.get("notes", "")

            assigned_to_id = data.get("assigned_to")

            assigned_user = None
            if assigned_to_id:
                assigned_user = User.objects.get(id=assigned_to_id)

            field = Field.objects.create(
                name=name,
                crop_type=crop_type,
                planting_date=planting_date,
                stage=stage,
                notes=notes,
                assigned_to=assigned_user
            )

            return JsonResponse({
                "message": "Field created successfully",
                "field_id": field.id
            })

        except User.DoesNotExist:
            return JsonResponse({"error": "Assigned user not found"}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        
@csrf_exempt
def update_field(request, id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            field = Field.objects.get(id=id)
            if "field_name" in data:
                field.name = data["field_name"]

            if "crop_type" in data:
                field.crop_type = data["crop_type"]

            if "planting_date" in data:
                field.planting_date = data["planting_date"]

            if "stage" in data:
                field.stage = int(data["stage"])

            if "notes" in data:
                field.notes = data["notes"]

            
            if "assigned_to" in data:
                if data["assigned_to"] is None:
                    field.assigned_to = None
                else:
                    field.assigned_to = User.objects.get(id=data["assigned_to"])

            field.save()

            return JsonResponse({
                "message": "Field updated successfully",
                "field_id": field.id
            })

        except Field.DoesNotExist:
            return JsonResponse({"error": "Field not found"}, status=404)

        except User.DoesNotExist:
            return JsonResponse({"error": "Assigned user not found"}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        
@csrf_exempt
def field_dashboard(request):

    data = Field.objects.aggregate(
        healthy_count=Count(
            Case(
                When(stage__in=[2, 3], then=1),
                output_field=IntegerField()
            )
        ),
        attention_count=Count(
            Case(
                When(stage=1, then=1),
                output_field=IntegerField()
            )
        ),
        harvested_count=Count(
            Case(
                When(stage=4, then=1),
                output_field=IntegerField()
            )
        ),
        total=Count("id")
    )

    return JsonResponse({
        "healthy_and_progressing": data["healthy_count"],
        "needs_attention": data["attention_count"],
        "harvested": data["harvested_count"],
        "total_fields": data["total"]
    })

@csrf_exempt
def field_status_overview(request):

    data = Field.objects.aggregate(
        total=Count("id"),

        risk_count=Count(
            Case(
                When(stage=1, then=1),
                output_field=IntegerField()
            )
        ),

        active_count=Count(
            Case(
                When(stage__in=[2, 3], then=1),
                output_field=IntegerField()
            )
        ),

        completed_count=Count(
            Case(
                When(stage=4, then=1),
                output_field=IntegerField()
            )
        ),
    )

    total = data["total"] or 1

    risk_pct = round((data["risk_count"] / total) * 100, 2)
    active_pct = round((data["active_count"] / total) * 100, 2)
    completed_pct = round((data["completed_count"] / total) * 100, 2)

    return JsonResponse({
        "risk": {
            "count": data["risk_count"],
            "percentage": risk_pct
        },
        "active": {
            "count": data["active_count"],
            "percentage": active_pct
        },
        "completed": {
            "count": data["completed_count"],
            "percentage": completed_pct
        },
        "total_fields": data["total"]
    })