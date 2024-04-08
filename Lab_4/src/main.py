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

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context
    
def crearIndice():
  if not os.path.exists("index"):
    os.mkdir("index")
  schema = Schema(titulo=TEXT(stored=True,phrase=False),
                  titulo_original=TEXT(stored=True,phrase=False),
                  fecha_estreno=NUMERIC(stored=True,numtype=int),
                  paises=KEYWORD(stored=True,commas=True,lowercase=True),
                  generos=KEYWORD(stored=True,commas=True,lowercase=True),
                  directores=KEYWORD(stored=True,commas=True,lowercase=True),
                  sinopsis=TEXT(stored=True,phrase=False),
                  url_detalles=ID(stored=True))
  ix = create_in("index", schema)
  return ix

def cargarEstrenos():
  if not os.path.exists("index"):
    ix = crearIndice()
  else:
    ix = open_dir("index")
  writer = ix.writer()
  for i in range(1, 3):
    url = f"https://www.elseptimoarte.net/estrenos/{i}/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    # Section con id estrenos
    contenedorEstrenos = soup.find("section", id="collections").find("ul", class_="elements")
    estrenos = contenedorEstrenos.find_all("li")
    for estreno in estrenos:
        enlace = estreno.find("h3").find("a")['href']
        responseEstreno = requests.get("https://www.elseptimoarte.net" + enlace)
        soupEstreno = BeautifulSoup(responseEstreno.text, "html.parser")
        highlight = soupEstreno.find("section", class_="highlight")
        titulo = highlight.find("dt", string="Título").find_next_sibling("dd").text.strip()
        print(titulo)
        titulo_original = highlight.find("dt", string="Título original").find_next_sibling("dd").text.strip()
        paises = highlight.find("dt", string="País").find_next_sibling("dd").text.strip()
        fecha_estreno = highlight.find("dt", string="Estreno en España").find_next_sibling("dd").text.strip()
        fecha_estreno = fecha_estreno.split("/")
        fecha_estreno = int(fecha_estreno[2] + fecha_estreno[1] + fecha_estreno[0])
        directores = highlight.find("dt", string="Director").find_next_sibling("dd").text.strip()
        generos = soupEstreno.find("div", id="datos_pelicula").find("p", class_="categorias").find("a").text.strip()
        sinopsis = soupEstreno.find("div", class_="info", itemprop="description").text.strip()
        writer.add_document(titulo=titulo,
                            titulo_original=titulo_original,
                            fecha_estreno=fecha_estreno,
                            paises=paises,
                            generos=generos,
                            directores=directores,
                            sinopsis=sinopsis,
                            url_detalles='https://www.elseptimoarte.net' + enlace)
  writer.commit()
  messagebox.showinfo("Información", f"Se han almacenado {ix.doc_count()} estrenos")

def buscarPorTituloSinopsis(busqueda):
  ix = open_dir("index")
  with ix.searcher() as searcher:
    query = MultifieldParser(["titulo", "sinopsis"], ix.schema).parse(busqueda)
    results = searcher.search(query, limit=None)
    if len(results) == 0:
      messagebox.showinfo("Información", "No se han encontrado resultados")
    else:
      # Listbox con scrollbar
      ventana = Toplevel()
      ventana.title("Resultados de la búsqueda")
      ventana.geometry("800x600")
      scrollbar = Scrollbar(ventana)
      scrollbar.pack(side=RIGHT, fill=Y)
      listbox = Listbox(ventana, yscrollcommand=scrollbar.set)
      listbox.config(width=500, height=300)
      for estreno in results:
        listbox.insert(END, f"{estreno['titulo']} - {estreno['titulo_original']} - {estreno['directores']} - {estreno['fecha_estreno']}")
      listbox.pack(side=LEFT, fill=BOTH)
      scrollbar.config(command=listbox.yview)
  
def buscaTituloSinopsis():
  ventana = Toplevel()
  ventana.title("Buscar por título o sinopsis")
  ventana.geometry("300x100")
  label = Label(ventana, text="Introduce palabra/s a buscar")
  label.pack()
  entry = Entry(ventana)
  entry.pack()
  boton = Button(ventana, text="Buscar", command=lambda: buscarPorTituloSinopsis(entry.get()))
  boton.pack()

def buscarPorGeneros(busqueda):
  ix = open_dir("index")
  with ix.searcher() as searcher:
    generos = [i.decode('utf-8') for i in searcher.lexicon('generos')]
    print(generos)
    if busqueda not in generos:
      messagebox.showinfo("Información", "Género no encontrado")
    else:
      query = QueryParser("generos", ix.schema).parse(busqueda)
      results = searcher.search(query, limit=20)
      if len(results) == 0:
        messagebox.showinfo("Información", "No se han encontrado resultados")
      else:
        # Listbox con scrollbar
        ventana = Toplevel()
        ventana.title("Resultados de la búsqueda")
        ventana.geometry("800x600")
        scrollbar = Scrollbar(ventana)
        scrollbar.pack(side=RIGHT, fill=Y)
        listbox = Listbox(ventana, yscrollcommand=scrollbar.set)
        listbox.config(width=500, height=300)
        for estreno in results:
          listbox.insert(END, f"{estreno['titulo']} - {estreno['titulo_original']} - {estreno['paises']}")
        listbox.pack(side=LEFT, fill=BOTH)
        scrollbar.config(command=listbox.yview)

