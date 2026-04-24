from django.urls import path
from .views import login_api, register_user

urlpatterns = [
    path('api/login/', login_api, name='login_api'),
    path('api/register/', register_user, name='register_user'),
]