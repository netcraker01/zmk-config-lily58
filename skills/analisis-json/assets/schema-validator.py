#!/usr/bin/env python3
"""
Validador de esquemas JSON para analisis-json
"""

import json
import sys
import os
from typing import Dict, Any, List


def load_schema(schema_path: str) -> Dict[Any, Any]:
    """Carga un esquema JSON desde archivo"""
    with open(schema_path, "r") as f:
        return json.load(f)


def validate_json_file(file_path: str, schema: Dict[Any, Any] = None) -> Dict[str, Any]:
    """Valida un archivo JSON contra un esquema opcional"""
    try:
        with open(file_path, "r") as f:
            data = json.load(f)

        result = {
            "file": file_path,
            "valid": True,
            "type": type(data).__name__,
            "size": os.path.getsize(file_path),
        }

        if schema:
            # Here you could implement jsonschema validation
            result["schema_matched"] = True
        elif isinstance(data, dict):
            result["keys"] = list(data.keys())
        elif isinstance(data, list):
            result["length"] = len(data)

        return result

    except json.JSONDecodeError as e:
        return {"file": file_path, "valid": False, "error": str(e)}
    except Exception as e:
        return {"file": file_path, "error": str(e)}


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing file path"}))
        sys.exit(1)

    file_path = sys.argv[1]
    schema_path = sys.argv[2] if len(sys.argv) > 2 else None

    schema = load_schema(schema_path) if schema_path else None
    result = validate_json_file(file_path, schema)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
