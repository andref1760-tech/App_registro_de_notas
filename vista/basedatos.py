import sys
from PyQt5.QtWidgets import QMessageBox, QDesktopWidget, QTableWidgetItem
from PyQt5 import uic, QtWidgets
import pyodbc


# ==============================================================================
# CLASE: BASEDATOS (VENTANA DE CONSULTA GENERAL Y REPORTE)
# ==============================================================================
# Muestra una tabla con el listado consolidado de alumnos y sus calificaciones
# para el curso seleccionado en la pantalla anterior.
class basedatos(QtWidgets.QMainWindow):
   
   # ---------------------------------------------------------------------------
   # INICIALIZACIÓN DE LA VENTANA Y RECIBIMIENTO DE PARÁMETROS
   # ---------------------------------------------------------------------------
   def __init__(self, curso_seleccionado):
      super().__init__()
      
      # Carga el diseño de la interfaz desde el archivo .ui correspondiente
      uic.loadUi("ui/basedatos.ui", self)
      
      # Guarda el parámetro del curso en una variable de instancia para usarlo en toda la clase
      self.curso = curso_seleccionado
      
      # Muestra el nombre del curso activo en una etiqueta de texto (QLabel) de la interfaz
      self.lbl_curso.setText(self.curso)
      
      # Configuración del evento clic para el botón de retroceso
      self.btn_atras.clicked.connect(self.salir)
      
      # Carga de datos automática al abrir la ventana
      self.cargar_tabla_curso()
   
   # ---------------------------------------------------------------------------
   # CARGA Y LLENADO DE LA TABLA CON CONSULTA MULTI-TABLA (JOINs)
   # ---------------------------------------------------------------------------
   def cargar_tabla_curso(self):
      """
      Consulta en la BD los datos del Alumno junto a sus Notas asociadas al Curso 
      y dibuja dinámicamente las filas en el QTableWidget (tbl_registros).
      """
      try:
         conexion = self.conexion_bd()
         cursor = conexion.cursor()
         
         # Consulta SQL relacional:
         # 1. Parte de la tabla NOTAS (N) como origen principal de calificaciones.
         # 2. Hace INNER JOIN con ALUMNO (A) para obtener Código, Nombre y Apellido del estudiante.
         # 3. Hace INNER JOIN con CURSOS (C) para traducir el CURSO_ID a texto y poder filtrar por C.NOMBRE.
         query_datos = """
            SELECT
               A.CODIGO,
               A.NOMBRE,
               A.APELLIDO,
               N.NOTA1,
               N.NOTA2,
               N.PROMEDIO
            FROM NOTAS N
            INNER JOIN ALUMNO A ON N.CODIGO = A.CODIGO
            INNER JOIN CURSOS C ON N.CURSO_ID = C.CURSO_ID
            WHERE C.NOMBRE = ?     
         """
         # Pasa la variable self.curso mediante parámetro tuple para prevenir inyecciones SQL
         cursor.execute(query_datos, (self.curso,))
         
         # fetchall() recupera todos los registros encontrados en una lista de tuplas
         fila = cursor.fetchall()
         
         # Resetea la tabla borrando todas las filas previas antes de pintar los nuevos datos
         self.tbl_registros.setRowCount(0)
         
         # Evaluamos si existen filas devueltas por la consulta SQL
         if fila:
            # 1er Bucle: Recorre cada registro/fila devuelto por la base de datos
            for fila, fila_datos in enumerate(fila):
               self.tbl_registros.insertRow(fila) # Inserta una nueva fila en el Widget de la tabla
               
               # 2do Bucle: Recorre cada valor (columna) dentro de la tupla actual
               for col_index, valor in enumerate(fila_datos):
                  # Inserta cada celda convirtiendo el valor a String (exigido por QTableWidgetItem)
                  self.tbl_registros.setItem(
                     fila, col_index, QTableWidgetItem(str(valor))
                  )
         else:
            # Mensaje informativo en caso de que la consulta devuelva una lista vacía
            QMessageBox.information(
               self, "Sin notas", f"El alumno {self.curso} aún no tiene notas registradas en {self.curso}."
            )
            conexion.close()
         
      except Exception as e:
         # Captura y despliegue de errores en la consulta de BD
         QMessageBox.critical(self, "Error BD", f"Error al consultar las notas: {e}")
      
   # ---------------------------------------------------------------------------
   # CONEXIÓN A LA BASE DE DATOS
   # ---------------------------------------------------------------------------
   def conexion_bd(self):
      """
      Establece y retorna la conexión activa con la BD SQL Server mediante pyodbc.
      """
      return pyodbc.connect(
         'DRIVER={ODBC DRIVER 17 FOR SQL SERVER};'
         'SERVER=LOCALHOST\\SQLEXPRESS;'
         'DATABASE=REGISTRO_CURSOS;'
         'TRUSTED_CONNECTION=YES;'
      )   
   
   # ---------------------------------------------------------------------------
   # CIERRE DE LA VENTANA
   # ---------------------------------------------------------------------------
   def salir(self):
      """
      Cierra la ventana actual de visualización de base de datos.
      """
      self.close()