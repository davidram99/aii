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
                  sinopsis=TEXT,
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
        listbox.insert(END, f"{estreno['titulo']} - {estreno['titulo_original']} - {estreno['directores']}")
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

  root.mainloop()

if __name__ == "__main__":
    ventanaPrincipal()