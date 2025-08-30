from django.db import models
from django.contrib.auth.models import User

class Coin(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    number_of_coins = models.PositiveIntegerField()
