from django.db import models
from django.contrib.auth.models import User
from courses.models import Course
# Create your models here.

class PlanCourse(models.Model):
    course = models.OneToOneField(Course)


class PlanUser(models.Model):
    user = models.OneToOneField(User)
    courses_taken = models.ManyToManyField(PlanCourse)
    # TODO: 
    # TODO: unmet requirements
