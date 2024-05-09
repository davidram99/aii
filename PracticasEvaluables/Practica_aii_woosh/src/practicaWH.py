#encoding:utf-8

from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import re, os, shutil
from datetime import datetime
from whoosh.index import create_in,open_dir
from whoosh.fields import Schema, TEXT, KEYWORD, DATETIME, NUMERIC, ID
from whoosh.qparser import QueryParser, MultifieldParser
from datetime import datetime
from whoosh import qparser, index, query
from datetime import datetime, timedelta
import os, ssl

if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

def crearIndice():
  schema = Schema(categoria=KEYWORD(stored=True,commas=True,lowercase=True),
                  titulo=TEXT(stored=True,phrase=False),
                  url=ID(stored=True,unique=True),
                  fecha=DATETIME(stored=True),
                  autor=TEXT(stored=True,phrase=False),
                  etiquetas=KEYWORD(stored=True,commas=True,lowercase=True),
                  resumen=TEXT(stored=True,phrase=False))
  if not os.path.exists("index"):
    os.mkdir("index")
  ix = create_in("index", schema)
  return ix

def cargarDatos():
  if not os.path.exists("index"):
    ix = crearIndice()
  else:
    ix = open_dir("index")
  writer = ix.writer()
  noticias = extraer_noticias()
  for noticia in noticias: 
    print(str(noticia[1]))
    separados = str(noticia[1]).split(" ")
    dia = separados[0]
    mesEnTexto = separados[1].replace(",", "")
    mesNumero = mesEnTexto.replace("enero", "01").replace("febrero", "02").replace("marzo", "03").replace("abril", "04").replace("mayo", "05").replace("junio", "06").replace("julio", "07").replace("agosto", "08").replace("septiembre", "09").replace("octubre", "10").replace("noviembre", "11").replace("diciembre", "12")
    anyo = separados[2]
    fecha = datetime.strptime(f"{anyo}-{mesNumero}-{dia}", "%Y-%m-%d")
    writer.add_document(categoria=str(noticia[0]), fecha=fecha, titulo=str(noticia[2]), url=str(noticia[3]), resumen=str(noticia[4]), autor=str(noticia[5]), etiquetas=str(noticia[6]))
  writer.commit()
  messagebox.showinfo("Información", f"Se han almacenado {ix.doc_count()} noticias")

def extraer_noticias():
    
    lista=[]
    
    for p in range(1,3):
        req = urllib.request.Request("https://muzikalia.com/category/noticia/page/"+str(p)+"/", headers={'User-Agent': 'Mozilla/5.0'})
        f = urllib.request.urlopen(req)
        s = BeautifulSoup(f, 'lxml')
        l = s.find_all('div', class_='article-content')

        for i in l:
            titulo = i.find('h2', class_='entry-title').a.string
            enlace = i.find('h2', class_='entry-title').a['href']
            fecha = i.find('time').string
            categoria = ",".join(list(i.find('span',class_='cat-links').stripped_strings))
            descripcion = i.find('div', class_='entry-content').p.string
            autor = i.find('span',class_='author').a.string.strip()
            if i.find('span',class_='tag-links'):
                etiquetas = i.find('span',class_='tag-links').get_text().strip()
            else:
                etiquetas=""                           
            lista.append((categoria, fecha, titulo, enlace, descripcion, autor, etiquetas))
   
    return lista

def listarUltimos14Dias():
  fecha_actual = datetime.now()
  fecha_hace_14_dias = fecha_actual - timedelta(days=14)
  
  parsed_date_today = fecha_actual.strftime("%Y-%m-%d")
  parsed_date_14 = fecha_hace_14_dias.strftime("%Y-%m-%d")
  
  ix = open_dir("index")
  with ix.searcher() as searcher:
    consulta = "fecha:[" + parsed_date_14 + " TO " + parsed_date_today + "]"
    query = QueryParser("fecha", ix.schema).parse(consulta)
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
      for r in results:
        listbox.insert(END, f"{r['titulo']}")
        listbox.insert(END, f"{r['url']}")
        listbox.insert(END, f"{r['fecha']}")
        listbox.insert(END, f"{r['categoria']}")
        listbox.insert(END, f"{r['autor']}")
        listbox.insert(END, "")
      listbox.pack(side=LEFT, fill=BOTH)
      scrollbar.config(command=listbox.yview)
  

def buscarAutores(etiqueta):
    ix = open_dir("index")
    print(etiqueta)
    autores_set = set()
    with ix.searcher() as searcher:
        query = QueryParser("etiquetas", ix.schema).parse('"'+etiqueta+'"')
        results = searcher.search(query, limit=None)
        if len(results) == 0:
            messagebox.showinfo("Información", "No se han encontrado autores con esa etiqueta")
        else:
            ventana = Toplevel()
            ventana.title("Resultados")
            ventana.geometry("500x300")
            scrollbar = Scrollbar(ventana)
            scrollbar.pack(side=RIGHT, fill=Y)
            listbox = Listbox(ventana, yscrollcommand=scrollbar.set)
            listbox.config(width=500, height=300)
            for r in results:
                autores_set.add(r['autor'])
            for autor in autores_set:
                listbox.insert(END, autor)
                listbox.insert(END, "")
            listbox.pack(side=LEFT, fill=BOTH)
            scrollbar.config(command=listbox.yview)
    ix.close()

