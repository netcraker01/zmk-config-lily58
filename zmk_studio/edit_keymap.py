#!/usr/bin/env python3
"""
Edit Keymap - Modificar keymap del teclado

Flujo de trabajo:
1. Extraer keymap actual del teclado
2. Cargar un archivo de cambios (diff JSON)
3. Aplicar cambios al keymap
4. Reenviar keymap modificado al teclado

Formato del archivo de cambios:
{
  "layers": [
    {
      "index": 0,
      "changes": [
        {"position": 10, "behavior_id": 3, "param1": 458800, "param2": 0}
      ]
    }
  ]
}

Donde:
- position: índice del binding en la capa (0-57 para Lily58)
- behavior_id: ID del behavior (3=kp, 16=bt, 20=rgb_ug, 6=mo, etc.)
- param1: primer parámetro (keycode para kp, modifier para mod-tap)
- param2: segundo parámetro (keycode para mod-tap)
"""

import argparse
import json
import logging
import sys

from pathlib import Path

from zmk_studio.extractor.keymap_extractor import KeymapExtractor

logger = logging.getLogger(__name__)


def load_changes(changes_file: str):
    """Carga archivo de cambios."""
    with open(changes_file, "r", encoding="utf-8") as f:
        return json.load(f)


def apply_changes(keymap: dict, changes: dict) -> dict:
    """Aplica cambios al keymap."""
    modified = False

    for layer_change in changes.get("layers", []):
        layer_idx = layer_change.get("index")
        if layer_idx is None:
            logger.warning(f"  Change sin índice de capa, omitiendo")
            continue

        # Encontrar capa correspondiente en keymap
        if layer_idx >= len(keymap.get("layers", [])):
            logger.warning(f"  Capa {layer_idx} no existe en keymap, omitiendo")
            continue

        layer = keymap["layers"][layer_idx]
        bindings = layer.get("bindings", [])

        # Aplicar cambios a bindings
        for change in layer_change.get("changes", []):
            pos = change.get("position")
            if pos is None or pos >= len(bindings):
                logger.warning(
                    f"  Posición {pos} inválida en capa {layer_idx}, omitiendo"
                )
                continue

            # Aplicar cambio
            bindings[pos] = {
                "behavior_id": change.get("behavior_id"),
                "param1": change.get("param1"),
                "param2": change.get("param2"),
                "behavior_name": "",  # Se llena al extraer
            }
            modified = True

    if modified:
        logger.info("Cambios aplicados exitosamente")
    else:
        logger.warning("No se aplicaron cambios (archivo vacío o posiciones inválidas)")

    return keymap


def edit_keymap(args):
    """Edita keymap del teclado."""
    print("[*] Editando keymap del teclado...")
    print(f"    Cambios: {args.changes}")
    print(f"    Puerto: {args.port if args.port else 'auto-detect'}")
    print()

    # Cargar archivo de cambios
    changes = load_changes(args.changes)
    print(
        f"[OK] Archivo de cambios cargado: {len(changes.get('layers', []))} capas con cambios"
    )

    # Extraer keymap actual del teclado
    print("[*] Extrayendo keymap actual del teclado...")
    extractor = KeymapExtractor(port=args.port, debug=args.verbose)
    current_keymap = extractor.extract(auto_unlock=args.unlock)

    if current_keymap is None:
        print("[X] Error al extraer keymap actual")
        return 1

    print(f"[OK] Keymap extraído: {len(current_keymap.get('layers', []))} capas")

    # Aplicar cambios
    modified_keymap = apply_changes(current_keymap, changes)

    # Mostrar resumen
    print()
    print("[*] Resumen de cambios:")
    for layer_change in changes.get("layers", []):
        layer_idx = layer_change.get("index")
        count = len(layer_change.get("changes", []))
        if count > 0:
            layer_name = current_keymap["layers"][layer_idx].get(
                "name", f"layer{layer_idx}"
            )
            print(f"    Capa {layer_name} ({layer_idx}): {count} cambios")

    print()
    print("[!] ATENCIÓN: La escritura al teclado aún no está implementada")
    print(
        "    Necesitamos la conversión de keymap modificado a formato binario protobuf"
    )
    print("    Solución práctica actual:")
    print("    1. Extrae el keymap modificado con este comando:")
    print(
        f"       python zmk_studio_cli.py extract --format json --output keymap_modificado.json"
    )
    print("    2. Sube el JSON al keymap-editor web")
    print("    3. GitHub Actions compila el firmware")
    print("    4. Flashea el nuevo UF2 al teclado")
    print()

    # Desconectar
    extractor.rpc_client.disconnect()

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Edita keymap del teclado ZMK",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-p",
        "--port",
        type=str,
        default="auto",
        help="Puerto serie (default: auto-detect)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Salida detallada")
    parser.add_argument(
        "--no-unlock",
        action="store_false",
        dest="unlock",
        help="No desbloquear automáticamente el teclado",
    )
    parser.add_argument(
        "changes",
        type=str,
        required=True,
        help="Archivo JSON con cambios (formato diff)",
    )

    args = parser.parse_args()

    # Logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
    else:
        logging.basicConfig(level=logging.INFO, format="%(message)s")

    return edit_keymap(args)


if __name__ == "__main__":
    sys.exit(main())
