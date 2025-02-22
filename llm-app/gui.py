import tkinter as tk
import requests

# Backend API URL
API_URL = "http://127.0.0.1:8000/chat"

def send_message():
    user_input = entry.get()
    if not user_input.strip():
        return

    # Display user input
    chat_history.insert(tk.END, f"You: {user_input}\n\n")

    try:
        # Send request to backend
        response = requests.post(API_URL, json={"message": user_input})

        if response.status_code == 200:
            ai_response = response.json().get("response", "Error: No response")
        else:
            ai_response = f"Error: {response.status_code} - {response.text}"

    except requests.exceptions.RequestException as e:
        ai_response = f"Error: Unable to connect to AI ({str(e)})"

    # Display AI response
    chat_history.insert(tk.END, f"AI: {ai_response}\n\n{'-'*50}\n\n")
    chat_history.yview(tk.END)  # Auto-scroll
    entry.delete(0, tk.END)

# Create GUI
root = tk.Tk()
root.title("TinyLlama Chatbot")
root.geometry("500x500")

chat_history = tk.Text(root, wrap=tk.WORD, height=20, width=60)
chat_history.pack(padx=10, pady=10)

entry = tk.Entry(root, width=50)
entry.pack(pady=5)

send_button = tk.Button(root, text="Send", command=send_message)
send_button.pack(pady=5)

root.mainloop()
