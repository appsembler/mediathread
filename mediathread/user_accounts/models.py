from django.db import models

# Create your models here.

class RegistrationModel(models.Model):
    HEAR_CHOICES =(
        ('CO', 'Conference'),
        ('WS', 'Web Search'),
        ('WM', 'World of mouth'),
        ('OT', 'Other')
    )
    POSITION_CHOICES = (
        ('PF', 'Professor'),
        ('ST', 'Student'),
        ('SA', 'Administrator'),
        ('IT', 'Instructional Technologist'),
        ('RD', 'Developer'),
        ('OT', 'Other')
    )

    email = models.EmailField()
    password = models.CharField(max_length=16)
    fullname = models.CharField(max_length=30)
    organization = models.ForeignKey('OrganizationModel')
    hear_mediathread_from = models.CharField(max_length=2, choices=HEAR_CHOICES)
    position_title = models.CharField(max_length=2, choices=POSITION_CHOICES)
    subscribe_to_newsletter = models.BooleanField()

    def __unicode__(self):
        return self.fullname + " from " + self.organization.name


class OrganizationModel(models.Model):
    name = models.CharField(max_length = 50)

    def __unicode__(self):
        return self.name