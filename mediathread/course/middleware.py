from django.conf import settings


class CallToActionMiddleware(object):
    """
    This is more of a one-time thing since we can't change the courseaffils select course view
    so when the user logs in and selects a course, we check how many students are in that course
    and set the session variable accordingly. Needs to be checked again if the user selects
    another course.
    """
    def process_request(self, request):
        if 'set_course' in request.REQUEST or 'unset_course' in request.GET:
            request.session.pop('no_students', False)

        if not request.is_ajax() and request.user.is_authenticated() and \
                request.session.get('courses_created', False) and not 'no_students' in request.session:
            # check how many students are in the currently active course (created by them)
            if request.course and request.course.id != settings.SAMPLE_COURSE_ID and\
                    request.course.is_faculty(request.user):
                student_count = len(request.course.students)
                if student_count == 0:
                    request.session['no_students'] = True
                else:
                    request.session['no_students'] = False
        return None
