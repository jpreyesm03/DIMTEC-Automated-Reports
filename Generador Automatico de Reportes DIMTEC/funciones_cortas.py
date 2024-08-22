from generador_tablas_y_graficas import extraer_cpcodes, tabla_de_trafico_por_cpcode, tabla_trafico_total_y_estadisticas, grafica_trafico_por_dia, grafica_hits_al_origen_por_tipo_de_respuesta, tabla_hits_por_tipo, tabla_hits_por_url  # type: ignore
import tkinter as tk
from tkinter import filedialog
import re
import configparser
import tkinter as tk
from datetime import datetime, timedelta
import time
import subprocess
import os
from dateutil.relativedelta import relativedelta

introduccion = "\n¡Hola! Puedes generar todos los reportes desde este programa. La idea es que solamente utilice números a lo largo del programa."

def agregar_tiempo(fecha_a_cambiar, cambio_tiempo = "1 MES"):
    # Definir un formato de fecha acorde al ISO 8601
    formato_de_fecha = "%Y-%m-%dT%H:%M:%SZ"
    
    # Cambiar el tipo de formato a Datetime
    fecha = datetime.strptime(fecha_a_cambiar, formato_de_fecha)
    
    if (cambio_tiempo == "6 HORAS"): # 6 horas porque es la diferencia de horario con UTC, zona horaria por default para las APIs
        fecha_posterior = fecha + timedelta(hours=6)

    elif (cambio_tiempo == "1 DIA"): # 1 Día porque a veces es lo más fácil para evitar problemas de intervalos al llamar los APIs
        fecha_posterior = fecha + timedelta(days=1)
        # Fijar la hora a 00:00:00
        fecha_posterior = fecha_posterior.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        # Agregar un mes porque es el plazo máximo para las APIs con interval de FIVE_MINUTES.
        # Se agrega un mes relativo con relativedelta, es decir, se busca la fecha del siguiente mes con el mismo día,
        # no necesariamente se agregan 31 días
        fecha_posterior = fecha + relativedelta(months=1)

    # Cambiar el tipo de formato a String acorde al ISO 8601
    nueva_fecha = fecha_posterior.strftime(formato_de_fecha)
    
    return nueva_fecha


def automatico_o_manual():
    # Imprimir en la consola las opciones
    print("""
          Existe un formato general de reporte. Desea que todas las empresas
          usen este formato predefinido? """ + "\n")
    print("1. Usar el formato predefinido de reporte para todas las empresas.")
    print("2. Escoger manualmente el contenido de cada reporte por empresa")

    # int_checker se asegura de que el usuario registre un número, entre [1 y 2]
    manual = int_checker("Seleccione la opción que desee (número): ", [1, 2])
    if manual == 2:
        return True
    else:
        return False
    
def correr_programa_subproceso(arg1):
    # El calendario GUI sólo funciona óptimamente cuando se corre como main_thread,
    # por eso es que se corre en un subproceso y se registra la fecha resultante
    result = subprocess.run(
        ['python', 'calendarioGUI.py', arg1], # Llamar al otro programa. arg1 se pasa como parámetro
        capture_output=True,
        text=True
    )
    return result.stdout.strip() # return el resultado del subproceso. strip() remueve el \n

def crear_carpeta(nombre_de_empresa = "", carpeta = "", fechas_para_el_titulo = []):
    dia = str("{:02}".format(datetime.now().day)) # Extraer el día en dos caracteres
    mes = str("{:02}".format(datetime.now().month)) # Extraer el mes en dos caracteres
    año = str(datetime.now().year) # Extraer el año

    if not nombre_de_empresa: # Si no se pasó ningún parametro
        nombre = "Reportes_por_Empresa_" + dia + "_" + mes + "_" + año # Nombre de la carpeta tentativo
        nombre_carpeta = definir_nombre(nombre) # Asegurarse de que el nombre no exista
        os.makedirs(nombre_carpeta) # Hacer carpeta
        imprimir_con_formato_establecido(f"Carpeta creada: {nombre_carpeta}")
        return nombre_carpeta
    else:   # Si sí se pasaron argumentos, entonces crear subcarpeta
        # El segundo parámetro contempla la función formatear_fechas que regresa las fechas en formato "13Ago24-06Sep24"
        return crear_subcarpeta(carpeta, f"Reporte_de_{nombre_de_empresa}_{formatear_fechas(fechas_para_el_titulo[0], fechas_para_el_titulo[1])}")

