from rest_framework import serializers
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

# def validate_image(value):
#     if value:
#         valid_extensions = ('.jpg', '.jpeg', '.png')
#         if not value.name.lower().endswith(valid_extensions):
#             raise ValidationError(_('Invalid image format. Only JPG, JPEG, PNG are allowed.'))
        
#         max_size = 500 * 1024  # 500 KB
#         if value.size > max_size:
#             raise ValidationError(_('Image file size must be less than 500KB.'))

def email_validator(value):
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, value):
        raise ValidationError("Enter a valid Email Format.")

def validate_password(password):
    if not 8 <= len(password) <= 15:
        raise ValidationError(
            _('Password must be between 8 and 15 characters long.'),
            code='password_length'
        )

    password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%#?&])[A-Za-z\d@$!%#?&]{8,15}$'
    if not re.match(password_regex, password):
        raise ValidationError(
            _('Password must contain at least one lowercase letter, one uppercase letter, one number, and one special character.'),
            code='password_complexity'
        )
    
# def validate_password(password):
#     if not 8 <= len(password) <= 15:
#         raise ValidationError(_('Password must be between 8 and 20 characters long.'), code='password_length')

#     password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'
#     if not re.match(password_regex, password):
#         raise ValidationError(_('Password must contain at least one lowercase letter, one uppercase letter, one number, and one special character.'), code='password_complexity')
    
mobile_number_validator = RegexValidator(
        regex=r'^[6-9]\d{9}$',
        message="Mobile number must be in correct format."
    )
class RegisterValidator(serializers.Serializer):
    full_name = serializers.CharField(required=True, max_length=30, allow_blank=False, error_messages={
        'required': 'Full Name is required.',
        'blank': 'Full Name cannot be blank.'
    })
    email = serializers.EmailField(required=True, allow_blank=False, error_messages={
        'required': 'Email is required.',
        'blank': 'Email cannot be blank.'
    }, validators=[email_validator])
    password = serializers.CharField(required=True, allow_null=False, allow_blank=False, min_length=8, error_messages={
        "required": "Password is a required field.",
        "null": "Password field cannot be null.",
        "blank": "Password field cannot be empty."
    },validators=[validate_password])
    confirm_password = serializers.CharField(required=True, allow_null=False, min_length=8, error_messages={
        "required": "Password is a required field.",
        "null": "Password field cannot be null.",
        "blank": "Password field cannot be empty."
    },validators=[validate_password])
    mobile = serializers.CharField(required=False, allow_blank=True, error_messages={
        'required': 'Phone number is required.',
        'blank': 'Phone number cannot be blank.'
    },validators=[mobile_number_validator]) 
    # currency = serializers.CharField(required =False, allow_blank=True, error_messages={
    #     'required':'currency is required',
    #     'blank':'currency cannot be blank'
    # })

    def validate(self, attrs):
        data = super().validate(attrs)
        if attrs['password'] != attrs['confirm_password']:
            raise ValidationError('Password and Confirm Password doesnot match.')
        return data

class LoginValidator(serializers.Serializer):
    email = serializers.EmailField(required=True, allow_blank=False, error_messages={
        'required': 'Email is required.',
        'blank': 'Email cannot be blank.'
    },validators=[email_validator])
    password = serializers.CharField(required=True, allow_null=False, allow_blank=False, error_messages={
        "required": "Password is a required field.",
        "null": "Password field cannot be null.",
        "blank": "Password field cannot be empty."
    })
    token_type = serializers.CharField(required=False)
    # fcm_token = serializers.CharField(required=False)
    
class ForgotPasswordEmailValidator(serializers.Serializer):
    email = serializers.EmailField(required=True, allow_blank=False, allow_null=False, error_messages={
        "required": "Email is a required field.",
        "null": "Email field cannot be null.",
        "blank": "Email field cannot be empty."
    })

class VerifyOTPValidator(serializers.Serializer):
    email = serializers.EmailField(required=True, allow_blank=False, allow_null=False, error_messages={
        "required": "Email is a required field.",
        "null": "Email field cannot be null.",
        "blank": "Email field cannot be empty."
    })
    otp = serializers.CharField(required=True, allow_blank=False, error_messages={
        "required": "OTP is a required field.",
        "blank": "OTP field cannot be empty."
    })

class DeleteProfileValidator(serializers.Serializer):
    password = serializers.CharField(required=True, allow_blank=False, allow_null=False, error_messages={
        'requried': 'Password is required.',
        'null': 'Password cannot be null.',
        'blank': 'Password cannot be blank.'
    }, validators=[validate_password])

class ChangePasswordValidator(serializers.Serializer):
    email = serializers.EmailField(required=True, allow_blank=False, allow_null=False, error_messages={
        "required": "Email is a required field.",
        "null": "Email field cannot be null.",
        "blank": "Email field cannot be empty."
    })
    new_password = serializers.CharField(required=True, allow_blank=False, allow_null=False, error_messages={
        "required": "New Password is a required field.",
        "null": "New Password field cannot be null.",
        "blank": "New Password field cannot be empty."
    })
    confirm_password = serializers.CharField(required=True, allow_blank=False, allow_null=False, error_messages={
        "required": "Confirm Password is a required field.",
        "null": "Confirm Password field cannot be null.",
        "blank": "Confirm Password field cannot be empty."
    })

    def validate(self, attrs):
        data = super().validate(attrs)
        if attrs['new_password'] != attrs['confirm_password']:
            raise ValidationError('New Password and Confirm Password does not match.')
        return data
    
class RefreshTokenValidator(serializers.Serializer):
    refresh = serializers.CharField(required=True, allow_blank=False, allow_null=False, error_messages = {
        'required': 'Refresh Token is required.',
        'blank': 'Refresh Token cannot be blank.',
        'null': 'Refresh Token cannot be null.'
    })

class UpdateUserValidator(serializers.Serializer):
    full_name = serializers.CharField(required=False, allow_blank=True, error_messages={
        'required':'full name is required',
        'blank':'full name cannot be blank'
    })

    mobile = serializers.CharField(required=False, allow_blank=True, error_messages={
        'required':'mobile is required',
        'blank':'mobile cannot be blank'
    })

    image = serializers.ImageField(required=False,error_messages={
        'required':'image field is required'
    })

    email =serializers.CharField(required=False, allow_blank=True, error_messages={
        'required':'email field is required'
    })
    
    # status = serializers.CharField(required=False, allow_blank=True)

class RefreshTokenValidator(serializers.Serializer):
    refresh = serializers.CharField(required=True, allow_blank=False, allow_null=False, error_messages = {
        'required': 'Refresh Token is required.',
        'blank': 'Refresh Token cannot be blank.',
        'null': 'Refresh Token cannot be null.'
    })
class ProfileImageValidator(serializers.Serializer):
    image = serializers.ImageField(required=False, error_messages={
        'required':'image is required',
    })