from funciones_cortas import seleccionar_archivo # type: ignore
from funciones_cortas import seleccionar_fecha # type: ignore
from funciones_cortas import seleccionar_empresas # type: ignore
from funciones_cortas import seleccionar_reportes # type: ignore
from funciones_cortas import generar_reportes # type: ignore
from funciones_cortas import automatico_o_manual # type: ignore
from funciones_cortas import reportes_generales # type: ignore
from funciones_cortas import multiples_fechas # type: ignore
from funciones_cortas import reportes_distintos # type: ignore

introduccion = "¡Hola! Puedes generar todos los reportes desde este programa. La idea es que solamente utilice números a lo largo del programa."

def main():
    print(introduccion)
    es_manual = automatico_o_manual()
    archivo = seleccionar_archivo()
    if (es_manual):
        empresas_y_credenciales = seleccionar_empresas(archivo)
        son_multiples_fechas = multiples_fechas()
        if (not son_multiples_fechas):
            fechas = seleccionar_fecha()
        son_reportes_distintos = reportes_distintos()
        if (not son_reportes_distintos):
            lista_de_reportes = seleccionar_reportes()
        contador = 0

        for empresa, credenciales in empresas_y_credenciales.items():
            if (son_multiples_fechas):
                fechas = seleccionar_fecha()
            if (son_reportes_distintos):
                lista_de_reportes = seleccionar_reportes(empresa)
            generar_reportes(empresa, credenciales[0], credenciales[1], credenciales[2], credenciales[3], fechas, lista_de_reportes)
            print("Quedan " + str(len(empresas_y_credenciales) - 1 - contador) + " reportes por generar.")
            contador += 1
    else:
        fecha = seleccionar_fecha()
        reportes_generales(archivo, fecha)
    print("La generación de reportes ha concluido. Si algún reporte faltase, probablemente tenía el archivo abierto.")
# Sólamente correrá el programa si se solicita correr directamente.
if __name__ == "__main__":
    main()