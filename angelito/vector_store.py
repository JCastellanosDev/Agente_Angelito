import re
import sqlite3
from pathlib import Path

from angelito.settings import DB_PATH

TOKEN_RE = re.compile(r"[a-zA-Z_][a-zA-Z0-9_]{2,}")


def _normalizar_tokens(texto: str) -> set[str]:
    return {token.lower() for token in TOKEN_RE.findall(texto)}


def inicializar_memoria_codigo(db_path: Path = DB_PATH) -> None:
    with sqlite3.connect(db_path) as conexion:
        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS codigo_fragmentos (
                ruta TEXT PRIMARY KEY,
                contenido TEXT NOT NULL,
                tokens TEXT NOT NULL,
                actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def indexar_codigo_local(ruta_archivo: str, contenido_codigo: str) -> None:
    contenido_limpio = contenido_codigo.strip()
    if not contenido_limpio:
        return

    tokens = " ".join(sorted(_normalizar_tokens(contenido_limpio)))
    inicializar_memoria_codigo()

    with sqlite3.connect(DB_PATH) as conexion:
        conexion.execute(
            """
            INSERT INTO codigo_fragmentos (ruta, contenido, tokens, actualizado_en)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(ruta) DO UPDATE SET
                contenido = excluded.contenido,
                tokens = excluded.tokens,
                actualizado_en = CURRENT_TIMESTAMP
            """,
            (ruta_archivo, contenido_limpio, tokens),
        )


def buscar_contexto_codigo(query: str, k: int = 3) -> str:
    inicializar_memoria_codigo()
    query_tokens = _normalizar_tokens(query)
    if not query_tokens:
        return ""

    with sqlite3.connect(DB_PATH) as conexion:
        registros = conexion.execute(
            "SELECT ruta, contenido, tokens FROM codigo_fragmentos"
        ).fetchall()

    resultados = []
    for ruta, contenido, tokens_texto in registros:
        tokens = set(tokens_texto.split())
        coincidencias = query_tokens.intersection(tokens)
        if not coincidencias:
            continue

        score = len(coincidencias)
        resultados.append((score, ruta, contenido))

    resultados.sort(key=lambda item: item[0], reverse=True)

    fragmentos = []
    for _, ruta, contenido in resultados[:k]:
        fragmentos.append(f"--- Fragmento de {ruta} ---\n{contenido}")

    return "\n\n".join(fragmentos)
