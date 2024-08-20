from generador_tablas_y_graficas import extraer_cpcodes, tabla_de_trafico_por_cpcode, tabla_trafico_total_y_estadisticas, grafica_trafico_por_dia, grafica_hits_al_origen_por_tipo_de_respuesta, tabla_hits_por_tipo, hits_por_url  # type: ignore
from calendarioGUI import obtener_fechas_GUI
import tkinter as tk
from tkinter import filedialog
import re
import configparser
import tkinter as tk
from tkcalendar import DateEntry  # type: ignore
from datetime import datetime, timedelta, timezone
import time
import threading
import subprocess


def automatico_o_manual():
    print("\n" + """
          Existe un formato general de reporte. Desea que todas las empresas
          usen este formato predefinido? """ + "\n")
    print("1. Escoger manualmente el contenido de cada reporte por empresa")
    print("2. Usar el formato predefinido de reporte para todas las empresas.")
    manual = int_checker("Seleccione la opción que desee (número): ", [1, 2])
    if manual == 1:
        return True
    else:
        return False

def crear_folder(empresa, fechas):
    return

def definir_fecha(mes_eleccion):
    # mes_dos_digitos = str("{:02}".format(mes))
    año_actual = datetime.now().year
    mes_actual = datetime.now().month
    dia_inicial = "01"
    dia_final = dia_inicial
    if (mes_eleccion == mes_actual):
        año_inicial = str(año_actual)
        año_final = año_inicial
        mes_inicial = str("{:02}".format(mes_actual))
        mes_final = mes_inicial
        dia_final = f"{datetime.now().day:02}"
    elif (mes_eleccion < mes_actual):
        año_inicial = str(año_actual)
        año_final = año_inicial
        mes_inicial = str("{:02}".format(mes_eleccion))
        mes_final = str("{:02}".format(mes_eleccion + 1))
    elif (mes_eleccion == 11):
        año_inicial = str(año_actual - 1)
        año_final = año_inicial
        mes_inicial = "11"
        mes_final = "12"
    else:
        año_inicial = str(año_actual - 1)
        año_final = str(año_actual)
        mes_inicial = "12"
        mes_final = "01"

    fecha_inicial = año_inicial + "-" + mes_inicial + "-" + dia_inicial + "T00:00:00Z"
    fecha_final = año_final + "-" + mes_final + "-" + dia_final + "T00:00:00Z"
    return [fecha_inicial, fecha_final]

def extraer_todas_las_empresas(file_path):
    sections = []
    with open(file_path, 'r') as file:
        content = file.read()
        # Regular expression to find section headers
        matches = re.findall(r'\[([^\]]+)\]', content)
        sections.extend(matches)
    return sections


def fechas_formato_ISO_8601(lista_inicial, lista_final):
    return f"{lista_inicial[0]:04d}-{lista_inicial[1]:02d}-{lista_inicial[2]:02d}T{lista_inicial[3]:02d}:{lista_inicial[4]:02d}:00Z", f"{lista_final[0]:04d}-{lista_final[1]:02d}-{lista_final[2]:02d}T{lista_final[3]:02d}:{lista_final[4]:02d}:00Z"

def fechas_correctas(fecha_inicial, fecha_final, interval_incluido = False):
    
    return

def generar_reportes(empresa, client_secret, host, access_token, client_token, fechas, listas_de_reportes):
    funciones_disponibles = [tabla_de_trafico_por_cpcode, tabla_trafico_total_y_estadisticas, grafica_trafico_por_dia, grafica_hits_al_origen_por_tipo_de_respuesta, tabla_hits_por_tipo, tabla_hits_por_tipo, hits_por_url]
    crear_folder(empresa, fechas)
    for index in listas_de_reportes:
        print_next("Etapa actual: producción de tablas/gráficas. Este proceso suele tardas varios minutos por empresa.")
        if (index == 6):
            cpcodes = obtener_cpcodes(empresa, client_secret, host, access_token, client_token, fechas)
            for cpc in cpcodes:
                funciones_disponibles[index-1](empresa, client_secret, host, access_token, client_token, fechas, cpcode = cpc)
            continue
        funciones_disponibles[index-1](empresa, client_secret, host, access_token, client_token, fechas)
    return


