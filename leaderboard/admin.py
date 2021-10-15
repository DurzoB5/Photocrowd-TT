from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

from .models import Competition, Submission, User


class UserAdmin(DefaultUserAdmin):
    model = User
    list_display = [
        'username',
        'is_staff',
        'is_active',
        'last_login',
    ]
    list_filter = [
        'is_staff',
        'is_active',
        'last_login',
    ]
    fieldsets = [
        (
            None,
            {'fields': ('username', 'password')},
        ),
        ('Permissions', {'fields': ['is_staff', 'is_superuser', 'is_active']}),
    ]
    add_fieldsets = [
        (
            'User Details',
            {
                'classes': ('wide',),
                'fields': ('username'),
            },
        ),
        (
            'Password Details',
            {
                'classes': ('wide',),
                'fields': ('password1', 'password2'),
            },
        ),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'is_active')}),
    ]
    search_fields = ['id', 'username']
    ordering = ['username']


class CompetitionAdmin(admin.ModelAdmin):
    model = Competition
    list_display = [
        'id',
        'name',
    ]
    search_fields = ['id', 'name']
    ordering = ['name']


class SubmissionAdmin(admin.ModelAdmin):
    model = Submission
    list_display = ['id', 'name', 'score', 'user', 'competition']
    list_filter = [
        'user',
        'competition',
    ]
    search_fields = ['name', 'user', 'competition']
    ordering = ['name']


admin.site.register(User, UserAdmin)
admin.site.register(Competition, CompetitionAdmin)
admin.site.register(Submission, SubmissionAdmin)
