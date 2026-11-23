#!/usr/bin/env python3
# generar.py — empaqueta panel-web/index.html dentro de esp-idf/panel_html.h
# para que el robot ESP-IDF lo sirva desde flash. Uso:
#   python3 panel-web/generar.py
import pathlib

root = pathlib.Path(__file__).resolve().parent.parent
html = (root / "panel-web" / "index.html").read_text(encoding="utf-8")
assert ')PANEL_EOF"' not in html, "el HTML contiene el delimitador"
out = (
    "#pragma once\n"
    "// panel_html.h — HTML del panel web, generado desde panel-web/index.html.\n"
    "// No editar a mano: edita panel-web/index.html y corre: python3 panel-web/generar.py\n"
    'const char PANEL_HTML[] = R"PANEL_EOF(' + html + ')PANEL_EOF";\n'
)
(root / "esp-idf" / "panel_html.h").write_text(out, encoding="utf-8")
print(f"panel_html.h: {len(out)} bytes (html: {len(html)} bytes)")
