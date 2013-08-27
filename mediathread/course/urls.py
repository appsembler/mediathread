from django.conf.urls import include, patterns, url
from .views import *

urlpatterns = patterns('',
    url(r'create/$', course_create, name='course_create'),
    url(r'member-list/$', member_list, name='member_list'),
    url(r'promote-user/$', promote_student, name='promote_student'),
    url(r'resend-invite/$', resend_invite, name='resend_invite'),
    url(r'remove-student/$', remove_student, name='remove_student'),
    url(r'demote-faculty/$', demote_faculty, name='demote_faculty'),
)
