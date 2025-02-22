from llama_cpp import Llama

def main():
    # Initialize the Llama model
    model_path = "./tinyllama-1.1b-chat-v1.0.Q2_K.gguf"
    llm = Llama(model_path=model_path, use_mmap=True, verbose=False)

    # Define custom system instructions
    system_prompt = (
        "You are a helpful AI assistant. Answer questions concisely and professionally. "
        "Provide responses short and simple. Avoid technical jargon and complex sentences."
    )
    
    # User input
    user_input = "Who is Elon Musk?"
    
    # Combine system instructions with user input
    prompt = f"[SYSTEM]: {system_prompt}\n[USER]: {user_input}\n[ASSISTANT]:"

    # Generate response
    response = llm(
        prompt,
        max_tokens=256,
        temperature=0.7,
        top_p=0.9,
        top_k=50,
        repeat_penalty=1.1,
        stop=["[USER]:", "\n[ASSISTANT]:"]
    )

    # Extract and print the text from the response
    text = response["choices"][0]["text"]
    print(text)

if __name__ == "__main__":
    main()
