import analytics
import customerio
import textwrap
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.template.defaultfilters import pluralize
from django.utils.html import linebreaks
from django.views.generic.edit import FormView
from allauth.account.forms import SignupForm
from allauth.account.utils import send_email_confirmation
from allauth.account.utils import complete_signup
from allauth.account import app_settings
from allauth.account.views import ConfirmEmailView as AllauthConfirmEmailView
from allauth.account.views import LoginView as AllauthLoginView
from courseaffils.models import Course
from .forms import InviteStudentsForm, RegistrationForm, UserProfileForm
from .models import OrganizationModel, UserProfile


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


class LoginView(AllauthLoginView):
    def form_valid(self, form):
        # checks if the user has a default (dummypass) password so it can redirect it to the set password form
        self.default_password = form.user.check_password("dummypass")
        response = super(LoginView, self).form_valid(form)
        # check if the user is an instructor and is only in faculty group of sample course or in no course at all
        is_instructor = form.user.profile.user_type == "instructor"
        sample_course_faculty_group_id = Course.objects.get(id=settings.SAMPLE_COURSE_ID).faculty_group_id
        created_courses = Group.objects.exclude(
            id=sample_course_faculty_group_id).filter(user=form.user, name__startswith="faculty_").exists()

        # logs to the session,whether the user has created any courses, needed for call to action middleware
        if is_instructor and not created_courses:
            self.request.session['courses_created'] = False
        else:
            self.request.session['courses_created'] = True
        return response

    def get_success_url(self):
        url = "/"
        if self.default_password:
            url = reverse("set_password")
        return url

login_view = LoginView.as_view()


class ConfirmEmailView(AllauthConfirmEmailView):
    """
    View for comfirming user's email address and automatically login user
    """
    def post(self, *args, **kwargs):
        # perform login
        email_address_object = self.get_object().email_address
        user_to_login = User.objects.get(email=email_address_object.email)
        login_user(self.request, user_to_login)
        analytics.track(email_address_object.email, "Activated account")
        messages.success(self.request, "You've successfully activated your account.", fail_silently=True)
        return super(ConfirmEmailView, self).post(*args, **kwargs)


confirm_email_view = ConfirmEmailView.as_view()


class UserProfileView(FormView):
    """
    View for creating and updating profile data
    """
    form_class = UserProfileForm
    success_url = '/'
    template_name = 'user_accounts/edit_profile.html'

    def get_initial(self):
        user = self.request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
        if profile.organization:
            organization_value = profile.organization.name
        else:
            organization_value = None

        return {
            'organization': organization_value,
            'position_title': profile.position_title,
            'subscribe_to_newsletter': profile.subscribe_to_newsletter,
            'first_name': user.first_name,
            'last_name': user.last_name
        }

    def form_valid(self, form):
        user = self.request.user
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.save()

        profile, created = UserProfile.objects.get_or_create(user=user)
        old_subscription_setting = profile.subscribe_to_newsletter

        if form.cleaned_data['organization']:
            profile.organization, created = OrganizationModel.objects.get_or_create(
                name=form.cleaned_data['organization'])
            profile.organization.save()
            organization_name = profile.organization.name
        else:
            organization_name = ""

        profile.position_title = form.cleaned_data['position_title']
        profile.subscribe_to_newsletter = form.cleaned_data['subscribe_to_newsletter']
        profile.save()

        analytics.identify(
            user.email,
            {
                'email': user.email,
                'firstName': user.first_name,
                'lastName': user.last_name,
                'organization': organization_name,
            }
        )

        #if the setting has changed, we'll do an API call to Mailchimp
        if profile.subscribe_to_newsletter != old_subscription_setting:
            if profile.subscribe_to_newsletter:
                profile.newsletter_subscribe()
            else:
                profile.newsletter_unsubscribe()

        messages.success(self.request, "You've successfully updated your user profile.", fail_silently=True)
        return super(UserProfileView, self).form_valid(form)


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
        signup_form = SignupForm({
            'username': '',
            'email': form.cleaned_data['email'],
            'password1': form.cleaned_data['password'],
            'password2': form.cleaned_data['password'],
        })

        # if a new user is successfully created
        if signup_form.is_valid():
            signup_user = signup_form.save(self.request)
            signup_user.first_name = form.cleaned_data['first_name']
            signup_user.last_name = form.cleaned_data['last_name']
            signup_user.save()

            form.instance.user = signup_user
            profile = form.save()

            analytics.identify(
                signup_user.email,
                {
                    'email': signup_user.email,
                    'firstName': signup_user.first_name,
                    'lastName': signup_user.last_name,
                    'organization': profile.organization.name,
                }
            )
            analytics.track(signup_user.email, "Registered")
        else:
            self.signupform_error_msg = signup_form.errors
            signup_error = form.instance.get_form_errors()
            if 'password1' in signup_error:
                signup_error['password'] = signup_error['password1']
            form.errors.update(signup_error)
            return self.form_invalid(form)

        if profile.subscribe_to_newsletter:
            profile.newsletter_subscribe()

        return complete_signup(self.request, signup_user,
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

    def get_form_kwargs(self):
        kwargs = super(InviteStudentsView, self).get_form_kwargs()
        kwargs.update({
            'course': self.request.session['ccnmtl.courseaffils.course']
        })
        return kwargs

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
        if student_count > 0:
            self.request.session['no_students'] = False

        # update the remaining number of invites
        course.course_information.invites_left -= student_count
        course.course_information.save()

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
        course = self.request.session['ccnmtl.courseaffils.course']
        context['course_name'] = course
        context['invites_left'] = course.course_information.invites_left
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
