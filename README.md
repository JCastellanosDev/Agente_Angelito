# Angelito

Asistente de programación para la terminal, con memoria de conversación y búsqueda en tu propio código. Usa la API de Google Gemini para responder y SQLite para guardar el historial y un índice local de fragmentos de código.

Proyecto personal para practicar arquitectura por capas en Python, consumo de APIs y persistencia con SQLite.

## Qué hace

- Chat en consola con historial persistente: al iniciar carga los últimos mensajes.
- Indexa tu código desde un repositorio de GitHub, desde todos los repos públicos de un usuario o desde una carpeta local.
- Antes de cada pregunta busca fragmentos relacionados en el índice y se los pasa al modelo como contexto.
- Incluye comandos locales que no consumen la API (`/buscar-codigo`, `/indexar-*`).

## Cómo funciona

```text
Pregunta ──► busca fragmentos en el índice (SQLite) ──► prompt + contexto ──► Gemini ──► respuesta
                                                                                          │
                                                          historial de la conversación ◄──┘ (SQLite)
```

La búsqueda de contexto compara palabras clave entre la pregunta y los fragmentos indexados; no usa embeddings.

## Estructura

```text
App.py                      # Punto de entrada
angelito/
├── chat.py                 # Bucle de chat y comandos locales
├── llm.py                  # Cliente de la API de Gemini
├── database.py             # Historial de conversación (SQLite)
├── vector_store.py         # Índice y búsqueda de fragmentos de código
├── repository_indexer.py   # Indexado de repos de GitHub y carpetas locales
└── settings.py             # Configuración desde variables de entorno
scripts/                    # Utilidades de indexado y diagnóstico
```

## Requisitos

- Python 3.9 o superior
- Una API key de Gemini (Google AI Studio)

## Instalación

1. Crea y activa un entorno virtual.
2. Instala las dependencias:

```bash
pip install -r requirements.txt
```

3. Crea tu archivo `.env` a partir de `.env.example`:

```bash
cp .env.example .env
```

4. Agrega tu `GOOGLE_API_KEY` en `.env`.

### Variables de entorno

| Variable | Obligatoria | Por defecto | Descripción |
|---|---|---|---|
| `GOOGLE_API_KEY` | Sí | — | API key de Gemini |
| `CHAT_MODEL` | No | `gemini-2.5-flash` | Modelo de Gemini a usar |
| `GITHUB_USER` | No | `JCastellanosDev` | Usuario para `/indexar-usuario` |
| `MAX_HISTORY_MESSAGES` | No | `20` | Mensajes de historial que se envían al modelo |
| `MAX_CONTEXT_RESULTS` | No | `3` | Fragmentos de código que se añaden como contexto |
| `ANGELITO_DB_PATH` | No | `historial_angelito.db` | Ruta de la base de datos SQLite |

## Uso

Ejecuta el chat:

```bash
python App.py
```

Comandos locales dentro del chat:

```text
/ayuda
/indexar-github https://github.com/JCastellanosDev/SistemaReservasCanchas.git
/indexar-usuario JCastellanosDev
/indexar-directorio /ruta/a/tu/proyecto etiqueta
/buscar-codigo crear reserva cancha horario
/salir
```

### Indexado desde la terminal

Indexa ejemplos de código:

```bash
python -m scripts.indexar_ejemplos
```

Indexa un repositorio de GitHub:

```bash
python -m scripts.indexar_github https://github.com/JCastellanosDev/SistemaReservasCanchas.git --progreso
```

Indexa todos los repos públicos del usuario configurado:

```bash
python -m scripts.indexar_usuario_github JCastellanosDev --progreso
```

Indexa un proyecto local:

```bash
python -m scripts.indexar_directorio /ruta/a/tu/proyecto --etiqueta nombre-del-proyecto --progreso
```

Para repos privados, usa una URL SSH o deja tus credenciales configuradas en Git. Angelito no guarda tokens ni claves de GitHub.

### Diagnóstico

```bash
python -m scripts.diagnostico
```

## Privacidad

El archivo `.env` y la base de datos local (`historial_angelito.db`) están en `.gitignore`, así que tu API key y tu historial no se suben al repositorio.

## Autor

Jesús Castellanos - [@JCastellanosDev](https://github.com/JCastellanosDev)

## Licencia

MIT
