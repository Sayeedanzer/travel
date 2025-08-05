from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
import re

def validated_expense(value):
    if value<=0:
        raise serializers.ValidationError('Expense value must be greater than zero')
def validated_budget(value):
    if value <= 0:
        raise serializers.ValidationError('Budget value must be greater than zero.')
    
def validated_tripname(value):
    if not re.match(r"^[A-Za-z\s'-]+$", value):
        raise serializers.ValidationError('Trip name must contains only letters and hyphens')
    
class TripValidator(serializers.Serializer):
    destination = serializers.CharField(required=True, allow_null=True, allow_blank=False, error_messages={
        'required':'Destination is required',
        'null':'Destination cannot be null',
        'blank':'Destination cannot be blank'
    },validators=[validated_tripname])
    start_date =serializers.DateField(required=True, allow_null=True, error_messages={
        'required':'Start date is required',
        'null':'Start date cannot be null,',
        'blank':'Start date cannot be blank'
    })
    budget = serializers.DecimalField(required=True, max_digits=15,decimal_places=2,
                                      allow_null=False,error_messages={
        'required':'Budget is required',
        'null':'Budget cannot be null'
    },validators=[validated_budget])
    
    image = serializers.ImageField(required=False, error_messages={
        'required':'image is required'
    })

HEX_COLOR_VALIDATOR = RegexValidator(
    regex=r'^#(?:[0-9a-fA-F]{3}){1,2}$',
    message="Enter a valid hex color code (e.g., #AABBCC)."
)
class CategoryValidator(serializers.Serializer):
    category_name=serializers.CharField(required=True, allow_null=True, allow_blank=True, error_messages={
        'required':'Category is required',
        'null':'Category cannot be null',
        'blank':'Category cannot be blank'
    })
    color_code = serializers.CharField(
        max_length=7,
        default="#000000",
        validators=[HEX_COLOR_VALIDATOR]
    )

def validate_payment_method(value):
    allowed_methods = ['cash', 'online']
    
    if value.lower() not in allowed_methods:
        raise ValidationError("Only 'cash' and 'online' payment methods are allowed.")
    
    return value
class ExpenseValidator(serializers.Serializer):
    trip = serializers.CharField(required=True, allow_null=True, allow_blank=True, error_messages={
        'required':'Trip is required',
        'null':'Trip cannot be null',
        'blank':'Trip cannot be blank'
    })
    expense =serializers.DecimalField(required=True,allow_null=True,max_digits=15,decimal_places=2, error_messages={
        'required':'Expense is required',
        'null':'Expense cannot be null',
        'blank':'Expense cannot be blank'
    },validators=[validated_expense])
    category = serializers.CharField(required=True, allow_null=True, allow_blank=True, error_messages={
        'required':'Categroy is required',
        'null':'Category cannot be null',
        'blank':'Categroy cannot be blank'
    })
    date= serializers.DateField(required=True, allow_null=True, error_messages={
        'required':'Date is required',
        'null':'Date cannot be null',
        'blank':'Date cannot be blank'
    })
    remarks = serializers.CharField(required=True, allow_null=True, allow_blank=True, error_messages={
        'required':'Remarks is required',
        'null':'Remarks cannot be null',
        'blank':'Remarks cannot be blank'
    })
    bill_receipt= serializers.ImageField(required=False,allow_null=True, error_messages={
        'required':'Billrecipt is required',
        'null':'bill receipt cannot be null'
    })
    payment_mode = serializers.CharField(required=True, error_messages={
        'required':'Payment method is required'
    },validators=[validate_payment_method])