def crear_subcarpeta(carpeta_ancestra, nombre_de_subcarpeta_ideal):
    # Obtener el directorio actual
    actual_dir = os.getcwd()

    # Acceder a la carpeta madre recién creada
    carpeta_ancestra = os.path.join(actual_dir, carpeta_ancestra)

    # Asegurarse de que la subcarpeta se pueda crear con el nombre indicado (nombre_de_subcarpeta_ideal)
    subcarpeta_path = definir_nombre(nombre_de_subcarpeta_ideal, carpeta_ancestra_path = carpeta_ancestra, subcarpeta = True)
    
    # Crear subcarpeta
    os.makedirs(subcarpeta_path)
    imprimir_con_formato_establecido(f"Subcarpeta creada: {subcarpeta_path}")
    return subcarpeta_path

def definir_fecha_de_mes(mes_eleccion):
    año_actual = datetime.now().year
    mes_actual = datetime.now().month
    dia_inicial = "01"
    dia_final = dia_inicial
    if (mes_eleccion == mes_actual):
        año_inicial = str(año_actual)
        año_final = año_inicial
        mes_inicial = str("{:02}".format(mes_actual)) # Mes_actual forzado en dos caracteres
        mes_final = mes_inicial
        dia_final = f"{datetime.now().day:02}" # Dia actual forzado en dos caracteres
    elif (mes_eleccion < mes_actual):
        año_inicial = str(año_actual)
        año_final = año_inicial
        mes_inicial = str("{:02}".format(mes_eleccion)) # Mes_eleccion forzado en dos caracteres
        mes_final = str("{:02}".format(mes_eleccion + 1)) # Un mes despues que el elegido en 2 caracteres
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

    fecha_inicial = año_inicial + "-" + mes_inicial + "-" + dia_inicial + "T00:00:00Z" # ISO 8601
    fecha_final = año_final + "-" + mes_final + "-" + dia_final + "T00:00:00Z" # ISO 8601
    return [fecha_inicial, fecha_final] # Formato de lista

def definir_nombre(nombre_ideal, carpeta_ancestra_path = "", subcarpeta = False):
    if (not subcarpeta): # Caso carpeta
        contador = 1
        nombre_carpeta = nombre_ideal

        while os.path.exists(nombre_carpeta): # Si actualmente ya existe una carpeta "nombre_ideal"
            nombre_carpeta = f"{nombre_ideal}[{contador}]" # Nuevo nombre con el sufijo [1] dependiendo del contador
            contador += 1
        return nombre_carpeta
    
    else:   # Caso subcarpeta
        contador = 1
        subcarpeta_path = os.path.join(carpeta_ancestra_path, nombre_ideal) # Intento de nombre
        
        while os.path.exists(subcarpeta_path): # Si existe:
            subcarpeta_path = os.path.join(carpeta_ancestra_path, f"{nombre_ideal}[{contador}]")
            contador += 1
        return subcarpeta_path

def extraer_todas_las_empresas(file_path):
    sections = [] 
    with open(file_path, 'r') as file:
        content = file.read() # Lee el archivo .edgerc

        # Formato predefinido para buscar empresas en base a la libreria re en el archivo .edgerc
        matches = re.findall(r'\[([^\]]+)\]', content) 
        sections.extend(matches)

    return sections # Todas las empresas extraídas

