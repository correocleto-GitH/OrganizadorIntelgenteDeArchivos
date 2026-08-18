# Design — Organizador Inteligente

## 1. Arquitectura general

Patrón MVC ligero de tres capas, sin ORM ni frameworks de frontend:

```
┌─────────────────────────────────────────────────────┐
│  Navegador                                          │
│  HTML + CSS (variables, modo oscuro) + JS vanilla   │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP (Flask dev server)
┌──────────────────────▼──────────────────────────────┐
│  app.py  — Controlador                              │
│  Rutas Flask + validación de entrada + sesión       │
└──────┬────────────────────────┬─────────────────────┘
       │                        │
┌──────▼──────────┐   ┌─────────▼──────────┐
│ organizador.py  │   │ db.py              │
│ Lógica negocio  │   │ Capa de datos      │
│ os + shutil     │   │ sqlite3 stdlib     │
└─────────────────┘   └────────────────────┘
                                │
                       ┌────────▼──────────┐
                       │ organizador.db    │
                       │ SQLite en disco   │
                       └───────────────────┘
```

**Reglas de dependencia**:
- `app.py` importa de `organizador.py` y `db.py`. No ejecuta `os.path` de negocio ni SQL directamente.
- `organizador.py` no importa Flask ni `db.py`.
- `db.py` no importa Flask ni `organizador.py`.

## 2. Componentes

### 2.1 `app.py` — Controlador Flask

| Ruta | Método | Descripción |
|---|---|---|
| `/` | GET | Muestra inicio; analiza la carpeta en sesión si existe |
| `/seleccionar-carpeta` | GET | Abre `tkinter.filedialog`; guarda ruta en sesión |
| `/analizar` | POST | Recibe ruta del formulario; valida y guarda en sesión |
| `/organizar` | POST | Llama a `organizar_archivos()` en modo simulación o real |
| `/organizar/progreso` | GET | Endpoint SSE; organiza archivos emitiendo progreso en tiempo real |
| `/deshacer` | POST | Llama a `deshacer_operaciones()` con datos de sesión o BD |
| `/buscar` | GET | Devuelve JSON para búsqueda server-side |
| `/historial` | GET | Renderiza tabla con `obtener_historial()` |
| `/historial/exportar` | GET | Descarga el historial completo como CSV |
| `/historial/<lote_id>` | GET | Detalle de los archivos movidos en una operación concreta |
| `/modo-oscuro` | POST | Alterna `session["modo_oscuro"]` |
| `/limpiar` | GET | Limpia sesión y redirige al inicio |

**Estado de sesión**:
```
session["carpeta"]          → str   ruta absoluta activa
session["ultima_operacion"] → list  operaciones del último organizar (≤ 50 ops)
                           → dict  {"lote_id": str, "usar_db": True} (> 50 ops)
session["simulacion"]       → list  operaciones de la última simulación
session["modo_oscuro"]      → bool  preferencia visual
```

Cuando hay más de 50 operaciones, `session["ultima_operacion"]` almacena solo el `lote_id` para no superar el límite de 4 KB de la cookie. `/deshacer` detecta el formato y recupera las operaciones de la BD si es necesario.

**Context processor**: inyecta `modo_oscuro` en todos los templates automáticamente.

**Funciones de soporte internas**:
- `_guardar_en_sesion(ops, lote_id)` — centraliza la lógica del umbral de 50 operaciones.

**CSRF**: `Flask-WTF` con `CSRFProtect(app)`. El endpoint SSE `/organizar/progreso` está exento con `@csrf.exempt`.

### 2.2 `organizador/organizador.py` — Lógica de negocio

**Constantes**:
```python
CARPETAS_PROTEGIDAS: list[str]    # rutas de sistema leídas de variables de entorno
CATEGORIAS: dict[str, list[str]]  # categoría → lista de extensiones
ICONOS: dict[str, str]            # categoría → emoji
```

**API pública**:

