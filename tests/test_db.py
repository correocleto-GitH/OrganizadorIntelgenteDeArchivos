import pytest

import organizador.db as db_module
from organizador.db import (
    guardar_operaciones,
    obtener_historial,
    obtener_operaciones_por_lote,
    registrar_log,
)


# ---------------------------------------------------------------------------
# init_db
# ---------------------------------------------------------------------------

def test_init_db_crea_tabla_historial(bd_temporal):
    con = db_module.conectar()
    try:
        tablas = con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='historial'"
        ).fetchall()
        assert len(tablas) == 1
    finally:
        con.close()


def test_init_db_crea_tabla_operaciones(bd_temporal):
    con = db_module.conectar()
    try:
        tablas = con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='operaciones'"
        ).fetchall()
        assert len(tablas) == 1
    finally:
        con.close()


def test_init_db_es_idempotente(tmp_path, monkeypatch):
    monkeypatch.setattr(db_module, "DB", str(tmp_path / "idem.db"))
    monkeypatch.setattr(db_module, "_db_inicializada", False)
    db_module.init_db()
    db_module._db_inicializada = False
    db_module.init_db()
    con = db_module.conectar()
    try:
        tablas = [
            r[0] for r in
            con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        ]
        assert "historial" in tablas
        assert "operaciones" in tablas
    finally:
        con.close()
    monkeypatch.setattr(db_module, "_db_inicializada", False)


# ---------------------------------------------------------------------------
# registrar_log
# ---------------------------------------------------------------------------

def test_registrar_log_inserta_fila(bd_temporal):
    registrar_log("TEST", "/ruta/prueba", "detalle de prueba")
    historial = obtener_historial()
    assert len(historial) == 1
    assert historial[0]["tipo"] == "TEST"
    assert historial[0]["ruta"] == "/ruta/prueba"
    assert historial[0]["detalle"] == "detalle de prueba"


def test_registrar_log_multiples_inserciones(bd_temporal):
    registrar_log("A", "/ruta/a", "primera")
    registrar_log("B", "/ruta/b", "segunda")
    registrar_log("C", "/ruta/c", "tercera")
    historial = obtener_historial()
    assert len(historial) == 3


# ---------------------------------------------------------------------------
# guardar_operaciones
# ---------------------------------------------------------------------------

def test_guardar_operaciones_devuelve_lote_id(bd_temporal):
    ops = [{"archivo": "test.txt", "categoria": "Documentos", "origen": "/a/test.txt", "destino": "/b/test.txt"}]
    lote_id = guardar_operaciones(ops)
    assert lote_id is not None
    assert isinstance(lote_id, str)


def test_guardar_operaciones_lista_vacia(bd_temporal):
    resultado = guardar_operaciones([])
    assert resultado is None


def test_guardar_operaciones_recuperables_por_lote(bd_temporal):
    ops = [
        {"archivo": "a.pdf", "categoria": "Documentos", "origen": "/origen/a.pdf", "destino": "/destino/a.pdf"},
        {"archivo": "b.jpg", "categoria": "Imagenes", "origen": "/origen/b.jpg", "destino": "/destino/b.jpg"},
    ]
    lote_id = guardar_operaciones(ops)
    recuperadas = obtener_operaciones_por_lote(lote_id)
    assert len(recuperadas) == 2
    archivos = {r["archivo"] for r in recuperadas}
    assert archivos == {"a.pdf", "b.jpg"}


# ---------------------------------------------------------------------------
# obtener_historial
# ---------------------------------------------------------------------------

def test_obtener_historial_devuelve_lista_de_dicts(bd_temporal):
    registrar_log("TEST", "/ruta", "detalle")
    resultado = obtener_historial()
    assert isinstance(resultado, list)
    assert isinstance(resultado[0], dict)


def test_obtener_historial_orden_descendente(bd_temporal):
    registrar_log("PRIMERO", "/ruta", "primero")
    registrar_log("SEGUNDO", "/ruta", "segundo")
    historial = obtener_historial()
    assert historial[0]["tipo"] == "SEGUNDO"
    assert historial[1]["tipo"] == "PRIMERO"


def test_obtener_historial_limite_100(bd_temporal):
    for i in range(105):
        registrar_log("BULK", "/ruta", f"entrada {i}")
    historial = obtener_historial()
    assert len(historial) == 100
