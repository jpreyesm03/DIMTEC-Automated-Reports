import configparser
import csv
import requests # type: ignore
from akamai.edgegrid import EdgeGridAuth # type: ignore
from urllib.parse import urljoin
import forallpeople as si # type: ignore
import os
import pandas as pd # type: ignore


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



def tabla_de_trafico_por_cpcode(empresa, client_secret, host, access_token, client_token, fechas, subcarpeta_path):
    
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
    nombre_de_archivo = f"tabla_de_trafico_por_cpcode_{empresa}.csv"
    
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

def tabla_trafico_total_y_estadisticas(empresa, client_secret, host, access_token, client_token, fechas, subcarpeta_path):
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
    nombre_de_archivo = f"tabla_trafico_total_y_estaditicas_{empresa}.csv"
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

def grafica_trafico_por_dia(empresa, client_secret, host, access_token, client_token, fechas, subcarpeta_path):
    return 

def grafica_hits_al_origen_por_tipo_de_respuesta(empresa, client_secret, host, access_token, client_token, fechas, subcarpeta_path):
    return

def tabla_hits_por_tipo(empresa, client_secret, host, access_token, client_token, fechas, subcarpeta_path, cpcode = "all"):
    if (cpcode == "all"):
        nombre_de_archivo = f"tabla_hits_por_tipo_{empresa}.csv"
    else:
        nombre_de_archivo = f"tabla_hits_por_tipo_{empresa}_{cpcode}.csv"
    


    
    return f"--{nombre_de_archivo} creado--"

def tabla_hits_por_url(empresa, client_secret, host, access_token, client_token, fechas, subcarpeta_path):
    return




def main():
    return

if __name__ == "__main__":
    main()