#encoding:utf-8
from principal.models import Pais, DenominacionOrigen, TipoUva, Vino

path = 'data'

# Poblamos la tabla de Pais
def populatePais():
    # Eliminar todos los registros de la tabla
    Pais.objects.all().delete()
    # Creamos una lista vacia para cargar masivamente con bulk_create
    paises = []
    # Abrir el fichero de datos
    f = open(path + '/paises', 'r')
    # Leer las lineas del fichero
    lineas = f.readlines()
    # Las lineas vienen separadas con el separador |
    for linea in lineas:
        campos = str(linea.strip()).split('|')
        paises.append(Pais(IdPais=int(campos[0].strip()), Nombre=str(campos[1].strip())))
    # Cerramos el fichero
    f.close()
    # Insertamos los registros en la tabla
    Pais.objects.bulk_create(paises)
    # Devolvemos el numero de registros insertados
    return len(paises)

# Poblamos la tabla de DenominacionOrigen   
def populateDenominacion():
    DenominacionOrigen.objects.all().delete()
    
    lista=[]
    fileobj=open(path+"\\denominaciones", "r")
    for line in fileobj.readlines():
        rip = str(line.strip()).split('|')
        lista.append(DenominacionOrigen(IdDenominacion=int(rip[0].strip()), Nombre=str(rip[1].strip()), Pais=Pais.objects.get(IdPais=int(rip[2].strip()))))
    fileobj.close()
    DenominacionOrigen.objects.bulk_create(lista)  # bulk_create hace la carga masiva para acelerar el proceso
    
    return len(lista)

def populateUva():
    TipoUva.objects.all().delete()
    
    lista=[]
    fileobj=open(path+"\\uvas", "r")
    for line in fileobj.readlines():
        rip = str(line.strip()).split('|')
        lista.append(TipoUva(IdUva=int(rip[0].strip()), Nombre=str(rip[1].strip())))
    fileobj.close()
    TipoUva.objects.bulk_create(lista)  # bulk_create hace la carga masiva para acelerar el proceso
    
    return len(lista)

def populateVino():
    Vino.objects.all().delete()
    
    fileobj=open(path+"\\vinos", "r")
    for line in fileobj.readlines():
        rip = line.strip().split('|')
      
        vi = Vino(IdVino=int(rip[0].strip()), Nombre=str(rip[1].strip()), Precio=float(rip[2].strip()), DenominacionOrigen=DenominacionOrigen.objects.get(IdDenominacion=int(rip[3].strip())))
        vi.save()
        
        lista_aux=[]
        for i in range(4, len(rip)):
            lista_aux.append(TipoUva.objects.get(IdUva = int(rip[i].strip())))
    
        vi.TiposUvas.set(lista_aux)
        
    fileobj.close()    

    return Vino.objects.count()

def populate():
    p = populatePais()
    d = populateDenominacion()
    u = populateUva()
    v = populateVino()
    return (p,d,u,v)