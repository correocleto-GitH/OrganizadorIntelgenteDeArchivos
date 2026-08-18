# Organizador Inteligente de Archivos

Aplicación web **local para Windows** que organiza archivos de una carpeta por tipo. Elige una carpeta, la app escanea, clasifica cada archivo por extensión y los mueve a subcarpetas (Documentos, Imagenes, Videos, Audio, Comprimidos, Programas, Otros).

## Funcionalidades

- **Análisis y vista previa** — escanea sin mover nada
- **Simulación** — calcula qué movería sin ejecutar cambios
- **Organización real** — mueve archivos con gestión automática de duplicados (`_1`, `_2`…)
- **Recursividad opcional** — incluye o excluye subcarpetas
- **Deshacer** — revierte la última operación archivo por archivo
- **Buscador y filtros** — filtrado en tiempo real en cliente; búsqueda server-side para carpetas grandes
- **Progreso en tiempo real** — barra SSE para carpetas con más de 100 archivos
- **Historial** — registro de todas las operaciones en SQLite con vista de detalle por lote
- **Exportar CSV** — descarga el historial completo
- **Selector nativo de Windows** — diálogo de carpetas via `tkinter.filedialog`
- **Protección del sistema** — bloquea `C:\Windows`, `Program Files` y similares
- **Modo oscuro** — toggle por sesión

## Stack

| Capa | Tecnología |
|---|---|
| Backend | Python 3 + Flask 3.1.1 |
| Base de datos | SQLite (stdlib `sqlite3`) |
| Templates | Jinja2 |
| Frontend | HTML5 + CSS3 + JavaScript vanilla |
| Selector de carpetas | `tkinter.filedialog` (stdlib, solo Windows) |
| Variables de entorno | `python-dotenv` 1.1.1 |
| Seguridad | `Flask-WTF` 1.3.0 (CSRF) |
| Tests | `pytest` 8.3.5 |

## Instalación

```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Abrir: http://127.0.0.1:5000

Copiar `.env.example` a `.env` y definir `SECRET_KEY` para que las sesiones persistan entre reinicios.

## Estructura

```
app.py                  ← Rutas Flask + lógica de sesión
organizador/
  organizador.py        ← Lógica de negocio (analizar, organizar, deshacer, buscar, validar rutas)
  db.py                 ← Capa de datos SQLite
templates/              ← Jinja2 (index, historial, detalle_operacion, resultado)
static/
  css/estilos.css       ← Variables CSS + modo oscuro
  js/script.js          ← Filtrado cliente/servidor + SSE + progreso
tests/                  ← Suite pytest (52 tests)
```

## Tests

```cmd
venv\Scripts\pytest tests\ -v
```

52 tests cubriendo lógica de archivos, capa de datos y rutas Flask.

## Uso recomendado

Probar primero con una carpeta de prueba. La organización real **mueve archivos físicamente**. Usa "Simular" para previsualizar antes de ejecutar.

La aplicación está diseñada para uso local en Windows. `tkinter` requiere display local y no es compatible con despliegue en servidor remoto.
