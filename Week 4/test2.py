empresa = "Loco"
print("Jordi")
print(f"""
          De las siguientes opciones de tablas/gráficas, seleccione aquellas que
          desee agregar a su reporte de {empresa}:
          1. Tabla: Tráfico consumido por CPcode
          2. Tabla: Tráfico Total y Estadísticas (Bytes Total, Bytes por segundo Total, Mínimo y Máximo)
          3. Gráfica: Tráfico por día (Edge, Midgress, Origin y Offload)
          4. Gráfica: Hits al Origen por tipo de respuesta (0xx, 1xx, 2xx, 3xx, 4xx, 5xx)
          5. Tabla: Hits por tipo de respuesta, ordenados por Edge Hits
          6. Tabla: Hits por tipo de respuesta, de únicamente un CPcode
          """)
print("sobres")