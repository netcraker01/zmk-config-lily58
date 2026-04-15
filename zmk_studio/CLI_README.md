# ZMK Studio CLI

Herramienta CLI simple para extraer keymaps del teclado ZMK.

## Flujo de Trabajo Recomendado

Esta herramienta está diseñada para **leer** configuración del teclado y trabajar con **archivos de keymap JSON**.

```
┌─────────────────────────────────────────────────────────────────────┐
│  Teclado ZMK                                          │
│        │                                                    │
│        ▼                                                   │
│  Extraer (CLI)                                         │
│        │                                                    │
│  Archivo JSON (keymap.json)                                │
│        │                                                    │
│  Editar (keymap-editor web)                               │
│        │                                                    │
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

## Editar Keymap (Recomendado)

El flujo más práctico para editar keymaps es:

### 1. Extraer keymap actual

```bash
python zmk_studio_cli.py extract --format json --output keymap_actual.json
```

### 2. Editar en keymap-editor web

1. Ve a https://nickcoutsos.github.io/keymap-editor/
2. Conecta tu repositorio: `netcraker01/zmk-config-lily58`
3. El keymap-editor carga `config/info.json` automáticamente
4. Haz cambios visuales en el editor
5. Guarda los cambios (se suben a GitHub)

### 3. Compilar firmware

1. GitHub Actions compila automáticamente
2. Ve a Actions tab
3. Descarga los archivos UF2

### 4. Flashear al teclado

1. Conecta el nice!nano V2 via USB
2. Presiona el botón RESET (o double-tap reset)
3. Aparece la unidad `NICEBOOT`
4. Copia el archivo UF2 correcto:
   - `Lily58_left_oled.uf2` → lado izquierdo
   - `Lily58_right_oled.uf2` → lado derecho

## Por Qué No Escribir Directamente por Puerto Serie

La escritura por puerto serie tiene limitaciones:

1. **Formato binario complejo**: El keymap del teclado está en formato protobuf binario, no es fácil generar desde archivos JSON o `.keymap`

2. **Riesgo de corrupción**: Un error en la conversión podría dejar el teclado en estado no usable

3. **Falta de validación**: Es más difícil validar que el JSON es correcto antes de enviarlo

4. **Solución existente**: ZMK Studio web ya tiene toda la lógica para escribir keymaps

**Recomendación**: Usa el flujo basado en archivos descrito arriba. Es:
- Más seguro
- Más fácil de usar
- Tiene validación en el editor web
- Puede deshacer cambios fácilmente
- Versionado en Git

## Formatos de Salida

- **json**: Formato JSON con metadata y layers
- **yaml**: Formato YAML legible
- **csv**: Tabla para análisis
- **devicetree**: Archivo `.keymap` compatible con ZMK

## Opciones

- `-p, --port`: Puerto serie (default: auto-detect)
- `-v, --verbose`: Salida detallada
- `-f, --format`: Formato de salida (json, yaml, csv, devicetree)
- `-o, --output`: Archivo de salida
- `--no-unlock`: No desbloquear automáticamente el teclado
- `--refresh`: Refrescar behaviors desde el firmware (no usar caché)

## Ejemplos Completos

### Copia de seguridad antes de cambios

```bash
# Extraer backup actual
python zmk_studio_cli.py extract --format json --output backup_$(date +%Y%m%d).json
```

### Flujo completo de modificación

```bash
# 1. Extraer keymap actual
python zmk_studio_cli.py extract --format json --output actual.json

# 2. Comparar con backup (opcional)
python zmk_studio_cli.py compare backup.json actual.json

# 3. Editar en keymap-editor web
#    - Ir a https://nickcoutsos.github.io/keymap-editor/
#    - Cargar actual.json
#    - Hacer cambios
#    - Guardar en GitHub

# 4. Esperar compilación en GitHub Actions
#    - Ir a Actions tab en tu repo
#    - Esperar que termine
#    - Descargar firmware

# 5. Flashear
#    - Copiar UF2 al teclado
```

### Restaurar desde backup

```bash
# Comparar para verificar que es lo que quieres
python zmk_studio_cli.py compare backup.json nuevo_keymap.json

# Si está bien, restaurar
python zmk_studio_cli.py extract --format json --input backup.json --output restaurar.json
# Luego editar en keymap-editor web y seguir el flujo
```

## Compatibilidad

- Windows: Requiere Python 3.10+ y pyserial
- Linux/macOS: Requiere Python 3.10+ y pyserial
- Puertos: Auto-detect en Windows (COM*), en Linux/macOS (/dev/ttyACM*)

## Estructura del Proyecto

```
zmk_studio/
├── zmk_studio_cli.py    # CLI principal para extracción
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
