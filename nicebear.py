from flask import Flask, render_template, request, jsonify, send_from_directory
import requests
import json
import os
import threading
import webbrowser
import shutil
import base64

# Ollama API endpoint (default is localhost:11434)
OLLAMA_API_URL = "http://localhost:11434/api/generate"

app = Flask(__name__, static_folder='static')

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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '')
    if not user_input.strip():
        return jsonify({'response': 'Please enter a message'})
    
    response = generate_response(user_input)
    return jsonify({'response': response})

# Explicitly serve the bear image
@app.route('/bear.png')
def serve_bear_image():
    return send_from_directory(app.root_path, 'bear.png')

def open_browser():
    """Open the browser after a short delay"""
    webbrowser.open('http://localhost:5000')

# Create templates directory and HTML file
def create_template_files():
    # Create templates directory
    os.makedirs('templates', exist_ok=True)
    
    html_content = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>nicebear</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }
            .header {
                display: flex;
                align-items: center;
                margin-bottom: 20px;
            }
            .bear-image {
                width: 80px;
                height: 80px;
                margin-right: 20px;
            }
            #chat-container {
                height: 500px;
                border: 1px solid #ccc;
                padding: 10px;
                overflow-y: auto;
                margin-bottom: 10px;
                background-color: #f9f9f9;
            }
            .user-message {
                color: blue;
                margin-bottom: 10px;
            }
            .llm-message {
                color: green;
                margin-bottom: 20px;
            }
            .thinking {
                color: gray;
                font-style: italic;
            }
            #input-container {
                display: flex;
            }
            #user-input {
                flex-grow: 1;
                padding: 8px;
                margin-right: 10px;
            }
            button {
                padding: 8px 15px;
                background-color: #4CAF50;
                color: white;
                border: none;
                cursor: pointer;
            }
            button:hover {
                background-color: #45a049;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <img src="/bear.png" alt="Bear" class="bear-image">
            <h1>nicebear</h1>
        </div>
        <div id="chat-container">
            <div>chat with bear</div>
            <div>type your message</div>
            <br>
        </div>
        <div id="input-container">
            <input type="text" id="user-input" placeholder="Type your message here...">
            <button id="send-button">Send</button>
        </div>

        <script>
            const chatContainer = document.getElementById('chat-container');
            const userInput = document.getElementById('user-input');
            const sendButton = document.getElementById('send-button');
            
            function addMessage(text, className) {
                const messageDiv = document.createElement('div');
                messageDiv.className = className;
                messageDiv.textContent = text;
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
                return messageDiv;
            }
            
            async function sendMessage() {
                const message = userInput.value.trim();
                if (!message) return;
                
                // Add user message
                addMessage(`You: ${message}`, 'user-message');
                userInput.value = '';
                
                // Add thinking message
                const thinkingDiv = addMessage('nicebear says...', 'thinking');
                
                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ message }),
                    });
                    
                    const data = await response.json();
                    
                    // Remove thinking message
                    chatContainer.removeChild(thinkingDiv);
                    
                    // Add LLM response
                    addMessage(`LLM: ${data.response}`, 'llm-message');
                } catch (error) {
                    // Remove thinking message
                    chatContainer.removeChild(thinkingDiv);
                    
                    // Add error message
                    addMessage(`Error: ${error.message}`, 'llm-message');
                }
            }
            
            sendButton.addEventListener('click', sendMessage);
            userInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        </script>
    </body>
    </html>
    '''
    
    with open('templates/index.html', 'w') as f:
        f.write(html_content)

if __name__ == '__main__':
    create_template_files()
    
    print("IMPORTANT: Please save your bear image as 'bear.png' in the same directory as this script")
    
    # Open browser after a short delay
    threading.Timer(1.5, open_browser).start()
    
    # Run the Flask app
    app.run(debug=True) 