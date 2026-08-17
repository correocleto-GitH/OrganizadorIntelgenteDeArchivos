import sqlite3, os
DB = os.path.join(os.path.dirname(os.path.dirname(__file__)), "organizador.db")

def conectar():
    return sqlite3.connect(DB)

def init_db():
    with conectar() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS historial(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT DEFAULT CURRENT_TIMESTAMP,
            tipo TEXT NOT NULL,
            ruta TEXT,
            detalle TEXT)""")
        con.commit()

def registrar_log(tipo, ruta, detalle):
    init_db()
    with conectar() as con:
        con.execute("INSERT INTO historial(tipo,ruta,detalle) VALUES(?,?,?)",(tipo,ruta,detalle))
        con.commit()

def guardar_operaciones(operaciones):
    registrar_log("OPERACIONES", "", f"Se registraron {len(operaciones)} operaciones")

def obtener_historial():
    init_db()
    with conectar() as con:
        con.row_factory = sqlite3.Row
        return [dict(r) for r in con.execute("SELECT * FROM historial ORDER BY id DESC LIMIT 100")]
