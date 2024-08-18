from generador_tablas_y_graficas import obtener_cpcodes # type: ignore
import tkinter as tk
from tkinter import filedialog
import re
import configparser
from datetime import datetime
import time



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

def seleccionar_mes():
    mes_actual = datetime.now().month
    meses_nombres = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    numeros_de_mes_mencionados = []
    print("Akamai solo retiene información por 92 días. Considerando esto, ¿Sobre qué mes quiere el reporte?")
    for i in range(2,-1,-1):
        mes_nombre = meses_nombres[(mes_actual-1) - i]
        mes_numero = meses_nombres.index(mes_nombre) + 1
        numeros_de_mes_mencionados.append(mes_numero)
        if (i == 0):
            print(str(mes_numero) + ". " + mes_nombre + " (considere que la información no tomara en cuenta todo el mes)")
        else:
            print(str(mes_numero) + ". " + mes_nombre)
    print("")
    mes = int_checker("AKAMAI retiene solo 92 días. Seleccione mes (número): ", [numeros_de_mes_mencionados[0], numeros_de_mes_mencionados[-1]])
    return meses_nombres[mes-1]

def seleccionar_empresas(archivo):
    empresas = extraer_todas_las_empresas(archivo)
    empresas_escogidas = []
    first_time = True
    imprimir_empresas_o_cpcodes(empresas, first_time)
    eleccion = int_checker("Escoja qué empresa le interesa (número): ", [0, len(empresas)])
    if (eleccion == 0):
        empresas_escogidas = empresas
    else:
        first_time = False
        while (eleccion != -1 or len(empresas_escogidas) < len(empresas)):
            if (eleccion == 0):
                empresas_escogidas = empresas
                break
            if (empresas[eleccion-1] in empresas_escogidas):
                print("Ya habías elegido ese número anteriormente.")
                continue
            empresas_escogidas.append(empresas[eleccion-1])
            imprimir_empresas_o_cpcodes(empresas, first_time)
            eleccion = int_checker("Escoja qué empresa le interesa (número): ", [-1, len(empresas)])
            
    if (len(empresas_escogidas) == len(empresas)):
        print_next("Ha seleccionado todas las empresas.")
    else:
        print("Has seleccionado: ", end="")
        for emp in empresas_escogidas:
            print(emp, end=', ')
        print_next("")
    return obtener_credenciales(archivo, empresas_escogidas)
    
def seleccionar_reportes(archivo, fechas, counter, empresa=""):
    print(f"""
          De las siguientes opciones de tablas/gráficas, seleccione aquellas que
          desee agregar a su reporte de {empresa}:
          0. Todas las tablas/gráficas
          1. Tabla: Tráfico consumido por CPcode
          2. Tabla: Tráfico Total y Estadísticas (Bytes Total, Bytes por segundo Total, Mínimo y Máximo)
          3. Gráfica: Tráfico por día (Edge, Midgress, Origin y Offload)
          4. Gráfica: Hits al Origen por tipo de respuesta (0xx, 1xx, 2xx, 3xx, 4xx, 5xx)
          5. Tabla: Hits por tipo de respuesta, ordenados por Edge Hits
          6. Tabla: Hits por tipo de respuesta, de únicamente una CPcode
          """)
    números_elegidos = []
    cpcode = None
    eleccion = int_checker("Seleccione una opción (número): ", [0,6])
    if (eleccion == 0):
        números_elegidos = [1,2,3,4,5,6]
    else:
        while (eleccion != -1 or len(números_elegidos) < 6):
            eleccion = int_checker("Seleccione una opción (escoja -1 si ya seleccionó todos los de su interés): ", [-1,6]):
            if (eleccion == 0):
                números_elegidos = [1,2,3,4,5,6]
            elif (eleccion in números_elegidos):
                print("Ya seleccionó ese número anteriormente.")
                continue
            else:
                números_elegidos.append(eleccion)
    if (6 in números_elegidos):
        if (isinstance(fechas[counter], list)):
            números_elegidos.append(seleccionar_cpcode(archivo, fechas[counter], empresa))
        else:
            números_elegidos.append(seleccionar_cpcode(archivo, fechas, empresa))
    return números_elegidos

def seleccionar_cpcode(archivo, lista_de_fechas, empresa):
    print("""
          Una de sus selecciones fue 
          '6. Tabla: Hits por tipo de respuesta, de únicamente un CPcode.'
          A continuación, se mostrarán todos los CPcodes disponibles. Si
          desea generar varias tablas (una por CPCODE), favor de ingresar
          uno por uno. Este proceso puede tardar un momento...
          """)
    cpcodes = obtener_cpcodes(archivo, lista_de_fechas[0], lista_de_fechas[1])
    cpcodes_elegidos = []
    imprimir_empresas_o_cpcodes(cpcodes, True, cpcodes=True)
    eleccion = int_checker("Escoja qué CPcode le interesa (número): ", [0, len(cpcodes)])
    cpcodes_elegidos.append(cpcodes[eleccion-1].strip(": ")[1])
    while (eleccion != -1 or len(cpcodes_elegidos) < len(cpcodes)):
        eleccion = int_checker("Seleccione una opción (escoja -1 si ya seleccionó todos los de su interés): ", [-1,len(cpcodes)])
        if (eleccion == 0):
            print("0 was not an option, choose another number.")
            continue
        elif (cpcodes[eleccion-1].strip(": ")[1] in cpcodes_elegidos):
            print("Ya seleccionó ese número anteriormente.")
            continue
        else:
            cpcodes_elegidos.append(cpcodes[eleccion-1].strip(": ")[1])
    

    return

