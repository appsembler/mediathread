from uuid import uuid4

from django.db import models
from django.contrib.auth.models import Group
from django.template.defaultfilters import slugify

from mediathread.user_accounts.models import OrganizationModel
from courseaffils.models import Course

STUDENT_AMOUNT_CHOICES = (
    (10, '1-9'),
    (20, '10-19'),
    (50, '20-49'),
    (100, '50-99'),
    (500, '100+')
)


class OrganizationIsEmptyException(Exception):
    """
    Organization could not be empty
    """
    pass


class GroupTypeIncorrectException(Exception):
    """
    Group type can be only member either or faculty
    """
    pass


class CourseInformation(models.Model):
    student_amount = models.IntegerField(choices=STUDENT_AMOUNT_CHOICES)
    organization = models.ForeignKey(OrganizationModel, null=True)
    course = models.ForeignKey('courseaffils.Course', null=True)
    sample_course = models.BooleanField(default=False)

    def __unicode__(self):
        if self.course:
            return self.course.title

    def __init__(self, *args, **kwargs):
        if 'organization_name' in kwargs:
            self.organization_name = kwargs.pop('organization_name')
        if 'title' in kwargs:
            self.title = kwargs.pop('title')
        super(CourseInformation, self).__init__(*args, **kwargs)

    def create_course(self):
        """
        Method to create a Course instance in from courseaffils.models
        """
        course_name_slug = slugify(self.title)
        random_uuid = uuid4()

        # create course instance in courseaffils with temporary group names
        course = Course.objects.create(
            title=self.title,
            group=Group.objects.create(name="member_{0}".format(random_uuid)),
            faculty_group=Group.objects.create(name="faculty_{0}".format(random_uuid))
        )

        # max 30 characters from the course title
        member_group_name = "member_{0}_{1}".format(course_name_slug[:30], course.id)
        faculty_group_name = "faculty_{0}_{1}".format(course_name_slug[:30], course.id)
        course.group.name = member_group_name
        course.group.save()
        course.faculty_group.name = faculty_group_name
        course.faculty_group.save()

        return course

    def add_member(self, user, faculty=False):
        """
        method for adding user into groups
        """
        member_group = self.course.group
        faculty_group = self.course.faculty_group

        member_group.user_set.add(user)
        if faculty:
            # if faculty is True, add user to faculty group
            faculty_group.user_set.add(user)

    def save(self, force_insert=False, force_update=False, using=None):
        course = self.create_course()
        c_organization, org_created = OrganizationModel.objects.get_or_create(
            name=self.organization_name)
        self.course = course
        self.organization = c_organization
        super(CourseInformation, self).save(force_insert, force_update, using)