def buscaGeneros():
  ventana = Toplevel()
  ventana.title("Buscar por género")
  ventana.geometry("300x100")
  label = Label(ventana, text="Introduce género")
  label.pack()
  entry = Entry(ventana)
  entry.pack()
  boton = Button(ventana, text="Buscar", command=lambda: buscarPorGeneros(entry.get()))
  boton.pack()  

def buscarPorFechas(busqueda):
  fecha1 = int(busqueda[:8])
  fecha2 = int(busqueda[9:])
  print(fecha1, type(fecha1), fecha2, type(fecha2))
  ix = open_dir("index")
  with ix.searcher() as searcher:
    rango_fechas = '[{} TO {}]'.format(fecha1, fecha2)
    query = QueryParser("fecha_estreno", ix.schema).parse(rango_fechas)
    results = searcher.search(query, limit=None)
    if len(results) == 0:
      messagebox.showinfo("Información", "No se han encontrado resultados")
    else:
      # Listbox con scrollbar
      ventana = Toplevel()
      ventana.title("Resultados de la búsqueda")
      ventana.geometry("800x600")
      scrollbar = Scrollbar(ventana)
      scrollbar.pack(side=RIGHT, fill=Y)
      listbox = Listbox(ventana, yscrollcommand=scrollbar.set)
      listbox.config(width=500, height=300)
      for estreno in results:
        listbox.insert(END, f"{estreno['titulo']} - {estreno['titulo_original']} - {estreno['fecha_estreno']}")
      listbox.pack(side=LEFT, fill=BOTH)
      scrollbar.config(command=listbox.yview)
      
def buscaFechas():
  ventana = Toplevel()
  ventana.title("Buscar por fechas")
  ventana.geometry("300x100")
  label = Label(ventana, text="Introduce fecha de estreno")
  label.pack()
  entry = Entry(ventana)
  entry.pack()
  boton = Button(ventana, text="Buscar", command=lambda: buscarPorFechas(entry.get()))
  boton.pack()

def modificarFechaEstreno(titulo, fecha):
  # Queremos modificar la fecha_estreno de cualquier estreno que contenga el título
  ix = open_dir("index")
  with ix.searcher() as searcher:
    query = QueryParser("titulo", ix.schema).parse(titulo)
    results = searcher.search(query, limit=None)
    if len(results) == 0:
      messagebox.showinfo("Información", "No se han encontrado resultados")
    else:
      ventana = Toplevel()
      ventana.title("Resultados de la búsqueda")
      ventana.geometry("800x600")
      scrollbar = Scrollbar(ventana)
      scrollbar.pack(side=RIGHT, fill=Y)
      listbox = Listbox(ventana, yscrollcommand=scrollbar.set)
      listbox.config(width=500, height=300)
      for estreno in results:
        listbox.insert(END, f"{estreno['titulo']} - {estreno['titulo_original']} - {estreno['fecha_estreno']}")
      
  respuesta = messagebox.askyesno("Información", "¿Desea modificar la fecha de estreno?")
  if respuesta:
    writer = ix.writer()
    for estreno in results:
      writer.update_document(titulo=estreno['titulo'],
                             titulo_original=estreno['titulo_original'],
                             fecha_estreno=int(fecha),
                             paises=estreno['paises'],
                             generos=estreno['generos'],
                             directores=estreno['directores'],
                             sinopsis=estreno['sinopsis'],
                             url_detalles=estreno['url_detalles'])
    writer.commit()
    messagebox.showinfo("Información", "Fecha de estreno modificada correctamente")

def modificarFecha():
  # Ahora queremos dos entrys, uno para titulo y otro para la nueva fecha
  ventana = Toplevel()
  ventana.title("Modificar fecha de estreno")
  ventana.geometry("300x150")
  label = Label(ventana, text="Introduce título")
  label.pack()
  entry = Entry(ventana)
  entry.pack()
  label2 = Label(ventana, text="Introduce nueva fecha de estreno")
  label2.pack()
  entry2 = Entry(ventana)
  entry2.pack()
  boton = Button(ventana, text="Modificar", command=lambda: modificarFechaEstreno(entry.get(), entry2.get()))
  boton.pack()

def ventanaPrincipal():
  root = Tk()
  root.title("Buscador de estrenos")
  root.geometry("500x300")
  menu = Menu(root)
  root.config(menu=menu)
  datos = Menu(menu, tearoff=0)
  datos.add_command(label="Cargar", command=cargarEstrenos)
  datos.add_separator()
  datos.add_command(label="Salir", command=root.quit)
  menu.add_cascade(label="Datos", menu=datos)
  buscar = Menu(menu, tearoff=0)
  menu.add_cascade(label="Buscar", menu=buscar)
  buscar.add_command(label="Título o Sinópsis", command=buscaTituloSinopsis)
  buscar.add_command(label="Géneros", command=buscaGeneros)
  buscar.add_command(label="Fecha", command=buscaFechas)
  buscar.add_command(label="Modifica Fecha", command=modificarFecha)

  root.mainloop()

if __name__ == "__main__":
    ventanaPrincipal()