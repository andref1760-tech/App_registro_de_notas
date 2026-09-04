import sys
from PyQt5.QtWidgets import QMessageBox, QDesktopWidget, QTableWidgetItem
from PyQt5 import uic, QtWidgets
import pyodbc

# Importación de las subventanas (vistas) que se abrirán desde este menú principal
from vista.basedatos import basedatos
from vista.notas import notas
from vista.registro import registros


# ==============================================================================
# CLASE PRINCIPAL: INICIO
# ==============================================================================
# Representa la ventana principal del sistema donde el usuario selecciona el curso 
# y redirige a los módulos de Registro, Notas o Base de Datos.
class inicio(QtWidgets.QMainWindow):
   
   # ---------------------------------------------------------------------------
   # INICIALIZACIÓN Y CONFIGURACIÓN DE LA VENTANA
   # ---------------------------------------------------------------------------
   def __init__(self):
      super().__init__()
      
      # Carga dinámicamente la interfaz gráfica definida en el archivo Qt Designer (.ui)
      uic.loadUi("ui/cursos.ui", self)
      
      # Enlace de eventos (Signal/Slot) entre los botones del UI y sus métodos
      self.btn_registrar.clicked.connect(self.registrar)
      self.btn_notas.clicked.connect(self.notas)
      self.btn_base.clicked.connect(self.basedatos)
      self.btn_salir.clicked.connect(self.salir)
      
      # Consulta y llena el desplegable (ComboBox) con los cursos disponibles en la BD
      self.cargar_cursos()
      
   # ---------------------------------------------------------------------------
   # CONEXIÓN A LA BASE DE DATOS
   # ---------------------------------------------------------------------------
   def conexion_bd(self):
      """
      Establece y retorna una conexión con la base de datos SQL Server mediante ODBC.
      Usa autenticación de Windows (TRUSTED_CONNECTION=YES).
      """
      return pyodbc.connect(
         'DRIVER={ODBC DRIVER 17 FOR SQL SERVER};'
         'SERVER=LOCALHOST\\SQLEXPRESS;'
         'DATABASE=REGISTRO_CURSOS;'
         'TRUSTED_CONNECTION=YES;'
      )
   
   # ---------------------------------------------------------------------------
   # CARGA INICIAL DE CURSOS EN EL COMBOBOX
   # ---------------------------------------------------------------------------
   def cargar_cursos(self):
      """
      Consulta los nombres de los cursos en SQL Server y los inserta en cbo_cursos.
      """
      try:
         conexion = self.conexion_bd()
         cursor = conexion.cursor()
         
         # Consulta simple ordenada alfabéticamente
         query_cursos = "SELECT NOMBRE FROM CURSOS ORDER BY NOMBRE ASC"
         cursor.execute(query_cursos)
         
         # Limpieza del widget para evitar duplicados en recargas
         self.cbo_cursos.clear()
         
         # Opción por defecto para forzar una selección consciente del usuario
         self.cbo_cursos.addItem("--SELECCIONE--")
         
         # Iteración sobre los resultados de la BD y llenado del ComboBox
         for fila in cursor.fetchall():
            self.cbo_cursos.addItem(fila[0])
         
         # Cierre de conexión para liberar recursos en SQL Server
         conexion.close()
         
      except Exception as e:
         # Captura de errores de base de datos o conectividad y despliegue de alerta
         QMessageBox.critical(
            self, "Error BD", f"No se pudieron cargar los cursos desde la base de datos: {e}"
         )
         
   # ---------------------------------------------------------------------------
   # MÉTODO DE VALIDACIÓN AUXILIAR
   # ---------------------------------------------------------------------------
   def obtener_curso_seleccionado(self):
      """
      Valida si el usuario ha seleccionado un curso válido diferente a la opción por defecto.
      Retorna la cadena del nombre del curso o None en caso de selección inválida.
      """
      curso = self.cbo_cursos.currentText()
      if curso == "--SELECCIONE--" or not curso:
         QMessageBox.warning(self, "Advertencia", "Por favor seleccione un curso de la lista")
         return None
      return curso
   
   # ---------------------------------------------------------------------------
   # NAVEGACIÓN Y APERTURA DE SUBVENTANAS
   # ---------------------------------------------------------------------------
   def registrar(self):
      """
      Abre la ventana de Registro de Alumnos enviando el curso seleccionado.
      """
      curso = self.obtener_curso_seleccionado()
      if curso:
         # Se instancia la ventana asignándola a self.ventana para evitar que el Garbage Collector la destruya de la memoria
         self.ventana = registros(curso_seleccionado=curso)
         self.ventana.show()
         
   def notas(self):
      """
      Abre la ventana de Gestión de Notas enviando el curso seleccionado.
      """
      curso = self.obtener_curso_seleccionado()
      if curso:
         self.ventana = notas(curso_seleccionado=curso)
         self.ventana.show()
   
   def basedatos(self):
      """
      Abre la ventana de Consulta General (Base de Datos) enviando el curso seleccionado.
      """
      curso = self.obtener_curso_seleccionado()
      if curso:
         self.ventana = basedatos(curso_seleccionado=curso)
         self.ventana.show()
   
   # ---------------------------------------------------------------------------
   # CIERRE DE APLICACIÓN
   # ---------------------------------------------------------------------------
   def salir(self):
      """
      Cierra la ventana actual de inicio.
      """
      self.close()