# Tasks — Organizador Inteligente

## Estado del proyecto

Implementación completa. Todas las tareas base y opcionales están terminadas.

---

## Tareas completadas

- [x] 1. Estructura del proyecto Flask con patrón MVC de tres capas (`app.py`, `organizador/`, `templates/`, `static/`)
- [x] 2. Módulo `organizador.py`: `analizar_carpeta`, `organizar_archivos`, `deshacer_operaciones`, `obtener_resumen`, `buscar_archivos`
- [x] 3. Módulo `db.py`: `init_db` idempotente, `registrar_log`, `guardar_operaciones` con detalle por fila, `obtener_historial`
- [x] 4. Rutas Flask completas: `/`, `/seleccionar-carpeta`, `/analizar`, `/organizar`, `/deshacer`, `/buscar`, `/historial`, `/modo-oscuro`, `/limpiar`
- [x] 5. Protección de carpetas del sistema mediante `ruta_permitida()` y `CARPETAS_PROTEGIDAS`
- [x] 6. `SECRET_KEY` cargada desde variable de entorno con fallback `os.urandom(24)`
- [x] 7. `deshacer_operaciones` con manejo de errores por archivo (devuelve `(restaurados, errores)`)
- [x] 8. CSS con variables en `:root`, modo oscuro via clase `.dark`, sin valores de color repetidos
- [x] 9. Templates `index.html`, `historial.html`, `resultado.html` y `detalle_operacion.html` con modo oscuro consistente
- [x] 10. Filtrado cliente-side con JavaScript vanilla (buscador + filtros por categoría)
- [x] 11. `requirements.txt` con versiones fijas (`Flask==3.1.1`, `python-dotenv==1.1.1`, `Flask-WTF==1.3.0`)
- [x] 12. `.env.example` documentando la variable `SECRET_KEY`
- [x] 13. Steering files en `.kiro/steering/` (`project.md`, `conventions.md`, `database.md`)
- [x] 14. Conectar el endpoint `/buscar` al frontend — búsqueda server-side con SSE para carpetas con muchos archivos
- [x] 15. Añadir protección CSRF a los formularios POST (`/organizar`, `/deshacer`, `/modo-oscuro`)

---

## Tareas opcionales (completadas)

- [x] 16. Limitar el volumen de `session["ultima_operacion"]` para evitar superar el límite de 4 KB de la cookie
- [x] 17. Soporte para recursividad opcional — checkbox "Incluir subcarpetas" y parámetro `incluir_subcarpetas` en `analizar_carpeta` y `organizar_archivos`
- [x] 18. Vista de detalle de operaciones en historial — ruta `/historial/<int:lote_id>` y template `detalle_operacion.html`
- [x] 19. Exportar historial a CSV — ruta `/historial/exportar` con `csv.writer` de stdlib
- [x] 20. Indicador de progreso SSE — endpoint `/organizar/progreso` y barra `<progress>` en `index.html`
- [x] 21. Type hints completos en `organizador.py` y `db.py`
- [x] 22. Refactorización DRY/KISS — `_info_archivo`, `_consultar`, `_guardar_en_sesion`, `_crearCelda`; eliminados comentarios y docstrings
- [x] 23. Refactorización SRP — `ruta_permitida()` y `CARPETAS_PROTEGIDAS` movidos de `app.py` a `organizador.py`

---

## Tareas pendientes

- [x] 24. Crear suite de tests básica con `pytest` *
  - `tests/test_organizador.py`: `analizar_carpeta`, `organizar_archivos`, `deshacer_operaciones`, `obtener_resumen`, `buscar_archivos`
  - `tests/test_db.py`: `init_db`, `registrar_log`, `guardar_operaciones`, `obtener_historial`
  - `tests/test_rutas.py`: rutas principales con el cliente de pruebas de Flask
  - Añadir `pytest` a `requirements.txt` con versión fija
