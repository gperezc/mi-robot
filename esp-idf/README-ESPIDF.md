# ESP-IDF + Xiaozhi (voz completa)

Este es el único camino del proyecto: firmware ESP-IDF sobre el proyecto
abierto **Xiaozhi** (github.com/78/xiaozhi-esp32, licencia MIT), placa
`wk-esp32s3-dev`. Dices "Hi ESP" y te escucha, con conversación por voz.
Es el que usa Atomix.

> Esto es una guía + plantilla, no el proyecto completo: el proyecto
> Xiaozhi es enorme (cientos de archivos) y se clona aparte.

## 1. Instalar ESP-IDF 6.1

```sh
git clone -b release/v6.1 --recursive https://github.com/espressif/esp-idf.git
cd esp-idf && ./install.sh esp32s3
source export.sh
idf.py --version
```

## 2. Clonar Xiaozhi y compilar la placa de Atomix

```sh
git clone https://github.com/78/xiaozhi-esp32.git
cd xiaozhi-esp32
# Fija la versión que usaba el firmware original de Atomix (2.5.3, oct 2026):
git checkout 50e96be39844851579fe7fa9c8f52626b708be5b
```

Crea un `.env` en la carpeta del proyecto con tus claves:

```
XIAOZHI_TAVILY_API_KEY=tvly-...
XIAOZHI_TELEGRAM_BOT_TOKEN=123456789:AA...
XIAOZHI_TELEGRAM_CHAT_ID=tu-chat-id
```

Y compila:

```sh
source ~/esp-idf/export.sh
python3 scripts/build.py wk-esp32s3-dev --name wk-esp32s3-dev --wake-word hiesp --language es-ES
```

> En Xiaozhi 2.5.3 el flag es `--wake-word`, no `--custom-wake-word`:
> admite `hiesp` ("Hi ESP"), `nihaoxiaozhi`, `disabled` o un modelo
> ESP-SR como `wn9_jarvis_tts` (ver con
> `python3 scripts/build.py --list-wake-words`). La palabra "atomix" como
> wake word personalizada no viene en ESP-SR: Atomix entrenó su propio
> modelo WakeNet. Es un paso aparte (hay que generar un modelo
> `wn9_atomix` con las herramientas de Espressif); mientras tanto el
> robot funciona igual por voz, despertándose con "Hi ESP".

Cambia `atomix` por tu palabra de activación y `es-ES` por tu idioma.
El `.bin` queda en `build/`. Grábalo en `0x0` con esptool o esptool-js.

## 3. Tus funciones ya escritas (herramientas MCP)

Ya no es solo una plantilla: tus funciones están escritas en
`atomix_tools.h` y `atomix_tools.cc` (en esta misma carpeta), listas
para copiar a `main/boards/wk-esp32s3-dev/`. Ver `INTEGRACION.md` para
los pasos exactos y la lista completa: hábitos, tareas, recordatorios,
alarma, temporizador, Pomodoro, Telegram, búsqueda web (Tavily),
animaciones y PC. Las claves van en `atomix_secrets.h` (copia de
`atomix_secrets.h.example`), no en el `.env` de abajo.

Si quieres añadir una función nueva desde cero, la plantilla es esta:

```cpp
// Mi primera herramienta: saluda y muestra un mensaje en pantalla.
void InitializeTools() {
    static LampController lamp(LAMP_GPIO);

    auto& mcp_server = McpServer::GetInstance();
    mcp_server.AddTool("self.atomix.saludar",
        "Saluda al usuario por su nombre y muestra el saludo en pantalla.",
        PropertyList({
            Property("nombre", kPropertyTypeString),
        }),
        [this](const PropertyList& properties) -> ReturnValue {
            std::string nombre = properties["nombre"].value<std::string>();
            GetDisplay()->ShowNotification("Hola, " + nombre + "!");
            return std::string("Saludado a " + nombre);
        });
}
```

Reglas del proyecto Xiaozhi (de su `AGENTS.md`):

- No cambies los pines de `wk-esp32s3-dev`. Si tu hardware cambia,
  crea una placa nueva, no edites esta (afecta la compatibilidad OTA).
- Un build exporta exactamente una placa (`DECLARE_BOARD`).
- No pongas comportamiento de una placa en el código común (`main/`):
  tus funciones van en la carpeta de la placa.
- No edites archivos generados: `build/`, `managed_components/`, `sdkconfig*`.

## 4. Qué es de Atomix y qué no

Lo que **sí** trae Xiaozhi de serie: conversación por voz, wake word,
pantalla, volumen, cámara, OTA, estado del dispositivo.

Lo que **no** trae (era propio de Atomix y hay que recrearlo con la
plantilla de arriba, una herramienta por función): pomodoro, hábitos,
tareas, recordatorios, Telegram y búsqueda web. Los textos y límites
que usaba Atomix están documentados en el análisis previo del firmware:
recordatorios máx. 8, tareas máx. 20, hábitos máx. 15, temporizador
1–86400 s, pomodoro 25 min, animaciones `240`, `pelota`, `ovejas`,
`calma`, `descubre` y 12 más (`guino`, `enamorado`, `enojado`,
`mareado`, `llorando`, `verguenza`, `pensando`, `riendo`, `triste`,
`feliz`, `genial`, `normal`; ver `INTEGRACION.md`).
