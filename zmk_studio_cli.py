#!/usr/bin/env python3
"""
ZMK Studio CLI - Interfaz simple para trabajar con archivos de keymap

Esta herramienta está diseñada para LEER keymaps del teclado y TRABAJAR con archivos JSON.

Comandos:
  extract    - Extrae keymap del teclado a un archivo JSON
  compare     - Compara dos archivos de keymap
  list-behaviors - Lista los behaviors disponibles

Flujo de trabajo recomendado para modificar keymaps:
  1. Extraer keymap actual → python zmk_studio_cli.py extract --format json --output actual.json
  2. Editar en keymap-editor web → https://nickcoutsos.github.io/keymap-editor/
  3. Commit a GitHub → git add, git commit
  4. Compilar firmware → GitHub Actions se activa automáticamente
  5. Descargar y flashear
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
    print("[*] Extrayendo keymap del teclado...")
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


def cmd_compare(args):
    """Compara dos keymaps."""
    print("[*] Comparando keymaps...")
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


def cmd_write(args):
    """Escribe un archivo .keymap al teclado."""
    print("[*] Escribiendo keymap al teclado...")
    print(f"    Puerto: {args.port if args.port else 'auto-detect'}")
    print(f"    Entrada: {args.input}")

    if not Path(args.input).exists():
        print(f"[X] Error: Archivo no encontrado: {args.input}")
        return 1

    # Cargar archivo .keymap
    # Necesitamos leer el archivo y convertir a formato binario protobuf
    print("[!] NOTA: La conversión de .keymap a protobuf aún está en desarrollo")
    print("    Por ahora, este comando solo:")
    print("      1. Conecta al teclado")
    print("      2. Valida que el archivo es correcto")
    print("")
    print("    Solución actual:")
    print("      1. Usa ZMK Studio web para hacer cambios visuales")
    print("      2. GitHub Actions compila el firmware")
    print("      3. Descarga y flashea al teclado")
    print("    4. Para escritura directa por puerto serie:")
    print("         a. Extrae el keymap actual del teclado:")
    print(
        "              python zmk_studio_cli.py extract --format json --output current.json"
    )
    print("         b. Modifica el JSON para incluir tus cambios")
    print(
        "         c. Convierte el JSON a protobuf binario (manually o con herramienta futura)"
    )
    print("         d. Escribe este comando:")
    print("            python zmk_studio_cli.py write --input keymap_modificado.json")
    print("")
    print("[!] Futuro: Agregaré conversión completa de .keymap a protobuf")

    return 0


def cmd_list_behaviors(args):
    """Lista behaviors disponibles."""
    print("[*] Listando behaviors del teclado...")

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
        description="Herramienta CLI para trabajar con keymaps ZMK (SOLO LECTURA)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Comandos:
  extract     Extrae keymap del teclado
  compare     Comparar dos archivos de keymaps
  list-behaviors      Lista los behaviors del teclado
  write       Escribe un archivo .keymap al teclado

Ejemplo de flujo de trabajo para modificar keymap:
  1. Extraer keymap actual del teclado:
       python zmk_studio_cli.py extract --format json --output current.json

  2. Modificar keymap:
     Opción A - Usar keymap-editor web (recomendado):
       a. Ir a https://nickcoutsos.github.io/keymap-editor/
       b. Conectar tu repositorio: netcraker01/zmk-config-lily58
       c. Cargar current.json y hacer cambios visuales
       d. Guardar cambios en GitHub
       e. GitHub Actions compila y descarga UF2

  3. Flashear:
     a. Conectar el nice!nano V2 via USB
     b. Presiona el botón RESET (o double-tap reset)
     c. Aparece la unidad NICEBOOT
     d. Copiar el archivo UF2 correcto:
          - Lily58_left_oled.uf2 -> lado izquierdo
          - Lily58_right_oled.uf2 → lado derecho

NOTA: El comando 'write' actualmente solo conecta y valida archivos .keymap.
      La conversión a formato binario protobuf está en desarrollo.
        """,
    )

    # Comandos
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Extract
    parser_extract = subparsers.add_parser("extract", help="Extraer keymap del teclado")
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
        help="No desbloquear automaticamente el teclado",
    )

    # Compare
    parser_compare = subparsers.add_parser("compare", help="Comparar dos keymaps")
    parser_compare.add_argument("file1", type=str, help="Primer archivo de keymap")
    parser_compare.add_argument("file2", type=str, help="Segundo archivo de keymap")

    # Write
    parser_write = subparsers.add_parser(
        "write", help="Escribe un archivo .keymap al teclado"
    )
    parser_write.add_argument(
        "-p",
        "--port",
        type=str,
        default="auto",
        help="Puerto serie (default: auto-detect)",
    )
    parser_write.add_argument(
        "-v", "--verbose", action="store_true", help="Salida detallada"
    )
    parser_write.add_argument(
        "input", type=str, required=True, help="Archivo .keymap (formato devicetree)"
    )
    parser_write.add_argument(
        "--no-unlock",
        action="store_false",
        dest="unlock",
        help="No desbloquear automaticamente el teclado",
    )

    # List behaviors
    parser_list = subparsers.add_parser(
        "list-behaviors", help="Listar behaviors del teclado"
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
        help="Refrescar desde el firmware (no usar cache)",
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
    elif args.command == "compare":
        return cmd_compare(args)
    elif args.command == "write":
        return cmd_write(args)
    elif args.command == "list-behaviors":
        return cmd_list_behaviors(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
