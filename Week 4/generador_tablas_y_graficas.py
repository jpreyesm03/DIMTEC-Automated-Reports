import configparser
import csv
import requests # type: ignore
from akamai.edgegrid import EdgeGridAuth # type: ignore
from urllib.parse import urljoin
import forallpeople as si # type: ignore
import os
import pandas as pd # type: ignore
from datetime import datetime
import json

def formatear_fechas(fecha1, fecha2):
    # Diccionario para traducir los meses al español
    meses_es = {
        1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
        7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
    }
    # Convertir los textos a objetos datetime
    dt1 = datetime.strptime(fecha1, "%Y-%m-%dT%H:%M:%SZ")
    dt2 = datetime.strptime(fecha2, "%Y-%m-%dT%H:%M:%SZ")
    # Formatear las fechas
    fecha1_formateada = f"{dt1.day:02d}{meses_es[dt1.month]}{str(dt1.year)[-2:]}"
    fecha2_formateada = f"{dt2.day:02d}{meses_es[dt2.month]}{str(dt2.year)[-2:]}"
    # Retornar la cadena con el formato requerido
    return f"{fecha1_formateada}-{fecha2_formateada}"

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
    nombre_de_archivo = f"tabla_de_trafico_por_cpcode_{empresa}_{formatear_fechas(fechas[0], fechas[1])}.csv"
    
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
    nombre_de_archivo = f"tabla_trafico_total_y_estaditicas_{empresa}_{formatear_fechas(fechas[0], fechas[1])}.csv"
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
        nombre_de_archivo = f"tabla_hits_por_tipo_{empresa}_{formatear_fechas(fechas[0], fechas[1])}.csv"
        columnaCSV = 'Tipo de Respuesta'
    else:
        nombre_de_archivo = f"tabla_hits_por_tipo_{empresa}_{cpcode}_{formatear_fechas(fechas[0], fechas[1])}.csv"
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

def tabla_hits_por_url(empresa, client_secret, host, access_token, client_token, fechas, subcarpeta_path):
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
    
    print(f"Empresa: {empresa}")
    print(f"Client Secret: {client_secret}")
    print(f"Host: {host}")
    print(f"Access Token: {access_token}")
    print(f"Client Token: {client_token}")
    print(f"Fecha inicial: {fechas[0]}")
    print(f"Fecha final: {fechas[1]}")
    print(f"Subcarpeta: {subcarpeta_path}")


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
    nombre_de_archivo = f"tabla_hits_por_URL_{empresa}_{formatear_fechas(fechas[0], fechas[1])}.csv"
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
    file_path = r"C:\Users\jprey\OneDrive\Escritorio\JP\DIMTEC\Week 4\Reportes_por_Empresa_20_08_2024[17]\Reporte_de_eltiempo_12Jun24-05Jul24"
    tabla_hits_por_url("eltiempo", "ywILUu15mgi77NoDP/jwYQ+V0WN4l7OJKyrnQlcrYS4=", "akab-prsecj6xfjiyu53m-s4yf4arinrkdj2bj.luna.akamaiapis.net", "akab-nhx72hdajghp4bt5-sr5v6hirwta4lb3p",  "akab-wlno2a5rlzf2ykl5-4qx3tjtupr5nkj25", ["2024-06-01T00:00:00Z", "2024-07-01T00:00:00Z"], file_path)
    main()