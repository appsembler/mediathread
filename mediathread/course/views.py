import analytics
from allauth.account.models import EmailAddress
from courseaffils.models import CourseInfo
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from mediathread.user_accounts.models import RegistrationModel
from .models import CourseInformation
from .forms import CourseForm, MemberActionForm


class MemberActionView(FormView):
    http_method_names = ['post']
    form_class = MemberActionForm

    def form_valid(self, form):
        self.course = self.request.session['ccnmtl.courseaffils.course']
        self.user = get_object_or_404(User, id=form.cleaned_data['user_id'])
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('member_list')


class ResendInviteView(MemberActionView):
    def form_valid(self, form):
        response = super(ResendInviteView, self).form_valid(form)
        try:
            email = EmailAddress.objects.get(user=self.user, verified=False)
            email.send_confirmation(self.request, signup=False)
            messages.success(
                self.request,
                "You've successfully sent the activation email to {0}".format(self.user.email)
            )
        except EmailAddress.DoesNotExist:
            messages.error(self.request, "User already activated his account.")

        return response

resend_invite = ResendInviteView.as_view()


class RemoveStudentFromClassView(MemberActionView):
    def form_valid(self, form):
        response = super(RemoveStudentFromClassView, self).form_valid(form)
        if self.course.faculty_group.user_set.filter(id=self.request.user.id).exists():
            self.course.group.user_set.remove(self.user)
            messages.success(
                self.request,
                "Successfully removed {0} from the course {1}".format(
                    self.user.get_full_name(), self.course.title
                ))
        else:
            messages.error(self.request, "You must be an instructor in this course to do that.")
        return response

remove_student = RemoveStudentFromClassView.as_view()


class DemoteFacultyView(MemberActionView):
    def form_valid(self, form):
        response = super(DemoteFacultyView, self).form_valid(form)
        if self.course.faculty_group.user_set.filter(id=self.request.user.id).exists():
            self.course.faculty_group.user_set.remove(self.user)
            messages.success(
                self.request,
                "Successfully demoted {0} from the course {1}".format(
                    self.user.get_full_name(), self.course.title
                ))
        else:
            messages.error(self.request, "You must be an instructor in this course to do that.")
        return response

demote_faculty = DemoteFacultyView.as_view()


class PromoteStudentView(MemberActionView):
    def form_valid(self, form):
        response = super(PromoteStudentView, self).form_valid(form)
        if self.course.faculty_group.user_set.filter(id=self.request.user.id).exists():
            self.course.faculty_group.user_set.add(self.user)
            messages.success(
                self.request,
                "Successfully promoted {0} to faculty group on course {1}".format(
                    self.user.get_full_name(), self.course.title
                ))
        else:
            messages.error(self.request, "You must be an instructor in this course to do that.")
        return response

promote_student = PromoteStudentView.as_view()


class MemberListView(TemplateView):
    template_name = "course/members_list.html"

    def get_context_data(self, **kwargs):
        context = super(MemberListView, self).get_context_data(**kwargs)
        course = self.request.session['ccnmtl.courseaffils.course']
        context['faculty'] = course.faculty
        context['students'] = course.students
        for student in context['students']:
            try:
                EmailAddress.objects.get(user_id=student.id, verified=True)
                student.status = "Activated"
            except EmailAddress.DoesNotExist:
                student.status = "Invited"
        for instructor in context['faculty']:
            try:
                EmailAddress.objects.get(user_id=instructor.id, verified=True)
                instructor.status = "Activated"
            except EmailAddress.DoesNotExist:
                instructor.status = "Invited"
        context['members_count'] = len(context['faculty']) + len(context['students'])
        return context


member_list = MemberListView.as_view()


class CourseCreateFormView(FormView):
    """
    View that handles the creation of a new course by a logged in user.
    It stores the extra info in the CourseInformation model.
    """
    form_class = CourseForm
    template_name = 'course/create.html'
    success_url = '/'

    @method_decorator(login_required)
    def get(self, *args, **kwargs):
        return super(CourseCreateFormView, self).get(*args, **kwargs)

    def form_valid(self, form):
        # preparing data
        course_title = form.cleaned_data['title']
        course_student_amount = form.cleaned_data['student_amount']
        course_organization_name = form.cleaned_data['organization']
        term = form.cleaned_data['term']
        year = form.cleaned_data['year']

        # creating course
        course = CourseInformation(
            title=course_title,
            organization_name=course_organization_name,
            student_amount=course_student_amount)
        course.save()

        # save term and/or year data
        if term or year:
            CourseInfo.objects.create(
                course=course.course,
                term=term,
                year=year
            )

        # add user to that class as a faculty
        course.add_member(self.request.user, faculty=True)

        analytics.track(
            self.request.user.email,
            "Created a course",
            {
                "course_name": course_title,
                "predicted_student_num": course.student_amount,
                "organization": course_organization_name
            }
        )

        self.request.session['ccnmtl.courseaffils.course'] = course.course
        messages.success(self.request,
                         "You've successfully created a new course: {0}".format(course_title),
                         fail_silently=True)
        return super(CourseCreateFormView, self).form_valid(form)

    def get_initial(self):
        initial = self.initial.copy()
        try:
            initial['organization'] = self.request.user.registration_model.organization
        except RegistrationModel.DoesNotExist:
            pass
        return initial


course_create = CourseCreateFormView.as_view()