def buscarAutoresPorEtiquetas():
  ix = open_dir("index")
  with ix.searcher() as searcher:
    etiquetas = [i.decode('utf-8') for i in searcher.lexicon('etiquetas')]
  ventana = Toplevel()
  ventana.title("Buscar autores por etiquetas")
  ventana.geometry("300x100")
  label = Label(ventana, text="Selecciona una etiqueta")
  label.pack()
  spinbox = Spinbox(ventana, values=etiquetas)
  spinbox.pack()
  boton = Button(ventana, text="Buscar", command=lambda: buscarAutores(spinbox.get()))
  boton.pack()
  ix.close()

def buscarResumenYTitulo(busqueda):
  ix = open_dir("index")
  with ix.searcher() as searcher:
    queryTitulo = QueryParser("titulo", ix.schema).parse(busqueda)
    queryResumen = QueryParser("resumen", ix.schema).parse(busqueda)
    query = queryTitulo & queryResumen
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
      for r in results:
        listbox.insert(END, f"{r['titulo']}")
        listbox.insert(END, f"{r['url']}")
        listbox.insert(END, f"{r['fecha']}")
        listbox.insert(END, f"{r['categoria']}")
        listbox.insert(END, f"{r['autor']}")
        listbox.insert(END, "")
      listbox.pack(side=LEFT, fill=BOTH)
      scrollbar.config(command=listbox.yview)

def resumenYTítulo():
  ventana = Toplevel()
  ventana.title("Buscar por resumen y título")
  ventana.geometry("300x100")
  label = Label(ventana, text="Introduce palabra/s a buscar")
  label.pack()
  entry = Entry(ventana)
  entry.pack()
  boton = Button(ventana, text="Buscar", command=lambda: buscarResumenYTitulo(entry.get()))
  boton.pack()

def eliminarCategoriaDefinitivo(categoria, writer, query):
  writer.delete_by_query(query)
  writer.commit()
  messagebox.showinfo("Información", f"Se han eliminado las noticias de la categoría {categoria}")

def eliminarCategoriaSeleccionada(categoria):
  ix = open_dir("index")
  writer = ix.writer()
  with ix.searcher() as searcher:
    query = QueryParser("categoria", ix.schema).parse(categoria)
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
      for r in results:
        listbox.insert(END, f"{r['titulo']}")
        listbox.insert(END, f"{r['url']}")
        listbox.insert(END, f"{r['fecha']}")
        listbox.insert(END, f"{r['categoria']}")
        listbox.insert(END, f"{r['autor']}")
        listbox.insert(END, "")
      listbox.pack(side=LEFT, fill=BOTH)
      scrollbar.config(command=listbox.yview)
      ventanaConfirmar = Toplevel()
      ventanaConfirmar.title("Confirmar eliminación")
      ventanaConfirmar.geometry("500x100")
      label = Label(ventanaConfirmar, text=f"¿Estás seguro de que quieres eliminar la categoría {categoria}?")
      label.pack()
      boton = Button(ventanaConfirmar, text="Confirmar", command=lambda: eliminarCategoriaDefinitivo(categoria, writer, query))
      boton.pack()
  ix.close()

def eliminarCategoria():
  ix = open_dir("index")
  with ix.searcher() as searcher:
    categorias = [i.decode('utf-8') for i in searcher.lexicon('categoria')]
  ventana = Toplevel()
  ventana.title("Eliminar categoría")
  ventana.geometry("300x100")
  label = Label(ventana, text="Selecciona una categoría")
  label.pack()
  spinbox = Spinbox(ventana, values=categorias)
  spinbox.pack()
  boton = Button(ventana, text="Eliminar", command=lambda: eliminarCategoriaSeleccionada(spinbox.get()))
  boton.pack()
  ix.close()

def ventanaPrincipal():
  root = Tk()
  root.title("Práctica Whoosh")
  root.geometry("500x300")
  menu = Menu(root)
  root.config(menu=menu)
  datos = Menu(menu, tearoff=0)
  datos.add_command(label="Cargar", command=cargarDatos)
  datos.add_command(label="Listar últimos 14 días", command=listarUltimos14Dias)
  datos.add_separator()
  datos.add_command(label="Salir", command=root.quit)
  menu.add_cascade(label="Datos", menu=datos)
  buscar = Menu(menu, tearoff=0)
  menu.add_cascade(label="Buscar", menu=buscar)
  buscar.add_command(label="Autores por etiquetas", command=buscarAutoresPorEtiquetas)
  buscar.add_command(label="Resumen y título", command=resumenYTítulo)
  buscar.add_command(label="Eliminar Categoría", command=eliminarCategoria)

  root.mainloop()

if __name__ == "__main__":
    ventanaPrincipal()