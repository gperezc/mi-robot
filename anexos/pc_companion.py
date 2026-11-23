#!/usr/bin/env python3
"""pc_companion.py — compañero para PC de Mi Robot.

El robot le pregunta a tu computadora por HTTP:
  GET /estado   -> CPU, memoria, disco y archivos sueltos en el Escritorio
  GET /limpiar  -> mueve los archivos sueltos del Escritorio a
                   Escritorio/Ordenado-YYYY-MM-DD/ y cuenta qué hizo

Uso:
  python3 pc_companion.py            # escucha en http://0.0.0.0:8765
  python3 pc_companion.py --port 8765 --escritorio ~/Desktop

En el robot, pon en secrets.h:
  #define PC_COMPANION_URL "http://192.168.1.50:8765"
con la IP de tu PC en tu red local (no localhost, el robot está en otra máquina).

Seguridad: esto es solo para tu red local. No lo expongas a internet.
Requiere Python 3.8+. `psutil` es opcional (si no está, usa valores básicos).
"""
import argparse
import json
import os
import shutil
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

try:
    import psutil
except ImportError:
    psutil = None


def archivos_sueltos(escritorio: Path):
    if not escritorio.is_dir():
        return []
    return [p for p in escritorio.iterdir()
            if p.is_file() and not p.name.startswith(".")]


def estado(escritorio: Path):
    sueltos = archivos_sueltos(escritorio)
    info = {
        "equipo": os.uname().nodename if hasattr(os, "uname") else "mi-pc",
        "archivos_sueltos_escritorio": len(sueltos),
        "nombres": [p.name for p in sueltos[:10]],
    }
    if psutil:
        info["cpu_pct"] = psutil.cpu_percent(interval=0.5)
        mem = psutil.virtual_memory()
        info["memoria_pct"] = mem.percent
        disco = psutil.disk_usage(str(escritorio))
        info["disco_pct"] = disco.percent
    return info


def limpiar(escritorio: Path):
    sueltos = archivos_sueltos(escritorio)
    if not sueltos:
        return {"mensaje": "Escritorio limpio, no hay archivos sueltos para ordenar.",
                "movidos": 0}
    destino = escritorio / ("Ordenado-" + datetime.now().strftime("%Y-%m-%d"))
    destino.mkdir(exist_ok=True)
    movidos = []
    for p in sueltos:
        try:
            shutil.move(str(p), str(destino / p.name))
            movidos.append(p.name)
        except OSError as e:
            print(f"No pude mover {p.name}: {e}")
    return {"mensaje": f"Ordené {len(movidos)} archivos en {destino.name}.",
            "movidos": len(movidos), "archivos": movidos}


class Manejador(BaseHTTPRequestHandler):
    escritorio = Path.home() / "Desktop"

    def _json(self, datos, codigo=200):
        cuerpo = json.dumps(datos, ensure_ascii=False).encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def _texto(self, texto, codigo=200):
        cuerpo = texto.encode("utf-8")
        self.send_response(codigo)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_GET(self):
        if self.path == "/estado":
            info = estado(self.escritorio)
            texto = (f"PC {info['equipo']}: "
                     f"CPU {info.get('cpu_pct', '?')}%, "
                     f"memoria {info.get('memoria_pct', '?')}%, "
                     f"disco {info.get('disco_pct', '?')}%. "
                     f"Escritorio: {info['archivos_sueltos_escritorio']} archivos sueltos.")
            self._texto(texto)
        elif self.path == "/limpiar":
            resultado = limpiar(self.escritorio)
            self._texto(resultado["mensaje"])
        elif self.path == "/":
            self._texto("Mi Robot - companero de PC. Rutas: /estado y /limpiar")
        else:
            self._texto("Ruta no conocida. Prueba /estado o /limpiar", 404)

    def log_message(self, *args):
        pass  # silencioso


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--escritorio", default=str(Path.home() / "Desktop"))
    args = parser.parse_args()
    Manejador.escritorio = Path(args.escritorio).expanduser()
    servidor = HTTPServer(("0.0.0.0", args.port), Manejador)
    print(f"Companero de PC en http://0.0.0.0:{args.port}  (escritorio: {Manejador.escritorio})")
    print("Pulsa Ctrl+C para parar.")
    servidor.serve_forever()
