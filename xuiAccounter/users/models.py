from django.db import models
from django.contrib.auth.models import User

class UserMetaData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField(unique=True,null=False,blank=False)
    
    def __str__(self):
        return self.user.username