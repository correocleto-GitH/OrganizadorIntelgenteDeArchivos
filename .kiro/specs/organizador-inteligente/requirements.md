# Requirements — Organizador Inteligente

## 1. Selección de carpeta

WHEN el usuario hace clic en "Seleccionar carpeta"
THE SYSTEM SHALL abrir el diálogo nativo de Windows mediante `tkinter.filedialog.askdirectory()`

WHEN el usuario selecciona una carpeta válida
THE SYSTEM SHALL guardar la ruta en la sesión y mostrar un mensaje de confirmación

WHEN el usuario cancela el diálogo sin seleccionar
THE SYSTEM SHALL mostrar un mensaje informativo y no modificar la sesión

WHEN el usuario escribe una ruta manualmente en el formulario
THE SYSTEM SHALL validar que la carpeta existe en el sistema de archivos

WHEN la ruta indicada no existe o no es un directorio
THE SYSTEM SHALL mostrar un mensaje de error y no guardar la ruta en la sesión

WHEN la carpeta seleccionada es una carpeta del sistema (Windows, Program Files, etc.)
THE SYSTEM SHALL rechazarla y mostrar un mensaje de error de seguridad

## 2. Análisis de archivos

WHEN se ha seleccionado una carpeta válida
THE SYSTEM SHALL escanear todos los archivos del nivel raíz (sin recursividad por defecto) y clasificarlos por extensión

WHEN se analiza la carpeta
THE SYSTEM SHALL asignar a cada archivo una categoría según su extensión: Documentos, Imagenes, Videos, Audio, Comprimidos, Programas u Otros

WHEN se analiza la carpeta
THE SYSTEM SHALL mostrar un resumen con el conteo de archivos por categoría

WHEN la carpeta no contiene archivos en el nivel raíz
THE SYSTEM SHALL mostrar un estado vacío sin errores

## 3. Simulación

WHEN el usuario elige el modo "Simular" y confirma
THE SYSTEM SHALL calcular las operaciones de movimiento sin ejecutar ningún `shutil.move`

WHEN termina la simulación
THE SYSTEM SHALL mostrar cuántos archivos se organizarían y registrar el evento en el historial

## 4. Organización real de archivos

WHEN el usuario elige el modo "Organizar" y confirma
THE SYSTEM SHALL mover cada archivo a una subcarpeta con el nombre de su categoría dentro de la carpeta seleccionada

WHEN el archivo destino ya existe con el mismo nombre
THE SYSTEM SHALL añadir un sufijo numérico (_1, _2, …) para evitar sobreescrituras

WHEN termina la organización
THE SYSTEM SHALL guardar el detalle de cada operación (archivo, categoría, origen, destino) en la base de datos

WHEN termina la organización
THE SYSTEM SHALL guardar la lista de operaciones en la sesión para permitir el deshacer inmediato

## 5. Deshacer

WHEN el usuario pulsa "Deshacer" y existe una operación previa en sesión
THE SYSTEM SHALL mover cada archivo de vuelta a su ruta de origen en orden inverso

WHEN un archivo individual no puede restaurarse (permisos, ruta inexistente)
THE SYSTEM SHALL registrar el error, continuar con los demás archivos y notificar al usuario por cada fallo

WHEN termina el deshacer
THE SYSTEM SHALL eliminar la última operación de la sesión y mostrar cuántos archivos se restauraron

## 6. Búsqueda y filtrado

WHEN el usuario escribe en el buscador
THE SYSTEM SHALL filtrar las filas de la tabla en tiempo real por nombre de archivo (JavaScript, lado cliente)

WHEN el usuario hace clic en un botón de categoría
THE SYSTEM SHALL mostrar únicamente los archivos de esa categoría

WHEN el usuario hace clic en "Todas"
THE SYSTEM SHALL mostrar todos los archivos sin filtro

## 7. Historial

WHEN el usuario navega a la sección de historial
THE SYSTEM SHALL mostrar las últimas 100 entradas ordenadas de más reciente a más antigua

WHEN se registra cualquier acción (selección, análisis, simulación, organización, deshacer)
THE SYSTEM SHALL insertar una fila en la tabla `historial` con tipo, ruta y descripción

## 8. Modo oscuro

WHEN el usuario activa el modo oscuro
THE SYSTEM SHALL añadir la clase CSS `dark` al elemento `<html>` y persistir la preferencia en la sesión

WHEN el usuario desactiva el modo oscuro
THE SYSTEM SHALL eliminar la clase `dark` y actualizar la sesión

WHEN el usuario navega entre páginas (inicio, historial, resultado)
THE SYSTEM SHALL mantener el estado del modo oscuro aplicado en todas las vistas

## 9. Seguridad y protección

WHEN cualquier ruta llega al servidor (formulario o sesión)
THE SYSTEM SHALL verificar que no apunta a carpetas del sistema antes de operar

WHEN la app arranca
THE SYSTEM SHALL cargar `SECRET_KEY` desde la variable de entorno; si no existe, generar una aleatoria con `os.urandom(24)`

WHEN se realiza cualquier operación SQL
THE SYSTEM SHALL usar parámetros posicionales `?`; nunca concatenar valores en el SQL

## 10. Inicialización de la base de datos

WHEN la app arranca por primera vez
THE SYSTEM SHALL crear las tablas `historial` y `operaciones` si no existen

WHEN la app ya fue iniciada anteriormente
THE SYSTEM SHALL omitir la creación de tablas (comportamiento idempotente mediante flag de módulo)
