from django.contrib import admin
from principal.models import Pais, DenominacionOrigen, TipoUva, Vino

# Register your models here.

admin.site.register(Pais)
admin.site.register(DenominacionOrigen)
admin.site.register(TipoUva)
admin.site.register(Vino)