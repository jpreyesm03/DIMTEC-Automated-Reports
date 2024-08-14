import configparser
import requests # type: ignore
from akamai.edgegrid import EdgeGridAuth # type: ignore
from urllib.parse import urljoin
import csv
import forallpeople as si # type: ignore
import pandas as pd # type: ignore
import json
from datetime import datetime
import locale


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

def find_month(text_month):
    # Store the current locale
    current_locale = locale.getlocale(locale.LC_TIME)
    
    try:
        # Set the locale to Spanish
        locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
        # Parse the date string into a datetime object
        date_obj = datetime.strptime(text_month, "%Y-%m-%dT%H:%M:%SZ")
        # Extract the month name in Spanish and convert to lowercase
        month_name = date_obj.strftime("%B").lower()
        # Extract the last two digits of the year
        year = date_obj.strftime("%y")
        # Combine month name and year
        month_year = f"{month_name}{year}"
    finally:
        # Restore the previous locale
        locale.setlocale(locale.LC_TIME, current_locale)
    
    return month_year


# Parse the .edgerc file
config = configparser.ConfigParser()
config.read(r'C:\Users\jprey\OneDrive\Escritorio\JP\DIMTEC\Week 2\El Tiempo\.edgerc')  # replace with the path to your .edgerc file if it's not in the same directory

# Iterate over each section in the config file
for section in config.sections():
    client_secret = config[section]['client_secret']
    host = config[section]['host']
    access_token = config[section]['access_token']
    client_token = config[section]['client_token']
    

    baseurl = 'https://' + host + '/'  # this is the "host" value from your credentials file
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
    "metrics": "bytesOffload, edgeBytes, midgressBytes, originBytes", # Al menos una métrica es necesaria...
    "filters": "ca=cacheable",
    }
    mes = find_month(querystring.get("start"))
    # result = s.get(urljoin(baseurl, '/contract-api/v1/contracts/identifiers'))
    # result = s.get(urljoin(baseurl, '/cprg/v1/cpcodes'))
    result = s.get(urljoin(baseurl, path), params=querystring)
    print(f"Configuration: {section}")
    print(f"Status Code: {result.status_code}")
    
    response_json = result.json()
    print(f"Response JSON: {json.dumps(response_json, indent=2)}")
    data = response_json.get('data')
    print(data)
    # Define the CSV file name
    csv_file = f'report_{section}_{mes}_bytes_by_cpcode.csv'
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        header = ['CpCodeId', 'Offload Percentage', 'Edge Bytes', 'Midgress Bytes', 'Origin Bytes', 'sortingColumn']
        writer.writerow(header)
        for credential in data:
            print(credential)
            cpcode = credential.get('cpcode')
            specific_cpcode = s.get(urljoin(baseurl, '/cprg/v1/cpcodes/'+cpcode)).json()
            name = specific_cpcode.get('cpcodeName')
            final_name = name + " (" + cpcode + ")"
            print(cpcode, " JP: ", credential.get('bytesOffload'))
            # Write the values
            if data:
                writer.writerow(pretty_printer(final_name, credential.get('bytesOffload'), credential.get('edgeBytes'), credential.get('midgressBytes'), credential.get('originBytes')))     
        print(f"Data saved to {csv_file}")
        print("\n" + "-"*40 + "\n")
    sort_file(csv_file, "sortingColumn")
