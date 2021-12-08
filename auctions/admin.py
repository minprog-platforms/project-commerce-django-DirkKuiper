from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import User, Listing, Bid, Comments

admin.site.register(User)
admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(Comments)
