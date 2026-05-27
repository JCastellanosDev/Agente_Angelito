import sqlite3
from pathlib import Path

from angelito.settings import DB_PATH


def inicializar_db(db_path: Path = DB_PATH) -> None:
    with sqlite3.connect(db_path) as conexion:
        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS mensajes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rol TEXT NOT NULL,
                contenido TEXT NOT NULL,
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def guardar_mensaje(rol: str, contenido: str, db_path: Path = DB_PATH) -> None:
    contenido_limpio = contenido.strip()
    rol_limpio = rol.strip()

    if not contenido_limpio:
        return

    with sqlite3.connect(db_path) as conexion:
        conexion.execute(
            "INSERT INTO mensajes (rol, contenido) VALUES (?, ?)",
            (rol_limpio, contenido_limpio),
        )


def recuperar_historial(
    limite: int | None = None,
    db_path: Path = DB_PATH,
) -> list:
    query = "SELECT rol, contenido FROM mensajes ORDER BY id ASC"
    params: tuple[int, ...] = ()

    if limite is not None and limite > 0:
        query = """
            SELECT rol, contenido
            FROM (
                SELECT id, rol, contenido FROM mensajes ORDER BY id DESC LIMIT ?
            )
            ORDER BY id ASC
        """
        params = (limite,)

    with sqlite3.connect(db_path) as conexion:
        registros = conexion.execute(query, params).fetchall()

    mensajes = []
    for rol, contenido in registros:
        if not contenido:
            continue
        if rol == "usuario":
            mensajes.append({"role": "usuario", "content": contenido})
        elif rol == "agente":
            mensajes.append({"role": "agente", "content": contenido})

    return mensajes
