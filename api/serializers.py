from rest_framework import serializers
from . import models
import re

class TripSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model= models.Trip
        fields=['id','destination','start_date','budget', 'image']

    def get_image(self, obj):
        request =self.context.get('request')
        image_url = request.build_absolute_uri(obj.image.url) if obj.image else None
        return image_url


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Category
        fields=['id','category_name','is_default','color_code']

    def validate_color_code(self, value):
        if not re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', value):
            raise serializers.ValidationError("Invalid hex color code.")
        return value

class ExpenseSerializer(serializers.ModelSerializer):
    bill_receipt = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.category_name', read_only=True)
    trip = serializers.PrimaryKeyRelatedField(queryset=models.Trip.objects.all()) 
    category = serializers.PrimaryKeyRelatedField(queryset=models.Category.objects.all())

    class Meta:
        model = models.Expense
        fields = ['id', 'expense', 'category', 'date', 'remarks', 'payment_mode', 'category_name', 'trip','bill_receipt']

    def get_bill_receipt(self, obj):
        request = self.context.get('request')
        if obj.bill_receipt:
            return request.build_absolute_uri(obj.bill_receipt.url)
        return None
    
class PreviousTripSerializer(serializers.ModelSerializer):
    expenses = serializers.SerializerMethodField()

    class Meta:
        model = models.Trip
        fields = ['id', 'destination', 'start_date', 'expenses']

    def get_expenses(self, obj):
        from .models import Expense 
        from .serializers import ExpenseSerializer

        expenses = Expense.objects.filter(trip=obj)
        return ExpenseSerializer(expenses, many=True, context=self.context).data


    