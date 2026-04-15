# ZMK Studio CLI

Herramienta CLI simple para leer/escribir configuración del teclado ZMK.

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

### Extraer keymap del teclado

```bash
# Extraer y guardar en archivo JSON
python zmk_studio_cli.py extract --format json --output keymap.json

# Extraer en formato devicetree
python zmk_studio_cli.py extract --format devicetree --output Lily58.keymap

# Extraer en formato YAML
python zmk_studio_cli.py extract --format yaml --output keymap.yaml

# Ver en pantalla (sin guardar)
python zmk_studio_cli.py extract --format json

# Especificar puerto serie
python zmk_studio_cli.py extract -p COM8
```

### Comparar dos keymaps

```bash
# Comparar dos archivos JSON
python zmk_studio_cli.py compare keymap1.json keymap2.json
```

### Listar behaviors

```bash
# Listar behaviors disponibles (usando caché)
python zmk_studio_cli.py list-behaviors

# Refrescar desde el firmware
python zmk_studio_cli.py list-behaviors --refresh

# Mostrar detalles de cada behavior
python zmk_studio_cli.py list-behaviors --verbose
```

### Escribir keymap (Futuro)

```bash
# ADVERTENCIA: La escritura aún requiere keymap en formato binario protobuf
# Por ahora, este comando solo muestra instrucciones

# Paso 1: Extraer el keymap actual
python zmk_studio_cli.py extract --format json --output current.json

# Paso 2: Editar el archivo JSON generado

# Paso 3: Usar ZMK Studio web para subir los cambios
#    - Ir a https://nickcoutsos.github.io/keymap-editor/
#    - Conectar tu repositorio
#    - Cargar current.json desde el keymap-editor
#    - Hacer cambios
#    - Guardar al repositorio
#    - Compilar firmware en GitHub Actions
#    - Flashear al teclado

# Referencia: Este flujo es más fácil que escribir directamente por puerto serie
```

## Opciones

- `-p, --port`: Puerto serie (default: auto-detect)
- `-v, --verbose`: Salida detallada
- `-f, --format`: Formato de salida (json, yaml, csv, devicetree)
- `-o, --output`: Archivo de salida
- `--no-unlock`: No desbloquear automáticamente el teclado
- `--refresh`: Refrescar behaviors desde el firmware (no usar caché)

## Formatos de Salida

- **json**: Formato JSON con metadata y layers
- **yaml**: Formato YAML legible
- **csv**: Tabla para análisis
- **devicetree**: Archivo `.keymap` compatible con ZMK

## Ejemplos

```bash
# Flujo típico de trabajo:

# 1. Extraer configuración actual
python zmk_studio_cli.py extract --format json --output backup.json

# 2. Comparar con una versión anterior
python zmk_studio_cli.py compare backup.json version_anterior.json

# 3. Si todo bien, usar keymap-editor web
#    (Ver sección "Escribir keymap" arriba)
```

## Limitaciones

### Escritura

El comando `set` aún no está completamente implementado porque:

1. El formato binario protobuf es complejo de generar
2. Los archivos `.keymap` de devicetree no se pueden convertir fácilmente a protobuf
3. Es más práctico usar ZMK Studio web + GitHub Actions para compilar

**Recomendación**: Usar el flujo de:
1. `extract` → obtener keymap actual
2. Editar en `keymap-editor` web
3. Commit al GitHub
4. Actions compila firmware
5. Descargar y flashear

### Compatibilidad

- Windows: Requiere Python 3.10+ y pyserial
- Linux/macOS: Requiere Python 3.10+ y pyserial
- Puertos: Auto-detect en Windows (COM*), en Linux/macOS (/dev/ttyACM*)

## Estructura del Proyecto

```
zmk_studio/
├── cli.py                 # CLI principal
├── extractor/
│   ├── keymap_extractor.py  # Lógica de extracción
│   └── rpc_client.py       # Cliente RPC
├── mapping/
│   ├── keycodes.py         # Tabla de keycodes
│   ├── modifiers.py        # Procesamiento de modifiers
│   ├── rgb.py             # Constantes RGB
│   ├── ext_power.py       # Constantes ext_power
│   ├── behaviors.py       # Resolución de behaviors
│   └── layers.py          # Nombres de capas
├── protocol/
│   ├── serial.py           # Puerto serie
│   ├── framing.py          # Protocolo SOF/ESC/EOF
│   ├── protobuf.py         # Codificación/decodificación
│   └── rpc.py             # Requests/respuestas
└── formatter/
    ├── devicetree.py     # Formateador .keymap
    ├── json_formatter.py   # Formateador JSON
    ├── yaml_formatter.py   # Formateador YAML
    └── csv_formatter.py    # Formateador CSV
```

## Desarrollado por

Basado en protocolo ZMK Studio:
- Baudrate: 12500
- Framing: SOF=0xAB, ESC=0xAC, EOF=0xAD
- Encoding: Protobuf (varint + length-delimited)
