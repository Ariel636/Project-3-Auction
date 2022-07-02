from django.contrib import admin

from . models import User, Bid, Category, Comment, Listing, WatchList

# Create a class (which is a subclas of admin.ModelAdmin) to customize Admin Interface
# Read documentation to find a list of additional configuration attributes options available
class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description", "bid", "bids", "active")


class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "user_id", "listing_id", "bid")


class CommentAdmin(admin.ModelAdmin):
    list_display = ("user_id", "listing_id", "comment")


# Register your models here.
admin.site.register(User)
admin.site.register(Bid, BidAdmin)
admin.site.register(Category)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Listing, ListingAdmin),
#admin.site.register(WatchList)