def fechas_correctas_ISO_8601(fechas, interval = "NONE"):
    fecha_inicial_modificada = fechas[0]
    fecha_final_modificada = fechas[1]

    if (interval == "NONE"): # Tipo de intervalo de ciertas funciones
        for i in range(len(fechas)):
            if (fechas[i][15] != '0' and fechas[i][15] != '5'):
                if (i == 0):
                    # Si la fecha inicial no tiene minuto múltiplo de 5, cambiar a 5
                    fecha_inicial_modificada = fecha_inicial_modificada[:15] + "5" + fecha_inicial_modificada[16:]
                else:
                    # Si la fecha final no tiene minuto múltiplo de 5, cambiar a 5
                    fecha_final_modificada = fecha_final_modificada[:15] + "5" + fecha_final_modificada[16:]

    elif (interval == "HOUR"): # Tipo de intervalo de ciertas funciones

        # Asegurarse de que ambas fechas tengan minutos en 00
        fecha_inicial_modificada = fecha_inicial_modificada[:14] + "00" + fecha_inicial_modificada[16:]                
        fecha_final_modificada = fecha_final_modificada[:14] + "00" + fecha_final_modificada[16:]

    else: #Tipo de intervalo de ciertas funciones, interval = "FIVE_MINUTES"
        # Fijar fecha inicial en medianoche
        fecha_inicial_modificada = fecha_inicial_modificada[:11] + "00:00" + fecha_inicial_modificada[16:]

        # Si la distancia entre la fecha_final y la fecha_inicial es menos de un mes:
        if (primer_fecha_mas_reciente_que_segunda_fecha(agregar_tiempo(fecha_inicial_modificada, cambio_tiempo = "1 MES"), fecha_final_modificada)):   
            # Fecha_final agregar un día y fijar a medianoche
            fecha_final_modificada = agregar_tiempo(fecha_final_modificada, cambio_tiempo = "1 DIA")
            

        else: # Si la distancia entre la fecha_final y la fecha_inicial es más de un mes:
            # Cambiar fecha final a la fecha inicial un mes después
            print("Para la Tabla Tráfico Total y Estadísticas, el rango de fechas máximo es un mes")
            fecha_final_modificada = agregar_tiempo(fecha_inicial_modificada, cambio_tiempo = "1 MES")

    # return cada fecha 6 horas después para considerar la diferencia de zona horaria. Por default, se toma UTC que va +6 hrs adelante.        
    return [agregar_tiempo(fecha_inicial_modificada, cambio_tiempo = "6 HORAS"), agregar_tiempo(fecha_final_modificada, cambio_tiempo = "6 HORAS")]

def formatear_fechas(fecha1, fecha2):
    # Diccionario para traducir los meses al español
    meses_es = {
        1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
        7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
    }
    # Convertir los textos a objetos datetime
    dt1 = datetime.strptime(fecha1, "%Y-%m-%dT%H:%M:%SZ")
    dt2 = datetime.strptime(fecha2, "%Y-%m-%dT%H:%M:%SZ")

    # Formatear las fechas al formato ISO 8601
    fecha1_formateada = f"{dt1.day:02d}{meses_es[dt1.month]}{str(dt1.year)[-2:]}"
    fecha2_formateada = f"{dt2.day:02d}{meses_es[dt2.month]}{str(dt2.year)[-2:]}"
    
    # return las fechas legibles, ejemplo "13Ago24-06Sep24"
    return f"{fecha1_formateada}-{fecha2_formateada}"


