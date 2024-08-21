import csv
import requests # type: ignore
from akamai.edgegrid import EdgeGridAuth # type: ignore
from urllib.parse import urljoin
import forallpeople as si # type: ignore
import os
import pandas as pd # type: ignore
from datetime import datetime
import json
import locale
import numpy as np # type: ignore
import matplotlib.pyplot as plt # type: ignore
from matplotlib.ticker import FuncFormatter # type: ignore

def extraer_cpcodes(empresa, client_secret, host, access_token, client_token, fechas):
    lista_de_cpcodes = []
    baseurl = 'https://' + host + '/'
    s = requests.Session()
    s.auth = EdgeGridAuth(
        client_token=client_token,
        client_secret=client_secret,
        access_token=access_token
    )
    version = "1"
    name = "bytes-by-cpcode"
    path = '/reporting-api/v1/reports/{}/versions/{}/report-data'.format(name, version)
    querystring = {
    "start": "2024-06-01T06:00:00Z",
    "end": "2024-07-01T06:00:00Z",
    "objectIds": "all",
    "metrics": "edgeBytes", # Al menos una métrica es necesaria...
    "filters": "ca=cacheable",
    }
    result = s.get(urljoin(baseurl, path), params=querystring).json()
    data = result.get('data')
    for credential in data:
        cpcode = credential.get('cpcode')
        specific_cpcode_request = s.get(urljoin(baseurl, '/cprg/v1/cpcodes/'+cpcode)).json()
        name = specific_cpcode_request.get('cpcodeName')
        lista_de_cpcodes.append(name + " (" + cpcode + ")")
    return lista_de_cpcodes



def tabla_de_trafico_por_cpcode(empresa, client_secret, host, access_token, client_token, fechas, subcarpeta_path, fecha_correcta_nombre):
    
    def pretty_printer(final_name, off, ebt, mbt, obt):
        list_result = [final_name, str(off)+" %"]
        new_ebt = str(round(int(ebt)*si.A,2))
        new_mbt = str(round(int(mbt)*si.A,2))
        new_obt = str(round(int(obt)*si.A,2))
        list_result.append(new_ebt.replace("A", "B"))
        list_result.append(new_mbt.replace("A", "B"))
        list_result.append(new_obt.replace("A", "B"))
        list_result.append(int(ebt))
        return list_result

    def sort_file(file, column):
        sort_column = column
        df = pd.read_csv(file)
        sorted_df = df.sort_values(by=sort_column, ascending=False)
        sorted_df = sorted_df.drop(columns=[sort_column])
        sorted_df.to_csv(file, index=False)
    
    baseurl = 'https://' + host + '/'  # this is the "host" value from your credentials file
    s = requests.Session()
    s.auth = EdgeGridAuth(
        client_token=client_token,
        client_secret=client_secret,
        access_token=access_token
    )
    version = "1"
    nombre_de_cpcode = "bytes-by-cpcode"
    path = '/reporting-api/v1/reports/{}/versions/{}/report-data'.format(nombre_de_cpcode, version)
    querystring = {
    "start": fechas[0],
    "end": fechas[1],
    "metrics": "bytesOffload, edgeBytes, midgressBytes, originBytes", # Al menos una métrica es necesaria...
    "filters": "ca=cacheable",
    }
    result = s.get(urljoin(baseurl, path), params=querystring)
    print(f"Configuración (Tabla de Tráfico por CPcode): {empresa}")
    print(f"HTTPS clase de respuesta (Tabla de Tráfico por CPcode): {result.status_code}")
    response_json = result.json()
    data = response_json.get('data')
    # Define the CSV file name
    nombre_de_archivo = f"tabla_de_trafico_por_cpcode_{empresa}_{fecha_correcta_nombre}.csv"
    
    csv_ubicacion = os.path.join(subcarpeta_path, nombre_de_archivo)
    with open(csv_ubicacion, mode='w', newline='') as file:
        writer = csv.writer(file)
        header = ['CpCodeId', 'Offload Percentage', 'Edge Bytes', 'Midgress Bytes', 'Origin Bytes', 'sortingColumn']
        writer.writerow(header)
        for credential in data:
            cpcode = credential.get('cpcode')
            respuesta_de_extraccion_de_cpcodes = s.get(urljoin(baseurl, '/cprg/v1/cpcodes/' + str(cpcode))).json()
            nombre_de_cpcode = respuesta_de_extraccion_de_cpcodes.get('cpcodeName')
            nombre_final = nombre_de_cpcode + " (" + cpcode + ")"
            # Write the values
            if data:
                writer.writerow(pretty_printer(nombre_final, credential.get('bytesOffload'), credential.get('edgeBytes'), credential.get('midgressBytes'), credential.get('originBytes')))     
    sort_file(csv_ubicacion, "sortingColumn")
    
    return f"--{nombre_de_archivo} creado--"

