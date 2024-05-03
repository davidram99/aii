from django.shortcuts import render

# Create your views here.
#Se pide construir una web con un menú principal, en la parte superior de la ventana, que permita 
#las siguientes opciones: 
#a) Cargar BD. Poblar la base de datos desde los ficheros. Una vez cargada, mostrar el 
#número de registros almacenados en cada tabla

def cargarBD(request):
    from vinos.populateDB import populatePais, populateDenominacion, populateUva, populateVino
    paises = populatePais()
    denominaciones = populateDenominacion()
    uvas = populateUva()
    vinos = populateVino()
    return render(request, 'cargarBD.html', {'paises': paises, 'denominaciones': denominaciones, 'uvas': uvas, 'vinos': vinos})

