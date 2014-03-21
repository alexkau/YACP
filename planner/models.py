from django.db import models
from django.contrib.auth.models import User
from courses.models import Course
from scheduler.models import SavedSelection
from django.db.models.signals import post_save

class PlanCourse(models.Model):
    course = models.OneToOneField(Course)


class PlanUser(models.Model):
    user = models.OneToOneField(User)
    selections = models.OneToOneField(SavedSelection,null=True,blank=True)
    #courses_taken = models.ManyToManyField(PlanCourse,null=True,blank=True)
    def __unicode__(self):
    	return self.user.username
    # TODO: 
    # TODO: unmet requirements

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        PlanUser.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)