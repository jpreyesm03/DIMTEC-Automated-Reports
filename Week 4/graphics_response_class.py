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
import numpy as np # type: ignore
import matplotlib.pyplot as plt # type: ignore
from matplotlib.ticker import FuncFormatter # type: ignore
    


def pretty_printer(final_name, off, ebt, mbt, obt):
    list_result = [final_name, off]
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
    name = "traffic-by-timeandresponseclass"
    path = '/reporting-api/v1/reports/{}/versions/{}/report-data'.format(name, version)
    querystring = {
    "start": "2024-07-01T05:00:00Z",
    "end": "2024-07-03T03:00:00Z",
    "interval": "HOUR",
    "objectIds": "all",
    "metrics": "originHitsPerSecond", # Al menos una métrica es necesaria...
    "filters": "ca=cacheable",
    }
    # result = s.get(urljoin(baseurl, '/contract-api/v1/contracts/identifiers'))
    # result = s.get(urljoin(baseurl, '/cprg/v1/cpcodes'))
    result = s.get(urljoin(baseurl, path), params=querystring)
    print(f"Configuration: {section}")
    print(f"Status Code: {result.status_code}")
    mes = find_month(querystring.get("start"))
    response_json = result.json()
    print(f"Response JSON: {json.dumps(response_json, indent=2)}")
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
            # print("At " + dict.get("startdatetime") + ", the response class " + mini_dict.get("response_class") + ": " + mini_dict.get("originHitsPerSecond"))
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
    plt.title(f'{section}: Origin hits/sec by response class')
    ax1.grid(True)

    tick_positions = np.arange(1, length, 2*24)  # Custom positions for ticks (every 2 days)
    tick_labels = [f'Jul {1 + (i * 2)}' for i in range(len(tick_positions))]
    
    ax1.set_xlim(min(dates), max(dates))
    ax1.set_ylim(bottom=0)
    ax1.set_xticks(tick_positions)
    ax1.set_xticklabels(tick_labels, rotation=0)  # Rotate for readability
    ax1.spines['bottom'].set_color('none')  # Remove the bottom border

    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f'{int(x)}.00'))

    # Show the plot
    plt.show()
    print("\n"*4 + "-"*10 + section + "-"*10 + "\n"*4)
    break
    
    
    
