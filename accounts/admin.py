from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User

    list_display = (
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'is_active',
    )

    search_fields = (
        'email',
        'first_name',
        'last_name'
    )
    ordering = ('email',)
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'email', 'password',
                )
            }
        ),
        (
            'personal info',
            {
                'fields': (
                    'first_name',
                    'last_name',
                    'phone',
                )
            },
        ),
        (
            'Permissions',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                )
            },
        ),
        (
            'Important dates',
            {
                'fields': (
                    'last_login',
                    'date_joined',
                    'created_at',
                    'updated_at',

                )
            },
        ),
        (
            'Creation information',
            {
                'fields': (
                    'created_by_user',
                )
            },
        ),
    )

    readonly_fields = (
        'created_at',
        'updated_at',
        'last_login',
        'date_joined',
    )

    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': (
                    'email',
                    'first_name',
                    'last_name',
                    'phone',
                    'password1',
                    'password2',
                    'is_active',
                    'is_staff',
                ),
            },
        ),
    )