def generar_reportes(empresa, client_secret, host, access_token, client_token, fechas, listas_de_reportes, carpeta_creada):
    # Crear sub_carpeta por empresa para poner todos los reportes ahí
    subcarpeta_path = crear_carpeta(nombre_de_empresa = empresa, carpeta = carpeta_creada, fechas_para_el_titulo = fechas)
    
    # Lista de funciones disponibles del archivo generador_tablas_y_graficas.py
    funciones_disponibles = [tabla_de_trafico_por_cpcode, tabla_trafico_total_y_estadisticas, grafica_trafico_por_dia, grafica_hits_al_origen_por_tipo_de_respuesta, tabla_hits_por_tipo, tabla_hits_por_tipo, tabla_hits_por_url]
    imprimir_con_formato_establecido(f"Etapa actual: producción de tablas/gráficas. Este proceso suele tardar varios minutos por empresa: {empresa}")
    
    for index in listas_de_reportes:
        if (index == 2): # La tabla 2 tiene ciertas limitaciones para el tipo de fecha, por eso se checa el caso en particular
            # Se formatean las fechas considerando el interval = FIVE_MINUTES
            # Lo que funciones_disponibles[index-1] hace es buscar el elemento de la lista funciones_disponibles en la posición index - 1
            print(funciones_disponibles[index-1](empresa, client_secret, host, access_token, client_token, fechas_correctas_ISO_8601(fechas, interval = "FIVE_MINUTES"), subcarpeta_path, formatear_fechas(fechas[0], fechas[1])))
        
        elif (index == 3 or index == 4): # Las gráficas tienen limitaciones de fecha, por eso se checa el caso en particular
            # Se formatean las fechas considerando el interval = HOUR
            print(funciones_disponibles[index-1](empresa, client_secret, host, access_token, client_token, fechas_correctas_ISO_8601(fechas, interval = "HOUR"), subcarpeta_path, formatear_fechas(fechas[0], fechas[1])))
        
        elif (index == 6): # Para la tabla 6, hay que especificar el cpcpode que se usará
            # Llama a otra función. En esa otra función primeramente se muestran todos los cpcodes, y luego se seleccionan los que se usarán.
            # La variabla cpcodes almacena directamente los cpcodes seleccionados
            cpcodes = obtener_cpcodes(empresa, client_secret, host, access_token, client_token, fechas_correctas_ISO_8601(fechas, interval = "NONE"))
            
            # Iteración sobre cada cpcode escogida
            for cpc in cpcodes:
                print(funciones_disponibles[index-1](empresa, client_secret, host, access_token, client_token, fechas_correctas_ISO_8601(fechas, interval = "NONE"), subcarpeta_path, formatear_fechas(fechas[0], fechas[1]), cpcode = cpc))
        
        else: # Para el resto de los casos:
            print(funciones_disponibles[index-1](empresa, client_secret, host, access_token, client_token, fechas_correctas_ISO_8601(fechas, interval = "NONE"), subcarpeta_path, formatear_fechas(fechas[0], fechas[1])))
    return


def imprimir_linea_por_linea_de_lista(lista, primera_vez=False):
    if primera_vez:
        print("0. Todas las opciones")
    else:
        print("-1. Ya seleccione las opciones que me interesan.")
        print("0. Todas las opciones")
    
    # Imprime los elementos de la lista empezando del 1.
    for i in range(len(lista)):
        print(str(i + 1) + ". " + lista[i])
    print("")

def int_checker(mensaje, rango):
    posibles_números = []
    for i in range(rango[0], rango[1] + 1):
        posibles_números.append(i) # Inserta los posibles valores según el rango

    while True:
        try: # Intenta convertir lo que el usuario registró en número, si no puede, lo manda a except
            respuesta = input(mensaje)
            número = int(respuesta)

            if número not in posibles_números: # Si el número está fuera del rango dado
                print("El número que dio no era una opción." + "\n")
                continue

            print("")
            return número # El número registrado es válido. Este ciclo no se termina hasta que esto se dé.

        except ValueError: # Si no se registró un número:
            print("Sólo se aceptan números!" + "\n")


def main():
    # Programa principal. Nunca será llamado. Siempre se corre desde programa_principal.py
    print("Este programa es una librería de funciones que se usa en programa_principal.py")


def multiples_fechas():
    print("Desea que todos los reportes usen las mismas fechas?")
    print("1. Quiero usar la misma fecha para todos mis reportes.")
    print("2. Quiero usar distintas fechas para cada reporte.")

    # Checa que se registre un número válido
    answer = int_checker("Seleccione una opción (número): ", [1, 2])
    print("")
    if answer == 2:
        return True
    return False


