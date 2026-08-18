import sqlite3
import os
import time

DB: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "organizador.db")

_db_inicializada: bool = False


def conectar() -> sqlite3.Connection:
    return sqlite3.connect(DB)


def _consultar(sql: str, params: tuple = ()) -> list[dict]:
    con = conectar()
    con.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in con.execute(sql, params)]
    finally:
        con.close()


def init_db() -> None:
    global _db_inicializada
    if _db_inicializada:
        return
    con = conectar()
    try:
        con.execute("""
            CREATE TABLE IF NOT EXISTS historial (
                id     INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha  TEXT    DEFAULT CURRENT_TIMESTAMP,
                tipo   TEXT    NOT NULL,
                ruta   TEXT,
                detalle TEXT
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS operaciones (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha       TEXT    DEFAULT CURRENT_TIMESTAMP,
                archivo     TEXT    NOT NULL,
                categoria   TEXT,
                origen      TEXT    NOT NULL,
                destino     TEXT    NOT NULL
            )
        """)
        try:
            con.execute("ALTER TABLE operaciones ADD COLUMN lote_id TEXT")
        except sqlite3.OperationalError:
            pass
        con.commit()
        _db_inicializada = True
    finally:
        con.close()


def registrar_log(tipo: str, ruta: str, detalle: str) -> None:
    con = conectar()
    try:
        con.execute(
            "INSERT INTO historial (tipo, ruta, detalle) VALUES (?, ?, ?)",
            (tipo, ruta, detalle)
        )
        con.commit()
    finally:
        con.close()


def guardar_operaciones(operaciones: list[dict], lote_id: str | None = None) -> str | None:
    if not operaciones:
        return None
    if lote_id is None:
        lote_id = str(int(time.time() * 1000))
    con = conectar()
    try:
        con.executemany(
            "INSERT INTO operaciones (archivo, categoria, origen, destino, lote_id) VALUES (?, ?, ?, ?, ?)",
            [(op["archivo"], op["categoria"], op["origen"], op["destino"], lote_id) for op in operaciones]
        )
        con.commit()
    finally:
        con.close()
    registrar_log("OPERACIONES", "", f"Se registraron {len(operaciones)} operaciones (lote {lote_id})")
    return lote_id


def obtener_operaciones_por_lote(lote_id: str) -> list[dict]:
    return _consultar(
        "SELECT archivo, categoria, origen, destino FROM operaciones WHERE lote_id = ? ORDER BY id",
        (lote_id,)
    )


def obtener_historial() -> list[dict]:
    return _consultar("SELECT * FROM historial ORDER BY id DESC LIMIT 100")
