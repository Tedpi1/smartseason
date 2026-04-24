from django.db import models
from django.contrib.auth.models import User
import random
from django.utils import timezone

class UserProfile(models.Model):
    ADMIN = 1
    AGENT = 2

    ROLE_CHOICES = (
        (ADMIN, 'admin'),
        (AGENT, 'agent'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.IntegerField(choices=ROLE_CHOICES,default=AGENT)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.otp_created_at = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"