def obtener_cpcodes(empresa, client_secret, host, access_token, client_token, fechas):
    print(f"""
     Una de sus selecciones para {empresa} fue: 
     '6. Tabla: Hits por tipo de respuesta, de únicamente un CPcode.'
     A continuación, se mostrarán todos los CPcodes disponibles. Si
     desea generar varias tablas (una por CPCODE), favor de ingresar
     los números uno por uno. Este proceso puede tardar un momento...
     """)
    
    # Se extraen todos los cpcodes de la empresa usando la función extraer_cpcodes del prgograma generador_tablas_y_graficas.py
    cpcodes_list = extraer_cpcodes(empresa, client_secret, host, access_token, client_token, fechas)

    # Se imprimen todas las opciones de cpcode para que el usuario seleccione la que desee.
    imprimir_linea_por_linea_de_lista(cpcodes_list, primera_vez = True)
    mis_cpcodes = []
    eleccion = int_checker(f"Seleccione el cpcode para {empresa} (número de la lista, NO el cpcode): ", [0, len(cpcodes_list)])
    
    while (eleccion != -1):     # Ciclo que pide cpcodes mientras que el usuario no registre -1
        if (eleccion == 0):
            imprimir_con_formato_establecido("Ha seleccionado todos los cpcodes")
            return cpcodes_list
        
        elif (cpcodes_list[eleccion-1].split()[-1].strip('()') in mis_cpcodes):
            # Si el cpcode seleccionado ya había sido seleccionado.
            print("Ya seleccionó ese número anteriormente.")
            time.sleep(1) # El programa se pausa por un minuto para que el usuario tenga tiempo de leer el mensaje

        else:
            # Se agrega el cpcode a la lista
            mis_cpcodes.append(cpcodes_list[eleccion-1].split()[-1].strip('()'))

            if (len(mis_cpcodes) == len(cpcodes_list)): # Si la lista elegida es igual de grande a la lista original de cpcodes
                imprimir_con_formato_establecido("Ha seleccionado todos los cpcodes")
                return mis_cpcodes # return la lista elegida para que el orden preferido prevalezca
        # Imprimir las cpcodes y repetir el ciclo    
        imprimir_linea_por_linea_de_lista(cpcodes_list, primera_vez = False)
        eleccion = int_checker(f"Seleccione el cpcode para {empresa} (número de la lista, NO el cpcode): ", [-1, len(cpcodes_list)])
    
    return mis_cpcodes

def obtener_credenciales(archivo, empresas):
    # Crea un diccionario usando la empresa como clave, y una lista como valores. Los elementos de la lista son las
    # credenciales de la API
    diccionario_de_empresas = {} 
    config = configparser.ConfigParser() # Librería de python usada para leer archivos de tipo .edgerc
    config.read(archivo) # leer archivo
    for section in empresas:
        # Llenar al diccionario
        diccionario_de_empresas[section] = [config[section]['client_secret'], config[section]['host'], config[section]['access_token'], config[section]['client_token']]
    return diccionario_de_empresas

def primer_fecha_mas_reciente_que_segunda_fecha(primer_fecha, segunda_fecha):
    formato_de_fecha = "%Y-%m-%dT%H:%M:%SZ" # ISO 8601
    
    # Convierte los Strings a formato datetime
    fecha_a = datetime.strptime(primer_fecha, formato_de_fecha)
    fecha_b = datetime.strptime(segunda_fecha, formato_de_fecha)
    
    # Compara ambas fechas, la mayor es la más reciente
    if fecha_a >= fecha_b:
        return True
    
    return False

def imprimir_con_formato_establecido(text):
    # Función útil para darle buen formato a la consola. \n es como picarle "enter".
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
    # Checa lo que registra el usuario
    answer = int_checker("Seleccione una opción (número): ", [1,2])
    print("")
    if (answer == 2):
        return True
    return False

