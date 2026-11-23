# Integrar las herramientas propias en Xiaozhi (ESP-IDF)

Estado: el código de tus funciones ya está escrito y revisado contra la
API real de Xiaozhi 2.5.3 (`mcp_server.h`, `settings.h`, `display.h`) y
**la base ya compiló en tu Mac el 2026-11-23** ("Project build complete").
Cada vez que cambien `troko_tools.cc` o `troko_panel.cc`, hay que copiar
el archivo nuevo y recompilar antes de grabar.

## Archivos (en `esp-idf/` de este proyecto)

- `troko_tools.h` / `troko_tools.cc` — tus herramientas MCP y los comandos
  del panel web (`EstadoJSON()`, `EjecutarComando()`).
- `troko_panel.h` / `troko_panel.cc` — servidor web del panel del robot.
- `panel_html.h` — la página del panel, generada desde
  `panel-web/index.html` con `python3 panel-web/generar.py`.
- `troko_secrets.h.example` — copia como `troko_secrets.h` con tus
  claves (Telegram, Tavily, URL del PC). Nunca se comparte.

## Herramientas que registra (nombres `self.troko.*`)

| Herramienta | Qué hace |
|---|---|
| `habit_add`, `habit_list`, `habit_complete` | Hábitos (máx 15), guardados en NVS |
| `task_add`, `task_list`, `task_complete` | Tareas (máx 20) |
| `reminder_add`, `reminder_list` | Recordatorios (máx 8); fecha como `10m`, `2h`, `18:30` o ISO |
| `alarm_set`, `alarm_cancel` | Alarma a una hora |
| `timer_set`, `pomodoro_start`, `pomodoro_stop` | Temporizador (1 s a 24 h) y Pomodoro 25 min |
| `telegram_send` | Envía un mensaje a tu Telegram |
| `web_search` | Búsqueda web con Tavily |
| `show_animation` | Animaciones: `240`/`genial`, `pelota`, `ovejas`, `calma`, `descubre`, `guino`, `enamorado`, `enojado`, `mareado`, `llorando`, `verguenza`, `pensando`, `riendo`, `triste`, `feliz`, `oops`, `seguro`, `risa_apenada`, `shock`, `normal` |
| `pc_status`, `pc_clean_desktop` | Habla con el companion de PC |

El panel web usa los mismos datos: `EstadoJSON()` los sirve en
`/api/estado` y `EjecutarComando()` ejecuta los comandos del panel
(`habito`, `hecho`, `tarea`, `recordar`, `recordatorio hecho/posponer/
descartar`, `temporizador pausa/parar`, `pomodoro`, `ojos`, `buscar`,
`aviso`, `estado`, `ayuda`).

Los avisos (timer, pomodoro, alarma, recordatorio) se muestran en
pantalla, suenan por la voz y se mandan por Telegram si está configurado.
Todo se guarda en NVS (`namespace "troko"`), así que sobrevive a un
reinicio. Las claves se leen solo de `troko_secrets.h`.

## Pasos de integración (cuando la base compile)

1. Copia `troko_tools.h`, `troko_tools.cc`, `troko_panel.h`,
   `troko_panel.cc`, `panel_html.h` y tu `troko_secrets.h` a
   `main/boards/wk-esp32s3-dev/` del proyecto Xiaozhi.
   Las fuentes de la placa se recogen con GLOB (`*.cc`), así que los
   archivos nuevos se compilan solos.
2. En `main/boards/wk-esp32s3-dev/wk-esp32s3-dev.cc`, añade arriba:
   ```cpp
   #include "troko_tools.h"
   ```
   Y dentro de `InitializeTools()`, junto al `LampController` que ya hay:
   ```cpp
   static TrokoTools troko_tools(GetDisplay());
   troko_tools.Register();
   ```
   `Register()` también arranca el panel web. No toques `config.h` ni
   los pines de la placa.
3. Añade los componentes que usan `troko_tools.cc` y `troko_panel.cc`
   (HTTP para Telegram y Tavily, y el servidor del panel) a
   `main/CMakeLists.txt`, en la lista `PRIV_REQUIRES` de
   `idf_component_register` (antes de `${MAIN_PRIV_REQUIRES_EXTRA}`):
   ```cmake
                       esp_http_client
                       esp_http_server
   ```
   Sin esto la compilación falla con `esp_http_client.h: No such file or
   directory`, porque `main` no declara ese componente. Ojo: en ESP-IDF
   6.x NO añadas `esp_crt_bundle` — ya no es un componente aparte, vive
   dentro de `mbedtls` (que ya está en la lista) y CMake falla con
   "unknown name" si lo pones.
4. Compila:
   ```sh
   source ~/esp-idf/export.sh
   cd ~/xiaozhi-esp32
   python3 scripts/build.py wk-esp32s3-dev --name wk-esp32s3-dev --wake-word hiesp --language es-ES
   ```
5. El `.bin` sale en `build/`. Se graba con:
   ```sh
   idf.py -p /dev/cu.usbmodemXXXX flash monitor
   ```

## Panel web (lo sirve el propio robot)

El robot sirve su panel en `http://<ip-del-robot>/` (puerto 80, solo en
tu WiFi de casa). Es el mismo diseño de antes: **Hábitos** (anillo de
progreso y % completado, con Hoy / Semana / Todos), **Hoy** (lista con
marcas, añadir hábito y añadir tarea), **Temporizador** (anillo, pausa
y stop, atajos de 5/10/20 min y Pomodoro) y **Recordatorios** (con los
botones "Ya lo hice", "En 15 min" y "Ahora no", y añadir recordatorio).
Se actualiza solo cada 5 segundos.

Rutas que sirve el robot:

| Ruta | Qué hace |
|---|---|
| `/` | La página del panel |
| `/api/estado` | JSON con hábitos, tareas, recordatorios, temporizador y pomodoro |
| `/cmd` y `/api/cmd?texto=...` | Ejecuta un comando y devuelve la respuesta |

Para cambiar el diseño: edita `panel-web/index.html`, corre
`python3 panel-web/generar.py` (regenera `esp-idf/panel_html.h`), copia
el `panel_html.h` nuevo a la placa y recompila.

## Qué falta por verificar (necesita la compilación)

- Que `troko_tools.cc` compile sin errores contra Xiaozhi 2.5.3.
- Que el `.bin` resultante arranque en el hardware y las herramientas
  aparezcan en el servidor (se ven en los logs del puerto serie).
- El mapeo de animaciones (`240`/`genial`→`cool`, `pelota`/`feliz`→`happy`,
  `ovejas`→`sleepy`, `calma`→`relaxed`, `descubre`→`surprised`,
  `guino`→`winking`, `enamorado`→`loving`, `enojado`→`angry`,
  `mareado`→`dizzy`, `llorando`→`crying`, `verguenza`→`embarrassed`,
  `pensando`→`thinking`, `riendo`→`laughing`, `triste`→`sad`,
  `normal`→`neutral`) usa las emociones del paquete de assets de Xiaozhi.
  Si una emoción no está en el paquete, la herramienta lo dice en vez de
  fallar en silencio. Si añades tus GIF propios al `assets`, cambia el
  mapeo en `troko_tools.cc`. Las 4 últimas (`oops`, `seguro`,
  `risa_apenada`, `shock`) no tienen emoción propia en el paquete y se
  acercan a la más parecida: oops/shock → `surprised`, seguro → `cool`,
  risa_apenada → `embarrassed`.
