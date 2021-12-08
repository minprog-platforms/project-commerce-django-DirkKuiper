from typing import Text
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models.fields import DecimalField
from django.forms.widgets import Textarea
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, Listing, Comment, Bid

class NewBidForm(forms.Form):
    bid = forms.DecimalField(label="bid", decimal_places=2, max_digits=10)


class NewCommentForm(forms.Form):
    comment = forms.CharField(label="comment", widget=forms.Textarea)


def index(request):
    return render(request, "auctions/index.html",{
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
    listing = Listing.objects.filter(title=name).first()

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments": Comment.objects.filter(listing=listing),
        "bids" : Bid.objects.filter(listing=listing),
        "bidform": NewBidForm(),
        "commentform": NewCommentForm()
    })

