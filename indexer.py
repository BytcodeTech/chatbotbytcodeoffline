import os
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

def create_vector_db():
    print("Iniciando la creación/actualización de la base de datos de vectores...")
    
    # Cargar el modelo de embeddings
    print("Cargando el modelo SentenceTransformer...")
    model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
    print("Modelo cargado.")

    # Ruta a los documentos
    docs_path = "data/raw_docs"
    all_chunks = []
    
    # Leer todos los documentos .txt
    for filename in os.listdir(docs_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(docs_path, filename)
            print(f"Procesando archivo: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                doc_text = f.read()

            # --- ESTRATEGIA DE CHUNKING MEJORADA ---
            # Dividimos por párrafos (dos saltos de línea) en lugar de por líneas.
            # Esto crea chunks más grandes y con más contexto.
            paragraphs = doc_text.split('\n\n')
            # Filtramos los párrafos vacíos que puedan resultar del split.
            chunks = [para.strip() for para in paragraphs if para.strip()]
            all_chunks.extend(chunks)
            print(f"Se extrajeron {len(chunks)} párrafos (chunks) del archivo.")

    if not all_chunks:
        print("No se encontraron chunks para indexar. Abortando.")
        return

    # Generar embeddings para cada chunk
    print(f"Generando embeddings para {len(all_chunks)} chunks totales...")
    chunk_embeddings = model.encode(all_chunks, show_progress_bar=True)
    
    # Normalizar los vectores
    faiss.normalize_L2(chunk_embeddings)

    # Crear el índice FAISS
    dimension = chunk_embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index = faiss.IndexIDMap(index)
    
    # Añadir los vectores al índice
    ids = np.arange(len(all_chunks))
    index.add_with_ids(chunk_embeddings, ids)

    # Crear el mapa de chunks (ID -> texto)
    chunks_map = {str(i): chunk for i, chunk in enumerate(all_chunks)}

    # Guardar el índice y el mapa
    output_dir = "data/vector_db"
    os.makedirs(output_dir, exist_ok=True)
    
    index_path = os.path.join(output_dir, "bytcode_index.faiss")
    map_path = os.path.join(output_dir, "chunks_map.json")
    
    faiss.write_index(index, index_path)
    print(f"Índice FAISS guardado en: {index_path}")
    
    with open(map_path, 'w', encoding='utf-8') as f:
        json.dump(chunks_map, f, ensure_ascii=False, indent=4)
    print(f"Mapa de chunks guardado en: {map_path}")
    
    print("\n¡Base de datos de vectores actualizada con éxito!")

if __name__ == "__main__":
    create_vector_db()