def imprimir_linea_por_linea_de_lista(lista, first_time=False):
    if first_time:
        print("0. Todas las opciones")
    else:
        print("0. Todas las opciones")
        print("-1. Ya seleccione las opciones que me interesan.")
    for i in range(len(lista)):
        print(str(i + 1) + ". " + lista[i])
    print("")

def int_checker(mensaje, rango):
    posibles_números = []
    for i in range(rango[0], rango[1] + 1):
        posibles_números.append(i)
    while True:
        try:
            respuesta = input(mensaje)
            número = int(respuesta)
            if número not in posibles_números:
                print("El número que dio no era una opción." + "\n")
                continue
            print("")
            return número

        except ValueError:
            print("Sólo se aceptan números!" + "\n")


def main():
    print("Este programa es una librería de funciones que se usa en programa_principal.py")


def multiples_fechas():
    print("Desea que todos los reportes usen las mismas fechas?")
    print("1. Quiero usar la misma fecha para todos mis reportes.")
    print("2. Quiero usar distintas fechas para cada reporte.")
    answer = int_checker("Seleccione una opción (número): ", [1, 2])
    print("")
    if answer == 2:
        return True
    else:
        return False


def obtener_cpcodes(empresa, client_secret, host, access_token, client_token, fechas):
    print(f"""
     Una de sus selecciones para {empresa} fue: 
     '6. Tabla: Hits por tipo de respuesta, de únicamente un CPcode.'
     A continuación, se mostrarán todos los CPcodes disponibles. Si
     desea generar varias tablas (una por CPCODE), favor de ingresar
     los números uno por uno. Este proceso puede tardar un momento...
     """)
    cpcodes_list = extraer_cpcodes(empresa, client_secret, host, access_token, client_token, fechas)
    imprimir_linea_por_linea_de_lista(cpcodes_list, first_time = True)
    mis_cpcodes = []
    eleccion = int_checker(f"Seleccione el cpcode para {empresa} (número de la lista, NO el cpcode): ", [0, len(cpcodes_list)])
    while (eleccion != -1):
        if (eleccion == 0):
            print_next("Ha seleccionado todos los cpcodes")
            return cpcodes_list
        elif (cpcodes_list[eleccion-1].split()[-1].strip('()') in mis_cpcodes):
            print("Ya seleccionó ese número anteriormente.")
            time.sleep(1)
        else:
            mis_cpcodes.append(cpcodes_list[eleccion-1].split()[-1].strip('()'))
            if (len(mis_cpcodes) == len(cpcodes_list)):
                print_next("Ha seleccionado todos los cpcodes")
                return mis_cpcodes
        imprimir_linea_por_linea_de_lista(cpcodes_list, first_time = False)
        eleccion = int_checker(f"Seleccione el cpcode para {empresa} (número de la lista, NO el cpcode): ", [-1, len(cpcodes_list)])
    return mis_cpcodes

def obtener_credenciales(archivo, empresas):
    diccionario_de_empresas = {}
    config = configparser.ConfigParser()
    config.read(archivo)
    for section in empresas:
        diccionario_de_empresas[section] = [config[section]['client_secret'], config[section]['host'], config[section]['access_token'], config[section]['client_token']]
    return diccionario_de_empresas


def print_next(text):
    if text == "":
        print("\n" * 1 + "-" * 40 + "\n" * 1)
    else:
        print("\n" * 1 + "-" * 4 + text + "-" * 4 + "\n" * 1)

