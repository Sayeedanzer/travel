from rest_framework.views import APIView
from core.response import Response
from . import models, validators
from core.exceptions import SerializerError
from django.contrib.auth import authenticate, login
from core import general, messages
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import random
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from rest_framework_simplejwt.tokens import RefreshToken
from . import serializers
from .models import CURRENCY_SYMBOLS
import os
from rest_framework.exceptions import ValidationError

class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        context = {
            'success': 1,
            'message': 'User registered successfully',
            'data': {}
        }
        try:
            req_params = request.data
            print(req_params)
            validator = validators.RegisterValidator(data=req_params)
            if not validator.is_valid():
                raise SerializerError(validator.errors)
            validated_data = validator.validated_data
            if models.CustomUser.objects.filter(email=validated_data['email']).exists():
                raise Exception('Email is already registered.')
            if models.CustomUser.objects.filter(mobile=validated_data['mobile']).exists():
                raise Exception('Mobile number is already registered.')
            del validated_data['confirm_password']
            user = models.CustomUser.objects.create_user(**validated_data)
            if not user:
                raise Exception('Unable to register user.')
        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)
        return Response(context)
       
# class UserLogin(APIView):
#     authentication_classes = []
#     permission_classes = []

#     def post(self, request):
#         context = {
#             'success': 1,
#             'message': 'Successfully Logged in.',
#             'data': {}
#         }
#         try:
#             req_params = request.data
#             validator = validators.LoginValidator(data=req_params)
#             if not validator.is_valid():
#                 raise SerializerError(validator.errors)
#             validated_data = validator.validated_data
#             if not models.CustomUser.objects.filter(email=validated_data['email']).exists():
#                 raise Exception('No User Found with the given email.')
#             user = authenticate(request, username=validated_data['email'], password=validated_data['password'])
#             if not user:
#                 raise Exception('Invalid email or password.')
#             tokens = general.get_tokens_for_user(user)
#             context['data'] = {**context['data'], **tokens}
#         except Exception as e:
#             context['success'] = 0
#             context['message'] = str(e)
#         return Response(context)

class UserLogin(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        context = {
            'success': 1,
            'message': 'Successfully Logged in.',
            'data': {}
        }

        try:
            req_params = request.data
            validator = validators.LoginValidator(data=req_params)

            if not validator.is_valid():
                raise SerializerError(validator.errors)

            validated_data = validator.validated_data

            if not models.CustomUser.objects.filter(email=validated_data['email']).exists():
                raise Exception('No User Found with the given email.')

            user = authenticate(request, username=validated_data['email'], password=validated_data['password'])

            if not user:
                raise Exception('Invalid email or password.')

            tokens = general.get_tokens_for_user(user)
            context['data'] = tokens

        except ValidationError as e:
            context['success'] = 0
            context['message'] = self._get_clean_error_message(e)

        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)

        return Response(context)

    def _get_clean_error_message(self, exc):
        detail = getattr(exc, 'detail', str(exc))
        if isinstance(detail, dict):
            first_key = next(iter(detail))
            first_error = detail[first_key]
            return str(first_error[0] if isinstance(first_error, list) else first_error)
        elif isinstance(detail, list):
            return str(detail[0])
        return str(detail)

class DeleteProfileView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        context = {
            'success': 1,
            'message': 'Successfully deleted profile.',
            'data': {}
        }
        try:
            user = request.user
            if not user:
                raise Exception('Not a registered user.')
            validator = validators.DeleteProfileValidator(data=request.data)
            if not validator.is_valid():
                raise SerializerError(validator.errors)
            validated_data = validator.validated_data
            if not user.check_password(validated_data['password']):
                raise Exception('Password is incorrect to delete profile.')
            user.is_active = False
            user.save() 
        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)
        return Response(context)

class ForgotPasswordView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        context = {
            'success': 1,
            'message': 'OTP sent to the Email.',
            'data': {}
        }
        try:
            validator = validators.ForgotPasswordEmailValidator(data=request.data)
            if not validator.is_valid():
                raise SerializerError(validator.errors)
            validated_data = validator.validated_data
            user = models.CustomUser.objects.filter(email__iexact=validated_data['email'],is_active=True).first()
            if not user:
                raise Exception('Not a registered user.')
            otp = random.randint(100000, 999999)
            user.email_otp = otp
            user.save()
            template_data = { "payload": user, "otp": user }
            html_content = render_to_string("authentication/otp_email.html", template_data)
            alternative_text = f"To change your password for login, please use the One-Time Password (OTP): {user.email_otp}"
            email = EmailMultiAlternatives("Email Verification.", alternative_text, settings.EMAIL_HOST_USER, [validated_data['email']])
            email.attach_alternative(html_content, 'text/html')
            email.send()
        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)
        return Response(context)
    
