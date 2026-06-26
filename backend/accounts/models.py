"""Custom user model for the intake portal

End users (Submitter, Committee Member, Management) authenticates through the SPA.
Admin users (Superuser, Staff) authenticate through the Django admin interface.

Reference: https://docs.djangoproject.com/en/5.2/topics/auth/customizing/
"""

import uuid

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class Role(models.TextChoices):
    """The three portal roles
    User without a role is considered Anyone for read-only access.
    """

    SUBMITTER = "submitter", "Submitter"
    COMMITTEE = "committee", "Committee Member"
    MANAGEMENT = "management", "Management"


class UserManager(BaseUserManager):
    """Custom UserManager for users to email relationship

    This overrides the default UserManager to use email as the unique identifier
    for authentication instead of username.
    """

    use_in_migrations = True

    def create_user(self, email, name, role=None, password=None, **extra_fields):
        """For the intake portal users"""

        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, name=name, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        """For the Django admin users
        (system managers, developers, other staffs, etc.)
        """

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, name, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """A custom Intake Portal user model

    User gets authenticated by email and authorized by Role
    AbstractBaseUser supplies password hashing and last_login
    PermissionsMixin supplies is_superuser (Django's native groups/permissions is not used)
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=Role.choices, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.email
