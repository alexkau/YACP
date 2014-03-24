from django.db import models
from django.contrib.auth.models import User
from courses.models import Course
from scheduler.models import SavedSelection
# Create your models here.


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
