from .rag_retriever import RAGRetriever
from .model_router import ModelRouter
from connectors.google_connector import GoogleConnector
from connectors.openai_connector import OpenAIConnector
from connectors.deepseek_connector import DeepSeekConnector

class Orchestrator:
    def __init__(self):
        print("Orchestrator (Streaming) inicializado.")
        self.retriever = RAGRetriever()
        self.router = ModelRouter()
        self.connectors = {
            "google": GoogleConnector(),
            "openai": OpenAIConnector(),
            "deepseek": DeepSeekConnector()
        }
        # --- NUEVO: Diccionario para guardar historiales de chat ---
        self.chat_histories = {}
        print("Sistema listo para recibir peticiones.")

    def _get_or_create_history(self, session_id: str) -> list:
        """Obtiene el historial de una sesión o crea uno nuevo."""
        if session_id not in self.chat_histories:
            self.chat_histories[session_id] = []
        return self.chat_histories[session_id]

    def _get_system_prompt(self, context: str = None) -> str:
        """Genera el prompt de sistema basado en si hay contexto o no."""
        if context:
            return (
                "Actúa como un asistente entusiasta y muy amigable. Utiliza emojis 😊. "
                "Basándote estrictamente en el siguiente CONTEXTO, responde a la PREGUNTA del usuario. "
                f"CONTEXTO: --- {context} ---"
            )
        return (
            "Eres 'Bytbot', un asistente de IA creado por Bytcode 🤖. Tu personalidad es extremadamente amigable y entusiasta. "
            "Siempre usas emojis para expresarte mejor 🎉."
        )

    def handle_query_stream(self, user_id: str, query: str, bot_id: str):
        """Maneja la lógica principal y el historial de conversación."""
        print(f"\n--- Petición con Memoria --- \nUsuario: '{user_id}', Bot: '{bot_id}', Pregunta: '{query}'")

        # 1. Obtener/Crear historial de la sesión
        session_id = f"{user_id}_{bot_id}"
        history = self._get_or_create_history(session_id)

        # 2. Si es una conversación nueva, añadir RAG y prompt de sistema
        if not history:
            context, score = self.retriever.search(query)
            context_to_use = context if score < 1.5 else None
            system_prompt = self._get_system_prompt(context_to_use)
            history.append({"role": "system", "content": system_prompt})
        
        # 3. Añadir la pregunta actual del usuario al historial
        history.append({"role": "user", "content": query})

        # 4. Seleccionar modelo y conector
        model_decision = self.router.select_model(query=query, bot_id=bot_id)
        connector = self.connectors[model_decision["connector"]]
        model_id = model_decision["model_id"]
        
        # 5. Obtener el stream del conector
        response_stream = connector.get_response_stream(messages=history, model_id=model_id)
        
        # 6. Devolver el stream y guardar la respuesta completa en el historial
        full_bot_response = ""
        for chunk in response_stream:
            full_bot_response += chunk
            yield chunk
        
        # 7. Guardar la respuesta completa del bot en el historial para la próxima vez
        history.append({"role": "assistant", "content": full_bot_response})