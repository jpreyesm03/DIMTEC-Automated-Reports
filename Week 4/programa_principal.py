from funciones_cortas import seleccionar_archivo # type: ignore
from funciones_cortas import seleccionar_fecha # type: ignore
from funciones_cortas import seleccionar_empresas # type: ignore
from funciones_cortas import seleccionar_reportes # type: ignore
from funciones_cortas import generar_reportes # type: ignore
from funciones_cortas import automatico_o_manual # type: ignore
from funciones_cortas import reportes_generales # type: ignore

introduccion = "¡Hola! Puedes generar todos los reportes desde este programa. La idea es que solamente utilice números a lo largo del programa."

def main():
    print(introduccion)
    manual = automatico_o_manual()
    archivo = seleccionar_archivo()
    if (manual):
        empresas_y_credenciales = seleccionar_empresas(archivo)
        multiples_fechas = multiples_fechas()
        if (not multiples_fechas):
            lista_de_fechas = seleccionar_fecha()
        else:
            lista_de_fechas = []

        multiples_reportes = multiples_reportes()
        if (not multiples_reportes):
            lista_de_reportes = seleccionar_reportes()
        else:
            lista_de_reportes = {}
        counter = 0

        multiples_reportes = multiples_reportes()
        if (not multiples_reportes):
            lista_de_reportes = seleccionar_reportes()
        else:
            lista_de_reportes = {}
        counter = 0

        for empresa, credenciales in empresas_y_credenciales.items():
            if (multiples_fechas):
                lista_de_fechas.append(seleccionar_fecha())
            if (multiples_fechas):
                lista_de_reportes.append(seleccionar_reportes(archivo, lista_de_fechas, counter, empresa)) # if type(lista_de_reportes[0]) is list
            generar_reportes(empresa, credenciales[0], credenciales[1], credenciales[2], credenciales[3], lista_de_fechas, lista_de_reportes, counter)
            counter += 1
        print("La generación de reportes ha concluido. Si algún reporte faltase, probablemente tenía el archivo abierto.")
    else:
        fecha = seleccionar_fecha()
        reportes_generales()
    print("La generación de reportes ha concluido. Si algún reporte faltase, probablemente tenía el archivo abierto.")
# Sólamente correrá el programa si se solicita correr directamente.
if __name__ == "__main__":
    main()