def tabla_trafico_total_y_estadisticas(empresa, client_secret, host, access_token, client_token, fechas, subcarpeta_path, fecha_correcta_nombre):
    baseurl = 'https://' + host + '/'  # this is the "host" value from your credentials file
    s = requests.Session()
    s.auth = EdgeGridAuth(
        client_token=client_token,
        client_secret=client_secret,
        access_token=access_token
    )
    version = "1"
    name = "bytes-by-time"
    path = '/reporting-api/v1/reports/{}/versions/{}/report-data'.format(name, version)
    querystring = {
    "start": fechas[0],
    "end": fechas[1],
    "interval": "FIVE_MINUTES",
    "objectIds": "all",
    "metrics": "bytesOffload, bytesOffloadAvg, bytesOffloadMax, bytesOffloadMin, edgeBitsPerSecond, edgeBitsPerSecondMax, edgeBitsPerSecondMin, edgeBytesTotal, midgressBitsPerSecond, midgressBitsPerSecondMax, midgressBitsPerSecondMin, midgressBytesTotal, originBitsPerSecond, originBitsPerSecondMax, originBitsPerSecondMin, originBytesTotal", # Al menos una métrica es necesaria...
    "filters": "ca=cacheable",
    }
    result = s.get(urljoin(baseurl, path), params=querystring)
    print(f"Configuración (Tabla Tráfico Total y Estadísticas): {empresa}")
    print(f"HTTPS clase de respuesta (Tabla Tráfico Total y Estadísticas): {result.status_code}")
    response_json = result.json()
    summary_stats = response_json.get('summaryStatistics', [])
    columnas = ["", "Offload", "Edge", "Midgress", "Origin"]
    total = ["Total", f"{float(summary_stats.get("bytesOffloadAvg").get("value")):.2f} %", f"{str(round(int(float(summary_stats.get("edgeBytesTotal").get("value")))*si.A,2)).replace("A", "B")}", f"{str(round(int(float(summary_stats.get("midgressBytesTotal").get("value")))*si.A,2)).replace("A", "B")}", f"{str(round(int(float(summary_stats.get("originBytesTotal").get("value")))*si.A,2)).replace("A", "B")}"]
    minimos = ["Minimo", f"{float(summary_stats.get("bytesOffloadMin").get("value")):.2f} %", f"{str(round(int(float(summary_stats.get("edgeBitsPerSecondMin").get("value")))*si.A,2)).replace("A", "B")}/s", f"{str(round(int(float(summary_stats.get("midgressBitsPerSecondMin").get("value")))*si.A,2)).replace("A", "B")}/s", f"{str(round(int(float(summary_stats.get("originBitsPerSecondMin").get("value")))*si.A,2)).replace("A", "B")}/s"]
    maximos = ["Maximo", f"{float(summary_stats.get("bytesOffloadMax").get("value")):.2f} %", f"{str(round(int(float(summary_stats.get("edgeBitsPerSecondMax").get("value")))*si.A,2)).replace("A", "B")}/s", f"{str(round(int(float(summary_stats.get("midgressBitsPerSecondMax").get("value")))*si.A,2)).replace("A", "B")}/s", f"{str(round(int(float(summary_stats.get("originBitsPerSecondMax").get("value")))*si.A,2)).replace("A", "B")}/s"]
    # Define the file name as 'grafica_JP'
    nombre_de_archivo = f"tabla_trafico_total_y_estaditicas_{empresa}_{fecha_correcta_nombre}.csv"
    # Combine the file path and file name
    csv_ubicacion = os.path.join(subcarpeta_path, nombre_de_archivo)
    # Write the CSV file
    with open(csv_ubicacion, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(columnas)
        writer.writerow(total)
        writer.writerow(minimos)
        writer.writerow(maximos)
    return f"--{nombre_de_archivo} creado--"

def grafica_trafico_por_dia(empresa, client_secret, host, access_token, client_token, fechas, subcarpeta_path, fecha_correcta_nombre):
    baseurl = 'https://' + host + '/'  # this is the "host" value from your credentials file
    s = requests.Session()
    s.auth = EdgeGridAuth(
        client_token=client_token,
        client_secret=client_secret,
        access_token=access_token
    )
    version = "1"
    name = "bytes-by-time"
    path = '/reporting-api/v1/reports/{}/versions/{}/report-data'.format(name, version)
    querystring = {
    "start": fechas[0],
    "end": fechas[1],
    "interval": "HOUR",
    "objectIds": "all",
    "metrics": "bytesOffload, edgeBitsPerSecond, midgressBitsPerSecond, originBitsPerSecond", # Al menos una métrica es necesaria...
    "filters": "ca=cacheable",
    }
    result = s.get(urljoin(baseurl, path), params=querystring)
    print(f"Configuración (Gráfica de tráfico por día): {empresa}")
    print(f"HTTPS clase de respuesta (Gráfica de tráfico por día): {result.status_code}")

    response_json = result.json()
    data = response_json.get('data', [])
    length = len(data)
    values_dictionary = {
        "bytesOffload" : [],
        "edgeBitsPerSecond" : [],
        "midgressBitsPerSecond" : [],
        "originBitsPerSecond" : []
    }
    for value in data:
        values_dictionary["bytesOffload"].append(int(float(value.get('bytesOffload'))))
        values_dictionary["edgeBitsPerSecond"].append(int(float(value.get('edgeBitsPerSecond'))))
        values_dictionary["midgressBitsPerSecond"].append(int(float(value.get('midgressBitsPerSecond'))))
        values_dictionary["originBitsPerSecond"].append(int(float(value.get('originBitsPerSecond'))))
    
    dates = np.linspace(1, length, length)  # Days of the month
    edgeBitsPerSecond = np.array(values_dictionary["edgeBitsPerSecond"])  # Replace with actual edge data
    midgressBitsPerSecond = np.array(values_dictionary["midgressBitsPerSecond"])  # Replace with actual midgress data
    originBitsPerSecond = np.array(values_dictionary["originBitsPerSecond"])  # Replace with actual origin data
    bytesOffload = np.array(values_dictionary["bytesOffload"])  # Replace with actual offload data
    
    fig, ax1 = plt.subplots(figsize=(14, 6))
    plt.subplots_adjust(left=0.09, right=0.87, top=0.9, bottom=0.1)
    # Plot Edge, Midgress, and Origin on the left y-axis
    line1, = ax1.plot(dates, edgeBitsPerSecond, label='Edge', color='green')
    line2, = ax1.plot(dates, midgressBitsPerSecond, label='Midgress', color='purple')
    line3, = ax1.plot(dates, originBitsPerSecond, label='Origin', color='orange')
    ax1.set_ylabel('Bits/sec')
    # ax1.legend(loc='upper left', bbox_to_anchor=(1.05, 1), borderaxespad=0.1)
    
    # Create a second y-axis for Offload
    ax2 = ax1.twinx()
    line4, = ax2.plot(dates, bytesOffload, label='Offload', color='blue')
    ax2.set_ylabel('Offload', labelpad=0)
    ax2.set_ylim(0, 100)
    # ax2.legend(loc='upper left', bbox_to_anchor=(1.05, 1), borderaxespad=0.1)

    # Add title and grid
    plt.title(f'{empresa}: Edge, Midgress, and Origin bits/sec with Offload')
    ax1.grid(True)

    # Combine legends from both y-axes
    lines = [line4, line1, line2, line3]
    labels = [line4.get_label(), line1.get_label(), line2.get_label(), line3.get_label()]

    # Display the combined legend
    fig.legend(lines, labels, loc='upper left', bbox_to_anchor=(0.9, 0.9), borderaxespad=1.2)

    tick_positions = np.arange(1, length, 2*24)  # Custom positions for ticks (every 2 days)
    tick_labels = [f'Jul {1 + (i * 2)}' for i in range(len(tick_positions))]
    
    ax1.set_xlim(min(dates), max(dates))
    ax1.set_ylim(bottom=0)
    ax1.set_xticks(tick_positions)
    ax1.set_xticklabels(tick_labels, rotation=0)  # Rotate for readability
    ax1.spines['bottom'].set_color('none')  # Remove the right border
    ax2.spines['bottom'].set_color('none')  # Remove the right border

    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f'{str(round(int(x)*si.A,2)).replace("A", "B")}/s'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f'{int(x)}%'))

     # Save the figure
    nombre_de_archivo = f"Grafica_Trafico_Por_Dia_{empresa}_{fecha_correcta_nombre}.png"
    file_path = os.path.join(subcarpeta_path, nombre_de_archivo)
    plt.savefig(file_path)
    plt.close(fig)
    return f"--{nombre_de_archivo} creado--"

