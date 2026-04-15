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

## Requisitos

- Python 3.10+
- pyserial
- PyYAML (para formato YAML)
- click 8.0+

## Licencia

MIT