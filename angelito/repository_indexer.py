import shutil
import ssl
import subprocess
import tempfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import certifi

EXTENSIONES_CODIGO = {
    ".java",
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".html",
    ".css",
    ".scss",
    ".sql",
    ".xml",
    ".json",
    ".yml",
    ".yaml",
    ".md",
    ".properties",
}

DIRECTORIOS_IGNORADOS = {
    ".git",
    ".idea",
    ".vscode",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "target",
    "venv",
    ".venv",
    "qdrant_db",
}

ARCHIVOS_IGNORADOS = {
    ".env",
    ".env.local",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
}

MAX_BYTES_ARCHIVO = 80_000
SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


@dataclass(frozen=True)
class ResultadoIndexacion:
    archivos_indexados: int
    archivos_omitidos: int


@dataclass(frozen=True)
class RepoGithub:
    nombre: str
    clone_url: str
    fork: bool


def _es_archivo_indexable(ruta: Path) -> bool:
    if ruta.name in ARCHIVOS_IGNORADOS:
        return False
    if ruta.suffix.lower() not in EXTENSIONES_CODIGO:
        return False
    if ruta.stat().st_size > MAX_BYTES_ARCHIVO:
        return False
    return True


def _leer_texto(ruta: Path) -> str | None:
    try:
        return ruta.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def indexar_directorio(base_dir: Path, etiqueta: str | None = None) -> ResultadoIndexacion:
    return indexar_directorio_con_opciones(base_dir=base_dir, etiqueta=etiqueta)


def indexar_directorio_con_opciones(
    base_dir: Path | str,
    etiqueta: str | None = None,
    max_archivos: int | None = None,
    mostrar_progreso: bool = False,
) -> ResultadoIndexacion:
    base_dir = Path(base_dir).resolve()
    if not base_dir.exists():
        raise FileNotFoundError(f"No existe el directorio: {base_dir}")
    if not base_dir.is_dir():
        raise NotADirectoryError(f"No es un directorio: {base_dir}")

    indexados = 0
    omitidos = 0

    for ruta in base_dir.rglob("*"):
        if not ruta.is_file():
            continue
        if any(parte in DIRECTORIOS_IGNORADOS for parte in ruta.relative_to(base_dir).parts):
            omitidos += 1
            continue
        if not _es_archivo_indexable(ruta):
            omitidos += 1
            continue

        contenido = _leer_texto(ruta)
        if not contenido:
            omitidos += 1
            continue

        ruta_relativa = ruta.relative_to(base_dir).as_posix()
        origen = f"{etiqueta}/{ruta_relativa}" if etiqueta else ruta_relativa

        if mostrar_progreso:
            print(f"Indexando: {origen}", flush=True)

        from angelito.vector_store import indexar_codigo_local

        indexar_codigo_local(origen, contenido)
        indexados += 1

        if max_archivos is not None and indexados >= max_archivos:
            break

    return ResultadoIndexacion(archivos_indexados=indexados, archivos_omitidos=omitidos)


def clonar_repo(repo_url: str, destino: Path) -> Path:
    repo_nombre = repo_url.rstrip("/").removesuffix(".git").split("/")[-1]
    repo_dir = destino / repo_nombre

    subprocess.run(
        ["git", "clone", "--depth", "1", repo_url, str(repo_dir)],
        check=True,
        text=True,
        timeout=180,
    )
    return repo_dir


def indexar_repo_github(
    repo_url: str,
    max_archivos: int | None = None,
    mostrar_progreso: bool = False,
) -> ResultadoIndexacion:
    temp_dir = Path(tempfile.mkdtemp(prefix="angelito_repo_"))
    try:
        if mostrar_progreso:
            print(f"Clonando: {repo_url}", flush=True)
        repo_dir = clonar_repo(repo_url, temp_dir)
        return indexar_directorio_con_opciones(
            repo_dir,
            etiqueta=repo_dir.name,
            max_archivos=max_archivos,
            mostrar_progreso=mostrar_progreso,
        )
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def listar_repos_publicos_usuario(usuario: str, incluir_forks: bool = False) -> list[RepoGithub]:
    import json

    repos: list[RepoGithub] = []
    pagina = 1

    while True:
        url = (
            f"https://api.github.com/users/{usuario}/repos"
            f"?per_page=100&page={pagina}&sort=updated"
        )
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "angelito-local-indexer",
            },
        )

        with urllib.request.urlopen(request, timeout=30, context=SSL_CONTEXT) as response:
            data = json.loads(response.read().decode("utf-8"))

        if not data:
            break

        for item in data:
            es_fork = bool(item.get("fork"))
            if es_fork and not incluir_forks:
                continue
            repos.append(
                RepoGithub(
                    nombre=item["full_name"],
                    clone_url=item["clone_url"],
                    fork=es_fork,
                )
            )

        pagina += 1

    return repos


def indexar_repos_publicos_usuario(
    usuario: str,
    incluir_forks: bool = False,
    mostrar_progreso: bool = False,
) -> ResultadoIndexacion:
    repos = listar_repos_publicos_usuario(usuario, incluir_forks=incluir_forks)
    total_indexados = 0
    total_omitidos = 0

    for repo in repos:
        if mostrar_progreso:
            print(f"\nRepo: {repo.nombre}", flush=True)

        resultado = indexar_repo_github(repo.clone_url, mostrar_progreso=mostrar_progreso)
        total_indexados += resultado.archivos_indexados
        total_omitidos += resultado.archivos_omitidos

    return ResultadoIndexacion(
        archivos_indexados=total_indexados,
        archivos_omitidos=total_omitidos,
    )
