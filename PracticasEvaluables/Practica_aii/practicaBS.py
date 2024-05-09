from bs4 import BeautifulSoup
import urllib.request
import tkinter as tk
from tkinter import messagebox
from tkinter import Toplevel, Listbox, Scrollbar, END, Y, BOTH, RIGHT, LEFT, ttk
import sqlite3

# lineas para evitar error SSL
import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context

# Aparatado a.a
def carga_datos():
  conn = sqlite3.connect('eventos.db')
  cursor = conn.cursor()
  cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='eventos'")
  existe = cursor.fetchone()
  if existe is not None:
    cursor.execute("SELECT COUNT(*) FROM eventos")
    cantidad = cursor.fetchone()
    cursor.execute("SELECT name, sql, strftime('%Y-%m-%d %H:%M:%S') FROM sqlite_master WHERE type='table' AND name='eventos'")
    fechaCreacion = cursor.fetchone()
    respuesta = messagebox.askyesno("Carga de datos", "Hay "+str(cantidad[0])+" eventos en la base de datos creados en " + str(fechaCreacion[0]) +". ¿Desea cargar los datos?")
    if respuesta == False:
      return
  cursor.execute('''DROP TABLE IF EXISTS eventos''')
  cursor.execute('''CREATE TABLE eventos
                (titulo text, lugar text, direccion text, poblacion text, fecha text, hora text, categoria text)''')
  for i in range(1,5):
    req = urllib.request.Request("https://sevilla.cosasdecome.es/eventos/filtrar?pg="+str(i), 
    headers={'User-Agent': 'Mozilla/5.0'}) 
    f = urllib.request.urlopen(req) 
    s = BeautifulSoup(f, 'html.parser')
    eventos = s.find_all("h2", class_="block-elto post-title nombre")
    for evento in eventos:
      titulo = ""
      lugar = ""
      direccion = ""
      poblacion = ""
      fecha = ""
      hora = ""
      categoria = ""
      req1 = urllib.request.Request(evento.a['href'], headers={'User-Agent': 'Mozilla/5.0'}) 
      f1 = urllib.request.urlopen(req1) 
      s1 = BeautifulSoup(f1, 'html.parser')
      titulo = s1.find("div", class_="post-title entry-title value").text
      contenedorLugar = s1.find("div", class_="block-elto lugar")
      if contenedorLugar is not None:
        lugar = contenedorLugar.find("div", class_="value").text
      contenedorDireccion = s1.find("div", class_="block-elto direccion")
      if contenedorDireccion is not None:
        direccion = contenedorDireccion.find("div", class_="value").text
      contenedorDireccion = s1.find("div", class_="block-elto poblacion")
      if contenedorDireccion is not None:
        poblacion = contenedorDireccion.find("a", class_="label label-default").text
      fecha = s1.find("div", class_="post-date updated value").text.strip()
      contenedorHora = s1.find("div", class_="block-elto hora")
      if contenedorHora is not None:
        hora = contenedorHora.find("div", class_="value").text.strip()
        if "Desde las" in hora:
          hora = hora.replace("Desde las ", "")
          hora = hora.replace(".", ":")
      contenedorCategoria = s1.find("div", class_="block-elto categoria")
      if contenedorCategoria is not None:
        categoria = contenedorCategoria.find("a").text.strip()
      cursor.execute("INSERT INTO eventos VALUES (?,?,?,?,?,?,?)", (titulo, lugar, direccion, poblacion, fecha, hora, categoria))
      conn.commit()
  cursor.execute("SELECT COUNT(*) FROM eventos")
  cantidadFinal = cursor.fetchone()
  messagebox.showinfo("Carga de datos", "Se han cargado "+str(cantidadFinal[0])+" eventos en la base de datos.")
  conn.close()

