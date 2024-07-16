from django.db import models
from userapp.models import UserProfile


class Address(models.Model):
    address_name = models.CharField(max_length=100)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.address_name
