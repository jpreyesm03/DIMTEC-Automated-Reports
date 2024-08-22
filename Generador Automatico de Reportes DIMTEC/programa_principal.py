from funciones_cortas import seleccionar_archivo # type: ignore
from funciones_cortas import seleccionar_fecha # type: ignore
from funciones_cortas import seleccionar_empresas # type: ignore
from funciones_cortas import seleccionar_reportes # type: ignore
from funciones_cortas import generar_reportes # type: ignore
from funciones_cortas import automatico_o_manual # type: ignore
from funciones_cortas import reportes_generales # type: ignore
from funciones_cortas import multiples_fechas # type: ignore
from funciones_cortas import reportes_distintos # type: ignore
from funciones_cortas import crear_carpeta # type: ignore
from funciones_cortas import introduccion # type: ignore




def main():
    print(introduccion)
    es_manual = automatico_o_manual() # En base a la respuesta en la consola, se determina si los reportes serán generador manualmente o no.
    archivo = seleccionar_archivo() # GUI para abrir archivo
    carpeta = crear_carpeta() # Crea carpeta utilizando el día de hoy

    if (es_manual):
        empresas_y_credenciales = seleccionar_empresas(archivo) # De todas las empresas en el archivo, el usuario selecciona algunas.

        son_multiples_fechas = multiples_fechas() # Una fecha para todos los reportes, o una fecha distinta para cada empresa.
        if (not son_multiples_fechas):
            fechas = seleccionar_fecha() # Selecciona la única fecha

        son_reportes_distintos = reportes_distintos() # Un mismo formato para todos los reportes, o un formato distinto por empresa.
        if (not son_reportes_distintos):
            lista_de_reportes = seleccionar_reportes() # Un mismo formato para todos los reportes

        contador = 0 # Para determinar para cuántas empresas todavía hay que generar reportes
        for empresa, credenciales in empresas_y_credenciales.items(): # Por empresa seleccionada
            if (son_multiples_fechas):
                fechas = seleccionar_fecha(texto_empresa = empresa)
            if (son_reportes_distintos):
                lista_de_reportes = seleccionar_reportes(empresa)
            # En base a la fecha y a los reportes elegidos, se generan los reportes.
            generar_reportes(empresa, credenciales[0], credenciales[1], credenciales[2], credenciales[3], fechas, lista_de_reportes, carpeta)
            
            print("\n"*4 + "-"*6 + f"Reportes de {empresa} terminados" + "-"*6 + "\n"*4)
            print("Todavía hay que generar reportes para " + str(len(empresas_y_credenciales) - 1 - contador) + " empresa(s) más." + "\n")
            contador += 1

    else:
        fecha = seleccionar_fecha()
        # En base a la fecha, los reportes se generarán siguiendo un formato preestablecido.
        reportes_generales(archivo, fecha, carpeta)
    print("La generación de reportes ha concluido. Si algún reporte faltase, probablemente tenía el archivo abierto.")

# Sólamente correrá el programa si se solicita correr directamente.
if __name__ == "__main__":
    main()