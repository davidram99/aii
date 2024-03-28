#encoding:utf-8
import os, ssl
from tkinter import *
from tkinter import messagebox
from bs4 import BeautifulSoup
import requests
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, KEYWORD, NUMERIC, ID
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh import qparser, query

def crearIndice():
  if not os.path.exists("index"):
    os.mkdir("index")
  schema = Schema(titulo=TEXT(stored=True,phrase=False), precio=NUMERIC(stored=True,numtype=float), tematica=KEYWORD(stored=True,commas=True,lowercase=True), complejidad=ID(stored=True), jugadores=KEYWORD(stored=True,commas=True), detalles=TEXT)
  ix = create_in("index", schema)
  return ix

def cargarJuegos():
  if not os.path.exists("index"):
    ix = crearIndice()
  else:
    ix = open_dir("index")
  writer = ix.writer()
  for i in range(1, 4):
    url = f"https://zacatrus.es/juegos-de-mesa.html?p={i}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    # Buscmos la cuadricula que contiene los juegos, es un ol
    contenedorJuegos = soup.find("ol", class_="products list items product-items")
    # Dentro del ol, cada juego esta dentro de un li
    marcoJuegos = contenedorJuegos.find_all("li", class_="item product product-item")
    for juego in marcoJuegos:
      try:
        enlace = juego.find("a", class_="product-item-link")['href']
        responseJuego = requests.get(enlace)
        soupJuego = BeautifulSoup(responseJuego.text, "html.parser")
        titulo = soupJuego.find("h1", class_="page-title").find("span", class_="base").text
        print(titulo)
        precio = soupJuego.find("span", class_="price").text
        precio = float(precio.replace("€", "").replace(",", "."))
        contenedorDetalles = soupJuego.find("div", class_="product info detailed")
        description = contenedorDetalles.find("div", class_="product attribute description")
        if description is not None:
          detalles = description.find("div", class_="value")
          if detalles.div:
            detalles = detalles.div
          detalles = " ".join(list(detalles.stripped_strings))
        else:
          detalles = ""
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

          writer.add_document(titulo=titulo, precio=precio, tematica=tematica, complejidad=complejidad, jugadores=jugadores, detalles=detalles)
        else:
          writer.add_document(titulo=titulo, precio=precio, detalles=detalles)
      except Exception as e:
          print(e)
  writer.commit()
  messagebox.showinfo("Información", f"Se han almacenado {ix.doc_count()} juegos en el sistema")

def buscarIncluyeDetalles(detalles):
  # Abrimos el índice
  ix = open_dir("index")
  # Buscamos TODOS los juegos que contengan lo que recibimos en la variable detalles en su campo 'detalles
  with ix.searcher() as searcher:
    query = QueryParser("detalles", ix.schema).parse(detalles)
    results = searcher.search(query)
    if len(results) == 0:
      messagebox.showinfo("Información", "No se han encontrado juegos con esos detalles")
    else:
      # mensaje = ""
      # for r in results:
      #   mensaje += f"{r['titulo']} - {r['precio']}\n"
      # messagebox.showinfo("Información", mensaje)
      # Creamos una nueva ventana con un listbox con scrollbars para mostrar los resultados
      ventana = Toplevel()
      ventana.title("Resultados")
      ventana.geometry("500x300")
      scrollbar = Scrollbar(ventana)
      scrollbar.pack(side=RIGHT, fill=Y)
      listbox = Listbox(ventana, yscrollcommand=scrollbar.set)
      listbox.config(width=500, height=300)
      for r in results:
        listbox.insert(END, f"{r['titulo']} - {r['precio']} - {r['tematica']} - {r['complejidad']} - {r['jugadores']}")
      listbox.pack(side=LEFT, fill=BOTH)
      scrollbar.config(command=listbox.yview)
  ix.close()
  
def buscaDetalles():
  # Creamos una ventana con un entry
  ventana = Toplevel()
  ventana.title("Buscar detalles")
  ventana.geometry("300x100")
  label = Label(ventana, text="Introduce detalles del juego")
  label.pack()
  entry = Entry(ventana)
  entry.pack()
  boton = Button(ventana, text="Buscar", command=lambda: buscarIncluyeDetalles(entry.get()))
  boton.pack()

