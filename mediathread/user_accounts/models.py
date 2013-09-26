from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from .utils import add_email_to_mailchimp_list, unsubscribe_user_from_list

HEAR_CHOICES = (
    ('conference', 'Conference'),
    ('web_search', 'Web Search'),
    ('word_of_mouth', 'Word of mouth'),
    ('other', 'Other')
)
POSITION_CHOICES = (
    ('professor', 'Professor'),
    ('student', 'Student'),
    ('administrator', 'Administrator'),
    ('instructional_technologist', 'Instructional Technologist'),
    ('developer', 'Developer'),
    ('other', 'Other')
)
USER_TYPES = (
    ('student', 'student'),
    ('instructor', 'instructor')
)


class UserProfile(models.Model):
    user = models.OneToOneField(User, null=True, related_name="profile")
    organization = models.ForeignKey('OrganizationModel', null=True)
    subscribe_to_newsletter = models.BooleanField(default=False)
    position_title = models.CharField(max_length=30, choices=POSITION_CHOICES, blank=True)
    user_type = models.CharField(max_length=15, choices=USER_TYPES, default='student')

    def __unicode__(self):
        name = self.user.get_full_name() or self.user.username
        return u"{0} ({1})".format(name, self.user_type)

    def newsletter_subscribe(self):
        mailchimp_fields = {
            'title': dict(POSITION_CHOICES)[self.position_title],
            'org': self.organization.name,
            'fname': self.user.first_name,
            'lname': self.user.last_name
        }
        try:
            add_email_to_mailchimp_list(
                self.user.email,
                settings.MAILCHIMP_REGISTRATION_LIST_ID,
                **mailchimp_fields
            )
            self.subscribe_to_newsletter = True
            self.save()
            return True
        except Exception as e:
            self.subscribe_to_newsletter = False
            self.save()
            return False

    def newsletter_unsubscribe(self):
        try:
            unsubscribe_user_from_list(
                self.user.email,
                settings.MAILCHIMP_REGISTRATION_LIST_ID
            )
            self.subscribe_to_newsletter = False
            self.save()
            return True
        except Exception:
            self.subscribe_to_newsletter = True
            self.save()
            return False


class OrganizationModel(models.Model):
    name = models.CharField(unique=True, max_length=50)

    def __unicode__(self):
        return self.name
