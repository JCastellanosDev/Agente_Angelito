import argparse

from angelito.repository_indexer import indexar_repos_publicos_usuario
from angelito.settings import GITHUB_USER


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Indexa todos los repos publicos de un usuario de GitHub."
    )
    parser.add_argument(
        "usuario",
        nargs="?",
        default=GITHUB_USER,
        help="Usuario de GitHub. Por defecto usa GITHUB_USER.",
    )
    parser.add_argument("--incluir-forks", action="store_true", help="Tambien indexa forks.")
    parser.add_argument("--progreso", action="store_true", help="Muestra cada repo y archivo indexado.")
    args = parser.parse_args()

    resultado = indexar_repos_publicos_usuario(
        args.usuario,
        incluir_forks=args.incluir_forks,
        mostrar_progreso=args.progreso,
    )
    print(f"Archivos indexados: {resultado.archivos_indexados}")
    print(f"Archivos omitidos: {resultado.archivos_omitidos}")


if __name__ == "__main__":
    main()
