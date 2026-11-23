# Mi Robot — compañero de escritorio con ESP32-S3 (ESP-IDF + Xiaozhi)

Un robot parecido a Atomix, pero **tuyo**: mismo hardware, tus propias funciones,
tu propio nombre y tus propios anexos. El código está hecho para **manipularlo**,
no para leerlo de corrido.

> Atomix está basado en Xiaozhi (MIT). Este proyecto toma su **información pública**
> (hardware, pines y funciones) como base, pero el código de aquí es original
> y no copia el firmware de Atomix.

**Este proyecto es solo ESP-IDF.** Se compila con ESP-IDF 6.1 sobre el
proyecto abierto Xiaozhi, placa `wk-esp32s3-dev`, idioma español. La voz es
completa: dices "Hi ESP" y te escucha, y las funciones propias viven como
herramientas MCP (`self.atomix.*`) en `esp-idf/atomix_tools.cc`.

## Qué hace

- Voz completa con Xiaozhi: te escucha y te responde en español
- Ojos animados en pantalla ST7789 240×240 (21 animaciones por voz)
- Hábitos, tareas, recordatorios, alarmas, temporizadores y Pomodoro (25 min)
- Búsqueda web con Tavily (opcional, con tu API key)
- Telegram: el robot te avisa (alarmas, recordatorios, pomodoros) y le puedes
  pedir que te mande mensajes (`telegram_send`)
- **Panel web en el propio robot** (`http://<ip-del-robot>/`): hábitos con
  anillo de progreso, lista de hoy, temporizador con pausa y recordatorios
  con botones. Se puede ver y modificar todo desde el móvil, sin voz.
- Compañero para PC (`anexos/pc_companion.py`): estado del equipo y limpieza
  del escritorio
- Botones físicos: BOOT = hablar/acción, Vol+ / Vol−, LED de estado

## Hardware (el mismo de Atomix)

| Pieza | Modelo |
|---|---|
| Placa | ESP32-S3 N16R8 (16 MB flash, 8 MB PSRAM, USB-C) |
| Pantalla | ST7789 240×240, SPI |
| Micrófono | INMP441 (I2S) |
| Amplificador | MAX98357A (I2S, 3 W) + altavoz 4–8 Ω |
| Botones | BOOT (placa), Vol+ y Vol− |
| LED | + resistencia 220 Ω |

Tabla de pines completa en `anexos/cableado.md`. Solo WiFi 2.4 GHz.
Pines (los de la placa `wk-esp32s3-dev`, no se cambian): mic INMP441
WS 40 / SCK 42 / SD 41, altavoz DIN 21 / BCLK 47 / LRC 48, pantalla
ST7789 MOSI 8 / CLK 9 / CS 11 / DC 12 / RST 13 / BLK 10, Vol+ 38,
Vol− 39, LED 14, BOOT 0.

## Instalar y compilar (en tu Mac)

1. Instala ESP-IDF 6.1 (`~/esp-idf`) y haz `source ~/esp-idf/export.sh`.
2. Clona Xiaozhi y deja la versión 2.5.3:
   ```
   git clone https://github.com/78/xiaozhi-esp32.git ~/xiaozhi-esp32
   cd ~/xiaozhi-esp32
   git checkout 50e96be39844851579fe7fa9c8f52626b708be5b
   ```
3. Copia las funciones propias a la placa:
   ```
   cp esp-idf/atomix_tools.h esp-idf/atomix_tools.cc ~/xiaozhi-esp32/main/boards/wk-esp32s3-dev/
   cp esp-idf/atomix_secrets.h.example ~/xiaozhi-esp32/main/boards/wk-esp32s3-dev/atomix_secrets.h
   ```
4. En `atomix_secrets.h` pon tu token de Telegram, tu chat_id y tu clave
   de Tavily. **Nunca compartas ese archivo.**
5. En `main/boards/wk-esp32s3-dev/wk-esp32s3-dev.cc`, añade el include
   y, en `InitializeTools()`, debajo de la línea de `LampController`:
   ```cpp
   #include "atomix_tools.h"
   static AtomixTools atomix_tools(GetDisplay());
   atomix_tools.Register();
   ```
6. En `main/CMakeLists.txt`, en la lista `PRIV_REQUIRES`, añade solo
   `esp_http_client` antes de `${MAIN_PRIV_REQUIRES_EXTRA}`.
   (No añadas `esp_crt_bundle`: en ESP-IDF 6.x ya no existe como componente.)
7. Compila:
   ```
   python3 scripts/build.py wk-esp32s3-dev --name wk-esp32s3-dev --wake-word hiesp --language es-ES
   ```
8. Conecta la placa por USB-C y graba:
   ```
   idf.py -p /dev/cu.usbmodemXXXX flash monitor
   ```

El detalle paso a paso y la plantilla para añadir herramientas nuevas
están en `esp-idf/README-ESPIDF.md` y `esp-idf/INTEGRACION.md`.

## Panel web

El robot sirve su propio panel en `http://<ip-del-robot>/`, con el diseño
de antes: **Hábitos** (anillo de progreso y % completado), **Hoy**
(lista con marcas, añadir hábito y añadir tarea), **Temporizador**
(anillo, pausa y stop) y **Recordatorios** (con los botones "Ya lo hice",
"En 15 min" y "Ahora no", y añadir recordatorio). Se actualiza solo cada
5 segundos desde `/api/estado`, y cada botón llama a `/cmd`.

