from typing import Text
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models.fields import DecimalField
from django.forms.widgets import Textarea
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import User, Listing, Comment, Bid


class NewBidForm(forms.Form):
    bid = forms.DecimalField(label="bid", decimal_places=2, max_digits=10)


class NewCommentForm(forms.Form):
    comment = forms.CharField(label="comment", widget=forms.Textarea)


class NewListingForm(forms.Form):
    title = forms.CharField()
    startingbid = forms.DecimalField()
    description = forms.CharField(widget=forms.Textarea)
    image = forms.URLField(required=False)


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all()
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


def listing(request, name):
    # Saves listing for further reference
    listing = Listing.objects.filter(title=name).first()
    comments = Comment.objects.filter(listing=listing)
    bids = Bid.objects.filter(listing=listing)
    highestbid = Bid.objects.filter(listing=listing).first()

    # Handles user input on listing page for placing a bid
    if request.method == "POST" and "bid" in request.POST:

        form1 = NewBidForm(request.POST)
        
        if form1.is_valid():
            # Makes sure the big is higher than the previous highest bid
            if float(request.POST["bid"]) > listing.startingbid:
                # Saves bidding to database
                bidding = form1.cleaned_data["bid"]
                newbid = Bid(bid=bidding, user=request.user, listing=listing)
                newbid.save()
                listing.startingbid = bidding
                listing.save()
                return HttpResponseRedirect(reverse("listing", args=[name]))
            else:
                messages.error(request, 'This bid is not higher than the previous bid, try again!')
                return HttpResponseRedirect(reverse("listing", args=[name]))
        # If the form is not valid, return user to the original listing page
        else:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "comments": comments,
                "bids": bids,
                "highestbid": highestbid,
                "bidform": NewBidForm(),
                "commentform": NewCommentForm()
            })

        # Handles user input for user placing a comment on a listing
    elif request.method == "POST" and "comment" in request.POST:

        form2 = NewCommentForm(request.POST)
        print(form2)

        if form2.is_valid():
            # Saves comment to database
            comment = form2.cleaned_data["comment"]
            newcomment = Comment(comment=comment, user=request.user, listing=listing)
            newcomment.save()
            return HttpResponseRedirect(reverse("listing", args=[name]))
        else:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "comments": comments,
                "bids": bids,
                "highestbid": highestbid,
                "bidform": NewBidForm(),
                "commentform": NewCommentForm()
                })
    
    elif request.method == "POST" and "close" in request.POST:
            listing = Listing.objects.get(title=name)
            listing.closedlisting = True
            listing.save()
            return HttpResponseRedirect(reverse("listing", args=[name]))

    else:

        return render(request, "auctions/listing.html", {
            "listing": listing,
            "comments": comments,
            "bids": bids,
            "highestbid": highestbid,
            "bidform": NewBidForm(),
            "commentform": NewCommentForm()
        })

@login_required(login_url="login")
def new_listing(request):    
    if request.method == "POST":

        form = NewListingForm(request.POST)

        if form.is_valid():
            # Saves listing to database
            title = form.cleaned_data["title"]
            newlisting = Listing(title=title, startingbid=form.cleaned_data["startingbid"],description=form.cleaned_data["description"], url=form.cleaned_data["image"], user=request.user)
            newlisting.save()
            return HttpResponseRedirect(reverse("index"))

    return render(request, "auctions/new_listing.html", {
        "form" : NewListingForm(),
    })
