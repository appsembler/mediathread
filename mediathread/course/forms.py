import autocomplete_light
from crispy_forms.layout import Submit
from crispy_forms.helper import FormHelper
from django import forms
from .models import CourseInformation, STUDENT_AMOUNT_CHOICES


class CourseForm(forms.Form):
    title = forms.CharField(
        label="Course title",
        required=True,
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
