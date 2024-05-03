#encoding:utf-8
from principal.models import Pais,DenominacionOrigen,TipoUva,Vino
from principal.populateDB import populate
from django.shortcuts import render

# Create your views here.
# Se pide construir una web con un menú principal, en la parte superior de la ventana, que permita 
# las siguientes opciones: 
# a) Cargar BD. Poblar la base de datos desde los ficheros. Una vez cargada, mostrar el 
# número de registros almacenados en cada tabla. 

def index(request):
    return render(request, 'index.html')

def cargarBD(request):
    (p,d,u,v) = populate()
    print("Se han cargado " + str(p) + " paises, " + str(d) + " denominaciones, " + str(u) + " uvas y " + str(v) + " vinos.")
    info = "Se han cargado " + str(p) + " paises, " + str(d) + " denominaciones, " + str(u) + " uvas y " + str(v) + " vinos."
    return render(request, 'cargarBD.html', {'info':info})