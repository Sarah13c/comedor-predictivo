from tkinter import messagebox

import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sqlalchemy import create_engine
import datetime
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import *
from ttkthemes import ThemedTk
from tkinter.ttk import *
import pymysql
import tkinter.font as tkFont
# from forex_python.converter import CurrencyRates
import mysql


class ConexionBD:
    def __init__(self, usuario, password, host, puerto, base_datos):
        self.engine = create_engine(f'mysql+mysqlconnector://{usuario}:{password}@{host}:/{base_datos}')

    def ejecutar_query(self, query):
        with self.engine.connect() as conn:
            resultados = conn.execute(query).fetchall()
        return resultados


def prediccion_comida():
    # Crear una ventana para mostrar la información
    ventana = tk.Toplevel(root)

    engine = create_engine('mysql+mysqlconnector://root@localhost/comedor')

    # Cargar datos desde una base de datos
    df = pd.read_sql("SELECT vchDetalle, vchCantidad, fTotal, dtFecha FROM datawarehouse", con=engine)

    # Convertir la columna de fecha a un objeto datetime y extraer las características relevantes
    df['dtFecha'] = pd.to_datetime(df['dtFecha'])
    df['DiaSemana'] = df['dtFecha'].dt.dayofweek
    df['DiaMes'] = df['dtFecha'].dt.day
    df['Mes'] = df['dtFecha'].dt.month

    # Codificar variable categórica 'vchDetalle' con get_dummies()
    df = pd.get_dummies(df, columns=['vchDetalle'])

    # Dividir los datos en conjunto de entrenamiento y prueba basado en la fecha
    X = df.drop(['fTotal', 'dtFecha'], axis=1)
    y = df['fTotal']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)

    # Crear y entrenar el modelo
    modelo = LinearRegression()
    modelo.fit(X_train, y_train)

    # Obtener valores reales y predichos para el conjunto de prueba
    y_pred = modelo.predict(X_test)
    y_true = y_test.values

    # Crear arreglo para prediccion
    comida = 'COMIDA'
    cantidad = 2
    fecha = datetime.date.today() + datetime.timedelta(days=1)  # fecha de mañana
    codificacion_comida = pd.DataFrame([[fecha, comida, cantidad]], columns=['dtFecha', 'vchDetalle', 'vchCantidad'])
    codificacion_comida['dtFecha'] = pd.to_datetime(codificacion_comida['dtFecha'])
    codificacion_comida['DiaSemana'] = codificacion_comida['dtFecha'].dt.dayofweek
    codificacion_comida['DiaMes'] = codificacion_comida['dtFecha'].dt.day
    codificacion_comida['Mes'] = codificacion_comida['dtFecha'].dt.month
    codificacion_comida = pd.get_dummies(codificacion_comida, columns=['vchDetalle'])
    codificacion_comida = codificacion_comida.reindex(columns=X.columns, fill_value=0)

    # Realizar prediccion
    cantidad_predicha = modelo.predict(codificacion_comida)[0]

    # Crear el mensaje con la información
    messagebox.showinfo("Predicción",
                        f"La cantidad de {comida} que se solicitará mañana es de {cantidad_predicha} unidades")

    # Crear gráfica de barras para comparar valores reales y predichos
    plt.bar(['Valor real', 'Valor predicho'], [y_true.mean(), cantidad_predicha])
    plt.ylabel('Total de venta')
    plt.title('Comparación de valores reales y predichos')
    plt.show()


def graficacion_comida():
    # Conexión a la base de datos
    engine = create_engine('mysql+mysqlconnector://root@localhost/comedor')

    # Cargar datos desde una base de datos
    df = pd.read_sql("SELECT vchDetalle, vchCantidad, fTotal, dtFecha FROM datawarehouse", con=engine)

    # Convertir la columna de fecha a un objeto datetime y extraer las características relevantes
    df['dtFecha'] = pd.to_datetime(df['dtFecha'])
    df['DiaSemana'] = df['dtFecha'].dt.dayofweek
    df['DiaMes'] = df['dtFecha'].dt.day
    df['Mes'] = df['dtFecha'].dt.month

    # Codificar variable categórica 'vchDetalle' con get_dummies()
    df = pd.get_dummies(df, columns=['vchDetalle'])

    # Calcular el porcentaje de DESAYUNO, COMIDA y AGUA FRESCA en la base de datos
    total_desayunos = df['vchDetalle_DESAYUNO'].sum()
    total_comidas = df['vchDetalle_COMIDA'].sum()
    total_agua_fresca = df['vchDetalle_AGUA FRESCA'].sum()
    total_frutas = df['vchDetalle_FRUTA'].sum()
    total_registros = len(df)

    porcentaje_desayunos = (total_desayunos / total_registros) * 100
    porcentaje_comidas = (total_comidas / total_registros) * 100
    porcentaje_agua_fresca = (total_agua_fresca / total_registros) * 100
    porcentaje_frutas = (total_frutas / total_registros) * 100

    # Crear nueva columna para indicar si un registro corresponde a DESAYUNO o COMIDA
    df['TipoComida'] = df.apply(lambda row: 'DESAYUNO' if row['vchDetalle_DESAYUNO'] == 1 else 'COMIDA', axis=1)

    # Calcular el porcentaje de registros que tienen ambos valores en la columna TipoComida
    porcentaje_desayuno_comida = (df[(df['TipoComida'] == 'DESAYUNO') & (df['vchDetalle_COMIDA'] == 1)].shape[
                                      0] / total_registros) * 100

    labels = ['Desayunos', 'Comidas', 'Agua Fresca', 'Frutas']
    sizes = [porcentaje_desayunos, porcentaje_comidas, porcentaje_agua_fresca, porcentaje_frutas]

    # Configuración de la gráfica pastel
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax1.axis('equal')

    # Título de la gráfica
    plt.title('Porcentaje de alimentos en el comedor')

    # Mostrar la gráfica
    plt.show()


