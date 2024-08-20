import configparser
import requests # type: ignore
from akamai.edgegrid import EdgeGridAuth # type: ignore
from urllib.parse import urljoin
import csv
# import forallpeople as si # type: ignore
import pandas as pd # type: ignore
import json
from datetime import datetime
import locale
import os

def remove_spaces(text):
    new_text = ""
    for character in text:
        if character != ' ':
            new_text += character
    return new_text


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

def file_closed(file_path):
    try:
        # Try opening the file in write mode
        with open(file_path, mode='a', newline='') as file:
            pass  # If successful, the file is not open elsewhere
        return True
    except PermissionError:
        print(f"Error: The file '{file_path}' is already open. Please close it before running the script.")
        return False

def main(objectIDs = "all"):
    # Parse the .edgerc file
    config = configparser.ConfigParser()
    config.read(r'C:\Users\jprey\OneDrive\Escritorio\JP\DIMTEC\Week 2\El Tiempo\.edgerc')  # replace with the path to your .edgerc file if it's not in the same directory

    # Iterate over each section in the config file
    for section in config.sections():
        querystring = {
            "start": "2024-06-01T06:00:00Z",
            "end": "2024-07-01T06:00:00Z",
            "objectIds": objectIDs,
            "metrics": "",
            "filters": "ca=cacheable",
            }
        mes = find_month(querystring.get("start"))

        if (querystring.get("objectIds") not in ["", "all"]):
            response_class = 'Response Class (' + querystring.get("objectIds") + ")"
            report_section = section + "_(" + remove_spaces(querystring.get("objectIds")) + ")"
        else:
            response_class = 'Response Class'
            report_section = section

        csv_file = f'report_{report_section}_{mes}_traffic-by-response-class.csv'
        if (file_closed(csv_file)):
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
            name = "traffic-by-responseclass"
            path = '/reporting-api/v1/reports/{}/versions/{}/report-data'.format(name, version)
            result = s.get(urljoin(baseurl, path), params=querystring)
            print(f"Configuration: {section}")
            print(f"Status Code: {result.status_code}")
            response_json = result.json()
            data = response_json.get('data')

            with open(csv_file, mode='w', newline='') as file:
                writer = csv.writer(file)
                header = [response_class, 'Edge Hits', 'Edge Hits %', 'Origin Hits', 'Origin Hits %']
                writer.writerow(header)
                for response in data:
                    if response:
                        writer.writerow([response.get("response_class"), response.get('edgeHits'), response.get('edgeHitsPercent'), response.get('originHits'), response.get('originHitsPercent')])     
            sort_file(csv_file, "Edge Hits")
            
            
        else:
            # Handle the case where the file is open!
            print("-"*15 + section + "-"*15 + "\n"*8)
    current_file_path = __file__
    file_name = os.path.basename(current_file_path)
    print(f"CSV file(s) created. Located in the same directory than {file_name}.")

if __name__ == "__main__":
    main()