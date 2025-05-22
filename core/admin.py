# core/admin.py

from django.contrib import admin
from .models import User, Animal, Shelter, Report, Adoption, Review

admin.site.register(User)
admin.site.register(Animal)
admin.site.register(Shelter)
admin.site.register(Report)
admin.site.register(Adoption)
admin.site.register(Review)