# Apartado b.a
def lista_eventos():
  conn = sqlite3.connect('eventos.db')
  cursor = conn.cursor()
  ventana = Toplevel()
  ventana.title("Listado de eventos")
  scrollbar = Scrollbar(ventana)
  scrollbar.pack(side=RIGHT, fill=Y)
  lista = Listbox(ventana, yscrollcommand=scrollbar.set, width=200)
  cursor.execute("SELECT * FROM eventos")
  eventos = cursor.fetchall()
  for evento in eventos:
    lista.insert(END, "Título: "+evento[0])
    lista.insert(END, "Lugar: "+evento[1])
    lista.insert(END, "Dirección: "+evento[2])
    lista.insert(END, "Población: "+evento[3])
    lista.insert(END, "Fecha: "+evento[4])
    lista.insert(END, "Hora: "+evento[5])
    lista.insert(END, "Categoría: "+evento[6])
    lista.insert(END, "")
  lista.pack(side=LEFT, fill=BOTH)
  scrollbar.config(command=lista.yview)
  conn.close()

# Apartado b.b
def lista_eventos_noche():
  conn = sqlite3.connect('eventos.db')
  cursor = conn.cursor()
  ventana = Toplevel()
  ventana.title("Listado de eventos nocturnos")
  scrollbar = Scrollbar(ventana)
  scrollbar.pack(side=RIGHT, fill=Y)
  lista = Listbox(ventana, yscrollcommand=scrollbar.set, width=200)
  cursor.execute("SELECT * FROM eventos")
  eventos = cursor.fetchall()
  for evento in eventos:
    if "cena" in evento[5] or "cenas" in evento[5] or (":" in evento[5] and int(evento[5].split(":")[0]) >= 19):
      lista.insert(END, "Título: "+evento[0])
      lista.insert(END, "Lugar: "+evento[1])
      lista.insert(END, "Dirección: "+evento[2])
      lista.insert(END, "Población: "+evento[3])
      lista.insert(END, "Fecha: "+evento[4])
      lista.insert(END, "Hora: "+evento[5])
      lista.insert(END, "Categoría: "+evento[6])
      lista.insert(END, "")
  lista.pack(side=LEFT, fill=BOTH)
  scrollbar.config(command=lista.yview)
  conn.close()

