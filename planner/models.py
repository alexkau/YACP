from django.db import models
from django.contrib.auth.models import User
from courses.models import Course
from scheduler.models import SavedSelection
from django.db.models.signals import post_save


class PlanUser(models.Model):
    user = models.OneToOneField(User,related_name="planuser")
    selections = models.OneToOneField(SavedSelection,null=True,blank=True)
    def __unicode__(self):
        return self.user.username
    # TODO: 
    # TODO: unmet requirements

class PlanCourse(models.Model):
    course = models.ForeignKey(Course)
    semester = models.IntegerField(default=0) # 1 is Fall of Freshman, 8 is Spring of Senior, 0 is not yet placed
    user = models.ForeignKey(PlanUser,related_name="planner_courses")

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        PlanUser.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
