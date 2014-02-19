from django.db import models
from scheduler.models import SavedSelection
# Create your models here.

def YacsUser(AbstractBaseUser):
    email_address = models.EmailField(unique=True,db_index=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    saved_courses = models.OneToOneField(SavedSelection)

    USERNAME_FIELD = 'email_address'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        return self.first_name+" "+self.last_name
    def get_short_name(self):
        return self.first_name
    is_active = True
