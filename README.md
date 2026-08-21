# Organizador Inteligente de Archivos

Aplicación web **local para Windows** que clasifica y organiza archivos de cualquier carpeta por tipo de contenido. Accesible desde el navegador, sin instalación de servidores ni bases de datos externas.

---

## Funcionalidades

### Organización de archivos
- **Análisis y vista previa** — escanea la carpeta seleccionada y muestra todos los archivos con su categoría antes de mover nada.
- **Modo simulación** — calcula exactamente qué se movería y a dónde, sin ejecutar ningún cambio en disco.
- **Organización real** — mueve los archivos a subcarpetas por categoría con un solo clic.
- **Recursividad opcional** — checkbox "Incluir subcarpetas" para organizar también los archivos en carpetas anidadas.
- **Gestión de duplicados** — si ya existe un archivo con el mismo nombre en el destino, añade sufijo automático (`_1`, `_2`…) en lugar de sobreescribir.
- **Deshacer** — revierte la última operación archivo por archivo. Si alguno falla, los demás se restauran igualmente.

### Búsqueda y filtros
- **Filtros por categoría** — botones de filtro para ver solo Documentos, Imágenes, Videos, etc.
- **Buscador en tiempo real** — filtra por nombre de archivo mientras se escribe.
- **Búsqueda server-side automática** — para carpetas con más de 100 archivos, las búsquedas se delegan al servidor con debounce de 250 ms.

### Progreso en tiempo real
- **Barra de progreso SSE** — para carpetas grandes (más de 100 archivos), la organización emite eventos en tiempo real al navegador. La barra muestra `actual / total` sin bloquear la interfaz.

### Historial y exportación
- **Historial de operaciones** — todas las acciones quedan registradas en SQLite (seleccionar, analizar, simular, organizar, deshacer).
- **Vista de detalle por lote** — enlace "Ver detalle" en cada operación de organización para ver exactamente qué archivo se movió desde dónde hasta dónde.
- **Exportar a CSV** — descarga el historial completo como archivo CSV con un clic.

### Interfaz
- **Selector nativo de Windows** — botón que abre el diálogo de carpetas de Windows mediante `tkinter.filedialog`.
- **Modo oscuro** — toggle por sesión, sin recargar la página.
- **Diseño responsive** — funciona en cualquier resolución de pantalla.

---

## Categorías de archivos

| Categoría | Extensiones |
|---|---|
| 📄 Documentos | `.doc` `.docx` `.pdf` `.txt` `.xls` `.xlsx` `.ppt` `.pptx` `.csv` `.odt` `.ods` |
| 🖼️ Imágenes | `.jpg` `.jpeg` `.png` `.gif` `.bmp` `.webp` `.svg` `.tiff` `.ico` |
| 🎬 Videos | `.mp4` `.avi` `.mkv` `.mov` `.wmv` `.flv` `.webm` `.mpeg` |
| 🎵 Audio | `.mp3` `.wav` `.flac` `.aac` `.ogg` `.wma` `.m4a` |
| 📦 Comprimidos | `.zip` `.rar` `.7z` `.tar` `.gz` `.bz2` |
| ⚙️ Programas | `.exe` `.msi` `.bat` `.cmd` `.ps1` |
| 📁 Otros | Todo lo que no encaje en las categorías anteriores |

---

## Requisitos

