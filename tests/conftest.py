import os
import shutil
import tempfile

import pytest

import organizador.db as db_module


@pytest.fixture
def carpeta_temporal():
    directorio = tempfile.mkdtemp()
    nombres = ["informe.pdf", "foto.jpg", "video.mp4", "musica.mp3",
               "programa.exe", "comprimido.zip", "desconocido.xyz"]
    for nombre in nombres:
        open(os.path.join(directorio, nombre), "w").close()
    yield directorio
    shutil.rmtree(directorio, ignore_errors=True)


@pytest.fixture
def bd_temporal(tmp_path, monkeypatch):
    monkeypatch.setattr(db_module, "DB", str(tmp_path / "test.db"))
    monkeypatch.setattr(db_module, "_db_inicializada", False)
    db_module.init_db()
    yield
    monkeypatch.setattr(db_module, "_db_inicializada", False)


@pytest.fixture
def cliente(tmp_path, monkeypatch):
    monkeypatch.setattr(db_module, "DB", str(tmp_path / "test.db"))
    monkeypatch.setattr(db_module, "_db_inicializada", False)
    import app as app_module
    app_module.app.config["TESTING"] = True
    app_module.app.config["WTF_CSRF_ENABLED"] = False
    app_module.app.config["SECRET_KEY"] = "clave-test"
    db_module.init_db()
    with app_module.app.test_client() as c:
        yield c
    monkeypatch.setattr(db_module, "_db_inicializada", False)
