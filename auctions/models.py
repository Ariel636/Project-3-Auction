from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

# Create your models here.
class User(AbstractUser):
    pass


class Category(models.Model):
    catname = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.catname}"


class Listing(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userlistings")
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=128)
    bid = models.FloatField()
    bids = models.IntegerField(default=0)
    category = models.ForeignKey(Category, max_length=64, on_delete=models.CASCADE, blank=True, null=True, related_name="categorylistings")
    image = models.CharField(max_length=256, blank=True)
    created = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.id} - {self.title} - {self.description} - {self.bid} - {self.bids}"


class Bid(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userbids")
    listing_id = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listingbids")
    bid = models.FloatField()
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user_id} - {self.listing_id} - {self.bid}"


class Comment(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usercomments")
    listing_id = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listingcomments")
    comment = models.CharField(max_length=256)
    created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user_id} - {self.listing_id} - {self.comment}"


class WatchList(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userwhatchlist")
    listing_id = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listingcwhatchlist")
    def __str__(self):
        return f"USER: {self.user_id}   LISTING:{self.listing_id}"