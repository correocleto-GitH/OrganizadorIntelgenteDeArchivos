---
inclusion: fileMatch
fileMatchPattern: "organizador/db.py"
---

# Base de datos — SQLite

## Esquema

### Tabla `historial`
Registro de eventos de alto nivel (una fila por acción del usuario).

```sql
CREATE TABLE IF NOT EXISTS historial (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha   TEXT    DEFAULT CURRENT_TIMESTAMP,
    tipo    TEXT    NOT NULL,   -- SELECCION | ANALISIS | SIMULACION | ORGANIZACION | DESHACER | OPERACIONES
    ruta    TEXT,               -- Ruta de la carpeta afectada
    detalle TEXT                -- Descripción legible, ej: "42 archivos organizados"
)
```

### Tabla `operaciones`
Registro detallado de cada movimiento de archivo individual.

```sql
CREATE TABLE IF NOT EXISTS operaciones (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    fecha     TEXT    DEFAULT CURRENT_TIMESTAMP,
    archivo   TEXT    NOT NULL,
    categoria TEXT,             -- Documentos | Imagenes | Videos | Audio | Comprimidos | Programas | Otros
    origen    TEXT    NOT NULL, -- Ruta absoluta original
    destino   TEXT    NOT NULL  -- Ruta absoluta final
)
```

## Convenciones de acceso

- **Patrón de conexión obligatorio**: abrir con `conectar()`, operar en `try:`, cerrar en `finally: con.close()`. Nunca usar `with conectar() as con` para este propósito (gestiona transacción, no cierre).
- **`init_db()` se llama una sola vez** al arrancar la app (en `if __name__ == "__main__":`). El flag de módulo `_db_inicializada` garantiza idempotencia.
- **Nunca llamar `init_db()` dentro de otras funciones** de `db.py`.
- **Parámetros siempre posicionales** con `?`. Nunca formatear SQL con f-strings o concatenación.
- `registrar_log()` es la función central de auditoría. Toda acción relevante del sistema debe registrarse con ella.
- `guardar_operaciones()` persiste el detalle completo (origen → destino) de cada archivo movido, además de llamar a `registrar_log()` al final.
- `obtener_historial()` devuelve las últimas 100 entradas de `historial` como lista de `dict`.

## Agregar nuevas tablas o columnas

1. Añadir el `CREATE TABLE IF NOT EXISTS` correspondiente dentro de `init_db()`.
2. Si se modifica una tabla existente, usar `ALTER TABLE ... ADD COLUMN` también dentro de `init_db()`, protegido con `try/except` para no fallar si la columna ya existe.
3. Crear las funciones CRUD correspondientes en `db.py`. No poner SQL en `app.py` ni en `organizador.py`.
