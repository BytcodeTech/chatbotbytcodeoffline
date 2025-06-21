# En un nuevo archivo: core/conversation_manager.py

from collections import deque

class ConversationManager:
    """
    Gestiona el historial de conversaciones para múltiples usuarios.
    Usa un diccionario en memoria, donde cada clave es un user_id.
    """
    def __init__(self, max_history_length: int = 10):
        """
        Inicializa el gestor.
        :param max_history_length: Número máximo de intercambios (pregunta + respuesta) a recordar.
        """
        self.histories = {}
        # Usamos deque para limitar automáticamente la longitud del historial
        self.max_history_length = max_history_length * 2 # (user + assistant)
        print("ConversationManager inicializado (memoria de chat lista).")

    def get_history(self, user_id: str) -> list:
        """Recupera el historial de conversación para un usuario."""
        return list(self.histories.get(user_id, []))

    def add_message(self, user_id: str, role: str, content: str):
        """Añade un nuevo mensaje al historial de un usuario."""
        if user_id not in self.histories:
            self.histories[user_id] = deque(maxlen=self.max_history_length)
        
        # El formato debe coincidir con el que esperan las APIs (OpenAI, DeepSeek)
        self.histories[user_id].append({"role": role, "content": content})