def reportes_generales(archivo, fechas, carpeta_creada):
    # Obtener la información de las empresas seleccionadas
    empresas = obtener_credenciales(archivo, extraer_todas_las_empresas(archivo))
    contador = 0 # Para determinar para cuántas empresas todavía hay que generar reportes

    for empresa, credenciales in empresas.items(): # Para generar reportes por empresa
        imprimir_con_formato_establecido(f"Etapa actual: producción de tablas/gráficas. Este proceso suele tardar varios minutos por empresa: {empresa}")
        # Crea subcarpeta para almacenar todos los reportes de la empresa en cuestión
        subcarpeta_path = crear_carpeta(nombre_de_empresa = empresa, carpeta = carpeta_creada, fechas_para_el_titulo = fechas)
        
        # Extraer todos los cpcodes
        cpcodes = extraer_cpcodes(empresa, credenciales[0], credenciales[1], credenciales[2], credenciales[3], fechas_correctas_ISO_8601(fechas, interval = "NONE"))
        # Genera reportes
        print(tabla_de_trafico_por_cpcode(empresa, credenciales[0], credenciales[1], credenciales[2], credenciales[3], fechas_correctas_ISO_8601(fechas, interval = "NONE"), subcarpeta_path, formatear_fechas(fechas[0], fechas[1])))
        print(tabla_trafico_total_y_estadisticas(empresa, credenciales[0], credenciales[1], credenciales[2], credenciales[3], fechas_correctas_ISO_8601(fechas, interval = "FIVE_MINUTES"), subcarpeta_path, formatear_fechas(fechas[0], fechas[1])))
        print(grafica_trafico_por_dia(empresa, credenciales[0], credenciales[1], credenciales[2], credenciales[3], fechas_correctas_ISO_8601(fechas, interval = "HOUR"), subcarpeta_path, formatear_fechas(fechas[0], fechas[1])))
        print(grafica_hits_al_origen_por_tipo_de_respuesta(empresa, credenciales[0], credenciales[1], credenciales[2], credenciales[3], fechas_correctas_ISO_8601(fechas, interval = "HOUR"), subcarpeta_path, formatear_fechas(fechas[0], fechas[1])))
        print(tabla_hits_por_tipo(empresa, credenciales[0], credenciales[1], credenciales[2], credenciales[3], fechas_correctas_ISO_8601(fechas, interval = "NONE"), subcarpeta_path, formatear_fechas(fechas[0], fechas[1])))
        try:
            for i in range(len(cpcodes)): # Crea la tabla 6 para los 3 primeros cpcodes (mayor edgeBytesTotal)
                if (i < 3):
                    print(tabla_hits_por_tipo(empresa, credenciales[0], credenciales[1], credenciales[2], credenciales[3], fechas_correctas_ISO_8601(fechas, interval = "NONE"), subcarpeta_path, formatear_fechas(fechas[0], fechas[1]), cpcodes[i].split()[-1].strip('()')))
                else:
                    break
        except:
            print("No se detectaron cpcodes. ¿Está seguro que las credenciales de las APIs están vigentes?")
        # último reporte
        print(tabla_hits_por_url(empresa, credenciales[0], credenciales[1], credenciales[2], credenciales[3], fechas_correctas_ISO_8601(fechas, interval = "NONE"), subcarpeta_path, formatear_fechas(fechas[0], fechas[1])))
        
        print("\n"*4 + "-"*6 + f"Reportes de {empresa} terminados" + "-"*6 + "\n"*4)
        print("Todavía hay que generar reportes para " + str(len(empresas) - 1 - contador) + " empresas más." + "\n")
        contador += 1
    


def seleccionar_archivo():
    print("\n" + "Abriendo ventana para seleccionar archivo...")
    time.sleep(1) # Un segundo para que le usuario tenga tiempo de leer el mensaje.
    # Parámetros de la librería
    root = tk.Tk()
    root.withdraw()

    # Abrir ventana preguntando por archivo:
    direccion_de_archivo = filedialog.askopenfilename(
        title="Escoja Archivo (.edgerc):",
        filetypes=(("All files", "*.*"), ("Config files", "*.edgerc"))
    )

    # return dirección del archivo
    imprimir_con_formato_establecido(direccion_de_archivo)
    return direccion_de_archivo



def seleccionar_empresas(archivo):
    # Extraer todas las empresas
    empresas = extraer_todas_las_empresas(archivo)
    empresas_escogidas = []

    # Imprimir las empresas
    imprimir_linea_por_linea_de_lista(empresas, primera_vez = True)
    eleccion = int_checker("Escoja qué empresa le interesa (número): ", [0, len(empresas)])

    while (eleccion != -1):
        if eleccion == 0: # Si selecciona todas:
            imprimir_con_formato_establecido("Ha seleccionado todas las empresas")
            return obtener_credenciales(archivo, empresas)
        
        elif empresas[eleccion - 1] in empresas_escogidas: # Si la empresa elegida ya había sido elegida:
            print("Ya habías elegido ese número anteriormente.")
            time.sleep(1)

        else:
            # Agregar nueva empresa
            empresas_escogidas.append(empresas[eleccion - 1])
            if (len(empresas_escogidas) == len(empresas)): # Si la lista de empresas elegidas es del mismo tamaño que la original:
                imprimir_con_formato_establecido("Ha seleccionado todas las empresas")
                return obtener_credenciales(archivo, empresas_escogidas)

        # El ciclo sigue y se imprimen nuevamente las empresas disponibles        
        imprimir_linea_por_linea_de_lista(empresas, primera_vez = False)
        eleccion = int_checker("Escoja qué empresa le interesa (número): ", [-1, len(empresas)])

    # Se imprimen las empresas seleccionadas para darle formato a al consola.
    print("Has seleccionado: ", end="")
    for emp in empresas_escogidas:
        print(emp, end=', ')
    imprimir_con_formato_establecido("")
    return obtener_credenciales(archivo, empresas_escogidas)