def grafica_hits_al_origen_por_tipo_de_respuesta(empresa, client_secret, host, access_token, client_token, fechas, subcarpeta_path, fecha_correcta_nombre):
    baseurl = 'https://' + host + '/'  # this is the "host" value from your credentials file
    s = requests.Session()
    s.auth = EdgeGridAuth(
        client_token=client_token,
        client_secret=client_secret,
        access_token=access_token
    )
    version = "1"
    name = "traffic-by-timeandresponseclass"
    path = '/reporting-api/v1/reports/{}/versions/{}/report-data'.format(name, version)
    querystring = {
    "start": fechas[0],
    "end": fechas[1],
    "interval": "HOUR",
    "objectIds": "all",
    "metrics": "originHitsPerSecond", # Al menos una métrica es necesaria...
    "filters": "ca=cacheable",
    }
    result = s.get(urljoin(baseurl, path), params=querystring)
    print(f"Configuración (Gráfica de hits al origen por segundo y por tipo de respuesta): {empresa}")
    print(f"HTTPS clase de respuesta (Gráfica de hits al origen por segundo y por tipo de respuesta): {result.status_code}")
    response_json = result.json()
    data = response_json.get('data', [])
    length = len(data)
    values_dictionary = {
        "0xx" : [],
        "1xx" : [],
        "2xx" : [],
        "3xx" : [],
        "4xx" : [],
        "5xx" : []
    }
    for dict in data:
        mini_list = dict.get("data")
        for mini_dict in mini_list:
            values_dictionary[str(mini_dict.get("response_class"))].append(round(float(mini_dict.get('originHitsPerSecond')),4))
    
    if not values_dictionary["1xx"]:
        values_dictionary["1xx"] = [0] * length  
        
                      
    dates = np.linspace(1, length, length)  # Days of the month, create from 1 to length, length values.
    response_0xx = np.array(values_dictionary["0xx"])  
    response_1xx = np.array(values_dictionary["1xx"])  
    response_2xx = np.array(values_dictionary["2xx"])  
    response_3xx = np.array(values_dictionary["3xx"])  
    response_4xx = np.array(values_dictionary["4xx"])  
    response_5xx = np.array(values_dictionary["5xx"]) 

    fig, ax1 = plt.subplots(figsize=(14, 6))
    plt.subplots_adjust(left=0.09, right=0.87, top=0.9, bottom=0.1)
    # Error responses on the y-axis
    line1, = ax1.plot(dates, response_0xx, label='0xx', color='orange')
    line2, = ax1.plot(dates, response_1xx, label='1xx', color='blue')
    line3, = ax1.plot(dates, response_2xx, label='2xx', color='green')
    line1, = ax1.plot(dates, response_3xx, label='3xx', color='cyan')
    line2, = ax1.plot(dates, response_4xx, label='4xx', color='pink')
    line3, = ax1.plot(dates, response_5xx, label='5xx', color='red')
    ax1.set_ylabel('Hits/sec')
    ax1.legend(loc='upper left', bbox_to_anchor=(1.01, 1), borderaxespad=0.)
    
    # Add title and grid
    plt.title(f'{empresa}: Origin hits/sec by response class')
    ax1.grid(True)

    tick_positions = np.arange(1, length, 2*24)  # Custom positions for ticks (every 2 days)
    tick_labels = [f'Jul {1 + (i * 2)}' for i in range(len(tick_positions))]
    
    ax1.set_xlim(min(dates), max(dates))
    ax1.set_ylim(bottom=0)
    ax1.set_xticks(tick_positions)
    ax1.set_xticklabels(tick_labels, rotation=0)  # Rotate for readability
    ax1.spines['bottom'].set_color('none')  # Remove the bottom border

    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f'{int(x)}.00')) 

    nombre_de_archivo = f"Grafica_de_Hits_al_Origen_al_Tipo_de_respuesta_{empresa}_{fecha_correcta_nombre}.png"
    file_path = os.path.join(subcarpeta_path, nombre_de_archivo)
    plt.savefig(file_path)
    plt.close(fig)

    return f"--{nombre_de_archivo} creado--"

