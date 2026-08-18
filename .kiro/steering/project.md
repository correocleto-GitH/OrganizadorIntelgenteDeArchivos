# Organizador Inteligente — Descripción del proyecto

## Qué hace

Aplicación web **local para Windows** que organiza archivos de una carpeta por tipo. El usuario elige una carpeta, la app la analiza, clasifica cada archivo por extensión y los mueve a subcarpetas (Documentos, Imagenes, Videos, Audio, Comprimidos, Programas, Otros).

## Funcionalidades principales

- **Análisis y vista previa** — escanea la carpeta sin mover nada
- **Simulación** — calcula qué movería sin ejecutar `shutil.move`
- **Organización real** — mueve archivos físicamente con `shutil.move`
- **Deshacer** — revierte la última operación archivo por archivo, sin detener el proceso si uno falla
- **Buscador y filtros** — filtrado en tiempo real por nombre y categoría (JavaScript vanilla, lado cliente)
- **Historial** — registra cada acción en SQLite (`historial` y `operaciones`)
- **Selector nativo de Windows** — usa `tkinter.filedialog.askdirectory()`
- **Protección de carpetas del sistema** — bloquea `C:\Windows`, `Program Files` y similares
- **Modo oscuro** — toggle por sesión mediante clase CSS `.dark` en `<html>`
- **Gestión de duplicados** — `_destino_unico()` añade sufijos `_1`, `_2`… si el destino ya existe

## Arquitectura

Patrón MVC ligero sin ORM ni frameworks de frontend:

```
app.py                  ← Rutas Flask + lógica de sesión
organizador/
  organizador.py        ← Lógica de negocio (analizar, organizar, deshacer, buscar)
  db.py                 ← Capa de datos SQLite
  __init__.py           ← Vacío, marca el paquete
templates/              ← Vistas Jinja2 (index, resultado, historial)
static/css/estilos.css  ← Estilos con variables CSS y modo oscuro
static/js/script.js     ← Filtrado cliente-side (JavaScript vanilla)
organizador.db          ← SQLite generado en runtime (excluido de git)
```

`app.py` delega toda la lógica de archivos en `organizador.py` y toda la persistencia en `db.py`. El estado efímero entre requests (ruta activa, última operación) vive en la sesión Flask.

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Python 3 + Flask 3.1.1 |
| Base de datos | SQLite (stdlib `sqlite3`) |
| Templates | Jinja2 |
| Frontend | HTML5 + CSS3 + JavaScript vanilla |
| Selector de carpetas | `tkinter.filedialog` (stdlib, solo Windows) |
| Variables de entorno | `python-dotenv` 1.1.1 |
| Operaciones de ficheros | `os`, `shutil` (stdlib) |

Solo dos dependencias pip externas: `Flask` y `python-dotenv`. Sin ORM, sin frameworks JS, sin librerías de frontend.

## Cómo ejecutar

```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

La app escucha en `http://127.0.0.1:5000`. La `SECRET_KEY` se lee de `.env`; si no existe, se genera con `os.urandom(24)` (invalida sesiones entre reinicios).

## Variables de entorno

Documentadas en `.env.example`. La única variable requerida es `SECRET_KEY`.
