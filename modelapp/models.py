from django.db import models


class Model(models.Model):
    model_name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.model_name
