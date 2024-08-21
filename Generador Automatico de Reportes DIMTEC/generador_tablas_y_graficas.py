import csv
import requests # type: ignore
from akamai.edgegrid import EdgeGridAuth # type: ignore
from urllib.parse import urljoin
import forallpeople as si # type: ignore
import os
import pandas as pd # type: ignore
import numpy as np # type: ignore
import matplotlib.pyplot as plt # type: ignore
from matplotlib.ticker import FuncFormatter, MaxNLocator # type: ignore
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import locale

def extraer_cpcodes(empresa, client_secret, host, access_token, client_token, fechas):
    lista_de_cpcodes = []
    baseurl = 'https://' + host + '/' # Enlace base
    
    s = requests.Session() # Crea una "sesión"
    s.auth = EdgeGridAuth( # Solicita credenciales
        client_token=client_token,
        client_secret=client_secret,
        access_token=access_token
    )
    version = "1"
    name = "bytes-by-cpcode" # Nombre de la API

    # URL completo.
    path = '/reporting-api/v1/reports/{}/versions/{}/report-data'.format(name, version)
    querystring = { # Parámetros de la API
    "start": fechas[0],
    "end": fechas[1],
    "objectIds": "all",
    "metrics": "edgeBytes", # Al menos una métrica es necesaria
    "filters": "ca=cacheable",
    }
    result = s.get(urljoin(baseurl, path), params=querystring).json() # Respuestra tras llamar a la API
    data = result.get('data') # Del diccionario "result", extrae los elementos de llave "data".
    for credential in data: # Por elemento de la lista data:
        cpcode = credential.get('cpcode') # Obtener CPcode

        #Nueva request accediendo a la CPcode
        specific_cpcode_request = s.get(urljoin(baseurl, '/cprg/v1/cpcodes/'+cpcode)).json() 

        # Obtener el nombre de la CPcode
        name = specific_cpcode_request.get('cpcodeName')

        # Agregar CPcode con su nombre a la lista_de_cpcodes
        lista_de_cpcodes.append(name + " (" + cpcode + ")")
    return lista_de_cpcodes


