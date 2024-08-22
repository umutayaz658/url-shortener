from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone


class CustomURL(models.Model):
    short_url = models.CharField(max_length=255, unique=True)
    long_url = models.URLField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    validity_period = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    one_time_only = models.BooleanField(default=False)
    password = models.CharField(max_length=100, blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith('pbkdf2_sha256$'):
            print(self.password)
            self.password = make_password(self.password)
            print(self.password)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.validity_period

    def __str__(self):
        return f"{self.short_url}  ->  {self.long_url}"
