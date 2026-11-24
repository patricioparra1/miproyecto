"""Dashboard interactivo. Ejecutar desde la raiz con: python app.py [puerto]"""
import json
import os
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

if getattr(sys, "frozen", False):  # al ejecutarse como .exe, los recursos viajan dentro del paquete
    os.chdir(sys._MEIPASS)

from src.panel import calcular_vista, cargar, opciones

RUTA_DATOS = "datos/procesados/dataset_limpio.csv"
RUTA_HTML = os.path.join("interfaz", "index.html")
DATOS = None


def _entero(q, clave, defecto):
    try:
        return int(q.get(clave, [defecto])[0])
    except ValueError:
        return defecto


def parametros_desde_consulta(q):
    return {"variable": q.get("variable", ["temperatura"])[0], "estaciones": q.get("estacion") or None,
            "anio_min": _entero(q, "anio_min", 2008), "anio_max": _entero(q, "anio_max", 2017),
            "estaciones_anio": q.get("estacion_anio") or None, "modelo": q.get("modelo", ["comparar"])[0],
            "horizonte": _entero(q, "horizonte", 24), "ventana": _entero(q, "ventana", 12)}


class Manejador(BaseHTTPRequestHandler):
    def _enviar(self, codigo, contenido, tipo):
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(contenido)))
        self.end_headers()
        self.wfile.write(contenido)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/":
            with open(RUTA_HTML, "rb") as f:
                self._enviar(200, f.read(), "text/html; charset=utf-8")
        elif url.path == "/api/opciones":
            self._enviar(200, json.dumps(opciones(DATOS)).encode(), "application/json")
        elif url.path == "/api/vista":
            try:
                resultado = calcular_vista(DATOS, parametros_desde_consulta(parse_qs(url.query)))
            except Exception as error:  # el dashboard no debe caerse por una combinacion extrana
                resultado = {"error": f"No se pudo calcular esta combinación ({error})."}
            self._enviar(200, json.dumps(resultado).encode(), "application/json")
        else:
            self._enviar(404, b"No encontrado", "text/plain")

    def log_message(self, formato, *args):
        pass


def main():
    global DATOS
    if not os.path.exists(RUTA_DATOS):
        print(f"No existe {RUTA_DATOS}. Ejecute primero: python main.py")
        return
    DATOS = cargar(RUTA_DATOS)
    puerto = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 8501
    servidor = ThreadingHTTPServer(("127.0.0.1", puerto), Manejador)
    direccion = f"http://127.0.0.1:{puerto}"
    print(f"Dashboard disponible en {direccion} (Ctrl+C para cerrar)")
    if "--no-abrir" not in sys.argv:
        threading.Timer(0.8, lambda: webbrowser.open(direccion)).start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nDashboard cerrado.")


if __name__ == "__main__":
    main()
