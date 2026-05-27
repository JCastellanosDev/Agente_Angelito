import json
import ssl
import urllib.error
import urllib.request
from dataclasses import dataclass

import certifi

from angelito.settings import CHAT_MODEL, require_google_api_key

SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


@dataclass(frozen=True)
class RespuestaLLM:
    content: str


class GeminiClient:
    def __init__(self, model: str = CHAT_MODEL, timeout: int = 30) -> None:
        self.model = model
        self.timeout = timeout
        self.api_key = require_google_api_key()

    def invoke(self, mensajes: list[dict[str, str]], system_prompt: str) -> RespuestaLLM:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )
        payload = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [self._convertir_mensaje(mensaje) for mensaje in mensajes],
            "generationConfig": {
                "temperature": 0.3,
                "maxOutputTokens": 1000,
            },
        }

        request = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout, context=SSL_CONTEXT) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            detalle = error.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"Google API respondio con error {error.code}: {detalle}") from error

        texto = self._extraer_texto(data)
        return RespuestaLLM(content=texto)

    @staticmethod
    def _convertir_mensaje(mensaje: dict[str, str]) -> dict:
        rol = "model" if mensaje["role"] == "agente" else "user"
        return {"role": rol, "parts": [{"text": mensaje["content"]}]}

    @staticmethod
    def _extraer_texto(data: dict) -> str:
        candidatos = data.get("candidates", [])
        if not candidatos:
            return "No recibi respuesta del modelo."

        partes = candidatos[0].get("content", {}).get("parts", [])
        textos = [parte.get("text", "") for parte in partes]
        return "\n".join(texto for texto in textos if texto).strip()


def crear_llm() -> GeminiClient:
    return GeminiClient()
