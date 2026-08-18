import os
import shutil

import pytest

from organizador.organizador import (
    analizar_carpeta,
    buscar_archivos,
    deshacer_operaciones,
    obtener_categoria,
    obtener_resumen,
    organizar_archivos,
    ruta_permitida,
)


# ---------------------------------------------------------------------------
# obtener_categoria
# ---------------------------------------------------------------------------

def test_categoria_pdf():
    assert obtener_categoria(".pdf") == "Documentos"


def test_categoria_jpg():
    assert obtener_categoria(".jpg") == "Imagenes"


def test_categoria_mp4():
    assert obtener_categoria(".mp4") == "Videos"


def test_categoria_mp3():
    assert obtener_categoria(".mp3") == "Audio"


def test_categoria_zip():
    assert obtener_categoria(".zip") == "Comprimidos"


def test_categoria_exe():
    assert obtener_categoria(".exe") == "Programas"


def test_categoria_desconocida():
    assert obtener_categoria(".xyz") == "Otros"


def test_categoria_mayusculas():
    assert obtener_categoria(".PDF") == obtener_categoria(".pdf")
    assert obtener_categoria(".JPG") == obtener_categoria(".jpg")


# ---------------------------------------------------------------------------
# ruta_permitida
# ---------------------------------------------------------------------------

def test_ruta_normal_permitida(tmp_path):
    assert ruta_permitida(str(tmp_path)) is True


def test_ruta_system_root_bloqueada():
    system_root = os.environ.get("SystemRoot", r"C:\Windows")
    assert ruta_permitida(system_root) is False


def test_ruta_subcarpeta_system_root_bloqueada():
    system_root = os.environ.get("SystemRoot", r"C:\Windows")
    subcarpeta = os.path.join(system_root, "System32")
    assert ruta_permitida(subcarpeta) is False


def test_ruta_vacia_bloqueada():
    assert ruta_permitida("") is False


# ---------------------------------------------------------------------------
# analizar_carpeta
# ---------------------------------------------------------------------------

def test_analizar_carpeta_cantidad(carpeta_temporal):
    resultado = analizar_carpeta(carpeta_temporal)
    assert len(resultado) == 7


def test_analizar_carpeta_claves(carpeta_temporal):
    resultado = analizar_carpeta(carpeta_temporal)
    claves_esperadas = {"archivo", "extension", "categoria", "icono", "ruta"}
    for item in resultado:
        assert claves_esperadas.issubset(item.keys())


def test_analizar_carpeta_ruta_invalida():
    assert analizar_carpeta(r"C:\ruta\que\no\existe\jamas") == []


def test_analizar_carpeta_ruta_vacia():
    assert analizar_carpeta("") == []


def test_analizar_carpeta_incluir_subcarpetas(carpeta_temporal):
    subcarpeta = os.path.join(carpeta_temporal, "sub")
    os.makedirs(subcarpeta)
    open(os.path.join(subcarpeta, "extra.txt"), "w").close()
    resultado = analizar_carpeta(carpeta_temporal, incluir_subcarpetas=True)
    archivos = [r["archivo"] for r in resultado]
    assert "extra.txt" in archivos
    assert len(resultado) == 8


# ---------------------------------------------------------------------------
# organizar_archivos
# ---------------------------------------------------------------------------

def test_organizar_simulacion_no_mueve(carpeta_temporal):
    antes = set(os.listdir(carpeta_temporal))
    organizar_archivos(carpeta_temporal, simulacion=True)
    despues = set(os.listdir(carpeta_temporal))
    assert antes == despues


def test_organizar_real_mueve_archivos(carpeta_temporal):
    organizar_archivos(carpeta_temporal, simulacion=False)
    archivos_raiz = [
        f for f in os.listdir(carpeta_temporal)
        if os.path.isfile(os.path.join(carpeta_temporal, f))
    ]
    assert archivos_raiz == []


def test_organizar_claves_operacion(carpeta_temporal):
    ops = organizar_archivos(carpeta_temporal, simulacion=True)
    claves_esperadas = {"archivo", "categoria", "origen", "destino"}
    for op in ops:
        assert claves_esperadas.issubset(op.keys())


def test_organizar_callback_progreso(carpeta_temporal):
    llamadas = []

    def cb(actual, total):
        llamadas.append((actual, total))

    ops = organizar_archivos(carpeta_temporal, simulacion=True, callback_progreso=cb)
    assert len(llamadas) == len(ops)


# ---------------------------------------------------------------------------
# deshacer_operaciones
# ---------------------------------------------------------------------------

def test_deshacer_restaura_archivos(carpeta_temporal):
    ops = organizar_archivos(carpeta_temporal, simulacion=False)
    restaurados, errores = deshacer_operaciones(ops)
    assert len(restaurados) == 7
    assert errores == []
    archivos_presentes = os.listdir(carpeta_temporal)
    for op in ops:
        assert op["archivo"] in archivos_presentes


def test_deshacer_lista_vacia():
    restaurados, errores = deshacer_operaciones([])
    assert restaurados == []
    assert errores == []


def test_deshacer_devuelve_tupla_dos_listas():
    resultado = deshacer_operaciones([])
    assert isinstance(resultado, tuple)
    assert len(resultado) == 2
    restaurados, errores = resultado
    assert isinstance(restaurados, list)
    assert isinstance(errores, list)


# ---------------------------------------------------------------------------
# obtener_resumen
# ---------------------------------------------------------------------------

def test_resumen_categorias_correctas(carpeta_temporal):
    archivos = analizar_carpeta(carpeta_temporal)
    resumen = obtener_resumen(archivos)
    assert resumen["Documentos"] == 1   # informe.pdf
    assert resumen["Imagenes"] == 1     # foto.jpg
    assert resumen["Videos"] == 1       # video.mp4
    assert resumen["Audio"] == 1        # musica.mp3
    assert resumen["Programas"] == 1    # programa.exe
    assert resumen["Comprimidos"] == 1  # comprimido.zip
    assert resumen["Otros"] == 1        # desconocido.xyz


def test_resumen_lista_vacia():
    resumen = obtener_resumen([])
    for valor in resumen.values():
        assert valor == 0


# ---------------------------------------------------------------------------
# buscar_archivos
# ---------------------------------------------------------------------------

def test_buscar_sin_filtros(carpeta_temporal):
    resultado = buscar_archivos(carpeta_temporal)
    assert len(resultado) == 7


def test_buscar_por_termino(carpeta_temporal):
    resultado = buscar_archivos(carpeta_temporal, termino="foto")
    assert len(resultado) == 1
    assert resultado[0]["archivo"] == "foto.jpg"


def test_buscar_por_categoria(carpeta_temporal):
    resultado = buscar_archivos(carpeta_temporal, categoria="Imagenes")
    assert all(r["categoria"] == "Imagenes" for r in resultado)


def test_buscar_termino_inexistente(carpeta_temporal):
    resultado = buscar_archivos(carpeta_temporal, termino="zzznoencontrado")
    assert resultado == []
