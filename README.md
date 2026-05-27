# Mi Agente IA

Asistente local de programacion con historial y memoria de codigo en SQLite.

## Configuracion

1. Crea y activa un entorno virtual.
2. Instala dependencias:

```bash
pip install -r requirements.txt
```

3. Crea tu archivo `.env` a partir de `.env.example`:

```bash
cp .env.example .env
```

4. Agrega tu `GOOGLE_API_KEY` en `.env`.

## Uso

Ejecuta el chat:

```bash
python App.py
```

Dentro del chat puedes usar comandos locales:

```text
/ayuda
/indexar-github https://github.com/JCastellanosDev/SistemaReservasCanchas.git
/indexar-usuario JCastellanosDev
/indexar-directorio /ruta/a/tu/proyecto etiqueta
/buscar-codigo crear reserva cancha horario
```

Indexa ejemplos de codigo:

```bash
python -m scripts.indexar_ejemplos
```

Indexa un repositorio de GitHub:

```bash
python -m scripts.indexar_github https://github.com/JCastellanosDev/SistemaReservasCanchas.git --progreso
```

Indexa todos los repos publicos del usuario configurado:

```bash
python -m scripts.indexar_usuario_github JCastellanosDev --progreso
```

Indexa un proyecto local:

```bash
python -m scripts.indexar_directorio /ruta/a/tu/proyecto --etiqueta nombre-del-proyecto --progreso
```

Para repos privados, usa una URL SSH o deja tus credenciales configuradas en Git. Angelito no guarda tokens ni claves de GitHub.

Ejecuta diagnostico local:

```bash
python -m scripts.diagnostico
```

## Archivos que no se suben a Git

`.env`, bases `.db`, `qdrant_db/`, `venv/`, caches e IDEs quedan ignorados por `.gitignore`.
