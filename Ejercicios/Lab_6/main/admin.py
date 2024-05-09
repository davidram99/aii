from django.contrib import admin
from main.models import Usuario, Pelicula, Categoria, Ocupacion, Puntuacion
# Register your models here.

admin.site.register(Usuario)
admin.site.register(Pelicula)
admin.site.register(Categoria)
admin.site.register(Ocupacion)
admin.site.register(Puntuacion)