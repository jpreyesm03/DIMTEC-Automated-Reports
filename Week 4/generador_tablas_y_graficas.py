import configparser
import requests # type: ignore
from akamai.edgegrid import EdgeGridAuth # type: ignore
from urllib.parse import urljoin
import forallpeople as si # type: ignore


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
    return

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
    "start": "2024-07-01T00:00:00Z",
    "end": "2024-08-01T00:00:00Z",
    "interval": "FIVE_MINUTES",
    "objectIds": "all",
    "metrics": "bytesOffload, bytesOffloadAvg, bytesOffloadMax, bytesOffloadMin, edgeBitsPerSecond, edgeBitsPerSecondMax, edgeBitsPerSecondMin, edgeBytesTotal, midgressBitsPerSecond, midgressBitsPerSecondMax, midgressBitsPerSecondMin, midgressBytesTotal, originBitsPerSecond, originBitsPerSecondMax, originBitsPerSecondMin, originBytesTotal", # Al menos una métrica es necesaria...
    "filters": "ca=cacheable",
    }
    result = s.get(urljoin(baseurl, path), params=querystring)
    print(f"Configuration: {section}")
    print(f"Status Code: {result.status_code}")
    mes = find_month(querystring.get("start"))
    response_json = result.json()
    # print(f"Response JSON: {json.dumps(response_json, indent=2)}")
    summary_stats = response_json.get('summaryStatistics', [])
    columnas = ["", "Offload", "Edge", "Midgress", "Origin"]
    total = ["Total", f"{float(summary_stats.get("bytesOffloadAvg").get("value")):.2f} %", f"{str(round(int(float(summary_stats.get("edgeBytesTotal").get("value")))*si.A,2)).replace("A", "B")}", f"{str(round(int(float(summary_stats.get("midgressBytesTotal").get("value")))*si.A,2)).replace("A", "B")}/s", f"{str(round(int(float(summary_stats.get("originBytesTotal").get("value")))*si.A,2)).replace("A", "B")}/s"]
    minimos = ["Mínimo", f"{float(summary_stats.get("bytesOffloadMin").get("value")):.2f} %", f"{str(round(int(float(summary_stats.get("edgeBitsPerSecondMin").get("value")))*si.A,2)).replace("A", "B")}/s", f"{str(round(int(float(summary_stats.get("midgressBitsPerSecondMin").get("value")))*si.A,2)).replace("A", "B")}/s", f"{str(round(int(float(summary_stats.get("originBitsPerSecondMin").get("value")))*si.A,2)).replace("A", "B")}/s"]
    maximos = ["Máximo", f"{float(summary_stats.get("bytesOffloadMax").get("value")):.2f} %", f"{str(round(int(float(summary_stats.get("edgeBitsPerSecondMax").get("value")))*si.A,2)).replace("A", "B")}/s", f"{str(round(int(float(summary_stats.get("midgressBitsPerSecondMax").get("value")))*si.A,2)).replace("A", "B")}/s", f"{str(round(int(float(summary_stats.get("originBitsPerSecondMax").get("value")))*si.A,2)).replace("A", "B")}/s"]
    # Define the file name as 'grafica_JP'
    file_name = "grafica_JP.csv"
    
    # Combine the file path and file name
    csv_ubicacion = os.path.join(subcarpeta, file_name)
    
    
    # Write the CSV file
    with open(csv_ubicacion, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(columnas)
        writer.writerow(total)
        writer.writerow(minimos)
        writer.writerow(maximos)
    return

def grafica_trafico_por_dia(empresa, client_secret, host, access_token, client_token, fechas, subcarpeta_path):
    return

def grafica_hits_al_origen_por_tipo_de_respuesta(empresa, client_secret, host, access_token, client_token, fechas, subcarpeta_path):
    return

def tabla_hits_por_tipo(empresa, client_secret, host, access_token, client_token, fechas, subcarpeta_path, cpcode = "all"):
    return

def hits_por_url(empresa, client_secret, host, access_token, client_token, fechas, subcarpeta_path):
    return




def main():
    return

if __name__ == "__main__":
    main()