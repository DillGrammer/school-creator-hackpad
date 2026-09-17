# Hackpad pin map

View from above, USB-C at the top. Key numbers describe physical positions; existing SW references are preserved.

| Control | Reference / pad | XIAO label | RP2040 GPIO | Net |
|---|---|---|---|---|
| Top-left key | SW1 / 1 | D0 | 26 | KEY1 |
| Top-middle key | SW4 / 1 | D2 | 28 | KEY2 |
| Top-right key | SW2 / 1 | D6 | 0 | KEY3 |
| Bottom-left key | SW5 / 1 | D1 | 27 | KEY4 |
| Bottom-middle key | SW7 / 1 | D3 | 29 | KEY5 |
| Bottom-right key | SW3 / 1 | D7 | 1 | KEY6 |
| Encoder rotation A | SW6 / A | D10 | 3 | ENC_A |
| Encoder rotation B | SW6 / B | D9 | 4 | ENC_B |
| Encoder press / Enter | SW6 / S1 | D8 | 2 | ENC_CLICK |
| OLED data | J1 / 4 | D4 / SDA | 6 | OLED_SDA |
| OLED clock | J1 / 3 | D5 / SCL | 7 | OLED_SCL |
| OLED power | J1 / 2 | 3V3 | — | +3V3 |
| OLED ground | J1 / 1 | GND | — | GND |

All key pad 2 connections, encoder C, and encoder S2 connect to ground. Enable input pull-ups and software debounce for keys and encoder press. Use a quadrature decoder for rotation; configure its transitions-per-detent for the supplied encoder so one detent produces one menu step. Reverse direction in firmware if needed. Encoder press is independently wired and can mean Enter/select or another action by mode.

Six keys + three encoder inputs + two OLED signals use all 11 exposed GPIOs. Independent key wiring supports simultaneous presses without a switch matrix or diodes. Extra kit LEDs are not fitted in this design.

