import shutil
import sqlite3

from angelito.settings import DB_PATH, GOOGLE_API_KEY
from angelito.vector_store import inicializar_memoria_codigo


def main() -> None:
    inicializar_memoria_codigo()
    git_ok = shutil.which("git") is not None

    with sqlite3.connect(DB_PATH) as conexion:
        mensajes = conexion.execute("SELECT count(*) FROM mensajes").fetchone()[0]
        fragmentos = conexion.execute("SELECT count(*) FROM codigo_fragmentos").fetchone()[0]

    print(f"Git disponible: {'si' if git_ok else 'no'}")
    print(f"GOOGLE_API_KEY configurada: {'si' if GOOGLE_API_KEY else 'no'}")
    print(f"Mensajes guardados: {mensajes}")
    print(f"Fragmentos de codigo indexados: {fragmentos}")


if __name__ == "__main__":
    main()