def pantalla_comida_solicitada():
    mydb = pymysql.connect(host="localhost", user="root", password="", database="comedor1")
    mycursor = mydb.cursor()

    # Fecthing Data From mysql to my python progame
    mycursor.execute(
        "select vchMeta, dtFecha from movcomedor where dtFecha between '2023-02-13 08:00:00' and '2023-02-13 09:00:00'")
    result = mycursor.fetchall

    vchMeta = []
    dtFecha = []

    for i in mycursor:
        vchMeta.append(i[0])
        dtFecha.append(i[1])

    print("ID Usuario = ", vchMeta)
    print("Fecha = ", dtFecha)

    # Visualizing Data using Matplotlib
    plt.bar(vchMeta, dtFecha)
    plt.ylim(0, 55)
    plt.xlabel("Id_empleado")
    plt.ylabel("fecha_hora")
    plt.title("Solicitudes después de la hora estimada")
    plt.show()


def prediccion_comida_dia():
    ventana = tk.Toplevel(root)

    # Conexión a la base de datos
    engine = create_engine('mysql+mysqlconnector://root@localhost/comedor')

    # Cargar datos desde una base de datos
    df = pd.read_sql("SELECT vchDetalle, vchCantidad, fTotal, dtFecha FROM datawarehouse", con=engine)

    # Convertir la columna de fecha a un objeto datetime y extraer las características relevantes
    df['dtFecha'] = pd.to_datetime(df['dtFecha'])
    df['DiaSemana'] = df['dtFecha'].dt.dayofweek
    df['DiaMes'] = df['dtFecha'].dt.day
    df['Mes'] = df['dtFecha'].dt.month

    # Codificar variable categórica 'vchDetalle' con get_dummies()
    df = pd.get_dummies(df, columns=['vchDetalle'])

    # Dividir los datos en conjunto de entrenamiento y prueba basado en la fecha
    X = df.drop(['fTotal', 'dtFecha'], axis=1)
    y = df['fTotal']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)

    # Crear y entrenar el modelo
    modelo = LinearRegression()
    modelo.fit(X_train, y_train)

    # Crear arreglo para prediccion
    comida = 'COMIDA'
    cantidad = 2
    fecha = datetime.date.today() + datetime.timedelta(days=1)  # fecha de mañana
    codificacion_comida = pd.DataFrame([[fecha, comida, cantidad]], columns=['dtFecha', 'vchDetalle', 'vchCantidad'])
    codificacion_comida['dtFecha'] = pd.to_datetime(codificacion_comida['dtFecha'])
    codificacion_comida['DiaSemana'] = codificacion_comida['dtFecha'].dt.dayofweek
    codificacion_comida['DiaMes'] = codificacion_comida['dtFecha'].dt.day
    codificacion_comida['Mes'] = codificacion_comida['dtFecha'].dt.month
    codificacion_comida = pd.get_dummies(codificacion_comida, columns=['vchDetalle'])

    # Reindexar codificacion_comida para asegurarse de que tiene la misma estructura que X
    codificacion_comida = codificacion_comida.reindex(columns=X.columns, fill_value=0)

    # Realizar prediccion
    cantidad_predicha = modelo.predict(codificacion_comida)[0]

    # Obtener el día de la semana con la mayor cantidad de comida solicitada
    dia_predicho = modelo.coef_[0] * codificacion_comida['DiaSemana'] + cantidad_predicha
    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    indice_maximo = dia_predicho.argmax()
    dia_maximo = dias_semana[indice_maximo]

    # Crear un cuadro de texto con la información

    texto = tk.Text(ventana, width=50, height=10)
    texto.insert(tk.END,
                 f"La cantidad de {comida} que se solicitará mañana es de {cantidad_predicha} unidades." + f"\n\nAdemás, el día de la semana en el que se solicitará más comida es el {dia_maximo}.")
    texto.configure(fg='#000000', font=(mi_fuente3))
    texto.pack()


