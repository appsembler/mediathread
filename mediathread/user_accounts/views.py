import analytics
import customerio
import textwrap
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.template.defaultfilters import pluralize
from django.utils.html import linebreaks
from django.views.generic.edit import FormView
from allauth.account.forms import SignupForm
from allauth.account.utils import send_email_confirmation
from allauth.account.utils import complete_signup
from allauth.account import app_settings
from allauth.account.views import ConfirmEmailView as AllauthConfirmEmailView
from .forms import InviteStudentsForm, RegistrationForm
from .models import OrganizationModel


def login_user(request, user):
    """
        Log in a user without requiring credentials (using ``login`` from
        ``django.contrib.auth``, first finding a matching backend).
    """
    from django.contrib.auth import load_backend, login

    if not hasattr(user, 'backend'):
        for backend in settings.AUTHENTICATION_BACKENDS:
            if user == load_backend(backend).get_user(user.pk):
                user.backend = backend
                break
    if hasattr(user, 'backend'):
        return login(request, user)


class ConfirmEmailView(AllauthConfirmEmailView):
    """
    View for comfirming user's email address and automatically login user
    """
    def post(self, *args, **kwargs):
        # perform login
        email_address = self.get_object().email_address
        user_to_login = User.objects.get(email=email_address.email)
        login_user(self.request, user_to_login)
        analytics.track(email_address, "Activated account")
        messages.success(self.request, "You've successfully activated your account.", fail_silently=True)
        return super(ConfirmEmailView, self).post(*args, **kwargs)


confirm_email_view = ConfirmEmailView.as_view()

from .forms import UserProfileForm
from .models import UserProfile, RegistrationModel
from allauth.account.forms import ChangePasswordForm


from django.contrib.auth.decorators import login_required


class UserProfileView(FormView):
    """
    View for creating and updating profile data
    """
    form_class = UserProfileForm
    success_url = '/'
    template_name = 'user_accounts/user_profile.html'
    
    def get_initial(self):
        user_instance = User.objects.get(id=self.request.user.id)
        user_registration_model = RegistrationModel.objects.get(user=user_instance)
        profile, profile_created = UserProfile.objects.get_or_create(user=user_instance, defaults={})

        organization_value = profile.organization.name if profile.organization else user_registration_model.organization.name
        position_title_value = profile.position_title if profile.position_title else user_registration_model.position_title
        subscribe_to_newsletter_value = profile.subscribe_to_newsletter if profile.subscribe_to_newsletter != None else user_registration_model.subscribe_to_newsletter

        return {
            'organization': organization_value,
            'position_title': position_title_value,
            'subscribe_to_newsletter': subscribe_to_newsletter_value,
            'first_name': user_instance.first_name,
            'last_name': user_instance.last_name
        }

    def form_valid(self, form):
        user = User.objects.get(pk=self.request.user.pk)
        profile_defaults = {}
        profile, profile_created = UserProfile.objects.get_or_create(user=user, defaults=profile_defaults)
        
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']


        if profile.organization:
            profile.organization.name = form.cleaned_data['organization']
            profile.organization.save()
        else:
            profile.organization, created = OrganizationModel.objects.get_or_create(name=form.cleaned_data['organization'])
            profile.organization.save()

        profile.position_title = form.cleaned_data['position_title']
        profile.subscribe_to_newsletter = form.cleaned_data['subscribe_to_newsletter']

        if profile.subscribe_to_newsletter:
            pass
            # TODO: subscribe user to the list
        else:
            pass
            # TODO: unsubscribe user to the list
        
        profile.save()
        
        messages.success(self.request, "You've successfully updated your user profile.", fail_silently=True)
        return super(UserProfileView, self).form_valid(form)


    def form_invalid(self, form):
        return super(UserProfileView, self).form_invalid(form)


user_profile_view = login_required(UserProfileView.as_view())



