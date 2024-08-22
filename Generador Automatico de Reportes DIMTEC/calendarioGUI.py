import tkinter as tk
from tkcalendar import DateEntry  # type: ignore
from datetime import datetime, timedelta, timezone
import re
import argparse



def widget_calendario(fecha_minima_parametro = ""):

    def fecha_datetime(date_str): # Recibe una fecha en String y la devuelve en datetime
        # Formato de fecha ISO 8601
        formato_de_fechas = "%Y-%m-%dT%H:%M:%SZ"
        # Formato para la librería re
        pattern = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
        if not pattern.match(date_str):
            raise ValueError(f"String de fecha'{date_str}' no tiene el formato'{formato_de_fechas}'")
        
        try:
            return datetime.strptime(date_str, formato_de_fechas).replace(tzinfo=timezone.utc)
        except ValueError as e:
            print(f"Error formateando la fecha: {e}")
            raise
    
    # Variables globales
    fecha_seleccionada = None
    hora_seleccionada = None

    def obtener_fecha_y_hora():
        nonlocal fecha_seleccionada, hora_seleccionada
        try:
            fecha_seleccionada = cal.get_date()  # Obtener la fecha
            hora_seleccionada = tiempo_hora.get() + ":" + tiempo_minuto.get()  # Obtener la hora
        except Exception as e:
            print(f"Error obteniendo fecha y hora: {e}")
        finally:
            root.destroy()  # Asegurarse de que la GUI se destruya

    hoy = datetime.today().date()  # Usar datetime.today().date() para obtener la fecha de hoy.
    ahora = datetime.now()  # Usar datetime.now() para obtener la fecha de hoy.
    fecha_maxima = hoy - timedelta(days = 1) # Fecha máxima posible en el GUI
    titulo_a_mostrar = "Seleccione una fecha y hora inicial:"
    if not fecha_minima_parametro: # Si se pasó una fecha mínimo como parámetro:
        fecha_minima = hoy - timedelta(days = 91)
        fecha_a_mostrar = fecha_minima # Fecha por default en el GUI
        
    else: # Si se pasó una fecha mínimo como parámetro:
        try:
            # Formatear las fechas
            fecha_minima = fecha_datetime(fecha_minima_parametro)
            # La fecha mínima es el día 91 para evitar incovenientes.
            fecha_minima += timedelta(days = 1)
        except ValueError as e:
            return f"Error: {e}"
        fecha_a_mostrar =  fecha_maxima # Fecha por default en el GUI
    
    root = tk.Tk() # Mostrar GUI
    root.title(titulo_a_mostrar)

    # Definir parámetros del calendario GUI
    cal = DateEntry(root, width = 12, background = 'darkblue', foreground = 'white', borderwidth = 2, 
                    year = fecha_a_mostrar.year, month = fecha_a_mostrar.month, day = fecha_a_mostrar.day,
                    locale = 'es_ES', maxdate = fecha_maxima, mindate = fecha_minima, 
                    weekendbackground = 'white', weekendforeground = 'black')
    cal.pack(pady = 10)

    # Spinbox widget con sus parámetros de horas y de minutos
    tiempo_hora = tk.Spinbox(root, from_ = 0, to = 23, width = 2, format = "%02.0f", justify = 'center')
    tiempo_hora.pack(side = 'left', padx = (10, 5))
    tiempo_hora.delete(0, 'end')
    tiempo_hora.insert(0, f"{ahora.hour:02d}")
    tiempo_minuto = tk.Spinbox(root, from_ = 0, to = 59, width = 2, format = "%02.0f", justify = 'center')
    tiempo_minuto.pack(side = 'left', padx = (5, 10))
    tiempo_minuto.delete(0, 'end')
    tiempo_minuto.insert(0, f"{ahora.minute:02d}")

    # Botón para extraer la información
    button = tk.Button(root, text = "Obtener fecha y hora", command = obtener_fecha_y_hora)
    button.pack(pady = 10)

    # Iniciar proceso en el hilo principal
    root.mainloop()
    # Terminar proceso cuando el botón haya sido presionado
    root.quit()
    if fecha_seleccionada is not None and hora_seleccionada is not None:
        # return la fecha en formato ISO 8601
        return str(fecha_seleccionada) + "T" + str(hora_seleccionada) + ":00Z"
    else:
        return "No date and time selected"

def main():
    # Obtener argumentos pasados como parámetros en la consola desde funciones_cortas.py 
    parser = argparse.ArgumentParser(description="Calendar program")
    parser.add_argument('fecha_minima_parametro', type=str, help='Minimum date as an ISO 8601 string')
    args = parser.parse_args()

    # Extraer parámetro 
    fecha_minima_parametro = args.fecha_minima_parametro

    # Correr programa e imprimir respuesta
    fecha_y_hora = widget_calendario(fecha_minima_parametro)
    print(str(fecha_y_hora))

if __name__ == "__main__":
    main()
