from datetime import date

import autocomplete_light
from courseaffils.models import CourseInfo
from crispy_forms.layout import Submit
from crispy_forms.helper import FormHelper
from django import forms

from .models import CourseInformation, STUDENT_AMOUNT_CHOICES

EMPTY_CHOICE = [('', '---------')]


class MemberActionForm(forms.Form):
    user_id = forms.IntegerField()


class CourseForm(forms.Form):
    # current year and 2 next
    YEAR_CHOICES = [(y, y) for y in range(date.today().year, date.today().year+3)]

    title = forms.CharField(
        label="Course title",
        required=True,
    )
    term = forms.ChoiceField(
        choices=EMPTY_CHOICE + CourseInfo.term_choices.items(),
        required=False
    )
    year = forms.ChoiceField(
        choices=EMPTY_CHOICE + YEAR_CHOICES,
        required=False
    )
    student_amount = forms.ChoiceField(
        choices=STUDENT_AMOUNT_CHOICES,
        label="How many students do you expect will enroll?",
    )
    organization = forms.CharField(
        required=True,
        widget=autocomplete_light.TextWidget('OrganizationAutocomplete')
    )

    class Meta:
        widget = autocomplete_light.get_widgets_dict(CourseInformation)

    def __init__(self, *args, **kwargs):
        super(CourseForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = '.'
        submit_button = Submit('submit', 'Create course')
        submit_button.field_classes = 'btn btn-success'
        self.helper.add_input(submit_button)
