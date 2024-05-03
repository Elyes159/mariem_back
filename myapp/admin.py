from django.contrib import admin

# Import your models here
from .models import Etranger, StagiaireAdmin, Stagiaire, ResrvationEtranger, ResrvationStagiaire, TokenPourStagiaire

# Register your models with the admin site
admin.site.register(Etranger)
admin.site.register(StagiaireAdmin)
admin.site.register(Stagiaire)
admin.site.register(ResrvationEtranger)
admin.site.register(ResrvationStagiaire)
admin.site.register(TokenPourStagiaire)