# Genera Tabla de Tráfico por CPcode, ordenado por orden descendiente de Bytes de Edge
def tabla_de_trafico_por_cpcode(empresa, client_secret, host, access_token, client_token, fechas, subcarpeta_path, fecha_correcta_nombre):
    
    # Formatea los valores de acuerdo a la convención de DIMTEC para este tipo de tabla
    def formatear_valores(nombre_de_cpcode_formateado, OffloadBytes, edge_bytes_total, midgress_bytes_total, origin_bytes_total):
        lista_formateada = [nombre_de_cpcode_formateado, str(OffloadBytes)+" %"] # Coloca el símbolo de personaje
        
        # Encuentra el prefijo del Sistema Internacional correcto y redondea a 2 decimales
        nuevo_ebt = str(round(int(edge_bytes_total)*si.A,2)) 
        nuevo_mbt = str(round(int(midgress_bytes_total)*si.A,2))
        nuevo_obt = str(round(int(origin_bytes_total)*si.A,2))

        # Cambia A de amperes por Bytes. LA librería no tenía prestaciones para la unidad Bytes.
        lista_formateada.append(nuevo_ebt.replace("A", "B"))
        lista_formateada.append(nuevo_mbt.replace("A", "B"))
        lista_formateada.append(nuevo_obt.replace("A", "B"))
        
        # Columna extra para mostrar los elementos por orden descendiente de Bytes de Edge.
        lista_formateada.append(int(edge_bytes_total))
        return lista_formateada

    def filas_ordenadas(archivo, ordenar_por_esta_columna):
        columna = ordenar_por_esta_columna
        dataframe = pd.read_csv(archivo) # Lee el archivo

        # Ordena en orden descendiente el archivo en base a "columna"
        dataframe_ordenado = dataframe.sort_values(by=columna, ascending=False)

        # Elimina columna extra para ordenar
        dataframe_ordenado = dataframe_ordenado.drop(columns=[columna])
        dataframe_ordenado.to_csv(archivo, index=False) # Elimina columna index
    
    baseurl = 'https://' + host + '/'  
    s = requests.Session()
    s.auth = EdgeGridAuth(
        client_token=client_token,          # Credenciales de API
        client_secret=client_secret,
        access_token=access_token
    )
    version = "1"
    nombre_de_cpcode = "bytes-by-cpcode" # API
    path = '/reporting-api/v1/reports/{}/versions/{}/report-data'.format(nombre_de_cpcode, version)
    querystring = { # Parámetros de API
    "start": fechas[0],
    "end": fechas[1],
    "metrics": "bytesOffload, edgeBytes, midgressBytes, originBytes",
    "filters": "ca=cacheable",
    }

    result = s.get(urljoin(baseurl, path), params=querystring)
    print(f"Configuración (Tabla de Tráfico por CPcode): {empresa}")
    print(f"HTTPS clase de respuesta (Tabla de Tráfico por CPcode): {result.status_code}")
    response_json = result.json() # Respuesta en formato JSON
    data = response_json.get('data') # Acceder a Data
    
    # Nombre de archivo CSV a generar
    nombre_de_archivo = f"tabla_de_trafico_por_cpcode_{empresa}_{fecha_correcta_nombre}.csv"
    
    # Dónde guardar el archivo
    csv_ubicacion = os.path.join(subcarpeta_path, nombre_de_archivo)
    with open(csv_ubicacion, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Columnas
        header = ['CpCodeId', 'Offload Percentage', 'Edge Bytes', 'Midgress Bytes', 'Origin Bytes', 'sortingColumn']
        writer.writerow(header)
        for credential in data:
            # Obtener nombre de la cpcode
            cpcode = credential.get('cpcode')
            respuesta_de_extraccion_de_cpcodes = s.get(urljoin(baseurl, '/cprg/v1/cpcodes/' + str(cpcode))).json()
            nombre_de_cpcode = respuesta_de_extraccion_de_cpcodes.get('cpcodeName')
            nombre_final = nombre_de_cpcode + " (" + cpcode + ")"
            # Registrar los valores relevantes
            if data:
                writer.writerow(formatear_valores(nombre_final, credential.get('bytesOffload'), credential.get('edgeBytes'), credential.get('midgressBytes'), credential.get('originBytes')))     
    # Ordenar el archivo
    filas_ordenadas(csv_ubicacion, "sortingColumn")
    
    return f"--{nombre_de_archivo} creado--"

def tabla_trafico_total_y_estadisticas(empresa, client_secret, host, access_token, client_token, fechas, subcarpeta_path, fecha_correcta_nombre):
    baseurl = 'https://' + host + '/'  
    s = requests.Session()
    s.auth = EdgeGridAuth(
        client_token=client_token,      # Solicitar Sesión con credenciales de la API
        client_secret=client_secret,
        access_token=access_token
    )
    version = "1"
    name = "bytes-by-time" # Nombre de la API
    path = '/reporting-api/v1/reports/{}/versions/{}/report-data'.format(name, version)
    querystring = { # Parámetros de la API
    "start": fechas[0],
    "end": fechas[1],
    "interval": "FIVE_MINUTES", # Parámetro que define el formato de las fechas
    "objectIds": "all",
    "metrics": "bytesOffload, bytesOffloadAvg, bytesOffloadMax, bytesOffloadMin, edgeBitsPerSecond, edgeBitsPerSecondMax, edgeBitsPerSecondMin, edgeBytesTotal, midgressBitsPerSecond, midgressBitsPerSecondMax, midgressBitsPerSecondMin, midgressBytesTotal, originBitsPerSecond, originBitsPerSecondMax, originBitsPerSecondMin, originBytesTotal", # Al menos una métrica es necesaria...
    "filters": "ca=cacheable",
    }

    result = s.get(urljoin(baseurl, path), params=querystring)
    print(f"Configuración (Tabla Tráfico Total y Estadísticas): {empresa}")
    print(f"HTTPS clase de respuesta (Tabla Tráfico Total y Estadísticas): {result.status_code}")
    response_json = result.json() # Obtener respuesta de la Sesión en formato JSON

    summary_stats = response_json.get('summaryStatistics', [])
    columnas = ["", "Offload", "Edge", "Midgress", "Origin"]

    # Llenar listas con la información formateada
    total = ["Total", f"{float(summary_stats.get("bytesOffloadAvg").get("value")):.2f} %", f"{str(round(int(float(summary_stats.get("edgeBytesTotal").get("value")))*si.A,2)).replace("A", "B")}", f"{str(round(int(float(summary_stats.get("midgressBytesTotal").get("value")))*si.A,2)).replace("A", "B")}", f"{str(round(int(float(summary_stats.get("originBytesTotal").get("value")))*si.A,2)).replace("A", "B")}"]
    minimos = ["Minimo", f"{float(summary_stats.get("bytesOffloadMin").get("value")):.2f} %", f"{str(round(int(float(summary_stats.get("edgeBitsPerSecondMin").get("value")))*si.A,2)).replace("A", "B")}/s", f"{str(round(int(float(summary_stats.get("midgressBitsPerSecondMin").get("value")))*si.A,2)).replace("A", "B")}/s", f"{str(round(int(float(summary_stats.get("originBitsPerSecondMin").get("value")))*si.A,2)).replace("A", "B")}/s"]
    maximos = ["Maximo", f"{float(summary_stats.get("bytesOffloadMax").get("value")):.2f} %", f"{str(round(int(float(summary_stats.get("edgeBitsPerSecondMax").get("value")))*si.A,2)).replace("A", "B")}/s", f"{str(round(int(float(summary_stats.get("midgressBitsPerSecondMax").get("value")))*si.A,2)).replace("A", "B")}/s", f"{str(round(int(float(summary_stats.get("originBitsPerSecondMax").get("value")))*si.A,2)).replace("A", "B")}/s"]
    
    # Nombre de archivo CSV
    nombre_de_archivo = f"tabla_trafico_total_y_estaditicas_{empresa}_{fecha_correcta_nombre}.csv"
    # Dónde guardar el archivo
    csv_ubicacion = os.path.join(subcarpeta_path, nombre_de_archivo)
    
    # Llenar datos del CSV
    with open(csv_ubicacion, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(columnas)
        writer.writerow(total)
        writer.writerow(minimos)
        writer.writerow(maximos)
    return f"--{nombre_de_archivo} creado--"

def grafica_trafico_por_dia(empresa, client_secret, host, access_token, client_token, fechas, subcarpeta_path, fecha_correcta_nombre):
    # Guardar las configuraciones Locale
    original_locale = locale.getlocale(locale.LC_TIME)
    
    # Cambiar la configuracion Locale a Español para los meses de la gráfica
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    
    baseurl = 'https://' + host + '/'  
    s = requests.Session()
    s.auth = EdgeGridAuth(
        client_token=client_token,  # Crear Sesión con credenciales API
        client_secret=client_secret,
        access_token=access_token
    )
    version = "1"
    name = "bytes-by-time" # Nombre de la API
    path = '/reporting-api/v1/reports/{}/versions/{}/report-data'.format(name, version)
    querystring = { # Parámetros de la API
    "start": fechas[0],
    "end": fechas[1],
    "interval": "HOUR", # Parámetro que define el formato de las fechas
    "objectIds": "all",
    "metrics": "bytesOffload, edgeBitsPerSecond, midgressBitsPerSecond, originBitsPerSecond", # Métricas seleccionadas
    "filters": "ca=cacheable",
    }
    result = s.get(urljoin(baseurl, path), params=querystring)
    print(f"Configuración (Gráfica de tráfico por día): {empresa}")
    print(f"HTTPS clase de respuesta (Gráfica de tráfico por día): {result.status_code}")

    response_json = result.json() # Obtener respuesta de Sesión en formato JSON
    data = response_json.get('data', [])
    length = len(data) # Número de elementos devueltos al llamar a la API
    values_dictionary = {
        "bytesOffload" : [],
        "edgeBitsPerSecond" : [],
        "midgressBitsPerSecond" : [],
        "originBitsPerSecond" : []
    }
    for value in data:
        # Llenar diccionario con todos los valores iterando
        values_dictionary["bytesOffload"].append(int(float(value.get('bytesOffload'))))
        values_dictionary["edgeBitsPerSecond"].append(int(float(value.get('edgeBitsPerSecond'))))
        values_dictionary["midgressBitsPerSecond"].append(int(float(value.get('midgressBitsPerSecond'))))
        values_dictionary["originBitsPerSecond"].append(int(float(value.get('originBitsPerSecond'))))
    
    # Convertir String de fecha en formato datetime
    start_date = datetime.fromisoformat(fechas[0].replace('Z', ''))
    end_date = datetime.fromisoformat(fechas[1].replace('Z', ''))

    # Calcular el número total de horas en base a los segundos totales
    num_hours = int((end_date - start_date).total_seconds() // 3600)

    # Generarar un array en base a la cantidad de horas, sumando una hora a la vez
    date_array = [start_date + timedelta(hours=i) for i in range(num_hours)]

    # Formato np.array
    edgeBitsPerSecond = np.array(values_dictionary["edgeBitsPerSecond"])  
    midgressBitsPerSecond = np.array(values_dictionary["midgressBitsPerSecond"])  
    originBitsPerSecond = np.array(values_dictionary["originBitsPerSecond"])
    bytesOffload = np.array(values_dictionary["bytesOffload"]) 
    
    # Crear gráfica
    fig, ax1 = plt.subplots(figsize=(14, 6))
    # Posicionar gráficas en los márgenes de la ventana.
    plt.subplots_adjust(left=0.09, right=0.87, top=0.9, bottom=0.1)
    # Graficar Edge, Midgress, and Origin en el primer eje de las ordenadas
    line1, = ax1.plot(date_array, edgeBitsPerSecond, label='Edge', color='green')
    line2, = ax1.plot(date_array, midgressBitsPerSecond, label='Midgress', color='purple')
    line3, = ax1.plot(date_array, originBitsPerSecond, label='Origin', color='orange')
    
    # Nombre del primer eje de las ordenadas
    ax1.set_ylabel('Bits/sec')
    
    # Crear segunda eje de las ordenadas para el Offload
    ax2 = ax1.twinx()
    line4, = ax2.plot(date_array, bytesOffload, label='Offload', color='blue')
    ax2.set_ylabel('Offload', labelpad=0)
    ax2.set_ylim(0, 100)

    # Título de la gráfica
    plt.title(f'{empresa}, {fecha_correcta_nombre}: Edge, Midgress, y Origin bits/sec con Offload')
    ax1.grid(True) # Habilitar cuadrícula

    # Combinar leyendas de ambos ejes
    lines = [line4, line1, line2, line3]
    labels = [line4.get_label(), line1.get_label(), line2.get_label(), line3.get_label()]

    # Mostrar las leyendas juntas
    # Con los parámetros bbox_to_anchor y borderaxespad se puede posicionar la "caja de leyendas"
    fig.legend(lines, labels, loc='upper left', bbox_to_anchor=(0.9, 0.9), borderaxespad=1.2)

    # Delimitar cantidad de ticks a 16
    ax1.xaxis.set_major_locator(MaxNLocator(nbins=16))
    # Formatear ticks a mes en español (Agosto => ago.) y día en dos caracteres
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

    # Usando una expresión lambda, se formatean los nombres de las ticks: "ago. 16" => "Ago 16"
    ax1.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: mdates.num2date(x).strftime('%b %d').replace('.', '').capitalize()))

    # Asegurarse de que los gráficos comiencen en los bordes de la gráfica
    ax1.set_xlim(start_date, end_date)


    ax1.set_ylim(bottom=0) # El eje de las y empieza en 0
    # Quitar el borde de abajo de la gráfica para el eje de las ordenadas:
    ax1.spines['bottom'].set_color('none') # Eje de las ordenadas uno
    ax2.spines['bottom'].set_color('none') # Eje de las ordenadas dos

    # Formatear el texto de ambos ejes de las ordenadas
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f'{str(round(int(x)*si.A,2)).replace("A", "B")}/s'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f'{int(x)}%'))

    
    # Guardar imagen de la gráfica
    nombre_de_archivo = f"Grafica_Trafico_Por_Dia_{empresa}_{fecha_correcta_nombre}.png"
    ubicacion_de_archivo = os.path.join(subcarpeta_path, nombre_de_archivo)
    plt.savefig(ubicacion_de_archivo)
    plt.close(fig)

    # Restaurar configuaración Locale a la original
    locale.setlocale(locale.LC_TIME, original_locale)
    return f"--{nombre_de_archivo} creado--"

