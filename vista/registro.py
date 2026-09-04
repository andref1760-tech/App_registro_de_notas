import sys
from PyQt5.QtWidgets import QMessageBox, QDesktopWidget, QTableWidgetItem
from PyQt5 import uic, QtWidgets
import pyodbc


# ==============================================================================
# CLASE: REGISTROS (VENTANA PARA REGISTRO DE ALUMNOS Y MATRÍCULA)
# ==============================================================================
# Permite dar de alta a un nuevo estudiante en la base de datos y realizar 
# su matrícula vinculándolo al curso seleccionado en el menú de inicio.
class registros(QtWidgets.QMainWindow):
   
   # ---------------------------------------------------------------------------
   # INICIALIZACIÓN DE LA VENTANA Y RECIBIMIENTO DE PARÁMETROS
   # ---------------------------------------------------------------------------
   def __init__(self, curso_seleccionado):
      super().__init__()
      
      # Carga el diseño de la interfaz gráfica desde el archivo .ui correspondiente
      uic.loadUi("ui/registros.ui", self)
      
      # Guarda el nombre del curso activo para asociar las nuevas matrículas
      self.curso = curso_seleccionado
      
      # Enlace de eventos (Signal/Slot) de los botones con sus métodos
      self.btn_registrar.clicked.connect(self.registrar)
      self.btn_salir.clicked.connect(self.salir)
      
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
   # REGISTRO DE ALUMNO Y MATRÍCULA
   # ---------------------------------------------------------------------------
   def registrar(self):
      """
      Valida las cajas de texto, verifica que el código de alumno no esté repetido,
      inserta el nuevo registro en la tabla ALUMNO y crea su entrada en MATRICULAS.
      """
      # Captura los datos ingresados, remueve espacios vacíos al inicio/final (.strip())
      # y estandariza los textos a minúsculas (.lower())
      nombre = self.text_nombre.text().strip().lower()
      apellido = self.text_apellido.text().strip().lower()
      codigo = self.text_codigo.text().strip().lower()
      correo = self.text_correo.text().strip().lower()
   
      # Validación para evitar procesar campos vacíos en el formulario
      if (
         not nombre or 
         not apellido or
         not codigo or
         not correo):
         QMessageBox.warning(
            self, "Advertencia", "Por favor, complete todos los campos."
         )
         return
   
      try:
         conexion = self.conexion_bd()
         cursor = conexion.cursor()
         
         # 1. Obtener el CURSO_ID correspondiente al curso seleccionado
         query_curso = "SELECT CURSO_ID FROM CURSOS WHERE NOMBRE = ?"
         cursor.execute(query_curso, (self.curso,))
         resultado_curso = cursor.fetchone()

         if not resultado_curso:
            QMessageBox.warning(self, "Error", "El curso seleccionado no existe.")
            return

         curso_id = resultado_curso[0]
         
         # Validar la existencia de códigos duplicados consultando la llave primaria/código
         query_verificador = "SELECT ALUMNO_ID FROM ALUMNO WHERE CODIGO = ?"
         cursor.execute(query_verificador, (codigo,))
         
         # Si fetchone() retorna un registro, significa que el código ya existe
         if cursor.fetchone():
            QMessageBox.warning(
               self, "Registro Duplicado", f"El código '{codigo}' ya pertenece a un alumno registrado."
            )
            return
                  
         # 2. Insertar el nuevo alumno en la tabla ALUMNO
         # La cláusula OUTPUT INSERTED.ALUMNO_ID retorna la clave primaria autogenerada
         query_registro = """
            INSERT INTO ALUMNO(NOMBRE, APELLIDO, CODIGO, CORREO)
            OUTPUT INSERTED.ALUMNO_ID
            VALUES(?, ?, ?, ?)
         """
         cursor.execute(query_registro, (nombre, apellido, codigo, correo))
         
         # 3. Insertar la relación en la tabla MATRICULAS vinculando CURSO_ID y CODIGO
         query_registro2 = """
            INSERT INTO MATRICULAS(CURSO_ID, CODIGO)
            VALUES(?, ?)
         """
         cursor.execute(query_registro2, (curso_id, codigo))
         
         # Confirma la transacción guardando los cambios de forma definitiva
         conexion.commit()
         
         QMessageBox.information(
            self, "Exito", "Registro guardado correctamente"
         )
      
      except Exception as e:
         # Control de transacciones: si ocurre un fallo en cualquiera de las consultas,
         # se deshacen las operaciones ejecutadas para evitar datos inconsistentes
         if "conexion" in locals() and conexion:
            conexion.rollback()
            
         # Muestra una ventana de error en caso de fallo en la BD
         QMessageBox.critical(
            self,
            "Error BD",
            f"No se pudo guardar en la base de datos : {e}",
         )
      
      # Limpieza de las cajas de texto tras completar o fallar el proceso
      self.text_nombre.clear()
      self.text_apellido.clear()
      self.text_codigo.clear()
      self.text_correo.clear()
         
   # ---------------------------------------------------------------------------
   # CIERRE DE LA VENTANA
   # ---------------------------------------------------------------------------
   def salir(self):
      """
      Cierra la ventana actual de registros.
      """
      self.close()