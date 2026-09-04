import sys
from PyQt5.QtWidgets import QMessageBox, QDesktopWidget, QTableWidgetItem
from PyQt5 import uic, QtWidgets
import pyodbc


# ==============================================================================
# CLASE: NOTAS (VENTANA PARA REGISTRO Y MOSTRAR CALIFICACIONES)
# ==============================================================================
# Permite consultar si un alumno está matriculado en un curso, asignarle 
# calificaciones (Nota 1 y Nota 2), calcular su promedio y visualizar sus notas.
class notas(QtWidgets.QMainWindow):
   
   # ---------------------------------------------------------------------------
   # INICIALIZACIÓN DE LA VENTANA Y RECIBIMIENTO DE PARÁMETROS
   # ---------------------------------------------------------------------------
   def __init__(self, curso_seleccionado):
      super().__init__()
      
      # Carga dinámicamente la interfaz gráfica desde el archivo .ui correspondiente
      uic.loadUi("ui/notas.ui", self)
      
      # Guarda el curso seleccionado enviado desde el menú principal
      self.curso = curso_seleccionado
      
      # Enlace de eventos (Signal/Slot) de los botones con sus respectivos métodos
      self.btn_mostrar.clicked.connect(self.mostrar)
      self.btn_registrar.clicked.connect(self.registrar)
      self.btn_salir.clicked.connect(self.salir)
      
      # Poblar el ComboBox con la lista de alumnos disponibles
      self.cargar_cursos()
      
   # ---------------------------------------------------------------------------
   # CONEXIÓN A LA BASE DE DATOS
   # ---------------------------------------------------------------------------
   def conexion_bd(self):
      """
      Establece y retorna la conexión activa con la BD SQL Server mediante pyodbc.
      """
      return pyodbc.connect(
            'DRIVER={ODBC Driver 17 for SQL Server};'
            'SERVER=localhost\\SQLEXPRESS;'
            'DATABASE=REGISTRO_CURSOS;'
            'Trusted_Connection=yes;'  # Utiliza la autenticación de Windows
      )   
   
   # ---------------------------------------------------------------------------
   # CARGA DE ALUMNOS EN EL COMBOBOX
   # ---------------------------------------------------------------------------
   def cargar_cursos(self):
      """
      Consulta los nombres de los alumnos en la BD y los agrega a cbo_nombre.
      """
      try:
         conexion = self.conexion_bd()
         cursor = conexion.cursor()
         
         # Consulta simple ordenada alfabéticamente
         query_alumno = "SELECT NOMBRE FROM ALUMNO ORDER BY NOMBRE ASC"
         cursor.execute(query_alumno)
         
         # Limpieza preventiva para evitar duplicados
         self.cbo_nombre.clear()
         
         # Elemento por defecto
         self.cbo_nombre.addItem("--SELECCIONE--")
         
         # Agrega cada alumno obtenido de la base de datos
         for fila in cursor.fetchall():
            self.cbo_nombre.addItem(fila[0])
            
         conexion.close()
         
      except Exception as e:
         QMessageBox.critical(
            self, "Error BD", f"No se pudieron cargar los alumnos desde la base de datos: {e}"
         )
         
   # ---------------------------------------------------------------------------
   # CONSULTA DE MATRÍCULA Y DATOS DEL ALUMNO
   # ---------------------------------------------------------------------------
   def mostrar(self):
      """
      Valida si el alumno seleccionado está matriculado en el curso activo
      y muestra sus datos generales en la tabla tbl_datos.
      """
      alumno_seleccionado = self.cbo_nombre.currentText()
      
      # Validar que el usuario haya elegido un alumno válido del ComboBox
      if self.cbo_nombre.currentText() == 0 or not alumno_seleccionado:
         QMessageBox.warning(self, "Advertencia", "Por favor seleccione un código/alumno de la lista.")
         return
      
      try:
         conexion = self.conexion_bd()
         cursor = conexion.cursor()
         
         # Consulta relacional con JOINs entre MATRICULAS, ALUMNO y CURSOS
         query_alumno = """
            SELECT
               A.CODIGO,
               A.NOMBRE,
               A.APELLIDO,
               C.NOMBRE AS CURSO,
               A.CORREO
            FROM MATRICULAS M
            INNER JOIN ALUMNO A ON M.CODIGO = A.CODIGO
            INNER JOIN CURSOS C ON M.CURSO_ID = C.CURSO_ID
            WHERE A.NOMBRE = ?
         """
         cursor.execute(query_alumno, (alumno_seleccionado))
         
         # fetchone() recupera una sola fila ya que se consulta un alumno específico
         fila = cursor.fetchone()
         
         if fila:
            # Muestra el resultado devuelto en la primera fila de la tabla tbl_datos
            self.tbl_datos.setRowCount(1)
            for i, valor in enumerate(fila):
               self.tbl_datos.setItem(0, i, QTableWidgetItem(str(valor)))
               
         else:
            # Limpia la tabla y advierte si el alumno no registra matrícula
            self.tbl_datos.setRowCount(0)
            QMessageBox.information(
                  self, "Sin resultados", f"El alumno {alumno_seleccionado} no está matriculado en el curso {self.curso}."
            )

         conexion.close()

      except Exception as e:
         QMessageBox.critical(self, "Error BD", f"Error al consultar datos del alumno: {e}")
      
      # Reseteo preventivo de campos de notas y tabla de notas
      self.text_nota1.clear()
      self.text_nota2.clear()
      self.tbl_notas.setRowCount(0)
   
   # ---------------------------------------------------------------------------
   # REGISTRO Y RE-CONSULTA DE NOTAS
   # ---------------------------------------------------------------------------
   def registrar(self):
      """
      Valida, calcula el promedio e inserta las notas en la BD.
      Posteriormente vuelve a consultar para actualizar la tabla de notas (tbl_notas).
      """
      alumno_seleccionado = self.cbo_nombre.currentText()
      
      # Validar selección de alumno
      if self.cbo_nombre.currentText() == 0:
         QMessageBox.warning(self, "Advertencia", "Por favor, seleccione un alumno.")
         return
      
      # Captura de datos de las cajas de texto quitando espacios vacíos
      num1 = self.text_nota1.text().strip()
      num2 = self.text_nota2.text().strip()
      
      # Validar campos vacíos
      if (not num1 or not num2):
         QMessageBox.warning(self, "Advertencia", "Por favor, complete todos los campos.")
         return
      
      # Conversión a flotante, cálculo del promedio y validación de rango (0 - 20)
      try:
         n1 = float(num1)
         n2 = float(num2)
         promedio = (n1 + n2) / 2
         
         if not (0 <= n1 <= 20 and 0 <= n2 <= 20):
            QMessageBox.warning(
               self, "Advertencia", "Las notas deben estar dentro del rango de 0 a 20."
            )
            return 
      
      except ValueError:
         # Se dispara si el usuario ingresó texto/letras en lugar de números válidos
         QMessageBox.warning(self, "Advertencia", "Las notas deben estar dentro del rango de 0 a 20")
         return

      # Bloque para inserción de datos en la BD
      try:
         conexion = self.conexion_bd()
         cursor = conexion.cursor()
         
         # 1. Obtener el CURSO_ID a partir del nombre del curso activo
         query_curso = "SELECT CURSO_ID FROM CURSOS WHERE NOMBRE = ?"
         cursor.execute(query_curso, (self.curso,))
         respuesta_curso = cursor.fetchone()
         
         if not respuesta_curso:
            QMessageBox.warning(
               self, "Error", f"No se encontró el curso: {self.curso}"
            )
            conexion.close()
            return
               
         # 2. Obtener el CODIGO del alumno a partir de su nombre
         query_codigo = "SELECT CODIGO FROM ALUMNO WHERE NOMBRE = ?"
         cursor.execute(query_codigo, (alumno_seleccionado))
         respuesta_alumno = cursor.fetchone()
         
         if not respuesta_alumno:
            QMessageBox.warning(
               self, "Error", f"No se encontró el curso: {self.curso}"
            )
            conexion.close()
            return
                     
         codigo = respuesta_alumno[0]
         curso_id = respuesta_curso[0]

         # 3. Inserción de las notas y el promedio calculado
         query_notas = """
               INSERT INTO NOTAS (CURSO_ID, CODIGO, NOTA1, NOTA2, PROMEDIO)
               VALUES (?, ?, ?, ?, ?)            
         """
         cursor.execute(query_notas, (curso_id, codigo, n1, n2, promedio))
         
         # Guarda los cambios de forma permanente en SQL Server
         conexion.commit()
         conexion.close()

         QMessageBox.information(
               self, "Éxito", f"Notas registradas correctamente para {alumno_seleccionado}.\nPromedio: {promedio:.2f}"
         )
      except Exception as e:
         QMessageBox.critical(self, "Error BD", f"Error al registrar las notas: {e}")
      
      # Bloque para actualizar la tabla de notas e impactar los cambios visualmente
      try:
         conexion = self.conexion_bd()
         cursor = conexion.cursor()
         
         # Consulta de las notas registradas filtrando por Alumno y Curso
         query_notas = """
            SELECT
               N.NOTA1,
               N.NOTA2,
               N.PROMEDIO
            FROM NOTAS N
            INNER JOIN ALUMNO A ON N.CODIGO = A.CODIGO
            INNER JOIN CURSOS C ON N.CURSO_ID = C.CURSO_ID
            WHERE A.NOMBRE = ? AND C.NOMBRE = ?
         """
         cursor.execute(query_notas, (alumno_seleccionado, self.curso))
         fila = cursor.fetchall()
         
         # Resetea las filas existentes
         self.tbl_notas.setRowCount(0)
         
         if fila:
            # Iteración para rellenar el QTableWidget con todas las notas encontradas
            for fila, fila_datos in enumerate(fila):
               self.tbl_notas.insertRow(fila)
               for col_index, valor in enumerate(fila_datos):
                  self.tbl_notas.setItem(
                     fila, col_index, QTableWidgetItem(str(valor))
                  )
         else:
            QMessageBox.information(
               self, "Sin notas", f"El alumno {alumno_seleccionado} aún no tiene notas registradas en {self.curso}."
            )
            conexion.close()

      except Exception as e:
         QMessageBox.critical(self, "Error BD", f"Error al consultar las notas: {e}")
         
         # Limpieza de las cajas de texto de notas tras intentar la consulta
         self.text_nota1.clear()
         self.text_nota2.clear()

   # ---------------------------------------------------------------------------
   # CIERRE DE LA VENTANA
   # ---------------------------------------------------------------------------
   def salir(self):
      """
      Cierra la ventana actual de gestión de notas.
      """
      self.close()