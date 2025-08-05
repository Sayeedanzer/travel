from django.contrib.auth.forms import UserCreationForm
from django.contrib import admin
from . import models
from django.contrib.auth.admin import UserAdmin

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = models.CustomUser
        fields = ('full_name', 'email', 'mobile', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].required = True
        self.fields['password2'].required = True

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'mobile')}), 
        ('Permissions', {'fields': ('is_superuser', 'is_admin', 'is_staff', 'is_blocked', 'is_active')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'mobile', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'full_name', 'mobile', 'is_superuser', 'is_active', 'last_updated')  
    list_filter = ('is_superuser', 'is_active')  
    search_fields = ('email', 'full_name', 'mobile')
    ordering = ('email',)
    filter_horizontal = ()

admin.site.register(models.CustomUser, CustomUserAdmin)
