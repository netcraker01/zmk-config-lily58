---
name: mi-agente-ejemplo
description: >
  Agente de ejemplo que procesa datos de entrada y genera respuestas estructuradas.
  Trigger: Cuando el usuario necesita procesar datos o generar informes.
license: Apache-2.0
metadata:
  author: gentleman-programming
  version: "1.0"
---

## When to Use

- Quando necesitas procesar datos estructurados
- Para generar informes automáticos
- Cuando se requiere análisis de texto con formato específico

## Critical Patterns

1. **Siempre** validate input data before processing
2. **Nunca** aceptes datos sin formato definido
3. **Siempre** genera salida en formato JSON estructurado
4. **Nunca** proceses más de 1000 registros sin paginación

## Code Examples

### Procesamiento básico de datos
```bash
# Input validation
validate_data() {
  echo "Validating input data..."
  check_format $1
}

# Data processing
process_data() {
  python -c "
import json
import sys
data = json.load(sys.stdin)
processed = transform(data)
print(json.dumps(processed))
"
}
```

## Commands

```bash
# Crear nuevo agente
mkdir -p skills/nombre-agente
touch skills/nombre-agente/SKILL.md

# Probar agente
opencode --test skill nombre-agente

# Activar agente
opencode --enable skill nombre-agente
```

## Resources

- **Templates**: See [assets/](assets/) for data processing templates
- **Documentation**: See [references/](references/) for format specifications