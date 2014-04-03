from django.db import models
from django.contrib.auth.models import User
from courses.models import Course, Department
from scheduler.models import SavedSelection
from django.db.models.signals import post_save


class PlanUser(models.Model):
    user = models.OneToOneField(User,related_name="planuser")
    selections = models.ForeignKey(SavedSelection,null=True,blank=True)
    first_semester = models.IntegerField(null=True,blank=True) # 0 is Spring, 1 is Summer, 2 is Fall
    first_year = models.IntegerField(null=True,blank=True)
    def __unicode__(self):
        return self.user.username
    # TODO: 
    # TODO: unmet requirements

class PlanCourse(models.Model):
    semester = models.IntegerField()
    year = models.IntegerField()
    department = models.ForeignKey(Department)
    number = models.IntegerField()
    user = models.ForeignKey(PlanUser,related_name="planner_courses")

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        PlanUser.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
