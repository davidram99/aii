# Laboratiro 2 BeatuifulSoup
# Imports
from bs4 import BeautifulSoup
import requests
import tkinter as tk
from tkinter import messagebox
from tkinter import Toplevel, Listbox, Scrollbar, END, Y, BOTH, RIGHT, LEFT
import sqlite3
# lineas para evitar error SSL
import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


# Vamos a realizar webscraping, haciendo uso de BeautifulSoup, sobre la web del diario ‘as’:
# http://resultados.as.com/resultados/futbol/primera/2021_2022/calendario/.
# Dentro de cada resultado hay un link hacia la página de la retransmisión en directo, de la que
# podemos extraer alguno de los datos a mostrar.

# Buscamos construir un programa con Tkinter con cinco botones:
# a) “Almacenar Resultados”, que sea capaz de extraer y almacenar en una base de datos
# sqlite los resultados de todas las jornadas y los links a las retransmisiones en directo
# de cada partido. Muestre una ventana de información con el número de registros
# almacenados.

def almacenar_bd():
    # Conexión a la base de datos
    conn = sqlite3.connect('resultados.db')
    cursor = conn.cursor()
    # Creamos la tabla jornadas con las columnas id, numero, local, visitante, resultado, link
    cursor.execute("DROP TABLE IF EXISTS jornadas")
    cursor.execute("CREATE TABLE IF NOT EXISTS jornadas (numero INTEGER, local TEXT, visitante TEXT, resultado TEXT, link TEXT)")
    # Obtenemos la página web
    url = 'http://resultados.as.com/resultados/futbol/primera/2021_2022/calendario/'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    # Obtenemos las jornadas
    jornadas = soup.find_all('div', class_='cont-modulo resultados')
    for jornada in jornadas:
        # Obtenemos el número de la jornada
        idJornada = jornada.find('h2', class_='tit-modulo').find('a').text
        # De numero guardamos la segunda palabra en integer
        numero = idJornada.split()[1]
        numero = int(numero)
        tablaPartidos = jornada.find('table', class_='tabla-datos').find('tbody')
        partidos = tablaPartidos.find_all('tr')
        for partido in partidos:
            local = partido.find('td', class_='col-equipo-local').find('span', class_='nombre-equipo').text.strip()
            visitante = partido.find('td', class_='col-equipo-visitante').find('span', class_='nombre-equipo').text.strip()
            resultado = partido.find('td', class_='col-resultado').find('a', class_='resultado').text.strip()
            link = partido.find('td', class_='col-resultado').find('a', class_='resultado')['href']
            # Guardar la linea en BBDD
            conn.execute("""INSERT INTO jornadas (numero, local, visitante, resultado, link) VALUES(?,?,?,?,?)""", (numero, local, visitante, resultado, link))
            conn.commit()
    cursor = conn.execute("SELECT COUNT(*) FROM jornadas")
    messagebox.showinfo("Base Datos", "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " registros")
    conn.close()

def buscar_por_jornada(numero):
    try:
        # Conexión a la base de datos
        conn = sqlite3.connect('resultados.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jornadas WHERE numero = ?", (numero,))
        # Lo convertimos en una lista
        data = cursor.fetchall()
        # Cerramos la conexión
        conn.close()
        return data
    except Exception as e:
        messagebox.showerror("Error", "Error al buscar en la base de datos")
        return []

def listar_jornadas():
    # Conexión a la base de datos
    conn = sqlite3.connect('resultados.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jornadas")
    # Lo convertimos en una lista
    data = cursor.fetchall()
    # Extraemos un set con las jornadas
    jornadas = set([jornada[0] for jornada in data])
    # Creamos la ventana tipo listbox con scroll
    ventana = Toplevel()
    listbox = Listbox(ventana, width=50)
    scrollbar = Scrollbar(ventana)
    scrollbar.pack(side=RIGHT, fill=Y)
    listbox.pack(side=LEFT, fill=BOTH, expand=1)
    scrollbar.config(command=listbox.yview)
    listbox.config(yscrollcommand=scrollbar.set)
    # Añadimos las jornadas
    for jornada in jornadas:
        listbox.insert(END, f'JORNADA {jornada}')
        listbox.insert(END, "-------------------------------")
        for partido in data:
            if partido[0] == jornada:
                listbox.insert(END, f'{partido[1]} {partido[3]} {partido[2]}')
        listbox.insert(END, "-------------------------------")
        listbox.insert(END, "")
    conn.close()
    
def buscar_jornada():
    # Creamos la ventana
    ventana = Toplevel()
    ventana.title("Buscar Jornada")
    # Creamos el label
    label = tk.Label(ventana, text="Introduce el número de la jornada")
    label.pack()
    # Creamos el entry de número de jornada que solo acepta números entre 1 y 38
    entry = tk.Entry(ventana)
    entry.pack()
    entry.config(validate="key", validatecommand=(entry.register(lambda text: text.isdigit() and 0 < int(text) < 39), "%P"))
    # Función para llamar a la función buscar_por_jornada y guardar el resultado en una variable
    resultados = []
    def buscar_y_guardar():
        nonlocal resultados
        resultados = buscar_por_jornada(entry.get())
            # Creamos la ventana tipo listbox con scroll
        ventana = Toplevel()
        listbox = Listbox(ventana, width=50)
        scrollbar = Scrollbar(ventana)
        scrollbar.pack(side=RIGHT, fill=Y)
        listbox.pack(side=LEFT, fill=BOTH, expand=1)
        scrollbar.config(command=listbox.yview)
        listbox.config(yscrollcommand=scrollbar.set)
        # Añadimos las jornadas
        for partido in resultados:
            listbox.insert(END, f'{partido[1]} {partido[3]} {partido[2]}')
    # Creamos el boton
    boton = tk.Button(ventana, text="Buscar", command=buscar_y_guardar)
    boton.pack()

def estadisticas_jornada():
    # Creamos la ventana
    ventana = Toplevel()
    ventana.title("Buscar Jornada")
    # Creamos el label
    label = tk.Label(ventana, text="Introduce el número de la jornada")
    label.pack()
    # Creamos el entry de número de jornada que solo acepta números entre 1 y 38
    entry = tk.Entry(ventana)
    entry.pack()
    entry.config(validate="key", validatecommand=(entry.register(lambda text: text.isdigit() and 0 < int(text) < 39), "%P"))
    # Creamos el boton
    boton = tk.Button(ventana, text="Buscar", command=lambda: buscar_por_jornada(entry.get()))
    boton.pack()

# Genera la ventana principal
ventana = tk.Tk()
ventana.title("Laboratorio 2")
ventana.geometry("300x300")
# Boton para almacenar resultados
boton = tk.Button(ventana, text="Almacenar Resultados", command=almacenar_bd)
boton.pack()
# Boton para mostrar resultados
boton = tk.Button(ventana, text="Listar Jornadas", command=listar_jornadas)
boton.pack()
# Boton para buscar jornada
boton = tk.Button(ventana, text="Buscar Jornada", command=buscar_jornada)
boton.pack()
# Botón para ver estadísticas de una jornada
boton = tk.Button(ventana, text="Estadísticas Jornada", command=estadisticas_jornada)
boton.pack()

ventana.mainloop()