class VerifyOTPView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        context = {
            'success': 1,
            'message': 'OTP verified successfully.',
            'data': {}
        }
        try:
            validator = validators.VerifyOTPValidator(data=request.data)
            if not validator.is_valid():
                raise SerializerError(validator.errors)
            validated_data = validator.validated_data
            user = models.CustomUser.objects.filter(email__iexact=validated_data['email'],is_active=True).first()
            if not user:
                raise Exception('Not a registered user.')
            if not user.email_otp == int(validated_data['otp']):
                raise Exception('OTP did not match.')
            user.email_otp = None
            user.save()
        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)
        return Response(context)
    
class ChangePasswordView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        context = {
            'success': 1,
            'message': 'Successfully updated the password.',
            'data': {}
        }
        try:
            validator = validators.ChangePasswordValidator(data=request.data)
            if not validator.is_valid():
                raise SerializerError(validator.errors)
            validated_data = validator.validated_data
            user = models.CustomUser.objects.filter(email__iexact=validated_data['email'],is_active=True).first()
            if not user:
                raise Exception('Not a registered user.')
            if not validated_data['new_password'] == validated_data['confirm_password']:
                raise Exception('New Password and Confirm Password does not match.')
            user.set_password(validated_data['confirm_password'])
            user.save()
        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)
        return Response(context)
    
class RefreshTokenView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        context = {
            'success': 1,
            'message': 'Successfully generated the updated tokens.',
            'data': {}
        }
        try:
            req_data = request.data
            validator = validators.RefreshTokenValidator(data=req_data)
            if not validator.is_valid():
                raise SerializerError(validator.errors)
            validated_data = validator.validated_data
            refresh = validated_data['refresh']
            decoded_refresh = RefreshToken(refresh)
            user_obj = models.CustomUser.objects.filter(id=decoded_refresh['user_id'], is_active=True).first()
            if not user_obj:
                raise Exception('User not found')
            tokens = general.get_tokens_for_user(user_obj)
            context['data'] = {**context['data'], **tokens}
        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)
        return Response(context)

class UserDetailView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        context = {
            'success': 1,
            'message': messages.DATA_FOUND,
            'data': {}
        }         
        try:
            user_obj = models.CustomUser.objects.filter(id=request.user.id, is_active=True).first()
            serializer = serializers.UserDetailSerializer(user_obj, context={'request': request})
            context['data'] = serializer.data
        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)
        return Response(context)
    
    def put(self, request):
        context = {
            'success': 1,
            'message': messages.DATA_UPDATED,
            'data': {}
        }

        try:
            user_obj = models.CustomUser.objects.filter(id=request.user.id).first()
            if not user_obj:
                raise Exception("User not found.")

            data = request.data.copy()

            validator = validators.UpdateUserValidator(data=data)
            if not validator.is_valid():
                raise SerializerError(validator.errors)

            validated_data = validator.validated_data

            # Update validated fields
            for key, value in validated_data.items():
                setattr(user_obj, key, value)

            # Handle image upload
            if 'image' in request.FILES:
                user_obj.image = request.FILES['image']

            user_obj.save()

            # ✅ Serialize user after update to avoid returning raw file
            serializer = serializers.UserDetailSerializer(user_obj, context={'request': request})
            context['data'] = serializer.data

        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)

        return Response(context)

    
    # def put(self, request):
    #     context = {
    #         'success': 1,
    #         'message': messages.DATA_UPDATED,
    #         'data': {}
    #     }

    #     try:
    #         user_obj = models.CustomUser.objects.filter(id=request.user.id).first()
    #         if not user_obj:
    #             raise Exception("User not found.")

    #         data = request.data.copy()

    #         validator = validators.UpdateUserValidator(data=data)
    #         if not validator.is_valid():
    #             raise SerializerError(validator.errors)

    #         validated_data = validator.validated_data

    #         for key, value in validated_data.items():
    #             setattr(user_obj, key, value)

    #         if 'image' in request.FILES:
    #             user_obj.image = request.FILES['image']

    #         user_obj.save()

    #     except Exception as e:
    #         context['success'] = 0
    #         context['message'] = str(e)

    #     return Response(context)
    