def seleccionar_fecha(texto_empresa = "todas las empresas"):
    print(f"Desea seleccionar un mes para el reporte, o quiere consultar el consumo entre dos fechas especificas para {texto_empresa}: ")
    print("1. Seleccionar un mes.")
    print("2. Seleccionar dos fechas específicas")
    # Guarda la elección del usuario
    respuesta = int_checker("Seleccione una opción (número): ", [1,2])
    print("")

    if respuesta == 1: # Si seleccionó mes:
        return seleccionar_mes(texto_empresa)
    else: # Si no seleccionó mes:
        print("AKAMAI solo tiene retención de 92 días.") # Un recuerdo para argumentar la poca flexibilidad de la GUI.
        fecha_inicio = correr_programa_subproceso("") # Lanza GUI
        print("Fecha inicial: " + fecha_inicio)
        fecha_final = correr_programa_subproceso(str(fecha_inicio)) # Lanza GUI nuevamente para la fecha final
        print("Fecha final: " + fecha_final)
        imprimir_con_formato_establecido(f"La fecha inicial para {texto_empresa} es {fecha_inicio} y la final {fecha_final}")
        return [fecha_inicio, fecha_final]
    



def seleccionar_mes(empresa):
    mes_actual = datetime.now().month # mes actual
    meses_nombres = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    
    numeros_de_mes_mencionados = []
    print(f"Akamai solo retiene información por 92 días. Considerando esto, ¿Sobre qué mes quiere el reporte para {empresa}?")
    
    # se muestran los últimos dos meses y el mes actual. Ya que solamente esos meses "completos" se pueden abarcar en 92 días.
    for i in range(2, -1, -1):
        mes_nombre = meses_nombres[(mes_actual - 1) - i]
        mes_numero = meses_nombres.index(mes_nombre) + 1
        numeros_de_mes_mencionados.append(mes_numero)
        if (i == 0):
            print(str(mes_numero) + ". " + mes_nombre + " (considere que la información no tomara en cuenta todo el mes)")
        else:
            print(str(mes_numero) + ". " + mes_nombre)
    print("")
    # Registra mes
    mes = int_checker("AKAMAI retiene solo 92 días. Seleccione mes (número): ", [numeros_de_mes_mencionados[0], numeros_de_mes_mencionados[-1]])
    return definir_fecha_de_mes(mes) # La función definir_fecha_de_mes devuelve la fecha inicial y final de el mes elegido.

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
    # Imprime las opciones
    imprimir_linea_por_linea_de_lista(lista_de_tablas_y_graficas, primera_vez = True)
    números_elegidos = []
    eleccion = int_checker(f"Seleccione una opción para {empresa} (número): ", [0,7])
    
    while (eleccion != -1):
        if (eleccion == 0): # Si seleccionó todas:
            imprimir_con_formato_establecido("Ha seleccionado todas las tablas/gráficas")
            return [1,2,3,4,5,6,7]
        
        elif (eleccion in números_elegidos): # Si seleccionó una tabla/gráfica que ya había elegido
            print("Ya seleccionó ese número anteriormente.")
            time.sleep(1) # Tiempo para dormir para que el usuario tenga tiempo de leer el mensaje.
        else:
            # Agregar tabla/gráfica
            números_elegidos.append(eleccion)
            if (len(números_elegidos) == 7): # Si selecciona todas las tablas/gráficas una por una.
                imprimir_con_formato_establecido("Ha seleccionado todas las tablas/gráficas")
                return números_elegidos
        
        # Sigue el ciclo y vuelve a imprimir las opciones
        imprimir_linea_por_linea_de_lista(lista_de_tablas_y_graficas, primera_vez = False)
        eleccion = int_checker(f"Seleccione una opción {empresa} (número): ", [-1,7])
    
    return números_elegidos

if __name__ == "__main__": # Se asegura de que las funciones puedan ser importadas sin problema.
    main()
