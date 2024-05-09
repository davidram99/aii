#encoding:utf-8
from django.db import models

# Create your models here.
# Construir el modelo de datos en Django que almacene la información siguiente: 
# a) Vino: IdVino, Nombre, Precio, DenominacionOrigen, TiposUvas. 
# b) DenominacionOrigen: IdDenominacion, Nombre, Pais. 
# c) Pais: IdPais, Nombre. 
# d) TipoUva: IdUva, Nombre 

class Pais(models.Model):
    IdPais = models.AutoField(primary_key=True)
    Nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.Nombre
    
class DenominacionOrigen(models.Model):
    IdDenominacion = models.AutoField(primary_key=True)
    Nombre = models.CharField(max_length=50)
    Pais = models.ForeignKey(Pais, on_delete=models.CASCADE)

    def __str__(self):
        return self.Nombre
    
class TipoUva(models.Model):
    IdUva = models.AutoField(primary_key=True)
    Nombre = models.CharField(max_length=50)

    def __str__(self):
        return self.Nombre
    
class Vino(models.Model):
    IdVino = models.AutoField(primary_key=True)
    Nombre = models.CharField(max_length=50)
    Precio = models.DecimalField(max_digits=5, decimal_places=2)
    DenominacionOrigen = models.ForeignKey(DenominacionOrigen, on_delete=models.CASCADE)
    TiposUvas = models.ManyToManyField(TipoUva)

    def __str__(self):
        return self.Nombre
