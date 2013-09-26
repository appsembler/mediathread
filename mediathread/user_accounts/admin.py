from django.contrib import admin
from .models import OrganizationModel, UserProfile
import autocomplete_light


class OrganizationAdmin(admin.ModelAdmin):
    class Meta:
        model = OrganizationModel


class UserProfileAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(UserProfile)

    class Meta:
        model = UserProfile


admin.site.register(OrganizationModel, OrganizationAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
