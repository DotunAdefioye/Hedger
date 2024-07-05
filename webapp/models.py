import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class CustomerUserManager(BaseUserManager):
    def _create_user(self, email, first_name, last_name, is_staff, is_supervisor, **extra_fields):
        if not email:
            raise ValueError('Email field must be set')
        email = self.normalize_email(email).lower().strip()
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_staff=is_staff,
            is_active=True,
            is_supervisor=is_supervisor,
            last_login=timezone.now(),
            date_joined=timezone.now(),
            **extra_fields
        )
        user.set_password(extra_fields.get('password'))
        user.save(using=self._db)
        return user

    def create_user(self, email, first_name, last_name, **extra_fields):
        return self._create_user(email, first_name, last_name, is_staff=False, is_supervisor=False, **extra_fields)

    def create_superuser(self, email, first_name='', last_name='', **extra_fields):
        return self._create_user(email, first_name, last_name, is_staff=True, is_supervisor=True, **extra_fields)

    def create_staff(self, email, first_name, last_name, **extra_fields):
        return self._create_user(email, first_name, last_name, is_staff=True, is_supervisor=False, **extra_fields)


class BankInfo(models.Model):
    # Define your fields here
    bank_name = models.CharField(max_length=255)
    account_number = models.CharField(max_length=255)
    ifsc_code = models.CharField(max_length=50)

    def __str__(self):
        return self.bank_name


class Record(AbstractBaseUser, PermissionsMixin):
    GENDER_NA = 'X'
    GENDER_MALE = 'M'
    GENDER_FEMALE = 'F'
    GENDER_CHOICES = (
        (GENDER_NA, 'N/A'),
        (GENDER_MALE, 'Male'),
        (GENDER_FEMALE, 'Female')
    )

    MARITAL_STATUS_NA = 'X'
    MARITAL_STATUS_SINGLE = 'S'
    MARITAL_STATUS_DIVORCE = 'D'
    MARITAL_STATUS_WIDOWED = 'W'
    MARITAL_STATUS_MARRIED = 'M'
    MARITAL_STATUS = (
        (MARITAL_STATUS_SINGLE, 'Single'),
        (MARITAL_STATUS_DIVORCE, 'Divorced'),
        (MARITAL_STATUS_WIDOWED, 'Widowed'),
        (MARITAL_STATUS_MARRIED, 'Married')
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(_('First Name'), max_length=50)
    last_name = models.CharField(_('Last Name'), max_length=50)
    email = models.EmailField(_('Email address'), unique=True)
    date_of_birth = models.DateField(_('Date of birth'), null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default=GENDER_NA)
    marital_status = models.CharField(max_length=1, choices=MARITAL_STATUS, default=MARITAL_STATUS_NA)
    phone_number = PhoneNumberField(blank=True, unique=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    one_signal_id = models.CharField(max_length=255, blank=True)
    profile_picture = models.ImageField(upload_to='accounts', null=True, blank=True)
    phone_id = models.CharField(max_length=255, unique=True, null=True, blank=True)

    # Next of kin info
    next_of_kin_name = models.CharField(_('Next of Kin Name'), max_length=255, blank=True, null=True)
    next_of_kin_phone_number = PhoneNumberField(blank=True, null=True)

    confirmed_email = models.BooleanField(default=False)
    activation_key = models.UUIDField(unique=True, default=uuid.uuid4)
    otp_code = models.PositiveIntegerField(null=True, blank=True)

    is_staff = models.BooleanField(_('staff status'), default=False)
    is_superuser = models.BooleanField(_('superuser status'), default=False)
    is_active = models.BooleanField(_('active'), default=True)

    bank_info = models.ForeignKey('webapp.BankInfo', on_delete=models.SET_NULL, blank=True, null=True)

    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    date_updated = models.DateTimeField(_('date updated'), auto_now=True)

    groups = models.ManyToManyField(
        Group,
        related_name='webapp_user_set',  # Unique related_name
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='webapp_user_permissions_set',  # Unique related_name
        blank=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomerUserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        return '{0} {1}'.format(self.first_name, self.last_name)

    def get_short_name(self):
        return self.first_name
