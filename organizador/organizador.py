import os
import shutil
from collections.abc import Callable

CARPETAS_PROTEGIDAS: list[str] = [
    os.environ.get("SystemRoot", r"C:\Windows").lower(),
    os.environ.get("ProgramFiles", r"C:\Program Files").lower(),
    os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)").lower(),
]


def ruta_permitida(ruta: str) -> bool:
    try:
        if not ruta or not ruta.strip():
            return False
        ruta = os.path.abspath(ruta).lower()
        return not any(ruta == p or ruta.startswith(p + os.sep) for p in CARPETAS_PROTEGIDAS)
    except Exception:
        return False


CATEGORIAS: dict[str, list[str]] = {
    "Documentos":  [".doc", ".docx", ".pdf", ".txt", ".xls", ".xlsx", ".ppt", ".pptx", ".csv", ".odt", ".ods"],
    "Imagenes":    [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".svg", ".tiff", ".ico"],
    "Videos":      [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".mpeg"],
    "Audio":       [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
    "Comprimidos": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".jar", ".tar"],
    "Programas":   [".exe", ".msi", ".bat", ".cmd", ".ps1"]
}
ICONOS: dict[str, str] = {
    "Documentos":  "📄",
    "Imagenes":    "🖼️",
    "Videos":      "🎬",
    "Audio":       "🎵",
    "Comprimidos": "📦",
    "Programas":   "⚙️",
    "Otros":       "📁"
}


def obtener_categoria(extension: str) -> str:
    ext = extension.lower()
    for categoria, extensiones in CATEGORIAS.items():
        if ext in extensiones:
            return categoria
    return "Otros"


def _info_archivo(ruta_archivo: str) -> dict:
    archivo = os.path.basename(ruta_archivo)
    _, extension = os.path.splitext(archivo)
    categoria = obtener_categoria(extension)
    return {
        "archivo":   archivo,
        "extension": extension.lower(),
        "categoria": categoria,
        "icono":     ICONOS.get(categoria, "📁"),
        "ruta":      ruta_archivo,
    }


def analizar_carpeta(ruta: str, incluir_subcarpetas: bool = False) -> list[dict]:
    if not ruta or not os.path.isdir(ruta):
        return []
    if incluir_subcarpetas:
        return [
            _info_archivo(os.path.join(root, f))
            for root, _, files in os.walk(ruta)
            for f in files
        ]
    return [
        _info_archivo(os.path.join(ruta, f))
        for f in os.listdir(ruta)
        if os.path.isfile(os.path.join(ruta, f))
    ]


def _destino_unico(carpeta: str, archivo: str) -> str:
    destino = os.path.join(carpeta, archivo)
    if not os.path.exists(destino):
        return destino
    nombre, ext = os.path.splitext(archivo)
    i = 1
    while True:
        candidato = os.path.join(carpeta, f"{nombre}_{i}{ext}")
        if not os.path.exists(candidato):
            return candidato
        i += 1


def organizar_archivos(
    ruta: str,
    simulacion: bool = False,
    incluir_subcarpetas: bool = False,
    callback_progreso: Callable[[int, int], None] | None = None
) -> list[dict]:
    items = analizar_carpeta(ruta, incluir_subcarpetas=incluir_subcarpetas)
    total = len(items)
    operaciones: list[dict] = []
    for actual, item in enumerate(items, start=1):
        origen = item["ruta"]
        destino_dir = os.path.join(ruta, item["categoria"])
        destino = _destino_unico(destino_dir, item["archivo"])
        op = {
            "archivo":   item["archivo"],
            "categoria": item["categoria"],
            "origen":    origen,
            "destino":   destino
        }
        operaciones.append(op)
        if not simulacion:
            os.makedirs(destino_dir, exist_ok=True)
            shutil.move(origen, destino)
        if callback_progreso is not None:
            callback_progreso(actual, total)
    return operaciones


def deshacer_operaciones(operaciones: list[dict]) -> tuple[list, list]:
    restaurados: list[str] = []
    errores: list[dict] = []
    for op in reversed(operaciones or []):
        if os.path.exists(op["destino"]) and not os.path.exists(op["origen"]):
            try:
                os.makedirs(os.path.dirname(op["origen"]), exist_ok=True)
                shutil.move(op["destino"], op["origen"])
                restaurados.append(op["archivo"])
            except Exception as e:
                errores.append({"archivo": op["archivo"], "error": str(e)})
    return restaurados, errores


def obtener_resumen(archivos: list[dict]) -> dict[str, int]:
    resumen: dict[str, int] = {k: 0 for k in list(CATEGORIAS.keys()) + ["Otros"]}
    for a in archivos:
        resumen[a["categoria"]] += 1
    return resumen


def buscar_archivos(ruta: str, termino: str = "", categoria: str = "Todas") -> list[dict]:
    archivos = analizar_carpeta(ruta)
    termino = termino.lower()
    return [
        a for a in archivos
        if (not termino or termino in a["archivo"].lower())
        and (categoria == "Todas" or a["categoria"] == categoria)
    ]
