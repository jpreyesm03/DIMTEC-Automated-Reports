from funciones_cortas import seleccionar_archivo # type: ignore
from funciones_cortas import seleccionar_fecha # type: ignore
from funciones_cortas import seleccionar_empresas # type: ignore
from funciones_cortas import seleccionar_reportes # type: ignore
from funciones_cortas import seleccionar_cpcodes # type: ignore
from funciones_cortas import generar_reportes # type: ignore
from funciones_cortas import automatico_o_manual # type: ignore
from funciones_cortas import reportes_generales # type: ignore

introduccion = "¡Hola! Puedes generar todos los reportes desde este programa. La idea es que solamente utilice números a lo largo del programa."

def main():
    print(introduccion)
    manual = automatico_o_manual()
    archivo = seleccionar_archivo()
    fecha = seleccionar_fecha()
    if (manual):
        
        empresas_y_credenciales = seleccionar_empresas(archivo)
        reportes_por_empresa = seleccionar_reportes(empresas)
        # cpcodes_por_reporte = seleccionar_cpcodes()
        # generar_reportes(empresas, fecha, reportes_por_empresa, cpcodes_por_reporte)
        print("La generación de reportes ha concluido. Si algún reporte faltase, probablemente tenía el archivo abierto.")
    else:
        reportes_generales()
    print("La generación de reportes ha concluido. Si algún reporte faltase, probablemente tenía el archivo abierto.")
# Sólamente correrá el programa si se solicita correr directamente.
if __name__ == "__main__":
    main()