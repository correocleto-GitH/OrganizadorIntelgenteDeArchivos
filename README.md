# Organizador Inteligente de Archivos

Aplicación web local desarrollada con Python, Flask, HTML, CSS, JavaScript y SQLite.

## Funciones

- Análisis y vista previa.
- Organización por categorías.
- Modo simulación.
- Deshacer última operación.
- Buscador y filtros.
- Dashboard con contadores.
- Historial SQLite.
- Detección de nombres duplicados.
- Protección básica de carpetas del sistema.
- Diseño responsive.
- Modo oscuro.

## Instalación en Visual Studio Code

```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Abrir:

http://127.0.0.1:5000

## Recomendaciones

Probar primero con una carpeta de prueba. La aplicación mueve archivos físicamente cuando se ejecuta la organización.


## Selector de carpetas de Windows

La aplicación incluye el botón **"Seleccionar carpeta local de Windows"**.
Al pulsarlo, Flask abre el diálogo nativo de selección de carpetas mediante
`tkinter.filedialog.askdirectory()` y coloca automáticamente la ruta elegida
en la sesión de la aplicación.

Esta función está pensada para ejecutar Flask **localmente en Windows**.
