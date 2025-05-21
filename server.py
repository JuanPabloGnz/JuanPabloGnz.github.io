# Ejemplo de aplicación principal en Flask
from flask import render_template ,redirect, url_for, request, session, flash,send_file
from modules.config import app
from modules.funciones import cargar_datos, listar_peliculas, obtener_pregunta_y_opciones,generar_graficos,generar_pdf
from modules.resultados import guardar_partida,leer_puntajes
from datetime import datetime

# Página de inicio
@app.route('/inicio', methods=['GET', 'POST'])
def inicio():
    if request.method == 'POST':
        session.clear()
        nombre_usuario = request.form['nombre_usuario']
        nro_iteraciones = int(request.form['name_nro_iteraciones'])

        # Guardar el nombre de usuario y el número de iteraciones en la sesión
        
        session['nombre_usuario'] = nombre_usuario
        session['nro_iteraciones'] = nro_iteraciones
        

        # Redirigir a la página del juego
        return redirect(url_for('juego'))

    return render_template('inicio.html')

@app.route('/juego', methods=['GET', 'POST'])
def juego():
    if 'nro_iteraciones' not in session or 'nombre_usuario' not in session:
        return redirect(url_for('inicio'))  # Redirige si no hay datos en sesión

    # Cargar datos de frases y películas
    peliculas = cargar_datos("./data/frases_de_peliculas.txt")
    lista_peliculas = listar_peliculas(peliculas)

    # Inicializar variables de la sesión
    if 'pregunta_actual' not in session:
        session['pregunta_actual'] = 0
        session['aciertos'] = 0
        session['hora_inicio'] = datetime.now().strftime("%d/%m/%y %H:%M")
        session.modified = True  # Asegurar que la sesión se actualiza correctamente

    # Si es una respuesta POST, evaluamos la respuesta anterior
    if request.method == 'POST':
        respuesta_usuario = request.form['respuesta']
        respuesta_correcta = session.get('respuesta_correcta', None)  # Obtener la respuesta correcta almacenada
        
        if respuesta_usuario == respuesta_correcta:
            session['aciertos'] += 1
            flash("¡Felicitaciones! Elegiste la opción correcta")
            session.modified = True  # Asegurar que la sesión se actualiza
        else:
            flash("¡La respuesta anterior fue incorrecta! La frase en realidad pertenece a la película: " + respuesta_correcta)
        # Avanzar a la siguiente pregunta
        session['pregunta_actual'] += 1
        session.modified = True

        if session['pregunta_actual'] >= session['nro_iteraciones']:
             # Guardar los resultados en historial con la hora de inicio
            hora_inicio = session.get('hora_inicio', datetime.now().strftime("%d/%m/%y %H:%M"))  # Si falta, usa la hora actual
            guardar_partida(session['nombre_usuario'], session['aciertos'], session['nro_iteraciones'], hora_inicio)
            # Juego terminado, mostrar puntaje final
            return render_template('resultado.html', aciertos=session['aciertos'], total=session['nro_iteraciones'])

    # Generar una nueva pregunta si aún quedan iteraciones
    pregunta_data = obtener_pregunta_y_opciones(peliculas, lista_peliculas)
    
    # Guardamos la respuesta correcta en sesión para poder verificarla en el siguiente POST
    session['respuesta_correcta'] = pregunta_data['respuesta_correcta']
    session.modified = True  # Asegurar que la sesión se actualiza correctamente

    # Renderiza la página de juego con la frase y opciones
    return render_template('juego.html', 
                           nombre_usuario=session['nombre_usuario'],
                           frase=pregunta_data['frase'], 
                           opciones=pregunta_data['opciones'], 
                           nro_pregunta=session['pregunta_actual'] + 1, 
                           total_preguntas=session['nro_iteraciones'])


@app.route('/lista_peliculas', methods=['GET', 'POST'])
def lista_peliculas():
    lista_nombres = listar_peliculas(cargar_datos("./data/frases_de_peliculas.txt"))
    return render_template('lista_nombres.html',peliculas=lista_nombres)

@app.route('/puntajes')
def puntaje():
    partidas = leer_puntajes()  # Llamamos a la función
    return render_template("puntaje.html", partidas=partidas)

@app.route('/graficas')
def graficas():
    exito = generar_graficos()  # Llamamos a la función para generar los gráficos
    if not exito:
        return "No hay datos suficientes para generar gráficos."

    return render_template("graficas.html")

@app.route('/descargar_graficas')
def descargar_graficas():
    """
    Genera un PDF con las gráficas y lo ofrece para su descarga.
    """
    pdf_filename = generar_pdf()
    if not pdf_filename:
        return "No hay datos suficientes para generar el PDF."

    return send_file(pdf_filename, as_attachment=True, download_name="reporte.pdf")

    
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
    