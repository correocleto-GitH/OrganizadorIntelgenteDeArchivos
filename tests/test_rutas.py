import os

import pytest


# ---------------------------------------------------------------------------
# GET /
# ---------------------------------------------------------------------------

def test_inicio_status_200(cliente):
    resp = cliente.get("/")
    assert resp.status_code == 200


def test_inicio_devuelve_html(cliente):
    resp = cliente.get("/")
    assert b"<html" in resp.data.lower()


# ---------------------------------------------------------------------------
# POST /analizar
# ---------------------------------------------------------------------------

def test_analizar_ruta_invalida_redirige(cliente):
    resp = cliente.post("/analizar", data={"carpeta": r"C:\ruta\que\no\existe\jamas"})
    assert resp.status_code == 302


def test_analizar_ruta_valida_redirige_a_inicio(cliente, tmp_path):
    resp = cliente.post("/analizar", data={"carpeta": str(tmp_path)})
    assert resp.status_code == 302
    assert resp.headers["Location"].endswith("/")


# ---------------------------------------------------------------------------
# GET /historial
# ---------------------------------------------------------------------------

def test_historial_status_200(cliente):
    resp = cliente.get("/historial")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# GET /historial/exportar
# ---------------------------------------------------------------------------

def test_exportar_historial_status_200(cliente):
    resp = cliente.get("/historial/exportar")
    assert resp.status_code == 200


def test_exportar_historial_content_type_csv(cliente):
    resp = cliente.get("/historial/exportar")
    assert "text/csv" in resp.content_type


# ---------------------------------------------------------------------------
# GET /buscar
# ---------------------------------------------------------------------------

def test_buscar_con_carpeta_en_sesion(cliente, tmp_path):
    with cliente.session_transaction() as sess:
        sess["carpeta"] = str(tmp_path)
    resp = cliente.get("/buscar")
    assert resp.status_code == 200
    datos = resp.get_json()
    assert "archivos" in datos
    assert "total" in datos


# ---------------------------------------------------------------------------
# POST /modo-oscuro
# ---------------------------------------------------------------------------

def test_modo_oscuro_redirige(cliente):
    resp = cliente.post("/modo-oscuro")
    assert resp.status_code == 302


# ---------------------------------------------------------------------------
# GET /limpiar
# ---------------------------------------------------------------------------

def test_limpiar_redirige(cliente):
    resp = cliente.get("/limpiar")
    assert resp.status_code == 302


def test_limpiar_elimina_carpeta_de_sesion(cliente, tmp_path):
    with cliente.session_transaction() as sess:
        sess["carpeta"] = str(tmp_path)
    cliente.get("/limpiar")
    with cliente.session_transaction() as sess:
        assert "carpeta" not in sess
