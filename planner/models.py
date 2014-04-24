from django.db import models
from django.contrib.auth.models import User
from courses.models import Course
from courses.models import  Department
from scheduler.models import SavedSelection
from django.db.models.signals import post_save

# PlanUser holds a user's data related to the planner
class PlanUser(models.Model):
    user = models.OneToOneField(User, related_name="planuser")
    selections = models.ForeignKey(SavedSelection, null=True, blank=True)
    has_uploaded_capp = models.BooleanField(default=False)
    # 0 is Spring, 1 is Summer, 2 is Fall
    first_semester = models.IntegerField(null=True, blank=True)
    first_year = models.IntegerField(null=True, blank=True)
    def __unicode__(self):
        return self.user.username
    # TODO: unmet requirements

# PlanCourse is a course in the PlanUser's planner.
class PlanCourse(models.Model):
    semester = models.IntegerField()
    year = models.IntegerField()
    department = models.ForeignKey(Department)
    number = models.IntegerField()
    user = models.ForeignKey(PlanUser, related_name="planner_courses")
    movable = models.BooleanField(default=True)
    spring_difficulty = models.DecimalField(max_digits=2, decimal_places=1, null=True)
    fall_difficulty = models.DecimalField(max_digits=2, decimal_places=1, null=True)
    credits = models.IntegerField(default=4)

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        PlanUser.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
