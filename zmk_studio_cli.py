#!/usr/bin/env python3
"""
ZMK Studio CLI - Interfaz simple para leer/escribir configuración del teclado

Comandos:
  extract    - Extrae keymap del teclado a un archivo
  set        - Escribe un keymap al teclado (desde archivo extraído)
  compare     - Compara dos keymaps
  list-behaviors - Lista los behaviors disponibles
"""

import argparse
import json
import logging
import sys
from pathlib import Path

from zmk_studio.extractor.keymap_extractor import KeymapExtractor

logger = logging.getLogger(__name__)


def cmd_extract(args):
    """Extrae keymap del teclado."""
    print(f"[*] Extrayendo keymap del teclado...")
    print(f"    Puerto: {args.port if args.port else 'auto-detect'}")
    print(f"    Formato: {args.format}")
    print(f"    Salida: {args.output}")

    extractor = KeymapExtractor(port=args.port, debug=args.verbose)

    # Extraer
    keymap = extractor.extract(auto_unlock=args.unlock)

    if keymap is None:
        print("[X] Error al extraer keymap")
        return 1

    # Exportar
    output = extractor.export(keymap, args.format, args.output)

    print(f"[OK] Keymap extraido exitosamente")
    if args.output:
        print(f"    Guardado en: {args.output}")
    else:
        print(f"    Preview (primeras 100 lineas):")
        print(output[:1000] + ("..." if len(output) > 1000 else ""))

    return 0


def cmd_set(args):
    """Escribe un keymap al teclado."""
    print(f"[*] Escribiendo keymap al teclado...")
    print(f"    Puerto: {args.port if args.port else 'auto-detect'}")
    print(f"    Entrada: {args.input}")

    if not Path(args.input).exists():
        print(f"[X] Error: Archivo no encontrado: {args.input}")
        return 1

    # Cargar keymap
    with open(args.input, "r") as f:
        input_keymap = json.load(f)

    print(f"    Capas: {len(input_keymap.get('layers', []))}")

    # Para escribir, necesitamos los bytes exactos del formato protobuf
    # Por ahora, solo mostramos advertencia
    print("[!] Nota: La escritura requiere keymap en formato binario protobuf")
    print("    El protocolo soporta set_keymap, pero requiere los bytes exactos")
    print("    Solución actual:")
    print("    1. Extrae el keymap del teclado (comando 'extract')")
    print("    2. Edita el archivo JSON generado")
    print("    3. Usa ZMK Studio web para subir el archivo modificado")
    print("")
    print("    Futuro: Agregare conversion de JSON->protobuf")

    return 0


def cmd_compare(args):
    """Compara dos keymaps."""
    print(f"[*] Comparando keymaps...")
    print(f"    Archivo 1: {args.file1}")
    print(f"    Archivo 2: {args.file2}")

    if not Path(args.file1).exists():
        print(f"[X] Error: Archivo no encontrado: {args.file1}")
        return 1
    if not Path(args.file2).exists():
        print(f"[X] Error: Archivo no encontrado: {args.file2}")
        return 1

    # Leer
    with open(args.file1, "r") as f:
        km1 = json.load(f)
    with open(args.file2, "r") as f:
        km2 = json.load(f)

    # Comparar
    extractor = KeymapExtractor()
    match = extractor.verify(km1, km2)

    if match:
        print("[OK] Los keymaps son IDENTICOS")
    else:
        print("[X] Los keymaps son DIFERENTES")

        # Mostrar diferencias básicas
        layers1 = len(km1.get("layers", []))
        layers2 = len(km2.get("layers", []))
        if layers1 != layers2:
            print(f"    Diferencia: Capas {layers1} vs {layers2}")

    return 0 if match else 1


def cmd_list_behaviors(args):
    """Lista behaviors disponibles."""
    print(f"[*] Listando behaviors del teclado...")

    extractor = KeymapExtractor(port=args.port, debug=args.verbose)

    behaviors = extractor.list_behaviors(refresh=args.refresh)

    if not behaviors:
        print("[X] No se pudo obtener la lista de behaviors")
        return 1

    print(f"[OK] Encontrados {len(behaviors)} behaviors:")
    print("")

    # Agrupar por tipo
    kp_count = sum(1 for bid, name in behaviors.items() if "kp" in name.lower())
    mt_count = sum(1 for bid, name in behaviors.items() if "mod-tap" in name.lower())
    mo_count = sum(1 for bid, name in behaviors.items() if "layer" in name.lower())
    macro_count = sum(1 for bid, name in behaviors.items() if "macro" in name.lower())

    print(f"    kp (key press):       {kp_count}")
    print(f"    mod-tap:             {mt_count}")
    print(f"    layer (mo):           {mo_count}")
    print(f"    macro:                {macro_count}")
    print(
        f"    otros:                {len(behaviors) - kp_count - mt_count - mo_count - macro_count}"
    )
    print("")

    # Mostrar si se pide verbose
    if args.verbose:
        for bid, name in sorted(behaviors.items()):
            print(f"    [{bid:3d}] {name}")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Herramienta CLI para ZMK Studio - Leer y escribir configuración del teclado",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Comandos
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Extract
    parser_extract = subparsers.add_parser("extract", help="Extrae keymap del teclado")
    parser_extract.add_argument(
        "-p",
        "--port",
        type=str,
        default="auto",
        help="Puerto serie (default: auto-detect)",
    )
    parser_extract.add_argument(
        "-f",
        "--format",
        type=str,
        default="json",
        choices=["json", "yaml", "csv", "devicetree"],
        help="Formato de salida (default: json)",
    )
    parser_extract.add_argument(
        "-o",
        "--output",
        type=str,
        help="Archivo de salida (si no se especifica, muestra en pantalla)",
    )
    parser_extract.add_argument(
        "-v", "--verbose", action="store_true", help="Salida detallada"
    )
    parser_extract.add_argument(
        "--no-unlock",
        action="store_false",
        dest="unlock",
        help="No desbloquear automáticamente el teclado",
    )

    # Set
    parser_set = subparsers.add_parser("set", help="Escribe keymap al teclado")
    parser_set.add_argument(
        "-p",
        "--port",
        type=str,
        default="auto",
        help="Puerto serie (default: auto-detect)",
    )
    parser_set.add_argument(
        "input", type=str, help="Archivo JSON de keymap (extraído previamente)"
    )

    # Compare
    parser_compare = subparsers.add_parser("compare", help="Compara dos keymaps")
    parser_compare.add_argument("file1", type=str, help="Primer archivo de keymap")
    parser_compare.add_argument("file2", type=str, help="Segundo archivo de keymap")

    # List behaviors
    parser_list = subparsers.add_parser(
        "list-behaviors", help="Lista behaviors del teclado"
    )
    parser_list.add_argument(
        "-p",
        "--port",
        type=str,
        default="auto",
        help="Puerto serie (default: auto-detect)",
    )
    parser_list.add_argument(
        "-r",
        "--refresh",
        action="store_true",
        help="Refrescar desde el firmware (no usar caché)",
    )
    parser_list.add_argument(
        "-v", "--verbose", action="store_true", help="Mostrar todos los behaviors"
    )

    args = parser.parse_args()

    # Logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
    else:
        logging.basicConfig(level=logging.INFO, format="%(message)s")

    # Ejecutar comando
    if args.command == "extract":
        return cmd_extract(args)
    elif args.command == "set":
        return cmd_set(args)
    elif args.command == "compare":
        return cmd_compare(args)
    elif args.command == "list-behaviors":
        return cmd_list_behaviors(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
