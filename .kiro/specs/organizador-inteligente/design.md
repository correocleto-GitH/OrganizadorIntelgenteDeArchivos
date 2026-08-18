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
└──────┬────────────────────────┬────────────────────-┘
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
- `app.py` importa de `organizador.py` y `db.py`. No hace `os.path` ni SQL directamente.
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
| `/deshacer` | POST | Llama a `deshacer_operaciones()` con datos de sesión |
| `/buscar` | GET | Devuelve JSON para búsqueda programática |
| `/historial` | GET | Renderiza tabla con `obtener_historial()` |
| `/modo-oscuro` | POST | Alterna `session["modo_oscuro"]` |
| `/limpiar` | GET | Limpia sesión y redirige al inicio |

**Estado de sesión**:
```
session["carpeta"]          → str  ruta absoluta activa
session["ultima_operacion"] → list operaciones del último organizar real
session["simulacion"]       → list operaciones de la última simulación
session["modo_oscuro"]      → bool preferencia visual
```

**Context processor**: inyecta `modo_oscuro` en todos los templates automáticamente.

**Protección de rutas del sistema**:
```python
CARPETAS_PROTEGIDAS = [
    os.environ.get("SystemRoot", r"C:\Windows").lower(),
    os.environ.get("ProgramFiles", r"C:\Program Files").lower(),
    os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)").lower()
]
```
`ruta_permitida(ruta)` verifica que `os.path.abspath(ruta)` no coincida ni sea subdirectorio de ninguna carpeta protegida.

### 2.2 `organizador/organizador.py` — Lógica de negocio

**Constantes**:
```python
CATEGORIAS: dict[str, list[str]]  # extensión → categoría
ICONOS: dict[str, str]            # categoría → emoji
```

**API pública**:

```python
def analizar_carpeta(ruta: str, incluir_subcarpetas: bool = False) -> list[dict]
# Devuelve lista de {archivo, extension, categoria, icono, ruta}

def organizar_archivos(ruta: str, simulacion: bool = False) -> list[dict]
# Devuelve lista de {archivo, categoria, origen, destino}
# Si simulacion=False, ejecuta shutil.move()

def deshacer_operaciones(operaciones: list[dict]) -> tuple[list, list]
# Devuelve (restaurados, errores)
# Procesa en orden inverso; errores no detienen el resto

def obtener_resumen(archivos: list[dict]) -> dict[str, int]
# Devuelve {categoria: conteo} inicializado a 0

def buscar_archivos(ruta: str, termino: str = "", categoria: str = "Todas") -> list[dict]
# Filtra por nombre y/o categoría
```

**Función interna**:
```python
def _destino_unico(carpeta: str, archivo: str) -> str
# Añade sufijo _1, _2... si el destino ya existe
```

### 2.3 `organizador/db.py` — Capa de datos

**Tablas**:

```
historial   → log de eventos (tipo, ruta, detalle)
operaciones → detalle por archivo (archivo, categoria, origen, destino)
```

**API pública**:
```python
def init_db() -> None           # idempotente via _db_inicializada flag
def registrar_log(tipo, ruta, detalle) -> None
def guardar_operaciones(operaciones: list[dict]) -> None
def obtener_historial() -> list[dict]   # últimas 100, DESC por id
```

**Patrón de conexión** (todas las funciones):
```python
con = conectar()
try:
    # operaciones SQL con parámetros ?
    con.commit()
finally:
    con.close()
```

## 3. Flujo de datos principal

### Organizar archivos

```
Usuario → POST /organizar
  app.py: valida sesión["carpeta"]
    → organizador.py: organizar_archivos(ruta, simulacion=False)
        → analizar_carpeta(ruta)           # lista archivos
        → _destino_unico(dir, archivo)     # evita colisiones
        → shutil.move(origen, destino)     # mueve
        → devuelve lista de operaciones
    → db.py: guardar_operaciones(ops)      # persiste detalle
    → db.py: registrar_log("ORGANIZACION") # persiste evento
    → session["ultima_operacion"] = ops   # guarda para deshacer
  → flash + redirect /
```

### Deshacer

```
Usuario → POST /deshacer
  app.py: ops = session["ultima_operacion"]
    → organizador.py: deshacer_operaciones(ops)
        para cada op (reversed):
            shutil.move(destino, origen)  # restaura
            si falla → acumula en errores[]
        devuelve (restaurados[], errores[])
    → db.py: registrar_log("DESHACER")
    → session.pop("ultima_operacion")
  → flash(restaurados) + flash(errores) + redirect /
```

## 4. Modelo de datos SQLite

```sql
-- Eventos de alto nivel
CREATE TABLE historial (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha   TEXT    DEFAULT CURRENT_TIMESTAMP,
    tipo    TEXT    NOT NULL,
    ruta    TEXT,
    detalle TEXT
);

-- Detalle por archivo
CREATE TABLE operaciones (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha     TEXT    DEFAULT CURRENT_TIMESTAMP,
    archivo   TEXT    NOT NULL,
    categoria TEXT,
    origen    TEXT    NOT NULL,
    destino   TEXT    NOT NULL
);
```

## 5. Frontend

### Templates Jinja2

Tres vistas independientes que comparten el mismo sistema de diseño:

| Template | Propósito |
|---|---|
| `index.html` | Vista principal: selector de carpeta, análisis, acciones, tabla de archivos |
| `historial.html` | Tabla paginada de eventos del historial |
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

Clases de layout: `topbar`, `brand`, `container`, `card`, `section-title`, `hero`, `stats`, `stat`, `table-wrap`, `badge`, `action-grid`, `filters`, `filter`, `btn`, `alert`, `path-form`, `search`.

### JavaScript — `static/js/script.js`

Filtrado cliente-side en tiempo real: escucha `input` en `#buscador` y `click` en `.filter`. Oculta/muestra filas de `#tabla` sin request al servidor. Usa optional chaining para no fallar en páginas sin tabla.

## 6. Variables de entorno

| Variable | Requerida | Descripción |
|---|---|---|
| `SECRET_KEY` | Recomendada | Clave de firma de sesión Flask. Si ausente, se genera con `os.urandom(24)` (sesiones no persisten entre reinicios) |

Cargadas con `python-dotenv` desde `.env` (no versionado). Documentadas en `.env.example`.

## 7. Seguridad

- SQL: parámetros posicionales `?` siempre
- Sesiones: firmadas con `SECRET_KEY`; nunca se serializa información sensible
- Rutas: `ruta_permitida()` bloquea carpetas del sistema antes de cualquier operación
- Templates: Jinja2 escapa por defecto; no usar `| safe` con datos de rutas del sistema

## 8. Configuración del entorno

```
Python 3.x (con tkinter — no Python slim)
pip install -r requirements.txt   # Flask==3.1.1, python-dotenv==1.1.1
python app.py                     # arranca en http://127.0.0.1:5000
```

La app es local (Windows). No está diseñada para despliegue en servidor remoto (tkinter requiere display local).