def tabla_hits_por_tipo(empresa, client_secret, host, access_token, client_token, fechas, subcarpeta_path, fecha_correcta_nombre, cpcode = "all"):
    
    def pretty_printer(row):
        new_row = [row[0]]
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
        return new_row

    def sort_file(file, column):
        df = pd.read_csv(file)
        sorted_df = df.sort_values(by=column, ascending=False)
        new_rows = [pretty_printer(row) for row in sorted_df.values]
        final_df = pd.DataFrame(new_rows, columns=sorted_df.columns)
        final_df.to_csv(file, index=False)
    
    if (cpcode == "all"):
        nombre_de_archivo = f"tabla_hits_por_tipo_{empresa}_{fecha_correcta_nombre}.csv"
        columnaCSV = 'Tipo de Respuesta'
    else:
        nombre_de_archivo = f"tabla_hits_por_tipo_{empresa}_{cpcode}_{fecha_correcta_nombre}.csv"
        columnaCSV = f"Tipo de Respuesta ({cpcode})"
    baseurl = 'https://' + host + '/'  # this is the "host" value from your credentials file
    s = requests.Session()
    s.auth = EdgeGridAuth(
        client_token=client_token,
        client_secret=client_secret,
        access_token=access_token
    )
    version = "1"
    name = "traffic-by-responseclass"
    path = '/reporting-api/v1/reports/{}/versions/{}/report-data'.format(name, version)
    querystring = {
            "start": fechas[0],
            "end": fechas[1],
            "objectIds": cpcode,
            "metrics": "",
            "filters": "ca=cacheable",
            }
    result = s.get(urljoin(baseurl, path), params=querystring)
    print(f"Configuración (Tabla hits por tipo de respuesta): {empresa}")
    print(f"HTTPS clase de respuesta (Tabla hits por tipo de respuesta): {result.status_code}")
    response_json = result.json()
    data = response_json.get('data')
    csv_ubicacion = os.path.join(subcarpeta_path, nombre_de_archivo)
    with open(csv_ubicacion, mode='w', newline='') as file:
        writer = csv.writer(file)
        header = [columnaCSV, 'Edge Hits', 'Edge Hits %', 'Origin Hits', 'Origin Hits %']
        writer.writerow(header)
        for tipo_de_respuesta in data:
            if tipo_de_respuesta:
                writer.writerow([tipo_de_respuesta.get("response_class"), tipo_de_respuesta.get('edgeHits'), tipo_de_respuesta.get('edgeHitsPercent'), tipo_de_respuesta.get('originHits'), tipo_de_respuesta.get('originHitsPercent')])     
    
    sort_file(csv_ubicacion, "Edge Hits")
    return f"--{nombre_de_archivo} creado--"

