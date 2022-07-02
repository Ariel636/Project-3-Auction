from django import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .forms import AddCommentForm, AddListingForm
from .models import User, Bid, Comment, Category, Listing, WatchList 
from .utils import find_max_bid , find_winning_bids, usd


def index(request):
    listings = Listing.objects.all().order_by('-created').filter(active="True")
    # Convert bids to US$
    for listing in listings:
        listing.bid = usd(listing.bid)

    user = request.user
    watchlist = WatchList.objects.filter(user_id=user.id)
    watchlist_len = len(watchlist)
    bids = Bid.objects.filter(user_id=user.id)
    winning_bids = find_winning_bids(bids)

    return render(request, "auctions/index.html", {
        "listings": listings,
        "watchlist": watchlist,
        "winning_bids": winning_bids,
        "watchlist_len": watchlist_len,
    })


@login_required
def add_listing(request, user_id):
    watchlist = WatchList.objects.filter(user_id=user_id)
    watchlist_len = len(watchlist)

    # Request reaches route via POST
    if request.method == "POST":
        user = User.objects.get(id=user_id)
        form = AddListingForm(request.POST)
        if form.is_valid():
            # Get acess to all of the data the user submitted
            l = form.cleaned_data 
            listing = Listing(user_id=user,title=l["title"], description=l["description"], 
                            bid=l["bid"], category=l["category"], image=l["image"])
            listing.save()

            return HttpResponseRedirect(reverse("listing", args=(listing.id, )))

        else:
            return render(request, "auctions/addlisting.html", {
                "form": AddListingForm(),
                "watchlist_len": watchlist_len,
            })

    # Request reaches route via GET
    return render(request, "auctions/addlisting.html", {
                "form": AddListingForm(),
                "watchlist_len": watchlist_len,
    })


def categories(request):
    user = request.user
    watchlist = WatchList.objects.filter(user_id=user.id)
    watchlist_len = len(watchlist)
    categories = Category.objects.all().order_by('catname')
    
    # Find counts for each category
    catcounts = []
    for category in categories:   
        catcounts.append(len(Listing.objects.filter(category=category, active=True)))

    categories_w_counts = []
    for i in range(len(categories)):
        categories_w_counts.append({"id": categories[i].id, "catname": categories[i].catname, 
                                    "catcount": catcounts[i]} )

    categories = categories_w_counts

    return render(request, "auctions/categories.html", {
        "categories": categories,
        "watchlist_len": watchlist_len,
    })


def category(request, category_id):
    user = request.user
    watchlist = WatchList.objects.filter(user_id=user.id)
    watchlist_len = len(watchlist)
    category = Category.objects.get(pk=category_id)
    listings = Listing.objects.filter(category=category).order_by('-created').filter(active="True")
    
    # Convert bids to US$
    for listing in listings:
        listing.bid = usd(listing.bid)
    
    bids = Bid.objects.filter(user_id=user.id)
    winning_bids = find_winning_bids(bids)

    return render(request, "auctions/category.html", {
        "category": category,
        "listings": listings,
        "watchlist": watchlist,
        "winning_bids": winning_bids,
        "watchlist_len": watchlist_len,
    })



