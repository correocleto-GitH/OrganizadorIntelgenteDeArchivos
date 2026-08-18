import csv
import io
import json
import os

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, Response, stream_with_context
from flask_wtf.csrf import CSRFProtect

from organizador.organizador import analizar_carpeta, organizar_archivos, deshacer_operaciones, obtener_resumen, buscar_archivos, ruta_permitida
from organizador.db import init_db, guardar_operaciones, obtener_historial, obtener_operaciones_por_lote, registrar_log

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)
csrf = CSRFProtect(app)


@app.context_processor
def contexto():
    return {"modo_oscuro": session.get("modo_oscuro", False)}

def _guardar_en_sesion(ops: list, lote_id: str) -> None:
    if len(ops) > 50:
        session["ultima_operacion"] = {"lote_id": lote_id, "usar_db": True}
    else:
        session["ultima_operacion"] = ops

@app.route("/")
def inicio():
    ruta = session.get("carpeta", "")
    archivos = analizar_carpeta(ruta) if ruta and os.path.isdir(ruta) else []
    resumen = obtener_resumen(archivos)
    return render_template("index.html", ruta=ruta, archivos=archivos, resumen=resumen)


@app.route("/seleccionar-carpeta")
def seleccionar_carpeta():
    try:
        import tkinter as tk
        from tkinter import filedialog

        ventana = tk.Tk()
        ventana.withdraw()
        ventana.attributes("-topmost", True)

        carpeta = filedialog.askdirectory(title="Seleccionar una carpeta")
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
    ruta_abs = os.path.abspath(ruta)
    session["carpeta"] = ruta_abs
    archivos = analizar_carpeta(ruta_abs)
    registrar_log("ANALISIS", ruta_abs, f"{len(archivos)} archivos encontrados")
    return redirect(url_for("inicio"))

@app.route("/organizar", methods=["POST"])
def organizar():
    ruta = session.get("carpeta")
    if not ruta or not os.path.isdir(ruta):
        flash("Seleccione primero una carpeta válida.", "error")
        return redirect(url_for("inicio"))
    modo = request.form.get("modo", "ejecutar")
    incluir_subcarpetas = request.form.get("incluir_subcarpetas") == "on"
    operaciones = organizar_archivos(ruta, simulacion=(modo == "simular"), incluir_subcarpetas=incluir_subcarpetas)
    if modo == "simular":
        session["simulacion"] = operaciones
        registrar_log("SIMULACION", ruta, f"{len(operaciones)} archivos serían organizados")
        flash(f"Simulación terminada: {len(operaciones)} archivos serían organizados.", "info")
    else:
        lote_id = guardar_operaciones(operaciones)
        registrar_log("ORGANIZACION", ruta, f"{len(operaciones)} archivos organizados")
        _guardar_en_sesion(operaciones, lote_id)
        flash(f"Se organizaron {len(operaciones)} archivos correctamente.", "success")
    return redirect(url_for("inicio"))

@app.route("/organizar/progreso")
@csrf.exempt
def organizar_progreso():
    ruta = session.get("carpeta")
    if not ruta or not os.path.isdir(ruta) or not ruta_permitida(ruta):
        def _error_gen():
            yield f"data: {json.dumps({'error': 'Carpeta no válida o no seleccionada.'})}\n\n"
        return Response(stream_with_context(_error_gen()), mimetype="text/event-stream")

    modo = request.args.get("modo", "ejecutar")
    incluir_subcarpetas = request.args.get("incluir_subcarpetas", "0") == "1"
    simulacion = modo == "simular"

    def _generar():
        import queue
        import threading

        cola = queue.Queue()
        excepcion_ref = [None]

        def _callback(actual, total):
            cola.put(json.dumps({"actual": actual, "total": total}))

        def _worker():
            try:
                ops = organizar_archivos(
                    ruta,
                    simulacion=simulacion,
                    incluir_subcarpetas=incluir_subcarpetas,
                    callback_progreso=_callback
                )
                cola.put(("__completado__", ops))
            except Exception as e:
                excepcion_ref[0] = e
                cola.put("__error__")

        hilo = threading.Thread(target=_worker, daemon=True)
        hilo.start()

        while True:
            item = cola.get()
            if item == "__error__":
                yield f"data: {json.dumps({'error': str(excepcion_ref[0])})}\n\n"
                break
            if isinstance(item, tuple) and item[0] == "__completado__":
                ops = item[1]
                if not simulacion:
                    lote_id = guardar_operaciones(ops)
                    registrar_log("ORGANIZACION", ruta, f"{len(ops)} archivos organizados")
                    _guardar_en_sesion(ops, lote_id)
                else:
                    session["simulacion"] = ops
                    registrar_log("SIMULACION", ruta, f"{len(ops)} archivos serían organizados")
                yield f"data: {json.dumps({'completado': True, 'total': len(ops), 'simulacion': simulacion})}\n\n"
                break
            yield f"data: {item}\n\n"

    cabeceras = {
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",
    }
    return Response(stream_with_context(_generar()), mimetype="text/event-stream", headers=cabeceras)


@app.route("/deshacer", methods=["POST"])
def deshacer():
    entrada = session.get("ultima_operacion", [])
    if isinstance(entrada, dict) and entrada.get("usar_db"):
        operaciones = obtener_operaciones_por_lote(entrada["lote_id"])
    else:
        operaciones = entrada
    restaurados, errores = deshacer_operaciones(operaciones)
    registrar_log("DESHACER", session.get("carpeta", ""), f"{len(restaurados)} archivos restaurados")
    session.pop("ultima_operacion", None)
    flash(f"Se restauraron {len(restaurados)} archivos.", "success")
    if errores:
        for e in errores:
            flash(f"No se pudo restaurar '{e['archivo']}': {e['error']}", "error")
    return redirect(url_for("inicio"))

@app.route("/buscar")
def buscar():
    ruta = session.get("carpeta", "")
    termino = request.args.get("q", "").strip()
    categoria = request.args.get("categoria", "Todas")
    archivos = buscar_archivos(ruta, termino, categoria)
    return jsonify({"archivos": archivos, "total": len(archivos)})

@app.route("/historial/exportar")
def exportar_historial():
    registros = obtener_historial()
    salida = io.StringIO()
    escritor = csv.writer(salida)
    escritor.writerow(["id", "fecha", "tipo", "ruta", "detalle"])
    for fila in registros:
        escritor.writerow([fila["id"], fila["fecha"], fila["tipo"], fila["ruta"], fila["detalle"]])
    return Response(
        salida.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="historial.csv"'}
    )

@app.route("/historial")
def historial():
    return render_template("historial.html", historial=obtener_historial())

@app.route("/historial/<int:lote_id>")
def detalle_operacion(lote_id):
    operaciones = obtener_operaciones_por_lote(lote_id)
    return render_template("detalle_operacion.html", operaciones=operaciones, lote_id=lote_id)

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
