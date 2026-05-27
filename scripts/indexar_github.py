import argparse

from angelito.repository_indexer import indexar_repo_github


def main() -> None:
    parser = argparse.ArgumentParser(description="Clona e indexa un repo de GitHub en Angelito.")
    parser.add_argument("repo_url", help="URL HTTPS o SSH del repositorio.")
    parser.add_argument("--max-archivos", type=int, help="Limite opcional de archivos a indexar.")
    parser.add_argument("--progreso", action="store_true", help="Muestra cada archivo indexado.")
    args = parser.parse_args()

    resultado = indexar_repo_github(
        args.repo_url,
        max_archivos=args.max_archivos,
        mostrar_progreso=args.progreso,
    )
    print(f"Archivos indexados: {resultado.archivos_indexados}")
    print(f"Archivos omitidos: {resultado.archivos_omitidos}")


if __name__ == "__main__":
    main()
