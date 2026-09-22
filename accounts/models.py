import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(
        max_length=100,
        unique=True
    )

    description = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    level = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name


class User(AbstractUser):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    email = models.EmailField(
        unique=True
    )

    first_name = models.CharField(
        max_length=150
    )

    last_name = models.CharField(
        max_length=150
    )

    company = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    department = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    employee_id = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    bio = models.TextField(
        blank=True,
        null=True
    )

    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name="users",
        null=True,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    is_staff = models.BooleanField(
        default=False
    )

    is_email_verified = models.BooleanField(
        default=False
    )

    date_joined = models.DateTimeField(
        auto_now_add=True
    )

    last_login = models.DateTimeField(
        blank=True,
        null=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.username


class EmailVerification(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="email_verifications"
    )

    secret_key = models.CharField(
        max_length=255
    )

    is_used = models.BooleanField(
        default=False
    )

    attempts = models.PositiveSmallIntegerField(
        default=0
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    expires_at = models.DateTimeField()

    verified_at = models.DateTimeField(
        blank=True,
        null=True
    )

    last_sent_at = models.DateTimeField(
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Email verification - {self.user.username}"