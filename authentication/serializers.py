from rest_framework import serializers
from . import models 
from .models import CURRENCY_SYMBOLS

class CustomUserSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    currency = serializers.SerializerMethodField()
    class Meta:
        model = models.CustomUser
        fields = ['id','full_name','email','password','image','mobile','currency']

    def get_image(self, obj):
        request =self.context.get('request')
        image_url = request.build_absolute_uri(obj.image.url) if obj.image.url else None
        return image_url

    # def get_currency(self, obj):
    #     return CURRENCY_SYMBOLS[obj.currency]

class UserDetailSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    # status = serializers.SerializerMethodField()

    class Meta:
        model = models.CustomUser
        fields = ['id', 'full_name', 'image', 'email', 'mobile']

    # def get_image(self, obj):
    #     request = self.context.get('request')
    #     image_url = request.build_absolute_uri(obj.image.url) if obj.image else None
    #     return image_url

    def get_image(self, obj):
        request = self.context.get('request')
        image_url = request.build_absolute_uri(obj.image.url) if obj.image else None
        return image_url        

    # def get_status(self, obj):
    #     return obj.get_status_display()