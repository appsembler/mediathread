# Django
from django.views.generic.edit import FormView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import Group, User

# app
from mediathread.user_accounts.models import *
from courseaffils.models import Course
from .models import *
from .forms import *

# libs
from uuid import uuid4


class CourseCreateFormView(FormView):
    form_class = CourseForm
    template_name = 'course/create.html'
    success_url = '/'

    @method_decorator(login_required)
    def get(self, *args, **kwargs):
        return super(CourseCreateFormView, self).get(*args, **kwargs)


    def form_valid(self, form):
        # preparing data
        registration_record = RegistrationModel.objects.get(user=self.request.user)
        course_title = form.cleaned_data['title']
        course_student_amount = form.cleaned_data['student_amount']

        # ensure the organization
        course_organization, org_created = OrganizationModel.objects.get_or_create(name=form.cleaned_data['organization'])

        ## the following code are for creating a course, should be refactored later into utils.py
        # create both student and facultu group for the course to be created
        student_group = Group.objects.create(name="student_%s" % uuid4())
        faculty_group = Group.objects.create(name="faculty_%s" % uuid4())

        # get user instance in session
        user = self.request.user  # TODO

        # faculties should join faculty group
        user.groups.add(faculty_group)
        user.groups.add(student_group)
        user.save()
        created_course = Course.objects.create(
            group=student_group,
            faculty_group=faculty_group,
            title=course_title)
        created_course.save()

        # create an information record for operations
        course_info = CourseInformation.objects.create(
                course=created_course,
                organization = course_organization,
                student_amount = course_student_amount)
        course_info.save()

        self.request.session['ccnmtl.courseaffils.course'] = created_course

        return super(CourseCreateFormView, self).form_valid(form)


course_create = CourseCreateFormView.as_view()
