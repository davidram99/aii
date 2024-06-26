# Laboratiro 2 BeatuifulSoup
# Imports
from bs4 import BeautifulSoup
import requests
import tkinter as tk
from tkinter import messagebox
from tkinter import Toplevel, Listbox, Scrollbar, END, Y, BOTH, RIGHT, LEFT, ttk
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

def buscar_y_mostrar_resultados(numero):
    try:
        # Conexión a la base de datos
        conn = sqlite3.connect('resultados.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jornadas WHERE numero = ?", (numero,))
        # Lo convertimos en una lista
        data = cursor.fetchall()
        # Creamos la ventana tipo listbox con scroll
        ventana = Toplevel()
        listbox = Listbox(ventana, width=50)
        scrollbar = Scrollbar(ventana)
        scrollbar.pack(side=RIGHT, fill=Y)
        listbox.pack(side=LEFT, fill=BOTH, expand=1)
        scrollbar.config(command=listbox.yview)
        listbox.config(yscrollcommand=scrollbar.set)
        # Añadimos los partidos
        for partido in data:
            listbox.insert(END, f'{partido[1]} {partido[3]} {partido[2]}')
        # Cerramos la conexión
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", "Error al buscar en la base de datos")

def buscar_y_mostrar_estadisticas(numero):
    try:
        # Conexión a la base de datos
        conn = sqlite3.connect('resultados.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jornadas WHERE numero = ?", (numero,))
        # Lo convertimos en una lista
        data = cursor.fetchall()
        # Creamos la ventana tipo listbox con scroll
        ventana = Toplevel()
        listbox = Listbox(ventana, width=50)
        scrollbar = Scrollbar(ventana)
        scrollbar.pack(side=RIGHT, fill=Y)
        listbox.pack(side=LEFT, fill=BOTH, expand=1)
        scrollbar.config(command=listbox.yview)
        listbox.config(yscrollcommand=scrollbar.set)
        goles_jornada = 0
        empates_jornada = 0
        victorias_local_jornada = 0
        victorias_visitante_jornada = 0  
        for partido in data:
            # Total de goles de la jornada
            goles = partido[3].split('-')
            goles_jornada += int(goles[0]) + int(goles[1])
            # Empates
            if int(goles[0]) == int(goles[1]):
                empates_jornada += 1
            # Victorias locales
            elif int(goles[0]) > int(goles[1]):
                victorias_local_jornada += 1
            # Victorias visitantes
            else:
                victorias_visitante_jornada += 1
        listbox.insert(END, f'TOTAL GOLES JORNADA: {goles_jornada}')
        listbox.insert(END, '')
        listbox.insert(END, f'EMPATES: {empates_jornada}')
        listbox.insert(END, f'VICTORIAS LOCALES: {victorias_local_jornada}')
        listbox.insert(END, f'VICTORIAS VISITANTES: {victorias_visitante_jornada}')

    except Exception as e:
        messagebox.showerror("Error", "Error al buscar en la base de datos")

def buscar_goles_equipo(numero, local):
    try:
        # Conexión a la base de datos
        conn = sqlite3.connect('./Lab2_resultados.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jornadas WHERE numero = ? AND local = ?", (numero, local))
        # Lo convertimos en una lista
        data = cursor.fetchall()
        data = [partido for partido in data]
        url = data[0][4]
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        jugadores = soup.find_all('div', class_='scr-hdr__scorers')
        goleadores = []
        for jugador in jugadores:
            cancheros = jugador.find_all('span')
            for canchero in cancheros:
                if not canchero.has_attr("class"):
                    goleadores.append(canchero.text.strip())
        # Creamos la ventana tipo listbox con scroll
        ventana = Toplevel()
        listbox = Listbox(ventana, width=50)
        scrollbar = Scrollbar(ventana)
        scrollbar.pack(side=RIGHT, fill=Y)
        listbox.pack(side=LEFT, fill=BOTH, expand=1)
        scrollbar.config(command=listbox.yview)
        listbox.config(yscrollcommand=scrollbar.set)
        # Añadimos los goleadores
        for goleador in goleadores:
            listbox.insert(END, goleador)
        # Cerramos la conexión
        conn.close()
    except Exception as e:
        messagebox.showerror("Error", "Error al buscar en la base de datos")

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
    
def buscar_jornada(tipo_busqueda):
    # Conectamos a la base de datos
    conn = sqlite3.connect('resultados.db')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT numero FROM jornadas")
    # Lo convertimos en una lista
    data = cursor.fetchall()
    # Creamos la ventana
    ventana = Toplevel()
    ventana.title("Buscar Jornada")
    # Creamos el label
    label = tk.Label(ventana, text="Seleccione la jornada")
    label.pack()
    # Jornada será una lista con los números de las jornadas (el primer elemento de cada set de la lista data)
    jornadas = [jornada[0] for jornada in data]
    # Ordena la lista
    jornadas.sort()
    # Creamos el spinbox de número de jornada que solo acepta números entre 1 y 38
    entry = tk.Spinbox(ventana, from_=jornadas[0], to=jornadas[-1])
    entry.pack()
    # Creamos el boton
    if tipo_busqueda == "resultados":
        boton = tk.Button(ventana, text="Buscar", command = lambda:buscar_y_mostrar_resultados(entry.get()))
    elif tipo_busqueda == "estadisticas":
        boton = tk.Button(ventana, text="Buscar", command = lambda:buscar_y_mostrar_estadisticas(entry.get()))
    boton.pack()
    # Cerramos la conexión
    conn.close()

def buscar_goles():
    def rellenar_combobox(numero_jornada):
        # Conectamos a la base de datos
        conn = sqlite3.connect('resultados.db')
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT local FROM jornadas WHERE numero = ?", (numero_jornada,))
        # Lo convertimos en una lista
        data = cursor.fetchall()
        # Rellenamos el combobox
        select_local['values'] = [local[0] for local in data]
        # Cerramos la conexión
        conn.close()
    def rellenar_visitante(numero_jornada, local):
        # Conectamos a la base de datos
        conn = sqlite3.connect('resultados.db')
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT visitante FROM jornadas WHERE numero = ? AND local = ?", (numero_jornada, local))
        # Lo convertimos en una lista
        data = cursor.fetchall()
        data = [visitante[0] for visitante in data]
        # Rellenamos el entry
        entry2['state'] = 'normal'
        entry2.delete(0, END)
        entry2.insert(0, data[0])
        entry2['state'] = 'disabled'
        # Cerramos la conexión
        conn.close()
    # Conectamos a la base de datos
    conn = sqlite3.connect('resultados.db')
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT numero FROM jornadas")
    # Lo convertimos en una lista
    data = cursor.fetchall()
    # Creamos la ventana
    ventana = Toplevel()
    ventana.title("Buscar Goles")
    # Jornada será una lista con los números de las jornadas (el primer elemento de cada set de la lista data)
    jornadas = [jornada[0] for jornada in data]
    # Ordena la lista
    jornadas.sort()
    label = tk.Label(ventana, text="Seleccione jornada")
    label.pack(side=LEFT)
    # Creamos el spinbox de número de jornada que solo acepta números entre 1 y 38
    entry = tk.Spinbox(ventana, from_=jornadas[0], to=jornadas[-1], command=lambda:rellenar_combobox(entry.get()), state="readonly")
    entry.pack(side=LEFT)
    # Creamos el label
    label = tk.Label(ventana, text="Seleccione equipo local")
    label.pack(side=LEFT)
    # Creamos el spinbox de equipo local
    select_local = tk.Spinbox(ventana, values=[], state="readonly", command=lambda:rellenar_visitante(entry.get(), select_local.get()))
    select_local.pack(side=LEFT)
    # Creamos el label
    label = tk.Label(ventana, text="Equipo visitante")
    label.pack(side=LEFT)
    # Creamos el entry disabled
    entry2 = tk.Entry(ventana, state='disabled')
    entry2.pack(side=LEFT)
    # Creamos el boton
    boton = tk.Button(ventana, text="Buscar goles", command = lambda:buscar_goles_equipo(entry.get(), select_local.get()))
    boton.pack(side=LEFT)
    # Cerramos la conexión
    conn.close()

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
boton = tk.Button(ventana, text="Buscar Jornada", command=lambda:buscar_jornada('resultados'))
boton.pack()
# Botón para ver estadísticas de una jornada
boton = tk.Button(ventana, text="Estadísticas Jornada", command=lambda:buscar_jornada('estadisticas'))
boton.pack()
# Botón para buscar goles
boton = tk.Button(ventana, text="Buscar Goles", command=buscar_goles)
boton.pack()

ventana.mainloop()