import tkinter as tk
import tkinter.scrolledtext as scrolledtext
import requests
import json
import os

# Ollama API endpoint (default is localhost:11434)
OLLAMA_API_URL = "http://localhost:11434/api/generate"

def generate_response(prompt):
    """Generate a response from the Dolphin-Llama3 model using Ollama API"""
    try:
        data = {
            "model": "dolphin-llama3:8b",  # You can change to 70b if you have that version
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(OLLAMA_API_URL, json=data)
        if response.status_code == 200:
            return response.json().get('response', 'No response generated')
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error generating response: {str(e)}"

def send_query():
    """Send user query to the LLM and display the response"""
    user_input = entry.get()
    if not user_input.strip():
        return
    
    # Display user input
    chat_area.config(state=tk.NORMAL)
    chat_area.insert(tk.END, f"You: {user_input}\n\n", "user")
    
    # Show "thinking" message
    chat_area.insert(tk.END, "LLM: Thinking...\n", "thinking")
    chat_area.see(tk.END)
    chat_area.update_idletasks()
    
    # Generate response
    response = generate_response(user_input)
    
    # Remove thinking message and display actual response
    chat_area.delete("end-2l", "end")
    chat_area.insert(tk.END, f"LLM: {response}\n\n", "llm")
    chat_area.see(tk.END)
    chat_area.config(state=tk.DISABLED)
    
    # Clear entry field
    entry.delete(0, tk.END)

# Set up the GUI
root = tk.Tk()
root.title("Chat with Dolphin-Llama3")
root.geometry("800x600")

# Create a frame for the chat area
chat_frame = tk.Frame(root)
chat_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Create a scrolled text widget for the chat
chat_area = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, state=tk.DISABLED)
chat_area.pack(fill=tk.BOTH, expand=True)

# Configure text tags for styling
chat_area.tag_configure("user", foreground="blue")
chat_area.tag_configure("llm", foreground="green")
chat_area.tag_configure("thinking", foreground="gray")

# Create a frame for the input area
input_frame = tk.Frame(root)
input_frame.pack(padx=10, pady=10, fill=tk.X)

# Create an entry widget for user input
entry = tk.Entry(input_frame)
entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
entry.bind("<Return>", lambda event: send_query())

# Create a send button
send_button = tk.Button(input_frame, text="Send", command=send_query)
send_button.pack(side=tk.RIGHT, padx=5)

# Display welcome message
chat_area.config(state=tk.NORMAL)
chat_area.insert(tk.END, "Welcome to Dolphin-Llama3 Chat!\n")
chat_area.insert(tk.END, "Type your message and press Enter or click Send.\n\n")
chat_area.config(state=tk.DISABLED)

# Start the main loop
root.mainloop() 