- La página vive en `panel-web/index.html`. Ábrela en el navegador para
  ver el diseño con datos de ejemplo (sin robot, entra en modo vista previa).
- El firmware la sirve desde flash: `esp-idf/panel_html.h` se genera con
  `python3 panel-web/generar.py` después de cada cambio al diseño.
- El panel no necesita claves ni la nube: funciona en tu WiFi de casa.

## Nombre y palabra para despertarlo

- **Nombre (Atomix):** se pone en la consola de Xiaozhi (xiaozhi.me), en la
  configuración del agente, después de vincular el dispositivo con el
  código que muestra su pantalla. No es código.
- **Despertarlo diciendo "Atomix":** aún no. Hoy se despierta con "Hi ESP".
  Decir "Atomix" para despertarlo necesita un modelo WakeNet propio
  (`wn9_atomix`), un paso aparte para más adelante.

## Funciones propias (herramientas `self.atomix.*`)

| Herramienta | Qué hace |
|---|---|
| `habits.add/list/complete/toggle/delete/tracking/close` | Hábitos (máx. 15) |
| `tasks.add/list/complete` | Tareas (máx. 20) |
| `reminder.add/list/cancel` | Recordatorios (máx. 8) |
| `alarm.set/cancel/get_status` | Alarma a una hora |
| `timer.set` | Temporizador (1 s – 24 h) |
| `pomodoro.start/stop` | Pomodoro de 25 min |
| `telegram.send` | Manda un mensaje a tu Telegram |
| `web.search` | Búsqueda web con Tavily |
| `screen.show_animation` | Animación en pantalla (ver abajo) |
| `pc.status` / `pc.cleanup` | Estado de tu PC y limpieza de escritorio |

Los avisos (alarma, recordatorio, temporizador, pomodoro) suenan en el
robot, se muestran en pantalla y llegan a tu Telegram solos.

## Animaciones (21)

Se piden por voz: *"muéstrame la animación de shock"*.

`feliz`, `triste`, `durmiendo`, `sorprendido`, `pensando`, `escuchando`,
`guino`, `enamorado`, `enojado`, `mareado`, `llorando`, `verguenza`,
`genial` (gafas de sol, la "240"), `pelota` (sigue una pelota que bota),
`ovejas` (dormido con Zzz), `calma`, `descubre`, `riendo`, `oops`,
`seguro`, `risa_apenada`, `shock`, `normal`.

En la pantalla del robot se ven como las emociones del paquete de
Xiaozhi: las 4 últimas (`oops`, `seguro`, `risa_apenada`, `shock`) no
tienen emoción propia ahí y se acercan a la más parecida
(oops/shock → sorprendido, seguro → genial, risa_apenada → vergüenza).

## Añadir una función propia

1. Escribe la función en `esp-idf/atomix_tools.cc` siguiendo la plantilla
   de `esp-idf/INTEGRACION.md` (un `AddTool` con sus `Property`).
2. Si guarda datos, usa `Settings` (NVS) con el espacio de nombres `atomix`.
3. Recompila y graba. La voz la descubre sola por su descripción.

## Estructura

```
mi-robot/
├── README.md                  # este archivo
├── panel-web/
│   ├── index.html             # el panel web (fuente del diseño)
│   └── generar.py             # genera esp-idf/panel_html.h desde index.html
├── esp-idf/
│   ├── README-ESPIDF.md       # guía completa del camino ESP-IDF + Xiaozhi
│   ├── INTEGRACION.md         # pasos para integrar atomix_tools y plantilla MCP
│   ├── atomix_tools.h          # declaración de AtomixTools (18 herramientas)
│   ├── atomix_tools.cc         # tus funciones: hábitos, tareas, alarmas, Telegram…
│   ├── atomix_panel.h          # servidor web del panel
│   ├── atomix_panel.cc         # rutas /, /api/estado, /cmd
│   ├── panel_html.h           # la página del panel, generada (no editar a mano)
│   └── atomix_secrets.h.example # copia a atomix_secrets.h (NO se comparte)
└── anexos/
    ├── cableado.md            # tabla de pines y consejos de montaje
    ├── pc_companion.py        # compañero para PC: estado y limpieza de escritorio
    └── guia-telegram-tavily.md
```

## Anexos

- `anexos/pc_companion.py`: un programita en Python para tu PC. El robot
  le pregunta el estado (`/estado`) y le pide limpiar el escritorio
  (`/limpiar`). Pon su URL en `ATOMIX_PC_URL` en `atomix_secrets.h`.
- ¿Más anexos? Ideas listas para añadir: cámara, sensor de temperatura,
  tira LED, control de luces por MQTT/Home Assistant. Dime cuál quieres
  y lo añadimos como un archivo nuevo, sin tocar lo demás.

> Nota: antes el proyecto tenía también un sketch de Arduino. Se quitó
> el 2026-11-23 porque el proyecto es solo ESP-IDF; está en la papelera,
> recuperable hasta el 23 de diciembre de 2026. El panel web se reconstruyó
> para ESP-IDF: lo sirve el propio robot (ver arriba).