def grafica_hits_al_origen_por_tipo_de_respuesta(empresa, client_secret, host, access_token, client_token, fechas, subcarpeta_path, fecha_correcta_nombre):
    # Guardar las configuraciones Locale
    original_locale = locale.getlocale(locale.LC_TIME)
    
    # Cambiar la configuracion Locale a Español para los meses de la gráfica
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    
    baseurl = 'https://' + host + '/'  
    s = requests.Session()
    s.auth = EdgeGridAuth(
        client_token=client_token,  # Crear Sesión con credenciales API
        client_secret=client_secret,
        access_token=access_token
    )
    version = "1"
    name = "traffic-by-timeandresponseclass" # Nombre de la API
    path = '/reporting-api/v1/reports/{}/versions/{}/report-data'.format(name, version)
    querystring = { # Parámetros de la API
    "start": fechas[0],
    "end": fechas[1],
    "interval": "HOUR", # Parámetro que define el formato de las fechas
    "objectIds": "all",
    "metrics": "originHitsPerSecond", # Métricas seleccionadas
    "filters": "ca=cacheable",
    }
    result = s.get(urljoin(baseurl, path), params=querystring)
    print(f"Configuración (Gráfica de hits al origen por segundo y por tipo de respuesta): {empresa}")
    print(f"HTTPS clase de respuesta (Gráfica de hits al origen por segundo y por tipo de respuesta): {result.status_code}")
    response_json = result.json() # Obtener respuesta de Sesión en formato JSON
    data = response_json.get('data', [])
    length = len(data) # Número de elementos devueltos al llamar a la API
    values_dictionary = {
        "0xx" : [],
        "1xx" : [],
        "2xx" : [],
        "3xx" : [],
        "4xx" : [],
        "5xx" : []
    }
    for dict in data:
        # Acceder a mini lista dentro del diccionario con llave "data"
        mini_list = dict.get("data")
        for mini_dict in mini_list:
            # Acceder al mini diccionario dentro de la mini lista y adjuntar datos al diccionario "values_dictionary"
            values_dictionary[str(mini_dict.get("response_class"))].append(round(float(mini_dict.get('originHitsPerSecond')),4))
    
    if not values_dictionary["1xx"]:
        # A veces no hay respuestas 1xx, en ese caso llenar diccionario con 0s.
        values_dictionary["1xx"] = [0] * length  
        
                      
    # Convertir String de fecha en formato datetime
    start_date = datetime.fromisoformat(fechas[0].replace('Z', ''))
    end_date = datetime.fromisoformat(fechas[1].replace('Z', ''))

    # Calcular el número total de horas en base a los segundos totales
    num_hours = int((end_date - start_date).total_seconds() // 3600)

    # Generarar un array en base a la cantidad de horas, sumando una hora a la vez
    date_array = [start_date + timedelta(hours=i) for i in range(num_hours)]
    
    # Formato np.array
    response_0xx = np.array(values_dictionary["0xx"])  
    response_1xx = np.array(values_dictionary["1xx"])  
    response_2xx = np.array(values_dictionary["2xx"])  
    response_3xx = np.array(values_dictionary["3xx"])  
    response_4xx = np.array(values_dictionary["4xx"])  
    response_5xx = np.array(values_dictionary["5xx"]) 

    # Crear gráfica
    fig, ax1 = plt.subplots(figsize=(14, 6))
    # Posicionar gráficas en los márgenes de la ventana.
    plt.subplots_adjust(left=0.09, right=0.87, top=0.9, bottom=0.1)
    # Graficar Hits al Origen por Segundo en base al tipo de respuesta
    ax1.plot(date_array, response_0xx, label='0xx', color='orange')
    ax1.plot(date_array, response_1xx, label='1xx', color='blue')
    ax1.plot(date_array, response_2xx, label='2xx', color='green')
    ax1.plot(date_array, response_3xx, label='3xx', color='cyan')
    ax1.plot(date_array, response_4xx, label='4xx', color='pink')
    ax1.plot(date_array, response_5xx, label='5xx', color='red')
    
    # Nombre del eje de las ordenadas
    ax1.set_ylabel('Hits/sec')
    # Posicionar leyendas
    ax1.legend(loc='upper left', bbox_to_anchor=(1.01, 1), borderaxespad=0.)
    
    # Título de la gráfica
    plt.title(f'{empresa}, {fecha_correcta_nombre}: Origin hits/sec by response class')
    ax1.grid(True) # Habilitar cuadrícula

    # Delimitar cantidad de ticks a 16
    ax1.xaxis.set_major_locator(MaxNLocator(nbins=16))
    # Formatear ticks a mes en español (Agosto => ago.) y día en dos caracteres
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))

    # Usando una expresión lambda, se formatean los nombres de las ticks: "ago. 16" => "Ago 16"
    ax1.xaxis.set_major_formatter(FuncFormatter(lambda x, pos: mdates.num2date(x).strftime('%b %d').replace('.', '').capitalize()))

    # Asegurarse de que los gráficos comiencen en los bordes de la gráfica
    ax1.set_xlim(start_date, end_date)
    
    
    ax1.set_ylim(bottom=0) # El eje de las y empieza en 0
    ax1.spines['bottom'].set_color('none') # Quitar el borde de abajo de la gráfica

    # Formatear el texto del eje de las ordenadas
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f'{int(x)}.00')) 
    
    # Guardar imagen de la gráfica
    nombre_de_archivo = f"Grafica_de_Hits_al_Origen_al_Tipo_de_respuesta_{empresa}_{fecha_correcta_nombre}.png"
    ubicacion_de_archivo = os.path.join(subcarpeta_path, nombre_de_archivo)
    plt.savefig(ubicacion_de_archivo)
    plt.close(fig)

    # Restaurar configuaración Locale a la original
    locale.setlocale(locale.LC_TIME, original_locale)
    return f"--{nombre_de_archivo} creado--"

