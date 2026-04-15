# ZMK Studio CLI

Herramienta CLI para extraer keymaps del teclado ZMK.

## Flujo de Trabajo Recomendado

Esta herramienta está diseñada para LEER keymaps del teclado y TRABAJAR con archivos JSON.

```
┌─────────────────────────────────────────────────────────────────────┐
│  Teclado ZMK                                          │
│        │                                                    │
│  Extraer (CLI)                                         │
│  Archivo JSON (keymap.json)                                │
│        │                                                    │
│  Editar (keymap-editor web o CLI write)                │
│  Archivo JSON modificado                                      │
│        │                                                    │
│  Commit a GitHub                                            │
│        │                                                    │
│  GitHub Actions compila firmware                             │
│        │                                                    │
│  Archivo UF2                                               │
│        │                                                    │
│  Flashear a nice!nano                                      │
└─────────────────────────────────────────────────────────────────────┘
```

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

### Escribir keymap al teclado

```bash
# Comando write
python zmk_studio_cli.py write --input mi_keymap.keymap

NOTA: Actualmente este comando solo valida el formato .keymap.
      La conversión a formato binario protobuf para escribir al teclado
      está en desarrollo.
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

## Por Qué No Usar Escritura por Puerto Serie (Actualmente)

La escritura por puerto serie tiene limitaciones:

1. **Formato binario complejo**: El keymap del teclado está en formato protobuf binario, no es fácil generar desde archivos JSON o `.keymap`

2. **Riesgo de corrupción**: Un error en la conversión podría dejar el teclado en estado no usable

3. **Falta de validación**: Es difícil validar que el `.keymap` es correcto antes de enviarlo

4. **Solución existente**: ZMK Studio web ya tiene toda la lógica para escribir keymaps con validación

**Recomendación**: Usa el flujo A (keymap-editor web) para editar keymaps:
- Más seguro
- Más fácil de usar
- Tiene validación en el editor web
- Puede deshacer cambios fácilmente
- Versionado en Git

## Comandos

- `-p, --port`: Puerto serie (default: auto-detect)
- `-v, --verbose`: Salida detallada
- `--no-unlock`: No desbloquear automáticamente el teclado
- `--refresh`: Refrescar behaviors desde el firmware (no usar caché)

## Formatos de Salida

- **json**: Formato JSON con metadata y layers
- **yaml**: Formato YAML legible
- **csv**: Tabla para análisis
- **devicetree**: Archivo `.keymap` compatible con ZMK

## Ejemplos

### Copia de seguridad antes de cambios

```bash
# Extraer backup actual
python zmk_studio_cli.py extract --format json --output backup_$(date +%Y%m%d).json
```

### Flujo completo con keymap-editor web (Recomendado)

```bash
# 1. Extraer keymap actual
python zmk_studio_cli.py extract --format json --output actual.json

# 2. Editar en keymap-editor web
#    - Ir a https://nickcoutsos.github.io/keymap-editor/
#    - Conectar tu repositorio: netcraker01/zmk-config-lily58
#    - Cargar actual.json
#    - Hacer cambios visuales
#    - Guardar en GitHub

# 3. Esperar compilación en GitHub Actions
#    - Ir a Actions tab en tu repo
#    - Esperar que termine
#    - Descargar firmware

# 4. Flashear
#    - Copiar UF2 al teclado
```

## Compatibilidad

- Windows: Requiere Python 3.10+ y pyserial
- Linux/macOS: Requiere Python 3.10+ y pyserial
- Puertos: Auto-detect en Windows (COM*), en Linux/macOS (/dev/ttyACM*)

## Estructura del Proyecto

```
zmk_studio/
├── zmk_studio_cli.py    # CLI principal
├── extractor/
│   ├── keymap_extractor.py  # Lógica de extracción
│   └── rpc_client.py       # Cliente RPC (con set_keymap para escritura)
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
│   ├── protobuf.py         # Codificación/decodificación (con encode_bytes)
│   └── rpc.py             # Requests/respuestas
└── formatter/
    ├── devicetree.py     # Formateador .keymap
    ├── json_formatter.py   # Formateador JSON
    ├── yaml_formatter.py   # Formateador YAML
    └── csv_formatter.py    # Formateador CSV
```
