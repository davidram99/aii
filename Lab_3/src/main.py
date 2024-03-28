import os
from datetime import datetime
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, KEYWORD, DATETIME, ID
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh import qparser, query
from tkinter import *
from tkinter import messagebox
from bs4 import BeautifulSoup
import requests

# Se desea extraer información de distintos juegos de mesa para listar y hacer búsquedas por distintos criterios. 
# Mediante BeauttifulSoup extraeremos la información de la página
# https://zacatrus.es/juegos-de-mesa.html 
# ALMACENAR LOS JUEGOS DE LAS CUATRO PRIMERAS PÁGINAS 
# Buscamos construir un programa en Tkinter con un MENÚ con dos opciones: 
# a) “Datos”, con dos opciones: 
# a. “Cargar”, que cree esquema e índice en Whoosh que almacene los siguientes datos de cada juego: 
# título, precio, temática/s, complejidad, número de jugadores y detalles. Una vez cargadas, que 
# muestre una ventana de mensajes informando del número de juegos almacenados en el sistema.
# b. “Salir”, que cierre la aplicación.

# Funciones
def crearIndice():
    # Creamos el esquema
    schema = Schema(titulo=TEXT(stored=True), precio=TEXT(stored=True), tematica=TEXT(stored=True), complejidad=TEXT(stored=True), jugadores=TEXT(stored=True), detalles=TEXT(stored=True))
    # Creamos el índice
    if not os.path.exists("index"):
        os.mkdir("index")
    ix = create_in("index", schema)
    writer = ix.writer()
    # Extraemos la información de la página
    for i in range(1, 5):
        url = f"https://zacatrus.es/juegos-de-mesa.html?p={i}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        enlacesJuegos = soup.find_all("a", class_="product-item-link")
        # Guarda en un fichero lo que haya en enlacesJuegos
        with open("enlaces.txt", "w") as f:
          f.write(str(enlacesJuegos))
        for enlace in enlacesJuegos:
          print(enlace)
          urlJuego = enlace["href"]
          responseJuego = requests.get(urlJuego)
          soupJuego = BeautifulSoup(responseJuego.text, "html.parser")
          titulo = soupJuego.find("h1", class_="page-title").find("span", class_="base").text
          precio = soupJuego.find("span", class_="price").text
          detailsTable = soupJuego.find("div", class_="trs")
          if detailsTable is not None:
            contenedorTematica = detailsTable.find("div", class_="col", attrs={"data-th": "Temática"})
            if contenedorTematica is not None:
              tematica = contenedorTematica.text
            else:
              tematica = ""
            contenedorComplejidad = detailsTable.find("div", class_="col", attrs={"data-th": "Complejidad"})
            if contenedorComplejidad is not None:
              complejidad = contenedorComplejidad.text
            else:
              complejidad = ""
            contenedorJugadores = detailsTable.find("div", class_="col", attrs={"data-th": "Núm. jugadores"})
            if contenedorJugadores is not None:
              jugadores = contenedorJugadores.text
            else:
              jugadores = ""
            writer.add_document(titulo=titulo, precio=precio, tematica=tematica, complejidad=complejidad, jugadores=jugadores)
            print("Titulo: ", titulo, "Precio: ", precio, "Tematica: ", tematica, "Complejidad: ", complejidad, "Jugadores: ", jugadores)
          else:
            writer.add_document(titulo=titulo, precio=precio)
            print("Titulo: ", titulo, "Precio: ", precio)
    writer.commit()
    # messagebox.showinfo("Información", f"Se han almacenado {len(juegos)} juegos en el sistema")

crearIndice()

# root = Tk()
# root.title("Buscador de juegos de mesa")
# root.geometry("500x300")
# menu = Menu(root)
# root.config(menu=menu)
# datos = Menu(menu, tearoff=0)
# datos.add_command(label="Cargar", command=crearIndice)
# datos.add_separator()
# datos.add_command(label="Salir", command=root.quit)
# menu.add_cascade(label="Datos", menu=datos)
# buscar = Menu(menu, tearoff=0)
# menu.add_cascade(label="Buscar", menu=buscar)
# buscar.add_command(label="Detalles")
# buscar.add_command(label="Temática")
# buscar.add_command(label="Precio")
# buscar.add_command(label="Jugadores")

root.mainloop()