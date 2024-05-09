from django.db import models

# Create your models here.
class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    edad = models.IntegerField()
    sexo = models.CharField(max_length=1, choices=(('M', 'Masculino'), ('F', 'Femenino')))
    ocupacion = models.ForeignKey('Ocupacion', on_delete=models.CASCADE)
    codigo_postal = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.id_usuario}: {self.edad}, {self.get_sexo_display()}, {self.ocupacion}, {self.codigo_postal}"

class Pelicula(models.Model):
    id_pelicula = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=255)
    fecha_estreno = models.DateField()
    imdb_url = models.URLField()
    categorias = models.ManyToManyField('Categoria')

    def __str__(self):
        return f"{self.id_pelicula}: {self.titulo} ({self.fecha_estreno})"

class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre

class Ocupacion(models.Model):
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre

class Puntuacion(models.Model):
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    id_pelicula = models.ForeignKey(Pelicula, on_delete=models.CASCADE)
    puntuacion = models.IntegerField(choices=((1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')))

    def __str__(self):
        return f"{self.id_usuario} - {self.id_pelicula}: {self.puntuacion}"
