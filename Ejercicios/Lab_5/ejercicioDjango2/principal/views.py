#encoding:utf-8
from principal.models import Pais,Denominacion,Uva,Vino
from principal.populateDB import populate
from django.shortcuts import render
from principal.forms import VinosPorAnyo, VinosPorUvas

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

def vinosAgrupadosPorDenominacion(request):
    vinos= Vino.objects.all().order_by('denominacion') #los agrupa
    return render(request, 'denominacion_vinos.html',{'vinos':vinos})

def buscar_vinos_por_anyo(request):
    formulario = VinosPorAnyo()
    vinos = None
    anyo =""
    
    if request.method=='POST':
        formulario = VinosPorAnyo(request.POST)
        
        if formulario.is_valid():
            anyo = formulario.cleaned_data['anyo']
            vinos = Vino.objects.filter(nombre__contains=anyo)
            
    return render(request, 'vinosPorAnyo.html', {'formulario':formulario, 'vinos':vinos, 'anyo':anyo})

def buscar_vinos_por_uva(request):
    formulario = VinosPorUvas()
    vinos = None
    
    if request.method=='POST':
        formulario = VinosPorUvas(request.POST)      
        if formulario.is_valid():
            uva = Uva.objects.get(idUva=formulario.cleaned_data['uva'].idUva)
            vinos = uva.vino_set.all()
            
    return render(request, 'buscarVinosPorUva.html', {'formulario':formulario, 'vinos':vinos})