import configparser
import requests # type: ignore
from akamai.edgegrid import EdgeGridAuth # type: ignore
from urllib.parse import urljoin
import csv
import json

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
    # result = s.get(urljoin(baseurl, '/contract-api/v1/contracts/identifiers'))
    result = s.get(urljoin(baseurl, '/cprg/v1/cpcodes/83330'))
    # result = s.get(urljoin(baseurl, path), params=querystring)
    # print(f"Configuration: {section}")
    # print(f"Status Code: {result.status_code}")
    print(result.status_code)
    response_json = result.json()
    print(f"Response JSON: {json.dumps(response_json, indent=2)}")
    print()
    print()
    print()
    print()
    print()
    print()
    print()
    print()
    print()
    print()
    print("Finish printing:", {section})
    print()
    print()
    print()
    print()
    print()
    print()
    print()
    print()
    print()
    print("--------------------------------")

    


    
