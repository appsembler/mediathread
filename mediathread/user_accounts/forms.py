import autocomplete_light
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder
from django.contrib.auth.forms import SetPasswordForm
from django import forms
from django.template.defaultfilters import pluralize
from django.utils.safestring import mark_safe
from .models import RegistrationModel, OrganizationModel


class RegistrationForm(forms.ModelForm):
    email = forms.EmailField()
    agree_to_term = forms.BooleanField(
        label=mark_safe('I agree to the <a href="/terms-of-use">Terms of Service</a>')
    )
    organization = forms.CharField(
        widget=autocomplete_light.TextWidget('OrganizationAutocomplete')
    )
    password = forms.CharField(
        widget=forms.PasswordInput()
    )
    first_name = forms.CharField()
    last_name = forms.CharField()

    class Meta:
        model = RegistrationModel
        widget = autocomplete_light.get_widgets_dict(RegistrationModel)
        fields = [
            'email',
            'password',
            'first_name',
            'last_name',
            'organization',
            'position_title',
            'hear_mediathread_from',
            'subscribe_to_newsletter',
            'agree_to_term',
        ]

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = '.'
        submit_button = Submit('submit', 'Create my account')
        submit_button.field_classes = 'btn btn-success'
        self.helper.add_input(submit_button)

    def clean_organization(self):
        org_name = self.cleaned_data['organization']
        if org_name:
            org_name, created = OrganizationModel.objects.get_or_create(name=org_name)
        return org_name


class InviteStudentsForm(forms.Form):
    email_from = forms.EmailField(
        label="From"
    )
    student_emails = forms.CharField(
        initial="student1@example.com\nstudent2@example.com",
        widget=forms.Textarea(
            attrs={
                'cols': 80,
                'rows': 20,
            },
        ),
        label="To (enter the student email addresses in separate lines)",
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'cols': 80, 'rows': 20})
    )

    def __init__(self, *args, **kwargs):
        self.course = kwargs.pop('course', None)
        super(InviteStudentsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = '.'
        submit_button = Submit('submit', 'Invite students')
        submit_button.field_classes = 'btn btn-success'
        self.helper.add_input(submit_button)

    def clean_student_emails(self):
        data = self.cleaned_data['student_emails'].splitlines()
        emails = []
        for email in data:
            if "@" in email:
                emails.append(email.strip())
            else:
                raise forms.ValidationError("Error in an email address")
        invites_left = self.course.course_information.invites_left
        invited_students_count = len(emails)
        if invited_students_count > invites_left:
            raise forms.ValidationError(
                mark_safe("You exceeded your available number of invitations!<br/> You have "
                          "{0} available invite{1}, but you tried to invite {2} students, "
                          '<a href="http://getmediathread.com/plans.html">click here</a> to upgrade to a larger plan.'.format(
                          invites_left, pluralize(invites_left), invited_students_count)))
        return emails


class SetUserPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(SetUserPasswordForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = '.'
        submit_button = Submit('submit', 'Set password')
        submit_button.field_classes = 'btn btn-success'
        self.helper.add_input(submit_button)

    def clean_new_password2(self):
        password = super(SetUserPasswordForm, self).clean_new_password2()
        if len(password) < 6:
            raise forms.ValidationError("Password must be longer than 6 characters.")
        return password