```python
def ruta_permitida(ruta: str) -> bool
# Devuelve False para rutas de sistema (SystemRoot, ProgramFiles) y strings vacíos

def analizar_carpeta(ruta: str, incluir_subcarpetas: bool = False) -> list[dict]
# Devuelve lista de {archivo, extension, categoria, icono, ruta}
# incluir_subcarpetas=True usa os.walk en lugar de os.listdir

def organizar_archivos(
    ruta: str,
    simulacion: bool = False,
    incluir_subcarpetas: bool = False,
    callback_progreso: Callable[[int, int], None] | None = None
) -> list[dict]
# Devuelve lista de {archivo, categoria, origen, destino}
# simulacion=False ejecuta shutil.move(); callback_progreso se invoca tras cada archivo

def deshacer_operaciones(operaciones: list[dict]) -> tuple[list, list]
# Devuelve (restaurados, errores)
# Procesa en orden inverso; errores individuales no detienen el resto

def obtener_resumen(archivos: list[dict]) -> dict[str, int]
# Devuelve {categoria: conteo} inicializado a 0 para todas las categorías

def buscar_archivos(ruta: str, termino: str = "", categoria: str = "Todas") -> list[dict]
# Filtra por nombre (substring) y/o categoría
```

**Funciones internas**:
```python
def _info_archivo(ruta_archivo: str) -> dict      # construye el dict de metadatos de un archivo
def _destino_unico(carpeta: str, archivo: str) -> str  # añade sufijo _1, _2… si el destino ya existe
```

### 2.3 `organizador/db.py` — Capa de datos

**Tablas**:
```
historial   → log de eventos de alto nivel (tipo, ruta, detalle)
operaciones → detalle por archivo movido (archivo, categoria, origen, destino, lote_id)
```

**API pública**:
```python
def init_db() -> None
# Crea tablas si no existen. Idempotente via flag _db_inicializada.
# Incluye migración ALTER TABLE para añadir lote_id si la BD es antigua.

def registrar_log(tipo: str, ruta: str, detalle: str) -> None
# Inserta una fila en historial.

def guardar_operaciones(operaciones: list[dict], lote_id: str | None = None) -> str | None
# Persiste el detalle completo de cada movimiento.
# Genera lote_id por timestamp si no se proporciona.
# Devuelve el lote_id para que app.py pueda almacenarlo en sesión.
# Llama a registrar_log() al finalizar.

def obtener_operaciones_por_lote(lote_id: str) -> list[dict]
# Devuelve todas las operaciones de un lote ordenadas por id.

def obtener_historial() -> list[dict]
# Devuelve las últimas 100 entradas de historial en orden descendente.
```

**Función interna**:
```python
def _consultar(sql: str, params: tuple = ()) -> list[dict]
# Patrón DRY para consultas de solo lectura: conectar → row_factory → execute → close
```

**Patrón de conexión** (funciones de escritura):
```python
con = conectar()
try:
    con.execute(...)   # siempre con parámetros posicionales ?
    con.commit()
finally:
    con.close()
```

## 3. Flujo de datos principal

### Organizar archivos (POST normal)

```
Usuario → POST /organizar
  app.py: valida session["carpeta"]
    → organizador.py: organizar_archivos(ruta, simulacion, incluir_subcarpetas)
        → analizar_carpeta(ruta)            # descubre archivos
        → _destino_unico(dir, archivo)      # evita colisiones
        → shutil.move(origen, destino)      # mueve (si no es simulación)
        → devuelve lista de operaciones
    → db.py: guardar_operaciones(ops)       # persiste detalle + log
    → _guardar_en_sesion(ops, lote_id)      # cookie o referencia a BD
  → flash + redirect /
```

### Organizar archivos (SSE con progreso)

```
Usuario → GET /organizar/progreso
  app.py: valida session["carpeta"] y ruta_permitida()
    → hilo secundario: organizar_archivos(..., callback_progreso=_callback)
        → _callback(actual, total) → cola.put(json)
    → generador SSE lee cola y emite eventos:
        data: {"actual": N, "total": M}
        data: {"completado": true, "total": M}
    → al completar: guardar_operaciones + _guardar_en_sesion
  → EventSource en cliente recibe eventos → actualiza barra de progreso
```

### Deshacer

```
Usuario → POST /deshacer
  app.py: entrada = session["ultima_operacion"]
    si entrada es dict con usar_db=True:
      → db.py: obtener_operaciones_por_lote(lote_id)
    → organizador.py: deshacer_operaciones(ops)
        para cada op (reversed):
            shutil.move(destino, origen)   # restaura
            si falla → acumula en errores[]
        devuelve (restaurados[], errores[])
    → db.py: registrar_log("DESHACER")
    → session.pop("ultima_operacion")
  → flash(restaurados) + flash(errores) + redirect /
```

## 4. Modelo de datos SQLite

