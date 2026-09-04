import sys
from PyQt5 import QtWidgets
from vista.inicio import inicio

# ==============================================================================
# PUNTO DE ENTRADA PRINCIPAL DEL PROGRAMA
# ==============================================================================
# La condición __name__ == "__main__" asegura que este bloque solo se ejecute 
# cuando el archivo se ejecute directamente, y no cuando sea importado como módulo.
if __name__ == "__main__":
   
   # 1. Crear la instancia principal de la aplicación en PyQt.
   # sys.argv permite que la aplicación reconozca parámetros pasados por consola.
   app = QtWidgets.QApplication(sys.argv)

   # 2. Instanciar la ventana de inicio.
   # Se crea el objeto de la clase 'inicio' importada desde el paquete 'vista'.
   ventana = inicio()

   # 3. Hacer visible la interfaz gráfica creada.
   ventana.show()

   # 4. Iniciar el bucle de eventos (Event Loop) de la aplicación.
   # app.exec() mantiene la ventana abierta escuchando interacciones del usuario (clics, teclado).
   # sys.exit() garantiza un cierre limpio del sistema al salir de la aplicación.
   sys.exit(app.exec())