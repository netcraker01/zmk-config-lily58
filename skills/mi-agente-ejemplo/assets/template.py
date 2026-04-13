"""
Template para procesamiento de datos - mi-agente-ejemplo
Este es un ejemplo básico que puedes modificar según tus necesidades
"""

import json
import sys
from typing import Dict, Any


def validate_input(data: Dict[Any, Any]) -> bool:
    """Valida que los datos de entrada tengan el formato correcto"""
    required_fields = ["id", "content", "timestamp"]
    return all(field in data for field in required_fields)


def process_data(data: Dict[Any, Any]) -> Dict[str, Any]:
    """Procesa los datos y genera salida estructurada"""
    if not validate_input(data):
        raise ValueError("Invalid input format")

    return {
        "processed_id": data["id"],
        "result": data["content"].upper(),
        "processed_at": data["timestamp"],
        "status": "success",
    }


if __name__ == "__main__":
    try:
        # Leer desde stdin
        raw_input = sys.stdin.read()
        input_data = json.loads(raw_input)

        # Procesar y mostrar resultado
        result = process_data(input_data)
        print(json.dumps(result, indent=2))

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