```sql
CREATE TABLE historial (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha   TEXT    DEFAULT CURRENT_TIMESTAMP,
    tipo    TEXT    NOT NULL,   -- SELECCION | ANALISIS | SIMULACION | ORGANIZACION | DESHACER | OPERACIONES
    ruta    TEXT,
    detalle TEXT
);

CREATE TABLE operaciones (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha     TEXT    DEFAULT CURRENT_TIMESTAMP,
    archivo   TEXT    NOT NULL,
    categoria TEXT,
    origen    TEXT    NOT NULL,
    destino   TEXT    NOT NULL,
    lote_id   TEXT                -- agrupa las operaciones de un mismo organizar
);
```

## 5. Frontend

### Templates Jinja2

| Template | Propósito |
|---|---|
| `index.html` | Vista principal: selector de carpeta, estadísticas, tabla de archivos, acciones, barra de progreso |
| `historial.html` | Tabla de eventos con enlace "Ver detalle" y botón "Exportar CSV" |
| `detalle_operacion.html` | Tabla de archivos movidos (origen → destino) para un lote concreto |
| `resultado.html` | Vista previa alternativa antes de organizar |

Todas incluyen `class="{{ 'dark' if modo_oscuro else '' }}"` en `<html>` (inyectado vía context processor).

### CSS — `static/css/estilos.css`

Variables en `:root`:
```css
--color-primary, --color-primary-bg
--color-success, --color-warning, --color-secondary
--color-border, --color-surface, --color-bg
--color-text, --color-muted, --color-muted-2
--radius-card, --radius-btn, --shadow-card
```

Modo oscuro sobreescribe variables en `.dark {}`, sin duplicar reglas.

### JavaScript — `static/js/script.js`

Dos modos de operación según el número de archivos en tabla (`UMBRAL_SSE = 100`):

- **Modo cliente** (≤ 100 filas): filtra ocultando/mostrando filas sin request al servidor.
- **Modo servidor** (> 100 filas): llama a `GET /buscar` con debounce de 250 ms; reconstruye la tabla con el resultado.

Funciones principales:
- `interceptarOrganizar(evento)` — intercepta el submit del formulario de organizar; si hay > 100 archivos, usa SSE en lugar del POST normal y muestra la barra de progreso.
- `filtrarCliente()` — filtrado en memoria sobre las filas existentes.
- `buscarServidor()` — fetch con AbortController para cancelar búsquedas anteriores en vuelo.
- `sincronizarSubcarpetas()` — copia el estado del checkbox "Incluir subcarpetas" a los inputs ocultos de cada formulario antes del submit.

## 6. Variables de entorno

| Variable | Requerida | Descripción |
|---|---|---|
| `SECRET_KEY` | Recomendada | Clave de firma de sesión Flask. Si ausente, se genera con `os.urandom(24)` (sesiones no persisten entre reinicios) |

Cargadas con `python-dotenv` desde `.env` (no versionado). Documentadas en `.env.example`.

## 7. Seguridad

- **CSRF**: `Flask-WTF` protege todos los formularios POST. El endpoint SSE está exento.
- **SQL**: parámetros posicionales `?` siempre. Sin f-strings ni concatenación en queries.
- **Sesiones**: firmadas con `SECRET_KEY`. No se serializa información sensible.
- **Rutas**: `ruta_permitida()` en `organizador.py` bloquea `SystemRoot`, `ProgramFiles` y strings vacíos antes de cualquier operación de archivo.
- **Templates**: Jinja2 escapa por defecto. No se usa `| safe` con datos de rutas del sistema.

## 8. Tests

Suite de 52 tests con `pytest` en `tests/`:

| Archivo | Cobertura |
|---|---|
| `tests/test_organizador.py` | `obtener_categoria`, `ruta_permitida`, `analizar_carpeta`, `organizar_archivos`, `deshacer_operaciones`, `obtener_resumen`, `buscar_archivos` |
| `tests/test_db.py` | `init_db`, `registrar_log`, `guardar_operaciones`, `obtener_historial` |
| `tests/test_rutas.py` | Rutas principales con cliente de pruebas Flask |
| `tests/conftest.py` | Fixtures: `carpeta_temporal`, `bd_temporal`, `cliente` |

Ejecutar: `venv\Scripts\pytest tests\ -v`

## 9. Configuración del entorno

```
Python 3.x con tkinter (no Python slim)
pip install -r requirements.txt
python app.py   → http://127.0.0.1:5000
```

La app es exclusivamente local en Windows. `tkinter` requiere display local y no es compatible con despliegue en servidor remoto.
