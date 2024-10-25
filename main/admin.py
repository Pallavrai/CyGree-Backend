from django.contrib import admin
from main.models import UserProfile,PlasticCollection,Incentive
from unfold.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group

from unfold.admin import ModelAdmin







admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    pass


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass
# admin.site.register([UserProfile,PlasticCollection,Incentive])
# # Register your models here.


@admin.register(UserProfile)
class CustomAdminClass(ModelAdmin):
    pass