# Genera Tabla de Tráfico por CPcode, ordenado por orden descendiente de Bytes de Edge
def tabla_hits_por_tipo(empresa, client_secret, host, access_token, client_token, fechas, subcarpeta_path, fecha_correcta_nombre, cpcode = "all"):
    
    # Formatea los valores de acuerdo a la convención de DIMTEC para este tipo de tabla
    def formatear_valores(row):
        new_row = [row[0]] # El primer valor de cada fila se mantiene igual
        for value in row[1:]:
            if isinstance(value, int):
                new_row.append(f"{value:,}")
            elif isinstance(value, float):
                if (str(value)[0] == '0' and str(value)[2:4] == "00"):
                    new_row.append(f"{value:.7f} %")
                else:
                    new_row.append(f"{value:.2f} %")
            else:
                new_row.append(value)
        return new_row # return fila formateada

    def filas_ordenadas(archivo, ordenar_por_esta_columna):
        dataframe = pd.read_csv(archivo)  # Lee el archivo

        # Ordena en orden descendiente el archivo en base a "columna"
        dataframe_ordenado = dataframe.sort_values(by=ordenar_por_esta_columna, ascending=False)
       
        # Obtener nuevas filas
        nuevas_filas = [formatear_valores(row) for row in dataframe_ordenado.values]
        final_df = pd.DataFrame(nuevas_filas, columns=dataframe_ordenado.columns)
        final_df.to_csv(archivo, index=False) # Archivo actualizado
    
    if (cpcode == "all"): # Si no se pasa una cpcode como parametro
        # No se menciona la cpcode en los nombres
        nombre_de_archivo = f"tabla_hits_por_tipo_{empresa}_{fecha_correcta_nombre}.csv"
        columnaCSV = 'Tipo de Respuesta'
    else: # Si se pasa una cpcode como parametro
        # Se menciona la cpcode en los nombres
        nombre_de_archivo = f"tabla_hits_por_tipo_{empresa}_{cpcode}_{fecha_correcta_nombre}.csv"
        columnaCSV = f"Tipo de Respuesta ({cpcode})"
    
    baseurl = 'https://' + host + '/' 
    s = requests.Session()
    s.auth = EdgeGridAuth(
        client_token=client_token,  # Credenciales de API
        client_secret=client_secret,
        access_token=access_token
    )
    version = "1"
    name = "traffic-by-responseclass" # API
    path = '/reporting-api/v1/reports/{}/versions/{}/report-data'.format(name, version)
    querystring = { # Parámetros de API
            "start": fechas[0],
            "end": fechas[1],
            "objectIds": cpcode,
            "metrics": "",
            "filters": "ca=cacheable",
            }
    result = s.get(urljoin(baseurl, path), params=querystring)
    print(f"Configuración (Tabla hits por tipo de respuesta): {empresa}")
    print(f"HTTPS clase de respuesta (Tabla hits por tipo de respuesta): {result.status_code}")
    response_json = result.json() # Respuesta en formato JSON
    data = response_json.get('data') # Acceder a Data

    # Dónde guardar el archivo
    csv_ubicacion = os.path.join(subcarpeta_path, nombre_de_archivo)
    with open(csv_ubicacion, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Columnas
        header = [columnaCSV, 'Edge Hits', 'Edge Hits %', 'Origin Hits', 'Origin Hits %']
        writer.writerow(header)

        for tipo_de_respuesta in data: 
            if tipo_de_respuesta:
                # Registrar los valores relevantes
                writer.writerow([tipo_de_respuesta.get("response_class"), tipo_de_respuesta.get('edgeHits'), tipo_de_respuesta.get('edgeHitsPercent'), tipo_de_respuesta.get('originHits'), tipo_de_respuesta.get('originHitsPercent')])     
    
    # Ordenar el archivo
    filas_ordenadas(csv_ubicacion, "Edge Hits")
    return f"--{nombre_de_archivo} creado--"

def tabla_hits_por_url(empresa, client_secret, host, access_token, client_token, fechas, subcarpeta_path, fecha_correcta_nombre):
    def formatear_valores(row):
        new_row = [row[0]] # El primer valor de cada fila se mantiene igual
        for value in row[1:]:
            if isinstance(value, int):
                new_row.append(f"{value:,}")
            elif isinstance(value, float):
                if (str(value)[0] == '0' and str(value)[2:4] == "00"):
                    new_row.append(f"{value:.7f} %")
                else:
                    new_row.append(f"{value:.2f} %")
            else:
                new_row.append(value)
        return new_row # return fila formateada

    def filas_ordenadas(archivo, ordenar_por_esta_columna):
        dataframe = pd.read_csv(archivo) # Lee el archivo

        # Ordena en orden descendiente el archivo en base a "columna"
        dataframe_ordenado = dataframe.sort_values(by=ordenar_por_esta_columna, ascending=False)
        
        # Obtener nuevas filas
        nuevas_filas = [formatear_valores(row) for row in dataframe_ordenado.values]
        final_df = pd.DataFrame(nuevas_filas, columns=dataframe_ordenado.columns)
        final_df = final_df.head(10)
        final_df.to_csv(archivo, index=False) # Archivo actualizado
    
    baseurl = 'https://' + host + '/' 
    s = requests.Session()
    s.auth = EdgeGridAuth(
        client_token=client_token, # Credenciales de API
        client_secret=client_secret,
        access_token=access_token
    )
    version = "1"
    name = "urlhits-by-url" # API
    path = '/reporting-api/v1/reports/{}/versions/{}/report-data'.format(name, version)
    querystring = { # Parámetros de API
            "start": "2024-06-01T00:00:00Z",
            "end": "2024-07-01T00:00:00Z",
            "objectIds": "all",
            "metrics": "",
            "filters": "",
            }
    result = s.get(urljoin(baseurl, path), params=querystring)
    print(f"Configuración (Tabla hits por URL): {empresa}")
    print(f"HTTPS clase de respuesta (Tabla hits por URL): {result.status_code}")
    response_json = result.json() # Respuesta en formato JSON
    data = response_json.get('data') # Acceder a Data

    # Nombre de archivo y dónde guardarlo
    nombre_de_archivo = f"tabla_hits_por_URL_{empresa}_{fecha_correcta_nombre}.csv"
    csv_ubicacion = os.path.join(subcarpeta_path, nombre_de_archivo)
    with open(csv_ubicacion, mode='w', newline='') as file:
        writer = csv.writer(file)
        # Columnas
        header = ['URL', 'Edge Hits', 'Origin Hits', 'Offload']
        writer.writerow(header)
        for response in data:
            if response:
                # Registrar los valores relevantes
                writer.writerow([response.get("hostname.url"), response.get('allEdgeHits'), response.get('allOriginHits'), response.get('allHitsOffload')])     
    
    # Ordenar el archivo
    filas_ordenadas(csv_ubicacion, "Edge Hits")
    return f"--{nombre_de_archivo} creado--"


def main():
    return # Este programa debería correrse a través de programa_principal.py

if __name__ == "__main__":
    main()