import os, shutil

CATEGORIAS = {
    "Documentos": [".doc",".docx",".pdf",".txt",".xls",".xlsx",".ppt",".pptx",".csv",".odt",".ods"],
    "Imagenes": [".jpg",".jpeg",".png",".gif",".bmp",".webp",".svg",".tiff",".ico"],
    "Videos": [".mp4",".avi",".mkv",".mov",".wmv",".flv",".webm",".mpeg"],
    "Audio": [".mp3",".wav",".flac",".aac",".ogg",".wma",".m4a"],
    "Comprimidos": [".zip",".rar",".7z",".tar",".gz",".bz2"],
    "Programas": [".exe",".msi",".bat",".cmd",".ps1"]
}
ICONOS = {"Documentos":"📄","Imagenes":"🖼️","Videos":"🎬","Audio":"🎵","Comprimidos":"📦","Programas":"⚙️","Otros":"📁"}

def obtener_categoria(extension):
    ext = extension.lower()
    for categoria, extensiones in CATEGORIAS.items():
        if ext in extensiones:
            return categoria
    return "Otros"

def analizar_carpeta(ruta, incluir_subcarpetas=False):
    resultados = []
    if not ruta or not os.path.isdir(ruta):
        return resultados
    if incluir_subcarpetas:
        elementos = ((root, f) for root, _, fs in os.walk(ruta) for f in fs)
        for root, archivo in elementos:
            origen = os.path.join(root, archivo)
            nombre, extension = os.path.splitext(archivo)
            resultados.append({"archivo":archivo,"extension":extension.lower(),"categoria":obtener_categoria(extension),"icono":ICONOS.get(obtener_categoria(extension),"📁"),"ruta":origen})
    else:
        for archivo in os.listdir(ruta):
            origen = os.path.join(ruta, archivo)
            if os.path.isfile(origen):
                _, extension = os.path.splitext(archivo)
                categoria = obtener_categoria(extension)
                resultados.append({"archivo":archivo,"extension":extension.lower(),"categoria":categoria,"icono":ICONOS.get(categoria,"📁"),"ruta":origen})
    return resultados

def _destino_unico(carpeta, archivo):
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

def organizar_archivos(ruta, simulacion=False):
    operaciones = []
    for item in analizar_carpeta(ruta):
        origen = item["ruta"]
        destino_dir = os.path.join(ruta, item["categoria"])
        destino = _destino_unico(destino_dir, item["archivo"])
        op = {"archivo":item["archivo"],"categoria":item["categoria"],"origen":origen,"destino":destino}
        operaciones.append(op)
        if not simulacion:
            os.makedirs(destino_dir, exist_ok=True)
            shutil.move(origen, destino)
    return operaciones

def deshacer_operaciones(operaciones):
    restaurados = []
    for op in reversed(operaciones or []):
        if os.path.exists(op["destino"]) and not os.path.exists(op["origen"]):
            os.makedirs(os.path.dirname(op["origen"]), exist_ok=True)
            shutil.move(op["destino"], op["origen"])
            restaurados.append(op["archivo"])
    return restaurados

def obtener_resumen(archivos):
    resumen = {k:0 for k in list(CATEGORIAS.keys()) + ["Otros"]}
    for a in archivos:
        resumen[a["categoria"]] = resumen.get(a["categoria"], 0) + 1
    return resumen

def buscar_archivos(ruta, termino="", categoria="Todas"):
    archivos = analizar_carpeta(ruta)
    termino = termino.lower()
    return [a for a in archivos if (not termino or termino in a["archivo"].lower()) and (categoria=="Todas" or a["categoria"]==categoria)]
