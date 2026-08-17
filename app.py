from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from organizador.organizador import analizar_carpeta, organizar_archivos, deshacer_operaciones, obtener_resumen, buscar_archivos
from organizador.db import init_db, guardar_operaciones, obtener_historial, registrar_log
import os, json

app = Flask(__name__)
app.secret_key = "cambiar-esta-clave-en-produccion"

CARPETAS_PROTEGIDAS = [
    os.environ.get("SystemRoot", r"C:\Windows").lower(),
    os.environ.get("ProgramFiles", r"C:\Program Files").lower(),
    os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)").lower()
]

@app.context_processor
def contexto():
    return {"modo_oscuro": session.get("modo_oscuro", False)}

def ruta_permitida(ruta):
    try:
        ruta = os.path.abspath(ruta).lower()
        return not any(ruta == p or ruta.startswith(p + os.sep) for p in CARPETAS_PROTEGIDAS)
    except Exception:
        return False

@app.route("/")
def inicio():
    ruta = session.get("carpeta", "")
    archivos = analizar_carpeta(ruta) if ruta and os.path.isdir(ruta) else []
    resumen = obtener_resumen(archivos)
    return render_template("index.html", ruta=ruta, archivos=archivos, resumen=resumen)


@app.route("/seleccionar-carpeta")
def seleccionar_carpeta():
    """Abre el selector nativo de carpetas de Windows."""
    try:
        import tkinter as tk
        from tkinter import filedialog

        ventana = tk.Tk()
        ventana.withdraw()
        ventana.attributes("-topmost", True)

        carpeta = filedialog.askdirectory(
            title="Seleccionar una carpeta"
        )

        ventana.destroy()

        if not carpeta:
            flash("No se seleccionó ninguna carpeta.", "info")
            return redirect(url_for("inicio"))

        if not ruta_permitida(carpeta):
            flash(
                "Por seguridad, no se permite trabajar directamente sobre carpetas del sistema.",
                "error"
            )
            return redirect(url_for("inicio"))

        session["carpeta"] = os.path.abspath(carpeta)
        registrar_log("SELECCION", carpeta, "Carpeta seleccionada mediante diálogo de Windows")
        flash(f"Carpeta seleccionada: {carpeta}", "success")

    except Exception as e:
        flash(f"No fue posible abrir el selector de carpetas: {e}", "error")

    return redirect(url_for("inicio"))


@app.route("/analizar", methods=["POST"])
def analizar():
    ruta = request.form.get("carpeta", "").strip()
    if not os.path.isdir(ruta):
        flash("La carpeta indicada no existe o no es válida.", "error")
        return redirect(url_for("inicio"))
    if not ruta_permitida(ruta):
        flash("Por seguridad, no se permite trabajar directamente sobre carpetas del sistema.", "error")
        return redirect(url_for("inicio"))
    session["carpeta"] = os.path.abspath(ruta)
    registrar_log("ANALISIS", ruta, f"{len(analizar_carpeta(ruta))} archivos encontrados")
    return redirect(url_for("inicio"))

@app.route("/organizar", methods=["POST"])
def organizar():
    ruta = session.get("carpeta")
    if not ruta or not os.path.isdir(ruta):
        flash("Seleccione primero una carpeta válida.", "error")
        return redirect(url_for("inicio"))
    modo = request.form.get("modo", "ejecutar")
    operaciones = organizar_archivos(ruta, simulacion=(modo == "simular"))
    if modo == "simular":
        session["simulacion"] = operaciones
        registrar_log("SIMULACION", ruta, f"{len(operaciones)} archivos serían organizados")
        flash(f"Simulación terminada: {len(operaciones)} archivos serían organizados.", "info")
    else:
        guardar_operaciones(operaciones)
        session["ultima_operacion"] = operaciones
        registrar_log("ORGANIZACION", ruta, f"{len(operaciones)} archivos organizados")
        flash(f"Se organizaron {len(operaciones)} archivos correctamente.", "success")
    return redirect(url_for("inicio"))

@app.route("/deshacer", methods=["POST"])
def deshacer():
    operaciones = session.get("ultima_operacion", [])
    restaurados = deshacer_operaciones(operaciones)
    registrar_log("DESHACER", session.get("carpeta", ""), f"{len(restaurados)} archivos restaurados")
    session.pop("ultima_operacion", None)
    flash(f"Se restauraron {len(restaurados)} archivos.", "success")
    return redirect(url_for("inicio"))

@app.route("/buscar")
def buscar():
    ruta = session.get("carpeta", "")
    termino = request.args.get("q", "").strip()
    categoria = request.args.get("categoria", "Todas")
    archivos = buscar_archivos(ruta, termino, categoria)
    return jsonify({"archivos": archivos, "total": len(archivos)})

@app.route("/historial")
def historial():
    return render_template("historial.html", historial=obtener_historial())

@app.route("/modo-oscuro", methods=["POST"])
def modo_oscuro():
    session["modo_oscuro"] = not session.get("modo_oscuro", False)
    return redirect(request.referrer or url_for("inicio"))

@app.route("/limpiar")
def limpiar():
    session.pop("carpeta", None)
    session.pop("ultima_operacion", None)
    return redirect(url_for("inicio"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
