from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.fields import CharField, DecimalField, URLField


class User(AbstractUser):
    pass


# Charfields max_length based on eBay
class Listing(models.Model):
    title = CharField(max_length=80)
    description = CharField(max_length=4000)
    startingbid = DecimalField(decimal_places=2, max_digits=10)
    url = URLField(blank=True, max_length=400)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    closedlisting = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title}"


class Bid(models.Model):
    bid = DecimalField(decimal_places=2, max_digits=10)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    def __str__(self):
        f"{self.bid}"


class Comments(models.Model):
    comment = CharField(max_length=80)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)

    def __str__(self):
        f"{self.comment}"