def buscarPorTematica(tematica):
  ix = open_dir("index")
  with ix.searcher() as searcher:
    query = QueryParser("tematica", ix.schema).parse(tematica)
    results = searcher.search(query)
    if len(results) == 0:
      messagebox.showinfo("Información", "No se han encontrado juegos con esa temática")
    else:
      ventana = Toplevel()
      ventana.title("Resultados")
      ventana.geometry("500x300")
      scrollbar = Scrollbar(ventana)
      scrollbar.pack(side=RIGHT, fill=Y)
      listbox = Listbox(ventana, yscrollcommand=scrollbar.set)
      listbox.config(width=500, height=300)
      for r in results:
        listbox.insert(END, f"{r['titulo']} - {r['precio']} - {r['tematica']} - {r['complejidad']} - {r['jugadores']}")
      listbox.pack(side=LEFT, fill=BOTH)
      scrollbar.config(command=listbox.yview)
  ix.close()

def buscaTematicas():
  ix = open_dir("index")
  # Buscamos y almacenamos todas las temáticas de los juegos
  with ix.searcher() as searcher:
    query = QueryParser("tematica", ix.schema).parse("*")
    results = searcher.search(query)
    tematicas = set()
    for r in results:
      tematicas.add(r['tematica'])
  # Creamos una ventana con un spinbox para seleccionar la temática
  ventana = Toplevel()
  ventana.title("Buscar por temática")
  ventana.geometry("300x100")
  label = Label(ventana, text="Selecciona una temática")
  label.pack()
  spinbox = Spinbox(ventana, values=list(tematicas))
  spinbox.pack()
  boton = Button(ventana, text="Buscar", command=lambda: buscarPorTematica(spinbox.get()))
  boton.pack()
  ix.close()

def buscarPrecioInferior(precio):
  ix = open_dir("index")
  with ix.searcher() as searcher:
    query = QueryParser("precio", ix.schema).parse(f"[0 TO {precio}]")
    results = searcher.search(query)
    if len(results) == 0:
      messagebox.showinfo("Información", "No se han encontrado juegos con ese precio")
    else:
      ventana = Toplevel()
      ventana.title("Resultados")
      ventana.geometry("500x300")
      scrollbar = Scrollbar(ventana)
      scrollbar.pack(side=RIGHT, fill=Y)
      listbox = Listbox(ventana, yscrollcommand=scrollbar.set)
      listbox.config(width=500, height=300)
      for r in results:
        print(r)
        listbox.insert(END, f"{r['titulo']} - {r['precio']} - {r['tematica']} - {r['complejidad']} - {r['jugadores']}")
      listbox.pack(side=LEFT, fill=BOTH)
      scrollbar.config(command=listbox.yview)
  ix.close()

def buscaPrecio():
  ventana = Toplevel()
  ventana.title("Buscar precio inferior")
  ventana.geometry("300x100")
  label = Label(ventana, text="Introduce precio máximo")
  label.pack()
  entry = Entry(ventana)
  entry.pack()
  boton = Button(ventana, text="Buscar", command=lambda: buscarPrecioInferior(entry.get()))
  boton.pack()

def ventanaPrincipal():
  root = Tk()
  root.title("Buscador de juegos de mesa")
  root.geometry("500x300")
  menu = Menu(root)
  root.config(menu=menu)
  datos = Menu(menu, tearoff=0)
  datos.add_command(label="Cargar", command=cargarJuegos)
  datos.add_separator()
  datos.add_command(label="Salir", command=root.quit)
  menu.add_cascade(label="Datos", menu=datos)
  buscar = Menu(menu, tearoff=0)
  menu.add_cascade(label="Buscar", menu=buscar)
  buscar.add_command(label="Detalles", command=buscaDetalles)
  buscar.add_command(label="Temática", command=buscaTematicas)
  buscar.add_command(label="Precio", command=buscaPrecio)
  buscar.add_command(label="Jugadores")

  root.mainloop()

if __name__ == "__main__":
    ventanaPrincipal()