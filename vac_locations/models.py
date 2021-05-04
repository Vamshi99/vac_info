from django.db import models

# Create your models here.

class Subscription(models.Model):
    district_id = models.IntegerField()
    email_id = models.EmailField(max_length=254)