from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.backends import BaseBackend
from django.db.models import Q
from django.utils.timezone import now
from rest_framework.exceptions import ValidationError
from authentication.models import CustomUser


class AuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = CustomUser.objects.get(Q(email=username) | Q(mobile=username))

            if password:
                if not user.check_password(password):
                    raise ValidationError("Password didn't match.")

            if not user.is_active:
                raise ValidationError("This account is marked not active, please contact admin.")

            if user.is_blocked:
                raise ValidationError("This account has been blocked, please contact admin.")

            user.last_login = now()
            user.save()
            return user

        except CustomUser.DoesNotExist:
            raise ValidationError("No user found with the given email or mobile.")

    def get_user(self, user_id: int) -> AbstractBaseUser | None:
        try:
            return CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            raise ValidationError("No user found with the given ID.")