class DeleteUserProfile(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        context = {
            'success': 1,
            'message': messages.DATA_DELETED,
            'data': {}
        }

        try:
            user = request.user

            user.is_active = False
            user.save()

        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)

        return Response(context)

            

    
    # def put(self, request):
    #     context = {
    #         'success': 1,
    #         'message': messages.DATA_UPDATED,
    #         'data': {}
    #     }
    #     try:
    #         user_obj = models.CustomUser.objects.filter(id=request.user.id).first()

    #         # Remove image from request.data if present
    #         data = request.data.copy()
    #         data.pop('image', None)  # Just ignore image if sent

    #         validator = validators.UpdateUserValidator(data=data)
    #         if not validator.is_valid():
    #             raise SerializerError(validator.errors)

    #         validated_data = validator.validated_data
    #         for key, value in validated_data.items():
    #             setattr(user_obj, key, value)

    #         user_obj.save()

    #     except Exception as e:
    #         context['success'] = 0
    #         context['message'] = str(e)
    #     return Response(context)

    
class RefreshTokenView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        context = {
            'success': 1,
            'message': 'Successfully generated the updated tokens.',
            'data': {}
        }
        try:
            req_data = request.data
            validator = validators.RefreshTokenValidator(data=req_data)
            if not validator.is_valid():
                raise SerializerError(validator.errors)
            validated_data = validator.validated_data
            refresh = validated_data['refresh']
            decoded_refresh = RefreshToken(refresh)
            user_obj = models.CustomUser.objects.filter(id=decoded_refresh['user_id'], is_active=True).first()
            if not user_obj:
                raise Exception('User not found')
            tokens = general.get_tokens_for_user(user_obj)
            context['data'] = {**context['data'], **tokens}
        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)
        return Response(context)
    
# class CurrencyView(APIView):
#     authentication_classes=[]
#     permission_classes=[]

#     def get(self ,request):
#         context={
#             'success':1,
#             'message':messages.DATA_FOUND,
#             'data':{}
#         }
#         try:
#             currency_obj=models.CustomUser.CurrencyChoices.choices
#             currency_option=[]
#             for currency in currency_obj:
#                 currency_dict = {
#                     'key': CURRENCY_SYMBOLS[currency[0]],  
#                     'value': currency[1]
#                 }
#                 currency_option.append(currency_dict)
#             context['data']=currency_option
#         except Exception as e:
#             context['success']=0
#             context['message']=str(e)
#         return Response(context)
    
class ProfileImageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        context = {
            'success': 1,
            'message': messages.DATA_UPDATED,
            'data': {}
        }
        try:
            user = request.user
            serializer = serializers.CustomUserSerializer(user, context={'request': request})
            context['data'] = {
                'id':serializer.data.get('id'),
                'image': serializer.data.get('image')
            }
        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)
        return Response(context)
    
    def put(self, request):
        context = {
            'success': 1,
            'message': 'Image updated successfully',
            'data': {}
        }
        try:
            user = request.user
            image = request.FILES.get('image')
            if not image:
                raise Exception('No image file provided')

            # Delete old image if exists
            if user.image:
                old_path = user.image.path
                user.image.delete(save=False)
                if os.path.exists(old_path):
                    os.remove(old_path)

            user.image = image
            user.save()

            serializer = serializers.CustomUserSerializer(user, context={'request': request})
            context['data'] = {
                'id': serializer.data.get('id'),
                'image': serializer.data.get('image')
            }
        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)
        return Response(context)
    
    def delete(self, request):
        context = {
            'success': 1,
            'message': 'Image deleted successfully',
            'data': {}
        }
        try:
            user = request.user
            if user.image:
                image_path = user.image.path
                user.image.delete(save=False)  # Deletes reference in DB
                if os.path.exists(image_path):
                    os.remove(image_path)  # Deletes file from storage
                user.save()
            else:
                context['success'] = 0
                context['message'] = 'No image to delete'
        except Exception as e:
            context['success'] = 0
            context['message'] = str(e)
        return Response(context)
            

    

            