def listing(request, listing_id): 
    # Set global function variables
    listing = Listing.objects.get(id=listing_id) # or use pk instead of id #    
    listing_bid = listing.bid
    next_bid = listing_bid

    user = request.user 
    watchlist = WatchList.objects.filter(user_id=user.id, listing_id=listing_id)

    watchlist_len = WatchList.objects.filter(user_id=user.id)
    watchlist_len = len(watchlist_len)

    # Retrieves all comments for request's listing 
    comments = listing.listingcomments.all()
    # Retrieves all bids request's listing
    bids = listing.listingbids.all()
    high_bidder = User()
    
    # Set next_bid + 1 case one or more bids already have been placed
    if bids:
        max_bid = find_max_bid(bids)
        listing_bid = max_bid
        next_bid = listing_bid + 1
        
        high_bid = Bid.objects.get(bid=max_bid)
        high_bidder = high_bid.user_id
    
    # Request reaches route via POST
    if request.method == "POST":   
        com_form = AddCommentForm(request.POST)
        # Comment Form POST request:
        if com_form.is_valid():
            c = com_form.cleaned_data["comment"]
            user_id = request.POST["user_id"]
            listing_id = request.POST["listing_id"]
            user = User.objects.get(id=user_id) # or use pk instead of id # 
            listing = Listing.objects.get(id=listing_id) # or use pk instead of id # 

            # Create and save Comment instance
            comment = Comment(user_id=user, listing_id=listing, comment=c)
            comment.save()
            return HttpResponseRedirect(reverse("listing", args=(listing.id, )))
        
        # Bid Form POST request
        # Make sure if bid is not posted bid variable will return a False value.
        bid = request.POST.get('bid', False)
        if bid != False:
            bid = request.POST["bid"]
            user_id = request.POST["user_id"]
            listing_id = request.POST["listing_id"]
            user = User.objects.get(id=user_id) # or use pk instead of id # 
            listing = Listing.objects.get(id=listing_id) # or use pk instead of id #   
         
            # Create and save Bid instance
            bid = Bid(user_id=user, listing_id=listing, bid=bid)   
            # Assure bid will not be a duplicate
            for b in bids:
                if b.bid == int(bid.bid):
                    return HttpResponseRedirect(reverse("listing", args=(listing.id, )))
            # Save new Bid instance and redirect to Listing
            bid.save()
            # Update listing's bid value 
            listing.bid = bid.bid
            listing.save()
            return HttpResponseRedirect(reverse("listing", args=(listing.id, )))
            
        # Close (Auction) Form POST request
        active = request.POST.get("close", False)
        if active != False:
            watchlist = listing.listingcwhatchlist.all()
            watchlist.delete()    

            listing.active = False
            listing.save()
            return HttpResponseRedirect(reverse("listing", args=(listing.id, )))

        # Watchlist (Add or Remove) Form POST Request
        # Make sure if bid is not posted bid variable will return a False value.
        watchlist_toggle = request.POST.get('watchlist_toggle', False)
        if watchlist_toggle != False:
            if watchlist_toggle == "add":
                listing = Listing.objects.get(id=listing_id)
                watchlist = WatchList(user_id=user, listing_id=listing)
                watchlist.save()
                return HttpResponseRedirect(reverse("listing", args=(listing.id, )))
            if watchlist_toggle == "remove":
                watchlist.delete()
                return HttpResponseRedirect(reverse("listing", args=(listing.id, )))
        
    # Request reaches route via GET
    else:    
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "listing_bid": usd(listing_bid),
            "next_bid": next_bid,
            "comments": comments,
            "com_form": AddCommentForm(),
            "bids": len(bids),
            "high_bidder": high_bidder,
            "watchlist": watchlist,
            "watchlist_len": watchlist_len,
        })


@login_required
def mylistings(request, user_id):
    user = User.objects.get(pk=user_id)
    watchlist = WatchList.objects.filter(user_id=user.id)
    watchlist_len = len(watchlist)
    # Find user's open and closed listings
    mylistings_open = Listing.objects.filter(user_id=user, active=True).order_by('-created')
    mylistings_closed = Listing.objects.filter(user_id=user, active=False).order_by('-created')  
    # Convert bids to US$
    for listing in mylistings_open:
        listing.bid = usd(listing.bid)   
    for listing in mylistings_closed:
        listing.bid = usd(listing.bid) 
    
    # Find closed (other users) auctions excluding user's own listings
    otherlistings_closed = Listing.objects.exclude(user_id=user).filter(active=False)
    otherlistings_won = []
    for listing in otherlistings_closed:
        # Retrieve all bids for each listing in closed listings
        bids = listing.listingbids.all()
        if bids: 
            winning_bid = find_max_bid(bids)
            winning_bid_id = Bid.objects.filter(bid=winning_bid, listing_id=listing)
            
            if winning_bid_id[0].user_id == user:
                otherlistings_won.append({"id": listing.id, "title": listing.title, "bid": usd(listing.bid),
                                        "image": listing.image, "created":listing.created})
                    
    return render(request, "auctions/mylistings.html", {
        "mylistings_open": mylistings_open,
        "mylistings_closed": mylistings_closed,
        "otherlistings_won": otherlistings_won,
        "watchlist": watchlist,
        "watchlist_len": watchlist_len,
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def watchlist(request, user_id):
    user = User(id=user_id)
    watchlist = WatchList.objects.filter(user_id=user.id).order_by('-listing_id')
    
    # Convert bids to USD
    for listing in watchlist:
        listing.listing_id.bid = usd(listing.listing_id.bid)
    

    watchlist_len = len(watchlist)
    bids = Bid.objects.filter(user_id=user.id)
    winning_bids = find_winning_bids(bids)
    
    return render(request, "auctions/watchlist.html", {
        "watchlist": watchlist,
        "watchlist_len": watchlist_len,
        "winning_bids": winning_bids
    })


