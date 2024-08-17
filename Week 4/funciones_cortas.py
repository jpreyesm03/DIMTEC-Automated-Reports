import tkinter as tk
from tkinter import filedialog
import re
import configparser
from datetime import datetime

def seleccionar_archivo():
    # Parámetros de la librería
    root = tk.Tk()
    root.withdraw()

    # Abrir ventana preguntando por archivo:
    direccion_de_archivo = filedialog.askopenfilename(
        title="Escoja Archivo (.edgerc):",
        filetypes=(("All files", "*.*"), ("Config files", "*.edgerc"))
    )

    # Devolver dirección del archivo
    print_next(direccion_de_archivo)
    return direccion_de_archivo

def seleccionar_mes():
    mes_actual = datetime.now().month
    meses_nombres = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    numeros_de_mes_mencionados = []
    for i in range(2,-1,-1):
        mes_nombre = meses_nombres[(mes_actual-1) - i]
        mes_numero = meses_nombres.index(mes_nombre) + 1
        numeros_de_mes_mencionados.append(mes_numero)
        if (i == 0):
            print(str(mes_numero) + ". " + mes_nombre + " (considere que la información no tomara en cuenta todo el mes)")
        else:
            print(str(mes_numero) + ". " + mes_nombre)
    print("")
    try:
        mes = int(input("AKAMAI retiene solo 92 días. Seleccione mes (número): "))
        if (mes not in numeros_de_mes_mencionados):
            raise ValueError("AKAMAI retiene solo 92 días. No puede acceder en su totalidad al mes que proporcionó.")      
    except:
        print("\n"*2 + "-"*4 + "Solamente proporcione el número, sin punto. Vuelva a correr el programa" + "-"*4 + "\n"*2)
    print_next(str(meses_nombres[mes-1]))
    return meses_nombres[mes-1]

def seleccionar_empresas(archivo):
    empresas = extraer_todas_las_empresas(archivo)
    empresas_copia = empresas
    empresas_escogidas = []
    first_time = True
    imprimir_empresas(empresas, first_time)
    eleccion = int(input("Escoja qué empresa le interesa (número): "))
    if (eleccion == 0):
        empresas_escogidas = empresas
    else:
        empresas_escogidas = [empresas[eleccion-1]]
        first_time = False
        while (eleccion != -1):
            try:
                empresas_copia.pop(eleccion)
            except:
                empresas_escogidas = empresas
                break
            imprimir_empresas(empresas_copia, first_time)
            eleccion = int(input("Escoja qué empresa le interesa (número): "))
            empresas_escogidas.append(empresas[eleccion-1])
    if ("0. Todas las empresas." in empresas_escogidas or len(empresas_escogidas) >= len(empresas)):
        print_next("Ha seleccionado todas las empresas.")
        empresas_escogidas = empresas
    else:
        print("Has seleccionado: ", end="")
        for emp in empresas_escogidas:
            print(emp, end=', ')
        print_next("----------------")
    return obtener_credenciales(archivo, empresas_escogidas)
    
def seleccionar_reportes():
    return

def seleccionar_cpcodes():
    return

def generar_reportes():
    return

def automatico_o_manual():
    print("\n" + """
          Los reportes pueden producirse de manera general (automática)
           para cada empresa en el archivo seleccionado. También es 
          posible escoger que tablas/gráficas desea para el reporte de 
           cada empresa. """ + "\n")
    print("1. Escoger manualmente el contenido de cada reporte por empresa")
    print("2. Usar un formato general de reporte por empresa.")
    manual = int(input("Selecction la opción que desee (número): "))
    if (manual == 1):
        return True
    else:
        return False

def reportes_generales(archivo, fecha):
    return

def extraer_todas_las_empresas(file_path):
    sections = []
    with open(file_path, 'r') as file:
        content = file.read()
        # Regular expression to find section headers
        matches = re.findall(r'\[([^\]]+)\]', content)
        sections.extend(matches)
    return sections

def imprimir_empresas(empresas, first_time):
    if (first_time):
        print("0. Todas las empresas.")
    else:
        print("-1. Ya seleccione aquellas que me interesan.")
        print("0. Todas las empresas")
    for i in range(len(empresas)):
        print(str(i+1) + ". " + empresas[i])

def print_next(text):
    print("\n"*1 + "-"*4 + text + "-"*4 + "\n"*1)

def obtener_credenciales(archivo, empresas):
    diccionario_de_empresas = {}
    config = configparser.ConfigParser()
    config.read(archivo)
    for section in config.sections():
        if section in empresas:
            diccionario_de_empresas[section] = [config[section]['client_secret'], config[section]['host'], config[section]['access_token'], config[section]['client_token']] 
    return diccionario_de_empresas

def seleccionar_fecha():
    print("Desea seleccionar un mes para el reporte, o quiere consultar el consumo entre dos fechas especificas:")
    print("1. Seleccionar un mes.")
    print("2. Seleccionar dos fechas específicas")
    respuesta = int(input("Seleccione una opción (número): "))
    if (respuesta == 1):
        seleccionar_mes()
    else:
        print("AKAMAI solo tiene retención de 92 días.")
        año_inicio = int(input("El año de la primer fecha (yyyy): "))
        mes_inicio = int(input("El año de la primer fecha (mm): "))
        dia_inicio = int(input("El año de la primer fecha (dd): "))
        hora_inicio = input("El año de la primer fecha (hh:mm en formato 24h): ")

        
    

def main():
    print("Este programa es una librería de funciones que se usa en programa_principal.py")


# Sólamente correrá el programa si se solicita correr directamente.
if __name__ == "__main__":
    main()