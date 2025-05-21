import random
import datetime
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import pandas as pd
import os
from matplotlib.backends.backend_pdf import PdfPages

def cargar_datos(nombre_archivo:str) -> dict:
    """
    Carga los datos de un archivo de texto y los devuelve en un diccionario.
    """
    diccionario_frases = {}
    with open(nombre_archivo, "r", encoding="utf-8") as file:
        for linea in file :
            frase, pelicula = linea.strip().split(";", 1)  
            diccionario_frases[frase] = pelicula
    return diccionario_frases

def listar_peliculas(datos: dict):
    """
    función que lee datos desde un archivo y retorna esos datos en un diccionario donde las claves son las frases y los valores son las películas correspondientes
    """
    datos_ordenados = pd.DataFrame(sorted(datos.values())) #Pasamos el dict a un df para usar funciones de pandas
    datos = datos_ordenados.iloc[:,0].str.lower() # Pasamos a minuscula los strings de la primer col
    peliculas = datos.drop_duplicates() # Eliminamos duplicados
    list_peliculas = list(peliculas.str.title()) # Ponemos las mayúsculas en los títulos

    return list(sorted(list_peliculas))

def obtener_pregunta_y_opciones(diccionario_frases: dict, lista_peliculas: list) -> dict:
    """
    Elige una frase al azar y genera las opciones de película, donde una es correcta
    y las otras dos son incorrectas.
    """
    frase_correcta = random.choice(list(diccionario_frases.keys()))
    pelicula_correcta = diccionario_frases[frase_correcta]
    
    # Elegir dos películas incorrectas aleatorias
    opciones_incorrectas = random.sample([pelicula for pelicula in lista_peliculas if pelicula != pelicula_correcta], 2)
    
    # Juntar la correcta y las incorrectas
    opciones = [pelicula_correcta] + opciones_incorrectas
    random.shuffle(opciones)  # Mezclar las opciones

    return {
        'frase': frase_correcta,
        'opciones': opciones,
        'respuesta_correcta': pelicula_correcta
    }

def generar_graficos():
    """
    Genera y guarda dos gráficos: uno de líneas con aciertos/desaciertos y otro circular.
    """
    resultado = True

    df = leer_historial()
    if df.empty:
        resultado = False   # No hay datos para graficar

    # Ordenar por fecha
    df = df.sort_values("Fecha")

    #  Gráfico de líneas: Aciertos y desaciertos a lo largo del tiempo
    plt.figure(figsize=(10, 5))
    plt.plot(df["Fecha"], df["Aciertos"], marker="o", linestyle="-", label="Aciertos", color="green")
    plt.plot(df["Fecha"], df["Desaciertos"], marker="o", linestyle="-", label="Desaciertos", color="red")
    plt.xlabel("Fecha")
    plt.ylabel("Cantidad")
    plt.title("Evolución de Aciertos y Desaciertos")
    plt.legend()
    plt.xticks(rotation=45)
    plt.grid()
    plt.tight_layout()
    plt.savefig("./static/grafico_lineas.png")  # Guardar imagen temporalmente
    plt.close()

    #  Gráfico de torta: Proporción total de aciertos y desaciertos
    total_aciertos = df["Aciertos"].sum()
    total_desaciertos = df["Desaciertos"].sum()
    
    plt.figure(figsize=(6, 6))
    plt.pie([total_aciertos, total_desaciertos], labels=["Aciertos(" + str(total_aciertos)+")", "Desaciertos(" + str(total_desaciertos)+")"],
            autopct="%1.1f%%", colors=["green", "red"], startangle=90)
    plt.title("Distribución Total de Aciertos y Desaciertos")
    plt.tight_layout()
    plt.savefig("./static/grafico_torta.png")  # Guardar imagen temporalmente
    plt.close()

    return resultado

def generar_pdf():
    '''
    Genera un reporte en un archivo pdf a partir de dos imagenes de graficos.
    '''
    # Definir ruta de salida del PDF
    pdf_path = "./static/reporte.pdf"

    # Crear un objeto PdfPages
    with PdfPages(pdf_path) as pdf:
        # Lista de imágenes a incluir
        imagenes = ["./static/grafico_lineas.png", "./static/grafico_torta.png"]

        for img_path in imagenes:
            # Cargar imagen
            img = plt.imread(img_path)

            # Crear una figura y mostrar la imagen
            fig, ax = plt.subplots(figsize=(8, 6))  # Tamaño de la página
            ax.imshow(img)
            ax.axis("off")  # Ocultar ejes

            # Guardar la figura en el PDF
            pdf.savefig(fig)
            plt.close(fig)  # Cerrar la figura para liberar memoria

    print("PDF generado correctamente en", pdf_path)
    return pdf_path

if __name__ == "__main__":
    numero = 1
    for i in listar_peliculas(cargar_datos("./data/frases_de_peliculas.txt")):
        print(str(numero)+ ". " +i) 
        numero +=1

