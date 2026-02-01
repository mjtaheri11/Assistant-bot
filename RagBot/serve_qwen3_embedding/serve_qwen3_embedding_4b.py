import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Union
from transformers import AutoModel, AutoTokenizer

app = FastAPI(title="Qwen3-Embedding Local API")

# SET YOUR LOCAL PATH HERE
MODEL_PATH = "/home/jovyan/Assistant-bot/saved_models/Qwen3-Embedding-4B"

# Load model and tokenizer
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
model = AutoModel.from_pretrained(MODEL_PATH, trust_remote_code=True, device_map="auto")
model.eval()

class EmbeddingRequest(BaseModel):
    input: Union[str, List[str]]
    model: str = "qwen3-embedding-4b"

@app.post("/v1/embeddings")
async def get_embeddings(request: EmbeddingRequest):
    try:
        inputs = request.input if isinstance(request.input, list) else [request.input]
        
        # Tokenize and move to GPU if available
        encoded_input = tokenizer(inputs, padding=True, truncation=True, return_tensors='pt').to(model.device)

        with torch.no_grad():
            model_output = model(**encoded_input)
            # Qwen3-Embedding typically uses the [EOS] token or Mean Pooling
            # For standard embeddings, we use the last hidden state of the first token (or mean pool)
            embeddings = model_output.last_hidden_state[:, 0, :]
            
        # Normalize embeddings
        embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
        
        return {
            "object": "list",
            "data": [
                {"object": "embedding", "embedding": emb.tolist(), "index": i} 
                for i, emb in enumerate(embeddings)
            ],
            "model": request.model
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8100)