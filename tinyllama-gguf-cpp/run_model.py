from ctransformers import AutoModelForCausalLM

model_path = "tinyllama-1.1b-chat-v1.0.Q2_K.gguf"

# Ensure the correct model type
llm = AutoModelForCausalLM.from_pretrained(model_path, model_type="llama", gpu_layers=35)

response = llm("Hello! How are you?")
print(response)