def reportes_distintos():
    print("""
          Previamente seleccionó que prefiere crear un formato de reporte en lugar
          de usar el formato predefinido. ¿Desea que todos los reportes sigan el mismo
          nuevo formato?
          
          1. Quiero que todos los reportes usen el mismo nuevo formato.
          2. Quiero generar reportes distintos para cada empresa.
          """)
    answer = int_checker("Seleccione una opción (número): ", [1,2])
    print("")
    if (answer == 2):
        return True
    else:
        return False

def reportes_generales(archivo, fechas):
    empresas = obtener_credenciales(archivo, extraer_todas_las_empresas(archivo))
    
    for empresa, credenciales in empresas.items():
        print_next("Etapa actual: producción de tablas/gráficas. Este proceso suele tardas varios minutos por empresa.")
        crear_folder(empresa, fechas)
        cpcodes = extraer_cpcodes(empresa, credenciales[0], credenciales[1], credenciales[2], credenciales[3], fechas)
        tabla_de_trafico_por_cpcode(empresa, credenciales[0], credenciales[1], credenciales[2], credenciales[3], fechas)
        tabla_trafico_total_y_estadisticas(empresa, credenciales[0], credenciales[1], credenciales[2], credenciales[3], fechas)
        grafica_trafico_por_dia(empresa, credenciales[0], credenciales[1], credenciales[2], credenciales[3], fechas)
        grafica_hits_al_origen_por_tipo_de_respuesta(empresa, credenciales[0], credenciales[1], credenciales[2], credenciales[3], fechas)
        tabla_hits_por_tipo(empresa, credenciales[0], credenciales[1], credenciales[2], credenciales[3], fechas)
        try:
            for i in range(len(cpcodes)):
                if (i < 3):
                    tabla_hits_por_tipo(empresa, credenciales[0], credenciales[1], credenciales[2], credenciales[3], fechas, cpcodes[i].split()[-1].strip('()'))
                else:
                    break
        except:
            print("No se detectaron cpcodes. ¿Está seguro que las credenciales de las APIs están vigentes?")
        hits_por_url(empresa, credenciales[0], credenciales[1], credenciales[2], credenciales[3], fechas)
        print_next(f"Todos los reportes de {empresa} fueron generados.")
    
def run_calendar_program(arg1):
    # Execute the secondary program and capture the output
    result = subprocess.run(
        ['python', 'calendarioGUI.py', arg1],
        capture_output=True,
        text=True
    )
    # Output from the secondary program
    # print("Output MAIN run_calendar_program:", result.stdout.strip())
    # print("Error MAIN run_calendar_program:", result.stderr)
    return result.stdout.strip()

def seleccionar_archivo():
    print("\n" + "Abriendo ventana para seleccionar archivo...")
    time.sleep(1)
    # Parámetros de la librería
    root = tk.Tk()
    root.withdraw()

    # Abrir ventana preguntando por archivo:
    direccion_de_archivo = filedialog.askopenfilename(
        title="Escoja Archivo (.edgerc):",
        filetypes=(("All files", "*.*"), ("Config files", "*.edgerc"))
    )

    # Devolver dirección del archivo
    print_next(direccion_de_archivo)
    return direccion_de_archivo



def seleccionar_empresas(archivo):
    empresas = extraer_todas_las_empresas(archivo)
    empresas_escogidas = []
    imprimir_linea_por_linea_de_lista(empresas, first_time = True)
    eleccion = int_checker("Escoja qué empresa le interesa (número): ", [0, len(empresas)])

    while (eleccion != -1):
        if eleccion == 0:
            print_next("Ha seleccionado todas las empresas")
            return obtener_credenciales(archivo, empresas)
        elif empresas[eleccion - 1] in empresas_escogidas:
            print("Ya habías elegido ese número anteriormente.")
            time.sleep(1)
        else:
            empresas_escogidas.append(empresas[eleccion - 1])
            if (len(empresas_escogidas) == len(empresas)):
                print_next("Ha seleccionado todas las empresas")
                return obtener_credenciales(archivo, empresas_escogidas)
                
        imprimir_linea_por_linea_de_lista(empresas, first_time = False)
        eleccion = int_checker("Escoja qué empresa le interesa (número): ", [-1, len(empresas)])

    print("Has seleccionado: ", end="")
    for emp in empresas_escogidas:
        print(emp, end=', ')
    print_next("")
    return obtener_credenciales(archivo, empresas_escogidas)


