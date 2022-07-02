from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("add/<int:user_id>", views.add_listing, name="add"),
    path("categories", views.categories, name="categories"),
    path("category/<int:category_id>", views.category, name="category"),
    path("<int:listing_id>", views.listing, name="listing"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("mylistings/<int:user_id>", views.mylistings, name="mylistings"),
    path("register", views.register, name="register"),
    path("watchlist/<int:user_id>", views.watchlist, name="watchlist")
]