def prediccion_comida_costo():
    ventana = tk.Toplevel(root)
    # Conexión a la base de datos
    engine = create_engine('mysql+mysqlconnector://root@localhost/comedor')

    # Cargar datos desde una base de datos
    df = pd.read_sql("SELECT vchDetalle, vchCantidad, fTotal, dtFecha FROM datawarehouse", con=engine)

    # Convertir la columna de fecha a un objeto datetime y extraer las características relevantes
    df['dtFecha'] = pd.to_datetime(df['dtFecha'])
    df['DiaSemana'] = df['dtFecha'].dt.dayofweek
    df['DiaMes'] = df['dtFecha'].dt.day
    df['Mes'] = df['dtFecha'].dt.month

    # Codificar variable categórica 'vchDetalle' con get_dummies()
    df = pd.get_dummies(df, columns=['vchDetalle'])

    # Dividir los datos en conjunto de entrenamiento y prueba basado en la fecha
    X = df.drop(['fTotal', 'dtFecha'], axis=1)
    y = df['fTotal']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, shuffle=False)

    # Crear y entrenar el modelo
    modelo = LinearRegression()
    modelo.fit(X_train, y_train)

    # Crear arreglo para prediccion
    comida = 'COMIDA'
    cantidad = 2
    fecha = datetime.date.today() + datetime.timedelta(days=1)  # fecha de mañana
    codificacion_comida = pd.DataFrame([[fecha, comida, cantidad]], columns=['dtFecha', 'vchDetalle', 'vchCantidad'])
    codificacion_comida['dtFecha'] = pd.to_datetime(codificacion_comida['dtFecha'])
    codificacion_comida['DiaSemana'] = codificacion_comida['dtFecha'].dt.dayofweek
    codificacion_comida['DiaMes'] = codificacion_comida['dtFecha'].dt.day
    codificacion_comida['Mes'] = codificacion_comida['dtFecha'].dt.month
    codificacion_comida = pd.get_dummies(codificacion_comida, columns=['vchDetalle'])
    codificacion_comida = codificacion_comida.reindex(columns=X.columns, fill_value=0)

    # Realizar prediccion
    cantidad_predicha = modelo.predict(codificacion_comida)[0]

    print(f"La cantidad de {comida} que se solicitará mañana es de {cantidad_predicha}")

    # Calcular costos de la comida
    costo_por_plato = 90  # pesos mexicanos
    costo_total = cantidad_predicha * costo_por_plato
    print(f"El costo total de {comida} para mañana es de {costo_total} pesos mexicanos.")

    # Crear un cuadro de texto con la información

    texto = tk.Text(ventana, width=50, height=10)
    texto.insert(tk.END,
                 f"La cantidad de {comida} que se solicitará mañana es de {cantidad_predicha} unidades" + f"\n\nAdemás, teniendo en cuenta que su costo unitario es de {costo_por_plato} pesos mexicanos, el costo total de la {comida} es de {costo_total} pesos mexicanos.")
    texto.configure(fg='#000000', font=(mi_fuente3))
    texto.pack()


'''-------------------MAIN-------------------------------'''

# Crear la ventana principal
root = tk.Tk()
root.title("Modelo predictivo del comedor")
# Definir tamaño de boton
root.geometry("460x440")
root.configure(bg='#FFFFFF', width=50, height=30)  # Cambiar fondo de la ventana a blanco
labelInicial = Label(root, text="MODELO PREDICTIVO COMEDOR", width=30, font=("helvetica", 20, "bold"),
                     borderwidth=4, relief="raised")
labelInicial.place(x=3, y=12)
# Crear fuente personalizada
mi_fuente3 = tkFont.Font(family="Helvetica", size=12)

# Estilo del botón
estilo_boton = {
    "font": "mi_fuente",
    "fg": "black",
    "bg": "gray95",
    "borderwidth": 2,
    "relief": "ridge"
}
# Crear un botón para mostrar la información
boton = tk.Button(root, text="Predicción de comida", **estilo_boton, width="18", command=prediccion_comida)
boton.place(x=40, y=85)
boton2 = tk.Button(root, text="Porcentaje de Comida", **estilo_boton, command=graficacion_comida)
boton2.place(x=250, y=85)
boton3 = tk.Button(root, text="Comida Solictada", **estilo_boton, command=pantalla_comida_solicitada)
boton3.place(x=53, y=140)
boton4 = tk.Button(root, text="Predicción de Día", **estilo_boton, command=prediccion_comida_dia)
boton4.place(x=263, y=140)
boton5 = tk.Button(root, text="Predicción de Costo", **estilo_boton, command=prediccion_comida_costo)
boton5.place(x=150, y=195)

textoIntegrantes = "- Cameros Moran Kevin Eduardo.\n\n- Cano Balanta Sarah.\n\n- Rojas Pérez Ana María.\n\n- Velarde Medina Ximena Lizeth."

labelIntegrantesSN = Label(root, text="Integrantes", font=("helvetica", 10, "bold"),background="white",
                     borderwidth=4, relief="flat")
labelIntegrantesSN.place(x=3, y=310)

labelIntegrantesNombres = Label(root, text=textoIntegrantes, font=("helvetica", 8), background="white")
labelIntegrantesNombres.place(x=3, y=330)

labelasignatura = Label(root, text="Almacenes de Datos - I5906", font=("helvetica", 8, "bold"), background="white")
labelasignatura.place(x=300, y=418)



# Iniciar el bucle de eventos
root.mainloop()
