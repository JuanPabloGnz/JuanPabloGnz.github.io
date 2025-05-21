import pandas as pd
import os

def guardar_partida(nombre_usuario, aciertos, total_preguntas, hora_inicio):
    """
    Guarda los datos de una partida en un archivo de historial.
    """
    #Unir los tres parametros en la variable registro
    registro = f"{hora_inicio} ; {nombre_usuario} ; {aciertos}/{total_preguntas}\n"

    with open("./data/historial_partidas.txt", "a", encoding="utf-8") as file:
        file.write(registro)

def leer_puntajes():
    """
    Lee el historial de partidas desde un archivo y devuelve una lista de diccionarios.
    """
    historial_partidas = []
    try:
        with open("./data/historial_partidas.txt", "r", encoding="utf-8") as file:
            for linea in file:
                datos = linea.strip().split(";")
                if len(datos) == 3:
                    hora, usuario, aciertos = datos
                    historial_partidas.append({"hora": hora, "usuario": usuario, "aciertos": aciertos})
    
    except FileNotFoundError:
        historial_partidas = []  # Si el archivo no existe, la lista queda vacía

    return historial_partidas

def leer_historial():
    """
    Lee el archivo historial_partidas.txt y devuelve un DataFrame con los datos corregidos.
    """
    datos = []
    if os.path.exists("./data/historial_partidas.txt"):
        with open("./data/historial_partidas.txt", "r", encoding="utf-8") as file:
            for linea in file:
                try:
                    # Separar los datos según el nuevo formato
                    partes = linea.strip().split(" ; ")
                    if len(partes) == 3:
                        fecha_str, usuario, aciertos_str = partes

                        # Convertir la fecha al formato adecuado
                        #fecha = datetime.datetime.strptime(fecha_str, "%d/%m/%y %H:%M")
                        fecha = fecha_str

                        # Extraer aciertos y total de preguntas
                        aciertos, total = map(int, aciertos_str.split("/"))
                        desaciertos = total - aciertos

                        datos.append([fecha, usuario, aciertos, desaciertos])

                except Exception as e:
                    print(f"Error procesando la línea: {linea} - {e}")
                    continue  # Ignorar líneas mal formateadas

    return pd.DataFrame(datos, columns=["Fecha", "Usuario", "Aciertos", "Desaciertos"])