- **Windows** (el selector nativo de carpetas requiere entorno de escritorio)
- **Python 3.10 o superior** — instalador completo desde [python.org](https://www.python.org/downloads/) (no la versión "slim" o "embeddable", ya que `tkinter` no está incluido en ellas)

Verificar la instalación:

```cmd
python --version
```

---

## Instalación

### 1. Obtener el código

```cmd
git clone https://github.com/usuario/organizador_archivos.git
cd organizador_archivos
```

O descomprimir el ZIP del proyecto en cualquier carpeta.

### 2. Crear el entorno virtual
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
```

### 3. Activar el entorno virtual

```cmd
venv\Scripts\activate
```

El prompt muestra `(venv)` al inicio cuando está activo.

### 4. Instalar dependencias

```cmd
pip install -r requirements.txt
```

Dependencias instaladas:

| Paquete | Versión | Uso |
|---|---|---|
| Flask | 3.1.1 | Servidor web |
| Flask-WTF | 1.3.0 | Protección CSRF |
| python-dotenv | 1.1.1 | Variables de entorno |
| pytest | 8.3.5 | Suite de tests |

### 5. Configurar la clave secreta

```cmd
copy .env.example .env
```

Editar `.env` y establecer una clave segura:

```
SECRET_KEY=reemplazar-con-clave-segura
```

Para generar una clave robusta:

```cmd
python -c "import secrets; print(secrets.token_hex(32))"
```

> Sin `SECRET_KEY` la app funciona, pero genera una clave temporal en cada reinicio e invalida las sesiones activas.

### 6. Arrancar la aplicación

```cmd
python app.py
```

Abrir en el navegador: **http://127.0.0.1:5000**

---

## Uso

1. Pulsar **"Seleccionar carpeta"** o escribir la ruta manualmente y pulsar **"Analizar ruta"**.
2. Revisar la tabla de archivos con sus categorías asignadas. Usar el buscador y los filtros si es necesario.
3. Opcional: activar **"Incluir subcarpetas"** para procesar también carpetas anidadas.
4. Pulsar **"Simular organización"** para previsualizar sin mover nada.
5. Pulsar **"Organizar archivos"** para ejecutar la organización real.
6. Si el resultado no es el esperado, pulsar **"Deshacer última operación"**.

> Recomendación: probar siempre con una carpeta de prueba antes de usar en carpetas de trabajo reales. La organización mueve archivos físicamente en disco.

---

## Estructura del proyecto

```
organizador_archivos/
│
├── app.py                      ← Rutas Flask, validación de entrada, sesión
├── requirements.txt            ← Dependencias con versiones fijas
├── .env.example                ← Plantilla de variables de entorno
├── .gitignore
├── README.md
├── INFORME.md                  ← Informe técnico detallado del proyecto
│
├── organizador/
│   ├── __init__.py
│   ├── organizador.py          ← Lógica de negocio: analizar, organizar, deshacer, buscar
│   └── db.py                   ← Capa de datos SQLite: historial y operaciones
│
├── templates/
│   ├── index.html              ← Vista principal
│   ├── historial.html          ← Historial de operaciones + exportar CSV
│   ├── detalle_operacion.html  ← Detalle de archivos movidos por lote
│   └── resultado.html          ← Vista previa alternativa
│
├── static/
│   ├── css/estilos.css         ← Variables CSS, modo oscuro
│   └── js/script.js            ← Filtrado, búsqueda server-side, SSE, progreso
│
└── tests/
    ├── conftest.py             ← Fixtures: carpeta_temporal, bd_temporal, cliente
    ├── test_organizador.py     ← 31 tests de lógica de archivos
    ├── test_db.py              ← 11 tests de capa de datos
    └── test_rutas.py           ← 12 tests de integración HTTP
```

---

## Tests

```cmd
venv\Scripts\pytest tests\ -v
```

**52 tests, 0 fallos.**

| Archivo | Tests | Cubre |
|---|---|---|
| `test_organizador.py` | 31 | Categorización, validación de rutas, análisis, organización, deshacer, búsqueda |
| `test_db.py` | 11 | Inicialización de BD, logs, operaciones, historial |
| `test_rutas.py` | 12 | Rutas Flask con cliente de pruebas, CSRF desactivado en test |

Ejecutar un archivo específico:

```cmd
venv\Scripts\pytest tests\test_organizador.py -v
```

Ejecutar un test específico:

```cmd
venv\Scripts\pytest tests\test_organizador.py -v -k "test_organizar_simulacion"
```

---

## Arquitectura

El proyecto sigue un patrón MVC de tres capas con separación estricta de responsabilidades:

```
Navegador (HTML + CSS + JS vanilla)
        │
        │ HTTP
        ▼
    app.py  ←  Controlador: rutas, sesión, validación
    /     \
   ▼       ▼
organizador.py    db.py
Lógica negocio    Capa datos
os · shutil       sqlite3
                     │
                     ▼
               organizador.db
```

**Regla de dependencias:** `organizador.py` y `db.py` no importan Flask. `app.py` es el único que conoce ambas capas. Esto permite testear la lógica de negocio y la BD de forma completamente independiente.

---

## Seguridad

- **Carpetas del sistema protegidas** — `C:\Windows`, `C:\Program Files` y similares están bloqueadas. La protección lee las rutas desde las variables de entorno del sistema, no las asume fijas.
- **CSRF** — todos los formularios POST están protegidos con tokens mediante `Flask-WTF`.
- **SQL seguro** — todas las queries usan parámetros posicionales `?`. Sin concatenación de strings ni f-strings en SQL.
- **SECRET_KEY** — siempre desde variable de entorno, nunca en el código fuente.
- **Escapado automático** — Jinja2 escapa todo por defecto. Sin uso de `| safe` para datos del sistema de archivos.

---

## Variables de entorno

Documentadas en `.env.example`:

| Variable | Requerida | Descripción |
|---|---|---|
| `SECRET_KEY` | Recomendada | Clave de firma de cookies de sesión Flask |

---

## Referencia rápida de comandos

```cmd
:: Activar entorno virtual
venv\Scripts\activate

:: Instalar dependencias
pip install -r requirements.txt

:: Arrancar la app
python app.py

:: Ejecutar todos los tests
venv\Scripts\pytest tests\ -v

:: Generar SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"
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