def tabla_hits_por_url(empresa, client_secret, host, access_token, client_token, fechas, subcarpeta_path, fecha_correcta_nombre):
    def pretty_printer(row):
        new_row = [row[0]]
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
        return new_row

    def sort_file(file, column):
        df = pd.read_csv(file)
        sorted_df = df.sort_values(by=column, ascending=False)
        new_rows = [pretty_printer(row) for row in sorted_df.values]
        final_df = pd.DataFrame(new_rows, columns=sorted_df.columns)
        final_df = final_df.head(10)
        final_df.to_csv(file, index=False)
    
    baseurl = 'https://' + host + '/'  # this is the "host" value from your credentials file
    s = requests.Session()
    s.auth = EdgeGridAuth(
        client_token=client_token,
        client_secret=client_secret,
        access_token=access_token
    )
    version = "1"
    name = "urlhits-by-url"
    path = '/reporting-api/v1/reports/{}/versions/{}/report-data'.format(name, version)
    querystring = {
            "start": "2024-06-01T00:00:00Z",
            "end": "2024-07-01T00:00:00Z",
            "objectIds": "all",
            "metrics": "",
            "filters": "",
            }
    result = s.get(urljoin(baseurl, path), params=querystring)
    print(f"Configuración (Tabla hits por URL): {empresa}")
    print(f"HTTPS clase de respuesta (Tabla hits por URL): {result.status_code}")
    response_json = result.json()
    # print(f"Response JSON: {json.dumps(response_json, indent=2)}")
    data = response_json.get('data')
    nombre_de_archivo = f"tabla_hits_por_URL_{empresa}_{fecha_correcta_nombre}.csv"
    csv_ubicacion = os.path.join(subcarpeta_path, nombre_de_archivo)
    with open(csv_ubicacion, mode='w', newline='') as file:
        writer = csv.writer(file)
        header = ['URL', 'Edge Hits', 'Origin Hits', 'Offload']
        writer.writerow(header)
        for response in data:
            if response:
                writer.writerow([response.get("hostname.url"), response.get('allEdgeHits'), response.get('allOriginHits'), response.get('allHitsOffload')])     
    sort_file(csv_ubicacion, "Edge Hits")
    return f"--{nombre_de_archivo} creado--"


def main():
    return

if __name__ == "__main__":
    main()