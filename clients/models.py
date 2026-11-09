from django.db import models

class Client(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    nif = models.CharField(max_length=9)
    city = models.CharField(max_length=60)
    address = models.CharField(max_length=200)
    registered_at = models.DateField()
    notes = models.TextField()

    def __str__(self):
        return self.name
