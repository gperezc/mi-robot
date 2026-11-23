# Cableado — mismo hardware que Troko

Fuente: guía pública de Troko (trokotec.com/troko/build). Pines verificados
también contra el firmware original (placa `wk-esp32s3-dev`).

## Materiales

- ESP32-S3 N16R8 (16 MB flash, 8 MB PSRAM, USB-C). Imprescindible N16R8.
- Pantalla ST7789 240×240 IPS 1.3" o 1.54", SPI, 7 pines.
- Micrófono INMP441 (I2S).
- Amplificador MAX98357A (I2S, 3 W) + altavoz 4–8 Ω, 2–3 W, ~40 mm.
- 2 pulsadores (Vol+ / Vol−). El botón BOOT de la placa sirve para hablar.
- LED + resistencia 220 Ω (opcional).
- Cable USB-C **de datos**, no solo de carga.

## Tabla de pines

### Pantalla ST7789

| Pantalla | ESP32-S3 |
|---|---|
| SDA / MOSI | GPIO 8 |
| SCL / CLK | GPIO 9 |
| CS | GPIO 11 |
| DC | GPIO 12 |
| RES / RST | GPIO 13 |
| BLK | GPIO 10 |
| VCC | 3V3 |
| GND | GND |

Si tu pantalla de 7 pines no tiene CS, deja GPIO 11 sin conectar.

### Micrófono INMP441

| Micrófono | ESP32-S3 |
|---|---|
| SCK | GPIO 42 |
| WS | GPIO 40 |
| SD | GPIO 41 |
| L/R | GND |
| VDD | 3V3 |
| GND | GND |

### Amplificador MAX98357A

| Amplificador | ESP32-S3 |
|---|---|
| BCLK | GPIO 47 |
| LRC | GPIO 48 |
| DIN | GPIO 21 |
| VIN | 5V |
| GND | GND |
| SD, GAIN | sin conectar |
| + / − | altavoz |

### Botones y LED

| Elemento | ESP32-S3 |
|---|---|
| BOOT (hablar) | GPIO 0 |
| Volumen + | GPIO 38 |
| Volumen − | GPIO 39 |
| LED | GPIO 14 |

Botón: una pata al GPIO y la otra a GND. No hacen falta resistencias.

**No uses estos pines para otra cosa:** GPIO 19 y 20 (USB), 26 a 37
(flash y PSRAM) y 43–44 (puerto serie).

## Consejos de montaje

- Suelda los pines. Los pines solo apoyados en la protoboard son la causa
  número uno de fallos.
- Cables cortos, sobre todo en pantalla (GPIO 8 y 9): con cables largos
  la imagen sale con rayas o no aparece.
- No cruces BCLK con LRC ni SCK con WS: sin sonido o sin micrófono.
- Deja el pin SD del amplificador sin conectar. A GND, lo apaga.
- El pin L/R del micrófono va a GND: escucha por el canal izquierdo.
- El altavoz va a los bornes + y −, nunca a GND.
- Pantalla y micrófono a 3V3; amplificador a 5V. Todos los GND unidos.
- Revisa todo con la placa desconectada antes de enchufarla.
