import json
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from core.orchestrator import Orchestrator

ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Evento de Startup: Cargando el Orchestrator...")
    ml_models["orchestrator"] = Orchestrator()
    print("Evento de Startup: Orchestrator y todos los modelos cargados.")
    yield
    print("Evento de Shutdown: Limpiando modelos...")
    ml_models.clear()

app = FastAPI(title="Bytcode Chatbot", version="2.0.0", lifespan=lifespan)

try:
    with open("bots_config.json", "r", encoding="utf-8") as f:
        bots_config = json.load(f)
    print("INFO: bots_config.json cargado exitosamente.")
except Exception as e:
    print(f"ADVERTENCIA: No se pudo cargar bots_config.json. El selector de bots estará vacío. Error: {e}")
    bots_config = {}

class ChatRequest(BaseModel):
    user_id: str
    query: str
    bot_id: str

@app.post("/chat")
def handle_chat(request: ChatRequest):
    # --- LLAMADA AL NUEVO MÉTODO CON GESTIÓN DE HISTORIAL ---
    text_stream_generator = ml_models["orchestrator"].handle_query_stream(
        query=request.query,
        user_id=request.user_id,
        bot_id=request.bot_id
    )
    return StreamingResponse(text_stream_generator, media_type="text/plain; charset=utf-8")

@app.get("/bots")
async def get_bots():
    return bots_config

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=FileResponse)
async def read_root():
    return "index.html"