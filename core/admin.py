from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from . import models

# Register your models here.
@admin.register(models.User)
class UserAdmin(BaseUserAdmin):
    pass
