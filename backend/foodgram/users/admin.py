from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User, Subscription
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

#admin.site.unregister(User)
class UserAdmin(DefaultUserAdmin):
    search_fields=['username', 'email']

admin.site.register(User, UserAdmin) 
admin.site.register(Subscription)