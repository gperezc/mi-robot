# Guía: Telegram y Tavily

## Telegram (avisos del robot)

En esta versión (ESP-IDF) Telegram es de salida: el robot **te escribe a ti**.
Te llega un mensaje cuando suena una alarma, se cumple un recordatorio,
termina un temporizador o acaba un Pomodoro, y la voz puede mandarte
cualquier mensaje con la herramienta `telegram.send` ("mándame por
Telegram la lista de tareas").

1. En Telegram, abre **@BotFather** y envía `/newbot`.
2. Ponle nombre y usuario (tiene que terminar en `bot`, p. ej. `atomix_robot_bot`).
3. BotFather te da un **token** del tipo `123456789:AA...`. Es la contraseña
   de tu bot: no la compartas.
4. Búscalo en Telegram, pulsa Start y escríbele un "hola". Busca tu
   `chat_id` con **@userinfobot** (te responde con tu id).
5. En `esp-idf/atomix_secrets.h` pon:
   ```cpp
   #define ATOMIX_TELEGRAM_TOKEN   "123456789:AA..."
   #define ATOMIX_TELEGRAM_CHAT_ID "123456789"
   ```

Solo tu `chat_id` recibe los mensajes del robot. Si quieres que los avisos
lleguen a un grupo, pon el chat_id del grupo (negativo, p. ej.
`-1001234567890`) en lugar del tuyo: todos los miembros verán los avisos.

## Tavily (búsqueda web)

1. Crea una cuenta en **app.tavily.com** (plan gratuito con créditos mensuales).
2. En el panel, copia tu **API Key**. Empieza por `tvly-`.
3. En `esp-idf/atomix_secrets.h` pon:
   ```cpp
   #define ATOMIX_TAVILY_API_KEY "tvly-..."
   ```
4. Pruébalo por voz: *"busca quién ganó el partido de ayer"*.

Sin API key, la búsqueda responde que no está configurada.
Nunca compartas un firmware compilado con tus claves dentro.