# Apartado c.a
def buscar_fecha_celebración():
  ventana = Toplevel()
  ventana.title("Buscar fecha de celebración")
  label = tk.Label(ventana, text="Introduce la fecha de celebración (dd de mes de yyyy):")
  label.pack()
  fecha = tk.Entry(ventana)
  fecha.pack()
  boton = tk.Button(ventana, text="Buscar", command=lambda: buscar_fecha(fecha.get()))
  boton.pack()
  scrollbar = Scrollbar(ventana)
  scrollbar.pack(side=RIGHT, fill=Y)
  lista = Listbox(ventana, yscrollcommand=scrollbar.set, width=200)
  lista.pack(side=LEFT, fill=BOTH)
  scrollbar.config(command=lista.yview)
  def buscar_fecha(fecha):
    lista.delete(0, END)
    meses = {"enero": "01", "febrero": "02", "marzo": "03", "abril": "04", "mayo": "05", "junio": "06", "julio": "07", "agosto": "08", "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12"}
    fechaFormateada = fecha.split(" de ")
    fechaFormateada[1] = meses[fechaFormateada[1]]
    fechaFormateada = fechaFormateada[0]+"/"+fechaFormateada[1]+"/"+fechaFormateada[2]
    conn = sqlite3.connect('eventos.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM eventos")
    eventos = cursor.fetchall()
    for evento in eventos:
      if fechaFormateada in evento[4]:
        lista.insert(END, "Título: "+evento[0])
        lista.insert(END, "Lugar: "+evento[1])
        lista.insert(END, "Dirección: "+evento[2])
        lista.insert(END, "Población: "+evento[3])
        lista.insert(END, "Fecha: "+evento[4])
        lista.insert(END, "Hora: "+evento[5])
        lista.insert(END, "Categoría: "+evento[6])
        lista.insert(END, "")
      if " al " in evento[4]:
        rango = evento[4].split(" al ")
        if fechaFormateada >= rango[0] and fechaFormateada <= rango[1]:
          lista.insert(END, "Título: "+evento[0])
          lista.insert(END, "Lugar: "+evento[1])
          lista.insert(END, "Dirección: "+evento[2])
          lista.insert(END, "Población: "+evento[3])
          lista.insert(END, "Fecha: "+evento[4])
          lista.insert(END, "Hora: "+evento[5])
          lista.insert(END, "Categoría: "+evento[6])
          lista.insert(END, "")
    conn.close()
  
  pass

# Apartado c.b
def buscar_categoria_o_poblacion():
  def rellena_spinbox(spinbox, eleccion):
    conn = sqlite3.connect('eventos.db')
    cursor = conn.cursor()
    if eleccion == "categoria":
      cursor.execute("SELECT DISTINCT categoria FROM eventos")
    else:
      cursor.execute("SELECT DISTINCT poblacion FROM eventos")
    valores = cursor.fetchall()
    valores = [x[0] for x in valores]
    spinbox.config(values=valores)
    conn.close()
  ventana = Toplevel()
  ventana.title("Buscar por categoría o población")
  eleccion = tk.StringVar()
  eleccion.set("categoria")
  radioCategoria = tk.Radiobutton(ventana, text="Categoría", variable=eleccion, value="categoria", command=lambda: rellena_spinbox(spinbox, eleccion.get()))
  radioCategoria.pack()
  radioPoblacion = tk.Radiobutton(ventana, text="Población", variable=eleccion, value="poblacion", command=lambda: rellena_spinbox(spinbox, eleccion.get()))
  radioPoblacion.pack()
  conn = sqlite3.connect('eventos.db')
  cursor = conn.cursor()
  cursor.execute("SELECT DISTINCT categoria FROM eventos")
  categorias = cursor.fetchall()
  categorias = [x[0] for x in categorias]
  cursor.execute("SELECT DISTINCT poblacion FROM eventos")
  poblaciones = cursor.fetchall()
  poblaciones = [x[0] for x in poblaciones]
  conn.close()
  spinbox = ttk.Combobox(ventana, values=categorias)
  spinbox.pack()
  boton = tk.Button(ventana, text="Buscar", command=lambda: buscar_categoria_poblacion(eleccion.get(), spinbox.get()))
  boton.pack()
  scrollbar = Scrollbar(ventana)
  scrollbar.pack(side=RIGHT, fill=Y)
  lista = Listbox(ventana, yscrollcommand=scrollbar.set, width=200)
  lista.pack(side=LEFT, fill=BOTH)
  scrollbar.config(command=lista.yview)
  def buscar_categoria_poblacion(eleccion, valor):
    lista.delete(0, END)
    conn = sqlite3.connect('eventos.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM eventos WHERE "+eleccion+ "=? ORDER BY fecha", (valor,))
    eventos = cursor.fetchall()
    for evento in eventos:
      lista.insert(END, "Título: "+evento[0])
      lista.insert(END, "Lugar: "+evento[1])
      lista.insert(END, "Dirección: "+evento[2])
      lista.insert(END, "Población: "+evento[3])
      lista.insert(END, "Fecha: "+evento[4])
      lista.insert(END, "Hora: "+evento[5])
      lista.insert(END, "Categoría: "+evento[6])
      lista.insert(END, "")
    conn.close()  

# Ventana principal
def ventana_principal():
  # Apartado a.b
  def salir():
    ventana.destroy()

  ventana = tk.Tk()
  ventana.title("Práctica AII BS")
  ventana.geometry
  barraMenu = tk.Menu(ventana)
  menuDatos = tk.Menu(barraMenu, tearoff=0)
  menuDatos.add_command(label="Cargar", command=carga_datos)
  menuDatos.add_command(label="Salir", command=salir)
  barraMenu.add_cascade(label="Datos", menu=menuDatos)
  menuListar = tk.Menu(barraMenu, tearoff=0)
  menuListar.add_command(label="Eventos", command=lista_eventos)
  menuListar.add_command(label="Eventos por la noche", command=lista_eventos_noche)
  barraMenu.add_cascade(label="Listar", menu=menuListar)
  menuBuscar = tk.Menu(barraMenu, tearoff=0)
  menuBuscar.add_command(label="Fecha de celebración", command=buscar_fecha_celebración)
  menuBuscar.add_command(label="Eventos por categoría o población", command=buscar_categoria_o_poblacion)
  barraMenu.add_cascade(label="Buscar", menu=menuBuscar)

  ventana.config(menu=barraMenu)
  ventana.mainloop()
  
if __name__=="__main__":
  ventana_principal()