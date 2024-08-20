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
    "start": "2024-05-23T05:00:00Z",
    "end": "2024-08-18T03:00:00Z",
    "interval": "HOUR",
    "objectIds": "all",
    "metrics": "originHitsPerSecond", # Al menos una métrica es necesaria...
    "filters": "ca=cacheable",
    }
    result = s.get(urljoin(baseurl, path), params=querystring)
    print(f"Configuration: {section}")
    print(f"Status Code: {result.status_code}")
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
    
    
    
