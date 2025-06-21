import json

class ModelRouter:
    """
    Selecciona el conector y el ID del modelo de IA basándose en el bot_id.
    """
    def __init__(self, config_path="bots_config.json"):
        """
        Inicializa el enrutador cargando la configuración de bots desde un archivo JSON.
        """
        self.default_fallback = {"connector": "openai", "model_id": "gpt-3.5-turbo"}
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                self.bots_config = json.load(f)
            print("ModelRouter inicializado con la configuración de bots.")
        except Exception as e:
            print(f"ADVERTENCIA de ModelRouter: No se pudo cargar '{config_path}'. Se usará un fallback. Error: {e}")
            self.bots_config = {}

    def select_model(self, query: str, bot_id: str) -> dict:
        """
        Obtiene la configuración del modelo para un bot_id específico.
        """
        print(f"ModelRouter: Seleccionando modelo para bot_id='{bot_id}'")

        bot_config = self.bots_config.get(bot_id)
        
        if not bot_config:
            print(f"ADVERTENCIA: bot_id '{bot_id}' no encontrado. Usando fallback del bot principal.")
            bot_config = self.bots_config.get("bytcode_main_bot", {})

        # Lógica para elegir entre simple, complex, code (actualmente usa 'simple' por defecto)
        # Se puede expandir esta lógica analizando el 'query'
        model_type = "simple" 
        model_info = bot_config.get("active_models", {}).get(model_type)
        
        if model_info and "connector" in model_info and "model_id" in model_info:
            print(f"Modelo seleccionado: {model_info}")
            return model_info
        
        print(f"ADVERTENCIA: No se encontró una configuración válida para '{bot_id}'. Usando fallback por defecto.")
        return self.default_fallback