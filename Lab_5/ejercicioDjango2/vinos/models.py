from django.db import models

# Create your models here.
# Construir el modelo de datos en Django que almacene la información siguiente: 
# a) Vino: IdVino, Nombre, Precio, DenominacionOrigen, TiposUvas. 
# b) DenominacionOrigen: IdDenominacion, Nombre, Pais. 
# c) Pais: IdPais, Nombre. 
# d) TipoUva: IdUva, Nombre 

class Pais(models.Model):
  nombre = models.CharField(max_length=50)
  def __str__(self):
      return self.nombre
      
class Denominacion(models.Model):
  nombre = models.CharField(max_length=50)
  pais = models.ForeignKey(Pais,on_delete=models.CASCADE)
  def __str__(self):
      return self.nombre + " - " + self.pais.nombre
      
class Uva(models.Model):
  nombre = models.CharField(max_length=50)
  def __str__(self):
      return self.nombre
      
class Vino(models.Model):
  nombre = models.CharField(max_length=50)
  precio = models.FloatField()
  denominacion = models.ForeignKey(Denominacion,on_delete=models.CASCADE)
  uvas = models.ManyToManyField(Uva)
  def __str__(self):
      return self.nombre + " - " + str(self.precio) + " - " + self.denominacion.nombre



















# Para que Django sepa que este modelo debe ser creado en la base de datos,
# es necesario ejecutar el comando: python manage.py makemigrations
# Y luego: python manage.py migrate

# Para poder visualizar los datos en el administrador de Django, es necesario
# registrar los modelos en el archivo admin.py