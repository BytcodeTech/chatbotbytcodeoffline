import os
from openai import OpenAI
from dotenv import load_dotenv

class DeepSeekConnector:
    def __init__(self):
        print("Inicializando DeepSeekConnector...")
        load_dotenv()
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("¡Error Crítico! DEEPSEEK_API_KEY no fue encontrada.")
        self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
        print("DeepSeekConnector configurado y listo.")

    def get_response_stream(self, messages: list, model_id: str = "deepseek-chat", **kwargs):
        try:
            print(f"Iniciando STREAM con DeepSeek (modelo: {model_id})...")
            stream = self.client.chat.completions.create(
                model=model_id,
                messages=messages, # Pasamos el historial completo
                stream=True
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content is not None:
                    yield content
        except Exception as e:
            print(f"\n--- INICIO DEL ERROR DETALLADO DE DEEPSEEK ---\n{e}\n--- FIN DEL ERROR DETALLADO DE DEEPSEEK ---\n")
            yield "Lo siento, tuve un problema con la conexión a DeepSeek."