def seleccionar_fecha(texto_empresa = "todas las empresas"):
    print(f"Desea seleccionar un mes para el reporte, o quiere consultar el consumo entre dos fechas especificas para {texto_empresa}: ")
    print("1. Seleccionar un mes.")
    print("2. Seleccionar dos fechas específicas")
    respuesta = int_checker("Seleccione una opción (número): ", [1,2])
    print("")
    if respuesta == 1:
        seleccionar_mes(texto_empresa)
    else:
        print("AKAMAI solo tiene retención de 92 días.")
        fecha_inicio = run_calendar_program("")
        print("Fecha inicial: " + fecha_inicio)
        fecha_final = run_calendar_program(str(fecha_inicio))
        print("Fecha final: " + fecha_final)
        print_next(f"La fecha inicial para {texto_empresa} es {fecha_inicio} y la final {fecha_final}")
        return [fecha_inicio, fecha_final]
    



def seleccionar_mes(empresa):
    mes_actual = datetime.now().month
    meses_nombres = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    numeros_de_mes_mencionados = []
    print(f"Akamai solo retiene información por 92 días. Considerando esto, ¿Sobre qué mes quiere el reporte para {empresa}?")
    for i in range(2, -1, -1):
        mes_nombre = meses_nombres[(mes_actual - 1) - i]
        mes_numero = meses_nombres.index(mes_nombre) + 1
        numeros_de_mes_mencionados.append(mes_numero)
        if (i == 0):
            print(str(mes_numero) + ". " + mes_nombre + " (considere que la información no tomara en cuenta todo el mes)")
        else:
            print(str(mes_numero) + ". " + mes_nombre)
    print("")
    mes = int_checker("AKAMAI retiene solo 92 días. Seleccione mes (número): ", [numeros_de_mes_mencionados[0], numeros_de_mes_mencionados[-1]])
    return definir_fecha(mes)

def seleccionar_reportes(empresa="formato general"):
    lista_de_tablas_y_graficas = [
        "Tabla: Tráfico consumido por CPcode",
        "Tabla: Tráfico Total y Estadísticas (Bytes Total, Bytes por segundo Total, Mínimo y Máximo)",
        "Gráfica: Tráfico por día (Edge, Midgress, Origin y Offload)",
        "Gráfica: Hits al Origen por tipo de respuesta (0xx, 1xx, 2xx, 3xx, 4xx, 5xx)",
        "Tabla: Hits por tipo de respuesta, ordenados por Edge Hits",
        "Tabla: Igual que la tabla 5, pero de únicamente un CPcode",
        "Tabla: Hits por URL (Edge Hits, Origin Hits, Offload)"
    ]
    print(f"""
          De las siguientes opciones de tablas/gráficas, seleccione aquellas que
          desee agregar a su reporte ({empresa}):
          """)
    imprimir_linea_por_linea_de_lista(lista_de_tablas_y_graficas, first_time = True)
    números_elegidos = []
    eleccion = int_checker(f"Seleccione una opción para {empresa} (número): ", [0,7])
    while (eleccion != -1):
        if (eleccion == 0):
            print_next("Ha seleccionado todas las tablas/gráficas")
            return [1,2,3,4,5,6,7]
        elif (eleccion in números_elegidos):
            print("Ya seleccionó ese número anteriormente.")
            time.sleep(1)
        else:
            números_elegidos.append(eleccion)
            if (len(números_elegidos) == 7):
                print_next("Ha seleccionado todas las tablas/gráficas")
                return números_elegidos
        imprimir_linea_por_linea_de_lista(lista_de_tablas_y_graficas, first_time = False)
        eleccion = int_checker(f"Seleccione una opción {empresa} (número): ", [-1,7])
    
    return números_elegidos



