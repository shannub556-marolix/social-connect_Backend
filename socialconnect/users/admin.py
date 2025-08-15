from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, EmailVerificationToken, PasswordResetToken, Follow

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username', 'email', 'role', 'privacy_setting', 'is_staff', 'is_active', 'is_email_verified')
    list_filter = ('role', 'privacy_setting', 'is_staff', 'is_active', 'is_email_verified')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('email', 'bio', 'avatar_url', 'website', 'location', 'privacy_setting')}),
        ('Permissions', {'fields': ('role', 'is_staff', 'is_active', 'is_email_verified', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'is_staff', 'is_active')
        }),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)

class FollowAdmin(admin.ModelAdmin):
    list_display = ("follower", "following", "created_at")
    list_filter = ("created_at",)
    search_fields = ("follower__username", "following__username")
    ordering = ("-created_at",)

admin.site.register(User, CustomUserAdmin)
admin.site.register(EmailVerificationToken)
admin.site.register(PasswordResetToken)
admin.site.register(Follow, FollowAdmin)
