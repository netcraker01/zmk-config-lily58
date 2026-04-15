# ZMK Studio Keymap Extractor

Herramienta modular para extraer keymaps de teclados ZMK vía el protocolo ZMK Studio.

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

### Extraer keymap del teclado

```bash
# Extraer en formato devicetree (por defecto)
python -m zmk_studio.cli -p COM8 extract --format devicetree --output keymap.keymap

# Extraer en JSON
python -m zmk_studio.cli -p COM8 extract --format json --output keymap.json

# Extraer en YAML
python -m zmk_studio.cli -p COM8 extract --format yaml --output keymap.yaml

# Extraer en CSV
python -m zmk_studio.cli -p COM8 extract --format csv --output keymap.csv
```

### Otras opciones

```bash
# Listar behaviors disponibles
python -m zmk_studio.cli list-behaviors

# Verificar dos keymaps
python -m zmk_studio.cli verify keymap1.json keymap2.json

# Limpiar caché de behaviors
python -m zmk_studio.cli cache-clear

# Modo verboso
python -m zmk_studio.cli -v -p COM8 extract --format json
```

## Formatos de salida

- **devicetree**: Formato `.keymap` compatible con ZMK
- **json**: Estructura JSON con metadatos
- **yaml**: Formato YAML legible
- **csv**: Tabla para análisis

## Estructura del proyecto

```
zmk_studio/
├── cli.py                 # Interfaz de línea de comandos
├── extractor/
│   ├── keymap_extractor.py # Extractor principal
│   └── rpc_client.py       # Cliente RPC para ZMK Studio
├── formatter/
│   ├── devicetree.py       # Formateador .keymap
│   ├── json_formatter.py   # Formateador JSON
│   ├── yaml_formatter.py   # Formateador YAML
│   └── csv_formatter.py    # Formateador CSV
├── mapping/
│   ├── keycodes.py         # Tabla de keycodes HID
│   ├── modifiers.py        # Decodificación de modificadores
│   ├── rgb.py              # Constantes RGB
│   ├── ext_power.py        # Constantes ext_power
│   ├── behaviors.py        # Resolución de behaviors
│   └── layers.py           # Nombres de capas
├── protocol/
│   ├── serial.py           # Cliente serial CDC-ACM
│   ├── framing.py          # Protocolo SOF/ESC/EOF
│   ├── protobuf.py         # Codificación/decodificación
│   └── rpc.py              # Requests/responses
└── tests/
    └── *.py                 # Tests unitarios
```

## Protocolo ZMK Studio

- **Baudrate**: 12500 (no 115200)
- **Framing**: SOF (0xAB), ESC (0xAC), EOF (0xAD)
- **Encoding**: Protobuf
- **Subsystems**: Core (1), Keymap (2), Behaviors (3)

### Keycode Encoding

Los keycodes en ZMK Studio usan un formato de 32 bits:

```
Bits 24-31: Modifier flags (0x02 = SHIFT, 0x40 = RALT)
Bits 16-23: Usage page (0x07 = HID Keyboard, 0x05 = Consumer)
Bits 0-15: Usage code
```

### Modifiers Soportados

| Modifier | Bit | Constante ZMK |
|----------|-----|---------------|
| LCTRL    | 0   | LCTRL         |
| LSHIFT   | 1   | LSHFT         |
| LALT     | 2   | LALT          |
| LGUI     | 3   | LGUI          |
| RCTRL    | 4   | RCTRL         |
| RSHIFT   | 5   | RSHFT         |
| RALT     | 6   | RALT          |
| RGUI     | 7   | RGUI          |

## Limitaciones Conocidas

### Mod-Tap Multi-Modifier

ZMK's `&mt` behavior solo acepta un modifier. El extractor detecta mod-taps con múltiples modifiers y genera código comentado con una nota explicativa.

**Solución**: Usar un macro con `macro_press` y `macro_pause_for_release`:

```dts
macros {
    hyper_mod: hyper_mod {
        compatible = "zmk,behavior-macro";
        #binding-cells = <0>;
        bindings
            = <&macro_press &kp LCTRL &kp LALT &kp LGUI &kp RSHFT>
            , <&macro_pause_for_release>
            , <&macro_release &kp RSHFT &kp LGUI &kp LALT &kp LCTRL>
            ;
    };
};

behaviors {
    ht_hyper: ht_hyper {
        compatible = "zmk,behavior-hold-tap";
        #binding-cells = <2>;
        bindings = <&hyper_mod>, <&kp>;
    };
};

// Uso: &ht_hyper 0 UNDERSCORE
```

## Requisitos

- Python 3.10+
- pyserial
- PyYAML (para formato YAML)
- click 8.0+

## Licencia

MIT