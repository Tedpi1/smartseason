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

class Field(models.Model):

    
    PLANTED = 1
    GROWING = 2
    READY = 3
    HARVESTED = 4

    STAGE_CHOICES = (
        (PLANTED, "Planted"),
        (GROWING, "Growing"),
        (READY, "Ready"),
        (HARVESTED, "Harvested"),
    )

    
    STATUS_ACTIVE = "active"
    STATUS_AT_RISK = "at_risk"
    STATUS_COMPLETED = "completed"

    STATUS_CHOICES = (
        (STATUS_ACTIVE, "Active"),
        (STATUS_AT_RISK, "At Risk"),
        (STATUS_COMPLETED, "Completed"),
    )

    name = models.CharField(max_length=100)
    crop_type = models.CharField(max_length=100)
    planting_date = models.DateField()

    stage = models.IntegerField(choices=STAGE_CHOICES, default=PLANTED)

    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={"role": "agent"},
        related_name="fields"
    )

    notes = models.TextField(blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True)


    def status(self):
        if self.stage == self.HARVESTED:
            return self.STATUS_COMPLETED
        elif self.stage in [self.READY, self.GROWING]:
            return self.STATUS_ACTIVE
        else:
            return self.STATUS_AT_RISK

    def stage_name(self):
        return self.get_stage_display()