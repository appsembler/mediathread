from django.contrib.auth.models import Group, User
from django.test import TestCase

from courseaffils.models import Course


class CallToActionMiddlewareTest(TestCase):
    fixtures = ['unittest_sample_course.json']

    def setUp(self):
        self.course = Course.objects.get(pk=1)

    def test_create_course_shows(self):
        self.client.login(username="test_staff", password="test")
        session = self.client.session
        session['ccnmtl.courseaffils.course'] = self.course
        session['courses_created'] = False
        session.save()
        response = self.client.get("/")
        self.assertContains(response, "Want to create your own course? Click here")

    def test_create_course_not_shown_for_instructor_with_courses(self):
        self.client.login(username="test_instructor", password="test")
        session = self.client.session
        session['ccnmtl.courseaffils.course'] = self.course
        session['courses_created'] = True
        session.save()
        response = self.client.get("/")
        self.assertNotContains(response, "Want to create your own course? Click here")

    def test_create_course_not_shown_for_students(self):
        self.client.login(username="test_student_one", password="test")
        session = self.client.session
        session['ccnmtl.courseaffils.course'] = self.course
        session['courses_created'] = True
        session.save()
        response = self.client.get("/")
        self.assertNotContains(response, "Want to create your own course? Click here")

    def test_invite_students_shows_on_empty_course(self):
        user_group = Group.objects.create(name='test_users')
        faculty_group = Group.objects.create(name='test_faculty')
        new_course = Course.objects.create(title="testcourse", group=user_group, faculty_group=faculty_group)
        user = User.objects.get(username="test_staff")
        faculty_group.user_set.add(user)
        user_group.user_set.add(user)

        self.client.login(username="test_staff", password="test")
        session = self.client.session
        session['ccnmtl.courseaffils.course'] = new_course
        session['courses_created'] = True
        session.save()
        response = self.client.get("/")
        self.assertContains(response, "You haven't invited any students to this course. Click here to invite them:")

    def test_invite_students_doesnt_show_in_course_with_students(self):
        self.client.login(username="test_instructor", password="test")
        session = self.client.session
        session['ccnmtl.courseaffils.course'] = self.course
        session['courses_created'] = True
        session.save()
        response = self.client.get("/")
        self.assertNotContains(response, "You haven't invited any students to this course. Click here to invite them:")