import os
import google.generativeai as genai
from dotenv import load_dotenv

class GoogleConnector:
    def __init__(self):
        print("Inicializando GoogleConnector...")
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("¡Error Crítico! GOOGLE_API_KEY no fue encontrada.")
        genai.configure(api_key=api_key)
        print("GoogleConnector configurado y listo.")

    def get_response_stream(self, messages: list, model_id: str = "gemini-1.5-pro", **kwargs):
        try:
            print(f"Iniciando STREAM con Gemini (modelo: {model_id})...")
            
            # --- LÓGICA DE ADAPTACIÓN PARA GEMINI ---
            
            system_instruction = None
            # 1. Extraer el prompt del sistema si existe.
            if messages and messages[0]['role'] == 'system':
                system_instruction = messages[0]['content']
                # Quitamos el mensaje de sistema de la lista que pasaremos como historial.
                history_messages = messages[1:]
            else:
                history_messages = messages

            # 2. Convertir el resto del historial al formato de Gemini ('assistant' -> 'model')
            gemini_history = []
            for msg in history_messages[:-1]: # Todos menos el último mensaje del usuario
                gemini_history.append({
                    # Traducimos el rol 'assistant' a 'model' que es lo que espera Gemini
                    "role": "model" if msg["role"] == "assistant" else msg["role"],
                    "parts": [msg["content"]]
                })

            # 3. Inicializar el modelo con la instrucción del sistema
            model = genai.GenerativeModel(
                model_id,
                system_instruction=system_instruction
            )
            
            # 4. Iniciar el chat con el historial convertido
            chat = model.start_chat(history=gemini_history)
            
            # 5. Enviar el último mensaje del usuario
            last_user_message = history_messages[-1]["content"]
            response_stream = chat.send_message(last_user_message, stream=True)

            for chunk in response_stream:
                if hasattr(chunk, 'text') and chunk.text:
                    yield chunk.text

        except Exception as e:
            print(f"Ocurrió un error al contactar la API de Gemini: {e}")
            yield "Lo siento, tuve un problema para contactar a mi cerebro de IA (Gemini)."