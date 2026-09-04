# Registro de Notas (Registro_nota_py)

Este proyecto es una aplicación de escritorio desarrollada en **Python** para la gestión y registro de calificaciones/notas, cursos y bases de datos. Utiliza interfaces gráficas diseñadas con Qt (`.ui`) y una base de datos relacional alimentada por un script SQL.

---

## 📁 Estructura del Proyecto

A continuación se detalla la organización de los archivos y módulos dentro del proyecto:

```text
Registro_nota_py/
│
├── bd/
│   └── DATA.sql            # Script SQL con la base de datos inicial y registros.
│
├── ui/                     # Archivos de interfaz de usuario (Qt Designer / .ui)
│   ├── basedatos.ui        # Vista de configuración/conexión a BD.
│   ├── cursos.ui           # Vista de gestión de cursos.
│   ├── notas.ui            # Vista de registro e historial de notas.
│   └── registros.ui        # Vista principal de formularios y registros.
│
├── vista/                  # Controladores y lógica de presentación (Python)
│   ├── basedatos.py        # Lógica asociada a la BD.
│   ├── inicio.py           # Pantalla/Lógica inicial o menú principal.
│   ├── notas.py            # Gestión y control de lógica de notas.
│   └── registro.py         # Control de registros del sistema.
│
├── main.py                 # Punto de entrada principal para ejecutar la aplicación.
└── README.md               # Documentación del proyecto.
```[cite: 1]

---

## 🛠️ Requisitos Previos

Antes de ejecutar el proyecto, asegúrate de contar con los siguientes elementos instalados:

* **Python 3.x**
* Servidor de base de datos (por ejemplo, **MySQL / MariaDB** o **SQLite**, según el contenido de `DATA.sql`)[cite: 1].
* **PyQt5** o **PySide2 / PySide6** (necesario para cargar/procesar las interfaces de la carpeta `ui/`)[cite: 1].

---

## 🚀 Instalación y Configuración

1. **Clonar el repositorio o descargar el proyecto:**
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd Registro_nota_py