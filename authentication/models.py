from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
# from django.db.models.functions import Now
from datetime import datetime
from django.db import models
import uuid
from django.utils import timezone
import pytz
from django.conf import settings
from django.utils.timezone import now

class CommonModel(models.Model):
    id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, primary_key=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True) #db_default=Now())
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def last_updated(self):
        india_tz = pytz.timezone(settings.TIME_ZONE)
        return self.modified_at.astimezone(india_tz)
    
    def created_time(self):
        india_tz = pytz.timezone(settings.TIME_ZONE)
        return self.created_at.astimezone(india_tz)
    
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        try:
            if not email:
                raise ValueError('The Email field must be set.')
            email = self.normalize_email(email)
            user = self.model(email=email, **extra_fields)
            if password:
                user.set_password(password)
            user.save(using=self._db)
            return user
        except Exception as e:
            print(e)
    
    def create_admin(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The email field must be set.')
        if not extra_fields['mobile']:
            raise ValueError('The mobile field is required.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)
    
CURRENCY_SYMBOLS = {
            "USD": "$",
            "EUR": "€",
            "GBP": "£",
            "INR": "₹",
            "JPY": "¥",
            "AUD": "A$",
            "CAD": "C$",
            "NZD": "NZ$",
            "SGD": "S$",
            "HKD": "HK$",
            "NOK": "kr",
            "KRW": "₩",
            "TRY": "₺",
            "RUB": "₽",
            "BRL": "R$",
            "ZAR": "R",
            "MYR": "RM",
            "PHP": "₱",
            "IDR": "Rp",
            "THB": "฿",
    }
    
class CustomUser(AbstractBaseUser):    

    class StatusChoices(models.TextChoices):
        ACTIVE = 'active', _('Active')
        INACTIVE = 'in_active', _("In Active")

    class GenderChoices(models.TextChoices):
        MALE = 'male', _('Male')
        FEMALE = 'female', _('Female')
        OTHERS = 'others', _('Others')  

    class CurrencyChoices(models.TextChoices):
        US_DOLLAR = "USD", _("US Dollar")
        EURO = "EUR", _("Euro")
        BRITISH_POUND = "GBP", _("British Pound")
        INDIAN_RUPEE = "INR", _("Indian Rupee")
        JAPANESE_YEN = "JPY", _("Japanese Yen")
        AUSTRALIAN_DOLLAR = "AUD", _("Australian Dollar")
        CANADIAN_DOLLAR = "CAD", _("Canadian Dollar")
        NEW_ZEALAND_DOLLAR = "NZD", _("New Zealand Dollar")
        SINGAPORE_DOLLAR = "SGD", _("Singapore Dollar")
        HONG_KONG_DOLLAR = "HKD", _("Hong Kong Dollar")
        NORWEGIAN_KRONE = "NOK", _("Norwegian Krone")
        SOUTH_KOREAN_WON = "KRW", _("South Korean Won")
        TURKISH_LIRA = "TRY", _("Turkish Lira")
        RUSSIAN_RUBLE = "RUB", _("Russian Ruble")
        BRAZILIAN_REAL = "BRL", _("Brazilian Real")
        SOUTH_AFRICAN_RAND = "ZAR", _("South African Rand")
        MALAYSIAN_RINGGIT = "MYR", _("Malaysian Ringgit")
        PHILIPPINE_PESO = "PHP", _("Philippine Peso")
        INDONESIAN_RUPIAH = "IDR", _("Indonesian Rupiah")
        THAI_BAHT = "THB", _("Thai Baht")
    
    
    id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, primary_key=True)
    full_name = models.CharField(max_length=30, null=False)
    email = models.EmailField(unique=True, null=True, blank=True)
    mobile = models.CharField(max_length=15, null=True, blank=True, unique=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True, default='profile_images/Avatar.png')
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)
    gender = models.CharField(max_length=15, choices=GenderChoices.choices, null=True)
    currency = models.CharField(max_length=15, choices=CurrencyChoices.choices, null=True, default=CurrencyChoices.INDIAN_RUPEE)
    email_otp = models.IntegerField(null=True, blank=True)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    login_attempt = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    def currency_symbol(self):
        return CURRENCY_SYMBOLS[self.currency]

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now().astimezone(timezone.get_current_timezone())
        super().save(*args, **kwargs)

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser
    
    def last_updated(self):
        return datetime.strftime(self.modified_at, "%d %b %y %I:%M %p")
