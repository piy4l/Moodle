from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfileInfo(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)

    #additional
    date_of_birth = models.CharField(max_length = 20, blank = True)

    def __str__(self):
        return self.user.username

class Course(models.Model):
    course_id = models.IntegerField(primary_key=True)
    session_name = models.CharField(max_length = 80)
    course_title = models.CharField(max_length = 80)
    credit_hour = models.IntegerField()
    class Meta:
         db_table = "course"
