from angelito.database import guardar_mensaje, inicializar_db, recuperar_historial
from angelito.llm import crear_llm
from angelito.repository_indexer import (
    indexar_directorio_con_opciones,
    indexar_repo_github,
    indexar_repos_publicos_usuario,
)
from angelito.settings import GITHUB_USER, MAX_CONTEXT_RESULTS, MAX_HISTORY_MESSAGES
from angelito.vector_store import buscar_contexto_codigo

SYSTEM_PROMPT = (
    "Eres un asistente de programacion exclusivo para el desarrollador "
    "JCastellanosDev. Te llamas Angelito. Responde con ejemplos claros, "
    "explicaciones breves y texto plano. No uses emojis."
)

AYUDA_COMANDOS = """
Comandos locales:
/ayuda
/indexar-github URL_DEL_REPO
/indexar-usuario [usuario]
/indexar-directorio RUTA_LOCAL [etiqueta]
/buscar-codigo texto a buscar
/salir
""".strip()


def _crear_mensaje_usuario(user_input: str) -> dict[str, str]:
    try:
        contexto = buscar_contexto_codigo(user_input, k=MAX_CONTEXT_RESULTS)
    except Exception as error:
        contexto = ""
        print(f"No pude recuperar contexto de codigo: {error}")

    if not contexto:
        return {"role": "usuario", "content": user_input}

    return {
        "role": "usuario",
        "content": (
            "Usa este contexto de codigo local si es relevante. "
            "Si no sirve para la pregunta, ignoralo.\n\n"
            f"{contexto}\n\n"
            f"Pregunta del usuario: {user_input}"
        ),
    }


def _manejar_comando(user_input: str) -> bool:
    partes = user_input.split()
    comando = partes[0].lower()

    if comando in {"/ayuda", "ayuda"}:
        print(AYUDA_COMANDOS)
        return True

    if comando in {"/salir", "salir"}:
        print("Chayito")
        raise KeyboardInterrupt

    if comando == "/indexar-github":
        if len(partes) < 2:
            print("Uso: /indexar-github URL_DEL_REPO")
            return True
        resultado = indexar_repo_github(partes[1], mostrar_progreso=True)
        print(f"Archivos indexados: {resultado.archivos_indexados}")
        print(f"Archivos omitidos: {resultado.archivos_omitidos}")
        return True

    if comando == "/indexar-usuario":
        usuario = partes[1] if len(partes) > 1 else GITHUB_USER
        resultado = indexar_repos_publicos_usuario(usuario, mostrar_progreso=True)
        print(f"Archivos indexados: {resultado.archivos_indexados}")
        print(f"Archivos omitidos: {resultado.archivos_omitidos}")
        return True

    if comando == "/indexar-directorio":
        if len(partes) < 2:
            print("Uso: /indexar-directorio RUTA_LOCAL [etiqueta]")
            return True
        etiqueta = partes[2] if len(partes) > 2 else None
        resultado = indexar_directorio_con_opciones(
            partes[1],
            etiqueta=etiqueta,
            mostrar_progreso=True,
        )
        print(f"Archivos indexados: {resultado.archivos_indexados}")
        print(f"Archivos omitidos: {resultado.archivos_omitidos}")
        return True

    if comando == "/buscar-codigo":
        query = user_input.removeprefix("/buscar-codigo").strip()
        if not query:
            print("Uso: /buscar-codigo texto a buscar")
            return True
        contexto = buscar_contexto_codigo(query, k=MAX_CONTEXT_RESULTS)
        print(contexto or "No encontre fragmentos relacionados.")
        return True

    return False


def ejecutar_chat() -> None:
    inicializar_db()
    llm = crear_llm()

    historial = recuperar_historial(limite=MAX_HISTORY_MESSAGES)
    mensajes_base = [*historial]

    print(f"Agente Angelito inicializado. Mensajes cargados: {len(historial)}")
    print("Escribe 'salir' para terminar.")
    print("Escribe '/ayuda' para ver comandos locales.")

    try:
        while True:
            user_input = input("\nTu: ").strip()
            if not user_input:
                continue

            if _manejar_comando(user_input):
                continue

            guardar_mensaje("usuario", user_input)

            mensajes = [*mensajes_base, _crear_mensaje_usuario(user_input)]

            try:
                respuesta = llm.invoke(mensajes, system_prompt=SYSTEM_PROMPT)
            except Exception as error:
                print(f"\nHubo un error al conectar con la API: {error}")
                continue

            print(f"\nAgente: {respuesta.content}")
            guardar_mensaje("agente", respuesta.content)

            mensajes_base.extend(
                [
                    {"role": "usuario", "content": user_input},
                    {"role": "agente", "content": respuesta.content},
                ]
            )
            mensajes_base = mensajes_base[-MAX_HISTORY_MESSAGES:]
    except KeyboardInterrupt:
        pass
