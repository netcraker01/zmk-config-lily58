---
name: analisis-json
description: >
  Analiza archivos JSON y genera resúmenes estructurados.
  Trigger: Cuando necesita analizar, validar o extracter información de archivos JSON.
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
---

## When to Use

- Para validar estructura de archivos JSON
- Extraer estadísticas de datos JSON
- Generar reportes de archivos de configuración

## Critical Patterns

1. **Siempre** valida JSON antes de procesar
2. **Nunca** modificas el archivo original
3. **Siempre** genera salida en formato markdown con tablas
4. **Nunca** proceses archivos mayores a 10MB sin chunking

## Code Examples

### Validación básica
```bash
validate_json() {
  if python -c "import json; json.load(open('$1'))"; then
    echo "✅ JSON válido"
  else
    echo "❌ JSON inválido"
  fi
}
```

### Análisis de estructura
```bash
analyze_structure() {
  jq -r '
    {
      "tipo": type,
      "claves": (if type == "object" then keys | sort end),
      "longitud": (if type == "array" then length end)
    }
  ' "$1"
}
```

## Commands

```bash
# Analizar un archivo JSON
opencode --skill analisis-json --input datos.json

# Validar múltiples archivos
ls *.json | xargs -I {} opencode --skill analisis-json --validate {}

# Generar reporte completo
opencode --skill analisis-json --report --output reporte.md
```

## Resources

- **Templates**: See [assets/schema-validator.py](assets/schema-validator.py)
- **Examples**: See [assets/sample-config.json](assets/sample-config.json)