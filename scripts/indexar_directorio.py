import argparse
from pathlib import Path

from angelito.repository_indexer import indexar_directorio_con_opciones


def main() -> None:
    parser = argparse.ArgumentParser(description="Indexa un directorio local en la memoria de Angelito.")
    parser.add_argument("directorio", help="Ruta del directorio a indexar.")
    parser.add_argument("--etiqueta", help="Nombre opcional para identificar el origen.")
    parser.add_argument("--max-archivos", type=int, help="Limite opcional de archivos a indexar.")
    parser.add_argument("--progreso", action="store_true", help="Muestra cada archivo indexado.")
    args = parser.parse_args()

    resultado = indexar_directorio_con_opciones(
        Path(args.directorio),
        etiqueta=args.etiqueta,
        max_archivos=args.max_archivos,
        mostrar_progreso=args.progreso,
    )
    print(f"Archivos indexados: {resultado.archivos_indexados}")
    print(f"Archivos omitidos: {resultado.archivos_omitidos}")


if __name__ == "__main__":
    main()
