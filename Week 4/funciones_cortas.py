from generador_tablas_y_graficas import extraer_cpcodes, tabla_de_trafico_por_cpcode, tabla_trafico_total_y_estadisticas, grafica_trafico_por_dia, grafica_hits_al_origen_por_tipo_de_respuesta, tabla_hits_por_tipo, hits_por_url  # type: ignore
import tkinter as tk
from tkinter import filedialog
import re
import configparser
from datetime import datetime
import time


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

def definir_fecha(mes):
    fecha_inicial = ""
    fecha_final = ""
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
    respuesta = int(input("Seleccione una opción (número): "))
    print("")
    if respuesta == 1:
        seleccionar_mes(texto_empresa)
    else:
        print("AKAMAI solo tiene retención de 92 días.")
        año_inicio = int(input(f"El año de la primer fecha para {texto_empresa} (yyyy): "))
        mes_inicio = int(input(f"El mes de la primer fecha para {texto_empresa} (mm): "))
        dia_inicio = int(input(f"El día de la primer fecha para {texto_empresa} (dd): "))
        hora_inicio, minuto_inicio = input(f"La hora/minutos de la primer fecha para {texto_empresa} (hh:mm en formato 24h): ").split(":")
        año_final = int(input(f"El año de la última fecha para {texto_empresa} (yyyy): "))
        mes_final = int(input(f"El mes de la última fecha para {texto_empresa} (mm): "))
        dia_final = int(input(f"El día de la última fecha para {texto_empresa} (dd): "))
        hora_final, minuto_final = input(f"La hora/minutos de la última fecha para {texto_empresa} (hh:mm en formato 24h): ").split(":")
        fecha_inicio, fecha_final = fechas_formato_ISO_8601([año_inicio, mes_inicio, dia_inicio, int(hora_inicio), int(minuto_inicio)], [año_final, mes_final, dia_final, int(hora_final), int(minuto_final)])
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
    return definir_fecha(meses_nombres[mes - 1])

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



if __name__ == "__main__":
    main()
