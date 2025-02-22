from fastapi import FastAPI
from pydantic import BaseModel
from llama_cpp import Llama
import uvicorn
import os

app = FastAPI()

# Path to the GGUF model
MODEL_PATH = os.path.abspath("models/tinyllama-1.1b-chat-v1.0.Q2_K.gguf")

# Initialize the Llama model (loads on startup)
llm = Llama(model_path=MODEL_PATH, use_mmap=True, verbose=False)

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    user_input = request.message

    # System prompt for consistent behavior
    system_prompt = (
        "You are a helpful AI assistant. Answer questions concisely and professionally."
        "Provide responses short and simple. Avoid technical and complex answers."
        "Ensure responses are relevant to the user's question."
        "Always provide clear and accurate information."
    )
    
    prompt = f"[SYSTEM]: {system_prompt}\n[USER]: {user_input}\n[ASSISTANT]:"

    # Generate response
    response = llm(
        prompt,
        max_tokens=2000,
        temperature=0.5,
        top_p=0.5,
        top_k=50,
        repeat_penalty=1.1,
        stop=["[USER]:", "\n[ASSISTANT]:"]
    )

    # Extract and return response
    text = response["choices"][0]["text"].strip()
    return {"response": text if text else "Error: No output from AI"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
