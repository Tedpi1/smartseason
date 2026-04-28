from django.urls import path
from .views import login_api, register_user, create_fields, update_field, field_dashboard,field_status_overview, fetch_assigned_fields


urlpatterns = [
    path('api/login/', login_api, name='login_api'),
    path('api/register/', register_user, name='register_user'),
    path('api/add_fields/', create_fields, name='create_fields'),
    path('api/update_field/<int:id>/', update_field, name='update_field'),
    path('api/count/', field_dashboard, name='field_dashboard'),
    path('api/overview/', field_status_overview, name='field_status_overview'),
    path('api/assignment/', fetch_assigned_fields, name='fetch_assigned_fields'),
]