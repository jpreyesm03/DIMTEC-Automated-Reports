import configparser
import requests # type: ignore
from akamai.edgegrid import EdgeGridAuth # type: ignore
from urllib.parse import urljoin
import forallpeople as si # type: ignore

def extraer_cpcodes(empresa, client_secret, host, access_token, client_token, fechas):
    lista_de_cpcodes_y_edge_bytes = [[],[]]
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
        lista_de_cpcodes_y_edge_bytes[0].append(name + " (" + cpcode + ")")
        lista_de_cpcodes_y_edge_bytes[1].append(credential.get('edgeBytes'))
        print(name + " (" + cpcode + ")" + " has Edge Bytes: " + str(round(float(credential.get('edgeBytes'))*si.A,2)).replace("A", "B"))
    # Combine the two lists into a list of tuples
    combined = list(zip(lista_de_cpcodes_y_edge_bytes[0], lista_de_cpcodes_y_edge_bytes[1]))

    # Sort the combined list based on the second element of each tuple in descending order
    sorted_combined = sorted(combined, key=lambda x: x[1], reverse=True)

    # Unzip the sorted list back into two lists
    sorted_names, sorted_values = zip(*sorted_combined)

    # Convert back to list
    sorted_names = list(sorted_names)

    return sorted_names



def tabla_de_trafico_por_cpcode(empresa, client_secret, host, access_token, client_token, fechas):
    return

def tabla_trafico_total_y_estadisticas(empresa, client_secret, host, access_token, client_token, fechas):
    return

def grafica_trafico_por_dia(empresa, client_secret, host, access_token, client_token, fechas):
    return

def grafica_hits_al_origen_por_tipo_de_respuesta(empresa, client_secret, host, access_token, client_token, fechas):
    return

def tabla_hits_por_tipo(empresa, client_secret, host, access_token, client_token, fechas, lista_de_cpcodes = "all"):
    return

def hits_por_url(empresa, client_secret, host, access_token, client_token, fechas):
    return




def main():
    return

if __name__ == "__main__":
    main()