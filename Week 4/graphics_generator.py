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
    name = "bytes-by-time"
    path = '/reporting-api/v1/reports/{}/versions/{}/report-data'.format(name, version)
    querystring = {
    "start": "2024-07-01T00:00:00Z",
    "end": "2024-08-01T00:00:00Z",
    "interval": "HOUR",
    "objectIds": "all",
    "metrics": "bytesOffload, bytesOffloadAvg, bytesOffloadMax, bytesOffloadMin, edgeBitsPerSecond, edgeBitsPerSecondMax, edgeBitsPerSecondMin, edgeBytesTotal, midgressBitsPerSecond, midgressBitsPerSecondMax, midgressBitsPerSecondMin, midgressBytesTotal, originBitsPerSecond, originBitsPerSecondMax, originBitsPerSecondMin, originBytesTotal", # Al menos una métrica es necesaria...
    "filters": "ca=cacheable",
    }
    # result = s.get(urljoin(baseurl, '/contract-api/v1/contracts/identifiers'))
    # result = s.get(urljoin(baseurl, '/cprg/v1/cpcodes'))
    result = s.get(urljoin(baseurl, path), params=querystring)
    print(f"Configuration: {section}")
    print(f"Status Code: {result.status_code}")
    mes = find_month(querystring.get("start"))
    response_json = result.json()
    # print(f"Response JSON: {json.dumps(response_json, indent=2)}")
    data = response_json.get('data', [])
    summary_stats = response_json.get('summaryStatistics', [])
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
    plt.title(f'{section}: Edge, Midgress, and Origin bits/sec with Offload')
    ax1.grid(True)

    # Combine legends from both y-axes
    lines = [line4, line1, line2, line3]
    labels = [line4.get_label(), line1.get_label(), line2.get_label(), line3.get_label()]

    # Display the combined legend
    fig.legend(lines, labels, loc='upper left', bbox_to_anchor=(0.9, 0.9), borderaxespad=1.2)

    tick_positions = np.arange(1, length, 2*24)  # Custom positions for ticks (every 5 days)
    tick_labels = [f'Jul 1' if t == 1 else f'Jul {int(t//24)}' for t in tick_positions]  # Custom labels
    
    ax1.set_xlim(min(dates), max(dates))
    ax1.set_ylim(bottom=0)
    ax1.set_xticks(tick_positions)
    ax1.set_xticklabels(tick_labels, rotation=0)  # Rotate for readability
    ax1.spines['bottom'].set_color('none')  # Remove the right border
    ax2.spines['bottom'].set_color('none')  # Remove the right border

    ax1.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f'{str(round(int(x)*si.A,2)).replace("A", "B")}/s'))
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f'{int(x)}%'))

    # Show the plot
    plt.show()
    print("\n"*4 + "-"*10 + section + "-"*10 + "\n"*4)
    
    
