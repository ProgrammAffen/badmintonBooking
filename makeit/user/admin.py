from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['username','mobile','email','login_time','created_time']