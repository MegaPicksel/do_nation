from django.contrib import admin

from .models import Action, FoodPledge, EnergyPledge, Pledge

admin.site.register(Action)
admin.site.register(FoodPledge)
admin.site.register(EnergyPledge)
admin.site.register(Pledge)