class RegistrationFormView(FormView):
    """
    View for registering new users to the application. Once the user enters
    the required data, he'll get an email with the activation link he needs to
    visit in order to activate his account.
    """
    form_class = RegistrationForm
    template_name = 'user_accounts/registration_form.html'
    success_url = '/'

    def form_valid(self, form):
        signup_params = {
            'email': form.cleaned_data['email'],
            'password': form.cleaned_data['password'],
            'organization': form.cleaned_data['organization'],
            'first_name': form.cleaned_data['first_name'],
            'last_name': form.cleaned_data['last_name']
        }
        registration = form.instance
        success = registration.do_signup(self.request, **signup_params)
        if not success:
            signup_error = registration.get_form_errors()
            if signup_error.has_key('password1'):
                signup_error['password'] = signup_error['password1']
            form.errors.update(signup_error)
            return self.form_invalid(form)
        registration.save()

        # save to profile
        profile_defaults = {
            'organization': form.cleaned_data['organization'],
            'position_title': form.cleaned_data['position_title'],
            'subscribe_to_newsletter': form.cleaned_data['subscribe_to_newsletter']
        }
        profile, profile_created = UserProfile.objects.get_or_create(user=success, defaults=profile_defaults)

        # subscribe in mailchimp
        if registration.subscribe_to_newsletter:
            registration.subscribe_mailchimp_list(
                settings.MAILCHIMP_REGISTRATION_LIST_ID)

        return complete_signup(self.request, registration.get_user(),
                               app_settings.EMAIL_VERIFICATION,
                               self.get_success_url())


registration_form = RegistrationFormView.as_view()


class InviteStudentsView(FormView):
    """
    View that handles the inviting of students to a currently active class.
    Student will get an email notifying him that he is enrolled in a class,
    as well as an activation email if he doesn't already have an account
    in the system.
    """
    form_class = InviteStudentsForm
    template_name = 'user_accounts/invite_students.html'

    def form_valid(self, form):
        course = self.request.session['ccnmtl.courseaffils.course']
        emails = form.cleaned_data['student_emails']
        cio = customerio.CustomerIO(settings.CUSTOMERIO_SITE_ID,
                                    settings.CUSTOMERIO_API_KEY)
        cio.track(
            customer_id=self.request.user.email,
            name="invited_student"
        )
        for email in emails:
            user = None
            cio.identify(
                id=email,
                email=email,
                type="Student"
            )
            analytics.identify(
                email,
                {
                    "email": email,
                    "type": "Student"
                }
            )
            try:
                user = User.objects.get(email=email)
                course.group.user_set.add(user)
            except User.DoesNotExist:
                password = "dummypass"
                signup_form = SignupForm({
                    'username': '',
                    'email': email,
                    'password1': password,
                    'password2': password,
                })
                if signup_form.is_valid():
                    user = signup_form.save(self.request)
                    course.group.user_set.add(user)
                    send_email_confirmation(self.request, user, True)
            if user:
                cio.track(
                    customer_id=user.email,
                    name='course_invite',
                    course_name=course.title,
                    invitor_name=self.request.user.get_full_name(),
                    invitor_email=form.cleaned_data['email_from'],
                    message=linebreaks(form.cleaned_data['message']),
                )
        student_count = len(emails)
        analytics.track(
            self.request.user.email,
            "Invited students",
            {
                "course_name": course.title,
                "num_of_students": student_count
            }
        )
        messages.success(self.request,
                         "You've successfully invited {0} student{1}.".format(
                             student_count, pluralize(student_count)),
                         fail_silently=True)
        return super(InviteStudentsView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(InviteStudentsView, self).get_context_data(**kwargs)
        context['course_name'] = self.request.session['ccnmtl.courseaffils.course']
        return context

    def get_initial(self):
        initial = self.initial.copy()
        initial['email_from'] = self.request.user.email
        initial['message'] = textwrap.dedent("""
        Dear students,

        It's my pleasure to invite you to the {0} class.

        If you're new to Mediathread, you'll also get an activation link in a separate email, otherwise you can just log in using your existing username and password.

        If you need help getting started, check out this <a href="http://support.appsembler.com/knowledgebase/articles/236385-mediathread-quickstart-guide-for-students">quick start guide</a> to using Mediathread

        Thanks,
        {1}
        """.format(self.request.session['ccnmtl.courseaffils.course'].title,
                   self.request.user.get_full_name()))
        return initial

    def get_success_url(self):
        return reverse('member_list')


invite_students = InviteStudentsView.as_view()
