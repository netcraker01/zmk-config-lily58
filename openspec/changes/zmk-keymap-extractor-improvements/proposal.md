# Proposal: ZMK Keymap Extractor Improvements

## Intent

Refactorizar `zmk_extractor.py` (1047 líneas monolíticas) en una arquitectura modular para mejorar mantenibilidad, extensibilidad y soportar nuevas funcionalidades como resolución dinámica de behaviors, múltiples formatos de exportación, y mejor mapeo de keycodes HID y layer names.

## Scope

### In Scope

- Separación de responsabilidades: protocolo, mapeo, formato, extracción
- Implementación de resolución dinámica de behaviors (con caché persistente)
- Mapeo mejorado de keycodes HID y nombres de capas
- Soporte para múltiples formatos de exportación: JSON, YAML, CSV, devicetree
- CLI mejorada con subcomandos usando click 8.x+
- Sistema de caché para behaviors en JSON
- Documentación completa del protocolo ZMK Studio
- Pruebas unitarias básicas para protocolo y mapeo

### Out of Scope

- Modificación del firmware ZMK
- Soporte para protocolos de comunicación alternativos
- Interfaz gráfica de usuario
- Integración continua con repositorios de keymaps
- Compatibilidad hacia atrás completa con CLI original (se mantiene como backup)

## Capabilities

### New Capabilities

- `protocol-handling`: Framing SOF/ESC/EOF, encoder/decoder protobuf custom, cliente serial CDC-ACM
- `keymap-mapping`: Resolución dinámica de behaviors, tabla completa de keycodes HID, decodificación de modificadores, manejo de nombres de capas
- `format-export`: Serialización a JSON, YAML, CSV y formato devicetree (.keymap)
- `keymap-extraction`: Extracción de keymaps desde firmware ZMK vía protocolo serial
- `behavior-caching`: Sistema de caché persistente para behaviors en JSON

### Modified Capabilities

None - esta refactorización no cambia el comportamiento visible del extractor, solo su arquitectura interna.

## Approach

**Modularización**: Separar el código monolítico en módulos cohesivos con responsabilidades claras: `protocol/` (framing, protobuf, serial), `mapping/` (behaviors, keycodes, layers), `formatter/` (json, yaml, csv, devicetree).

**Resolución dinámica**: Consultar firmware ZMK para behaviors en tiempo real con caché JSON persistente como fallback, eliminando dependencia de tablas hardcoded.

**CLI moderna**: Implementar usando click 8.x+ con subcomandos (`extract`, `export`, `list-behaviors`) para mejor usabilidad y extensibilidad.

**Protocolo custom**: Mantener implementación protobuf custom para evitar dependencias externas de protobuf-python.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `zmk_extractor.py` | Deprecated | Mantener como backup, reemplazar por `extractor.py` |
| `zmk/extractor.py` | New | CLI principal con click |
| `zmk/protocol/` | New | Módulos: framing.py, protobuf.py, serial.py |
| `zmk/mapping/` | New | Módulos: behaviors.py, keycodes.py, layers.py |
| `zmk/formatter/` | New | Módulos: devicetree.py, json.py, yaml.py, csv.py |
| `zmk/tests/` | New | Tests: test_protocol.py, test_mapping.py |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Regresión de funcionalidad | Low | Mantener zmk_extractor.py como backup, pruebas unitarias |
| Lentitud en resolución dinámica | Med | Caché persistente en JSON para behaviors |
| Breaking changes en CLI | Low | Nueva CLI con opciones compatibles, mantener original |
| Errores en mapeo de keycodes | Low | Tabla completa HID Usage Page 7 + Consumer Page 0x0C |
| Falta de nombres de capas originales | Med | Fallback a nombres secuenciales (BASE, NAV, SYM, ADJUST) |

## Rollback Plan

1. Restaurar `zmk_extractor.py` desde backup
2. Eliminar directorios `zmk/protocol/`, `zmk/mapping/`, `zmk/formatter/`, `zmk/tests/`
3. Renombrar `zmk/extractor.py` a `extractor_old.py` si existe
4. Verificar que el extractor original funciona con pruebas existentes
5. Documentar en commit revertido las razones del rollback

## Dependencies

- Python 3.14.0 (ya instalado)
- pyserial (ya instalado)
- click 8.x+ (nueva dependencia)
- pyyaml (nueva dependencia para formato YAML)
- Firmware ZMK con protocolo ZMK Studio habilitado
- Conexión serial CDC-ACM al dispositivo ZMK

## Success Criteria

- [ ] Arquitectura modular separada en 4 dominios claros (protocol, mapping, formatter, extraction)
- [ ] Extracción de keymaps desde firmware funciona sin errores
- [ ] Resolución dinámica de behaviors con caché persistente funciona
- [ ] Mapeo de keycodes HID >95% de cobertura de HID Usage Page 7 + Consumer Page 0x0C
- [ ] Modificadores decodificados en formato legible (ej: `LSHFT(LCTRL)` en vez de `0x200002D`)
- [ ] Nombres de capas: preferencia de lectura desde keymap original, fallback a secuenciales
- [ ] Formatos de exportación funcionan: JSON, YAML, CSV, devicetree
- [ ] CLI con subcomandos `extract`, `export`, `list-behaviors` funciona
- [ ] Pruebas unitarias pasan: test_protocol.py (framing/protobuf), test_mapping.py (keycodes)
- [ ] Documentación del protocolo ZMK Studio completa
- [ ] Loco del extractor reducido en >50% (de 1047 a <500 líneas por archivo)
