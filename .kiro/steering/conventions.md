# Convenciones de código

## Nomenclatura

- **Variables y funciones** en `snake_case` en **español**: `analizar_carpeta`, `ruta_permitida`, `obtener_resumen`
- **Constantes de módulo** en `MAYUSCULAS`: `CATEGORIAS`, `ICONOS`, `CARPETAS_PROTEGIDAS`, `DB`
- **Funciones internas** (no parte de la API pública del módulo) con prefijo `_`: `_destino_unico`
- **Rutas Flask** en kebab-case en español: `/seleccionar-carpeta`, `/modo-oscuro`
- **Claves de sesión Flask** en `snake_case` en español: `session["ultima_operacion"]`, `session["modo_oscuro"]`

## Estructura de archivos

- `app.py` solo contiene rutas Flask y lógica de sesión. **No hace operaciones de archivos ni SQL directamente.**
- `organizador/organizador.py` contiene toda la lógica de negocio. No importa Flask.
- `organizador/db.py` contiene toda la persistencia SQLite. No importa Flask.
- Nuevas funcionalidades de archivos van en `organizador.py`; nuevas consultas van en `db.py`.

## Python

- Imports estándar al inicio, agrupados: stdlib primero, luego paquetes externos, luego módulos propios.
- Funciones pequeñas con responsabilidad única.
- No usar `import *`.
- Tipos de retorno explícitos cuando la función devuelve varios valores (usar tuplas nombradas o desempacar en el llamador).
- `deshacer_operaciones` devuelve `(restaurados: list, errores: list)` — siempre desempacar la tupla en `app.py`.

## Manejo de errores

- Los errores de validación de usuario en `app.py` se comunican con `flash()` + `redirect`. Nunca se deja pasar una ruta inválida.
- Los errores de operaciones de archivos se acumulan en una lista y se devuelven al llamador. No interrumpir el resto del proceso.
- `ruta_permitida()` captura cualquier `Exception` y devuelve `False` como fallback seguro.
- Nunca usar `except:` sin tipo. Mínimo `except Exception as e:`.

## Base de datos (SQLite)

Ver `database.md` para el esquema y convenciones de acceso.

## Templates Jinja2

- Todos los templates heredan el modo oscuro mediante `class="{{ 'dark' if modo_oscuro else '' }}"` en la etiqueta `<html>`.
- El `@app.context_processor` en `app.py` inyecta `modo_oscuro` en todos los templates automáticamente — no hace falta pasarlo explícitamente en cada `render_template`.
- No usar `{{ variable | safe }}` con datos provenientes de rutas del sistema de archivos.
- Las clases CSS del proyecto son: `topbar`, `brand`, `container`, `card`, `section-title`, `stats`, `stat`, `table-wrap`, `badge`, `action-grid`, `filters`, `filter`, `btn`, `primary`, `success`, `warning`, `secondary`, `full`, `alert`, `hero`, `path-form`, `search`.

## CSS

- Usar variables CSS definidas en `:root` en `estilos.css`. **No repetir valores de color en el CSS**.
- Variables disponibles: `--color-primary`, `--color-primary-bg`, `--color-success`, `--color-warning`, `--color-secondary`, `--color-border`, `--color-surface`, `--color-bg`, `--color-text`, `--color-muted`, `--color-muted-2`, `--radius-card`, `--radius-btn`, `--shadow-card`.
- El modo oscuro sobreescribe variables en `.dark { }`, no duplica reglas.
- CSS formateado con una declaración por línea (no minificado en el source).

## Seguridad

- `SECRET_KEY` siempre desde variable de entorno (`os.environ.get("SECRET_KEY")`). Nunca hardcodeada.
- Las rutas del sistema de archivos siempre pasan por `ruta_permitida()` antes de usarse.
- Las carpetas protegidas se leen de variables de entorno del SO (`SystemRoot`, `ProgramFiles`).
- Las queries SQL siempre usan parámetros posicionales `?` — nunca concatenación de strings.

## Dependencias

- Fijar versiones exactas en `requirements.txt` (`Flask==3.1.1`, no rangos).
- No añadir dependencias externas sin justificación explícita. El proyecto usa stdlib al máximo.
- Documentar cualquier prerrequisito no declarable en pip (ej: `tkinter` requiere Python completo, no slim).