# def widget_calendario(min_date_given=""):

#     def check_main_thread():
#         if threading.current_thread() is not threading.main_thread():
#             raise RuntimeError("Tkinter must be run on the main thread")

#     def corrected_date(date_str):
#         date_format = "%Y-%m-%dT%H:%M:%SZ"
#         pattern = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
#         if not pattern.match(date_str):
#             raise ValueError(f"Date string '{date_str}' does not match format '{date_format}'")

#         try:
#             return datetime.strptime(date_str, date_format).replace(tzinfo=timezone.utc)
#         except ValueError as e:
#             print(f"Error parsing date: {e}")
#             raise

#     selected_date = None
#     selected_time = None

#     def get_date_time():
#         nonlocal selected_date, selected_time
#         try:
#             selected_date = cal.get_date()  # Get the selected date from the DateEntry widget
#             selected_time = time_hour.get() + ":" + time_minute.get()  # Get the selected time from the Spinbox widgets
#         except Exception as e:
#             print(f"Error getting date and time: {e}")
#         finally:
#             root.after(0, root.destroy)  # Ensure the GUI window is destroyed on the main thread

#     def background_task():
#         # Simulate a long-running task
#         import time
#         time.sleep(2)  # Simulate delay
#         # You can call a function to update the GUI if needed
#         # root.after(0, update_gui)  # Example for GUI update

#     today = datetime.today().date()  # Use datetime.today().date() to get the current date
#     now = datetime.now()  # Use datetime.now() to get the current datetime
#     max_date = today - timedelta(days=1)

#     if not min_date_given:
#         min_date = today - timedelta(days=91)
#         fecha_a_mostrar = min_date
#         titulo_a_mostrar = "Seleccione una fecha y hora inicial:"
#     else:
#         try:
#             min_date = corrected_date(min_date_given)
#             min_date += timedelta(days=1)
#         except ValueError as e:
#             return f"Error: {e}"

#         fecha_a_mostrar = max_date
#         titulo_a_mostrar = "Seleccione una fecha y hora final:"

#     root = tk.Tk()
#     root.title(titulo_a_mostrar)
    
#     check_main_thread()  # Ensure Tkinter is on the main thread

#     # Set the DateEntry widget to start at max_date
#     cal = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2,
#                     year=fecha_a_mostrar.year, month=fecha_a_mostrar.month, day=fecha_a_mostrar.day,
#                     locale='es_ES', maxdate=max_date, mindate=min_date,
#                     weekendbackground='white', weekendforeground='black')
#     cal.pack(pady=10)

#     # Initialize Spinbox widgets for time with full range and default to current time
#     time_hour = tk.Spinbox(root, from_=0, to=23, width=2, format="%02.0f", justify='center')
#     time_hour.pack(side='left', padx=(10, 5))
#     time_hour.delete(0, 'end')
#     time_hour.insert(0, f"{now.hour:02d}")

#     time_minute = tk.Spinbox(root, from_=0, to=59, width=2, format="%02.0f", justify='center')
#     time_minute.pack(side='left', padx=(5, 10))
#     time_minute.delete(0, 'end')
#     time_minute.insert(0, f"{now.minute:02d}")

#     button = tk.Button(root, text="Obtener fecha y hora", command=get_date_time)
#     button.pack(pady=10)

#     # Start the background task in a separate thread
#     thread = threading.Thread(target=background_task)
#     thread.start()

#     root.mainloop()

#     # Capture the return values after the window is closed
#     if selected_date is not None and selected_time is not None:
#         return str(selected_date) + "T" + str(selected_time) + ":00Z"
#     else:
#         return "No date and time selected"



if __name__ == "__main__":
    seleccionar_fecha()
    main()
