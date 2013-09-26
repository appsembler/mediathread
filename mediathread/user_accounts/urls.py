from django.conf.urls import patterns, url
from django.contrib.auth.views import password_change
from django.core.urlresolvers import reverse_lazy
from .forms import SetUserPasswordForm
from .views import invite_students, registration_form, confirm_email_view, user_profile_view

urlpatterns = patterns('',
    url(r'^set_password/$',
        password_change, {
            'password_change_form': SetUserPasswordForm,
            'post_change_redirect': reverse_lazy('edit_profile'),
            'template_name': 'user_accounts/set_password.html',
        },
        name="set_password"),
    url(r'^invite_students/$',
        invite_students,
        name="invite-students"),
    url(r'^registration_form/$',
        registration_form,
        name='registration-form'),
    url(r'^confirm_email/(?P<key>\w+)/$',
        confirm_email_view,
        name='account_confirm_email'),
    url(r'^edit_profile/$',
        user_profile_view,
        name='edit_profile'),
)
