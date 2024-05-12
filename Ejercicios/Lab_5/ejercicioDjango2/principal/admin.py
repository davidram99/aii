from django.contrib import admin
from .models import Pais, Denominacion, Uva, Vino

# Register your models here.

admin.site.register(Pais)
admin.site.register(Denominacion)
admin.site.register(Uva)
admin.site.register(Vino)