def generar_reportes():
    return

def automatico_o_manual():
    print("\n" + """
          Existe un formato general de reporte. Desea que todas las empresas
          usen este formato predefinido? """ + "\n")
    print("1. Escoger manualmente el contenido de cada reporte por empresa")
    print("2. Usar el formato predefinido de reporte para todas las empresas.")
    manual = int_checker("Seleccione la opción que desee (número): ", [1,2])
    if (manual == 1):
        return True
    else:
        return False

def reportes_generales(archivo, fecha):
    return

def extraer_todas_las_empresas(file_path):
    sections = []
    with open(file_path, 'r') as file:
        content = file.read()
        # Regular expression to find section headers
        matches = re.findall(r'\[([^\]]+)\]', content)
        sections.extend(matches)
    return sections

def imprimir_empresas_o_cpcodes(empresas, first_time=False, cpcodes=False):
    if (first_time):
        if (not cpcodes):
            print("0. Todas las empresas")
    else:
        print("-1. Ya seleccione las opciones que me interesan.")
        if (not cpcodes):
            print("0. Todas las empresas")
    for i in range(len(empresas)):
        print(str(i+1) + ". " + empresas[i])

def print_next(text):
    if (text == ""):
        print("\n"*1 + "-"*40 + "\n"*1)
    else:
        print("\n"*1 + "-"*4 + text + "-"*4 + "\n"*1)

def obtener_credenciales(archivo, empresas):
    diccionario_de_empresas = {}
    config = configparser.ConfigParser()
    config.read(archivo)
    for section in empresas:
        diccionario_de_empresas[section] = [config[section]['client_secret'], config[section]['host'], config[section]['access_token'], config[section]['client_token']] 
    return diccionario_de_empresas

def multiples_fechas():
    print("Desea que todos los reportes usen las mismas fechas?")
    print("1. Quiero usar la misma fecha para todos mis reportes.")
    print("2. Quiero usar distintas fechas para cada reporte.")
    answer = int_checker("Seleccione una opción (número)", [1,2])
    print("")
    if (answer == 2):
        return True
    else:
        return False

def multiples_reportes():
    print("""
          Previamente seleccionó que prefiere crear un formato de reporte en lugar
          de usar el formato predefinido. ¿Desea que todos los reportes sigan el mismo
          nuevo formato?
          
          1. Quiero que todos los reportes usen el mismo nuevo formato.
          2. Quiero generar reportes distintos para cada empresa.
          """)
    answer = int_checker("Seleccione una opción (número)", [1,2])
    print("")
    if (answer == 2):
        return True
    else:
        return False

def int_checker(mensaje, rango):
    posibles_números = []
    for i in range(rango[0], rango[1]+1):
        posibles_números.append(i)
    while True:
        try:
            respuesta = input(mensaje)
            número = int(respuesta)
            if (número not in posibles_números):
                print("El número que dio no era una opción.")
                continue  
            
            return número 
        
        except ValueError:
            print("Proporcione sólamente un número.")

def seleccionar_fecha():
    print("Desea seleccionar un mes para el reporte, o quiere consultar el consumo entre dos fechas especificas:")
    print("1. Seleccionar un mes.")
    print("2. Seleccionar dos fechas específicas")
    respuesta = int(input("Seleccione una opción (número): "))
    print("")
    if (respuesta == 1):
        seleccionar_mes()
    else:
        print("AKAMAI solo tiene retención de 92 días.")
        año_inicio = int(input("El año de la primer fecha (yyyy): "))
        mes_inicio = int(input("El mes de la primer fecha (mm): "))
        dia_inicio = int(input("El día de la primer fecha (dd): "))
        hora_inicio, minuto_inicio = input("La hora/minutos de la primer fecha (hh:mm en formato 24h): ").split(":")
        año_final = int(input("El año de la última fecha (yyyy): "))
        mes_final = int(input("El mes de la última fecha (mm): "))
        dia_final = int(input("El día de la última fecha (dd): "))
        hora_final, minuto_final = input("La hora/minutos de la última fecha (hh:mm en formato 24h): ").split(":")
        fecha_inicio, fecha_final = fechas_formato_ISO_8601([año_inicio, mes_inicio, dia_inicio, int(hora_inicio), int(minuto_inicio)], [año_final, mes_final, dia_final, int(hora_final), int(minuto_final)])
        print_next(f"La fecha inicial {fecha_inicio} y la final {fecha_final}")
        return [fecha_inicio, fecha_final]
    
def fechas_formato_ISO_8601(lista_inicial, lista_final):
    return f"{lista_inicial[0]:04d}-{lista_inicial[1]:02d}-{lista_inicial[2]:02d}T{lista_inicial[3]:02d}:{lista_inicial[4]:02d}:00Z", f"{lista_final[0]:04d}-{lista_final[1]:02d}-{lista_final[2]:02d}T{lista_final[3]:02d}:{lista_final[4]:02d}:00Z"

def main():
    print("Este programa es una librería de funciones que se usa en programa_principal.py")


# Sólamente correrá el programa si se solicita correr directamente.
if __name__ == "__main__":
    main()