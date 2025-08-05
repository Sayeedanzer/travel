from django.urls import path
from . import views

urlpatterns = [
    path('register', views.RegisterView.as_view(), name='register'),
    path('login', views.UserLogin.as_view(), name='login'),
    path('delete-profile', views.DeleteProfileView.as_view(), name='delete-profile'),
    path('send-email-otp', views.ForgotPasswordView.as_view(), name='send-email-otp'),
    path('verify-email-otp', views.VerifyOTPView.as_view(), name='verify-email-otp'),
    path('change-password', views.ChangePasswordView.as_view(), name='change-password'),
    path('refresh-token', views.RefreshTokenView.as_view(), name='refresh-token'),
    path('user-detail', views.UserDetailView.as_view(), name='user-detail'),
    # path('currency',views.CurrencyView.as_view(), name='currency'),
    path('profile-image', views.ProfileImageView.as_view(), name='profile-image'),
    path('user-delete', views.DeleteUserProfile.as_view(), name='user-delete')
]