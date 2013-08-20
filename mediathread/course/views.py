import analytics
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView

from mediathread.user_accounts.models import RegistrationModel
from .models import CourseInformation
from .forms import CourseForm


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

        # creating course
        course = CourseInformation(
            title=course_title,
            organization_name=course_organization_name,
            student_amount=course_student_amount)
        course.save()

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
