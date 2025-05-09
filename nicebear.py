from flask import Flask, render_template, request, jsonify, send_from_directory
import requests
import json
import os
import threading
import webbrowser

# Ollama API endpoint (default is localhost:11434)
OLLAMA_API_URL = "http://localhost:11434/api/generate"

app = Flask(__name__, static_folder='static')

def generate_response(prompt):
    """Generate a response from the Dolphin-Llama3 model using Ollama API"""
    try:
        data = {
            "model": "nicebear",  # Using the custom model name
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
@app.route('/lightbear.png')
def serve_bear_image():
    return send_from_directory(app.root_path, 'lightbear.png')

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
                margin: 0;
                padding: 0;
                display: flex;
                height: 100vh;
            }
            
            /* Sidebar styles */
            #sidebar {
                width: 250px;
                background-color: #f0f0f0;
                border-right: 1px solid #ccc;
                overflow-y: auto;
                display: flex;
                flex-direction: column;
            }
            
            .sidebar-header {
                padding: 15px;
                border-bottom: 1px solid #ccc;
                text-align: center;
            }
            
            .conversation-list {
                flex-grow: 1;
                overflow-y: auto;
            }
            
            .conversation-item {
                padding: 10px 15px;
                border-bottom: 1px solid #ddd;
                cursor: pointer;
                position: relative;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .conversation-item:hover {
                background-color: #e0e0e0;
            }
            
            .conversation-item.active {
                background-color: #d0d0d0;
            }
            
            .delete-btn {
                visibility: hidden;
                color: #ff4d4d;
                cursor: pointer;
                font-weight: bold;
                padding: 2px 6px;
                border-radius: 3px;
            }
            
            .delete-btn:hover {
                background-color: #ffcccc;
            }
            
            .conversation-item:hover .delete-btn {
                visibility: visible;
            }
            
            .conversation-title {
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                flex-grow: 1;
            }
            
            .new-chat-btn {
                margin: 10px;
                padding: 8px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                text-align: center;
            }
            
            .new-chat-btn:hover {
                background-color: #45a049;
            }
            
            /* Main content styles */
            #main-content {
                flex-grow: 1;
                display: flex;
                flex-direction: column;
                max-width: calc(100% - 250px);
            }
            
            .header {
                display: flex;
                align-items: center;
                padding: 15px;
                border-bottom: 1px solid #ccc;
            }
            
            .bear-image {
                width: 50px;
                height: 50px;
                margin-right: 15px;
            }
            
            #chat-container {
                flex-grow: 1;
                padding: 15px;
                overflow-y: auto;
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
                padding: 10px;
                border-top: 1px solid #ccc;
            }
            
            #user-input {
                flex-grow: 1;
                padding: 10px;
                margin-right: 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            
            button {
                padding: 10px 15px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            
            button:hover {
                background-color: #45a049;
            }
        </style>
    </head>
    <body>
        <!-- Sidebar -->
        <div id="sidebar">
            <div class="sidebar-header">
                <h3>Conversations</h3>
            </div>
            <div class="new-chat-btn" onclick="startNewChat()">New Chat</div>
            <div id="conversation-list" class="conversation-list">
                <!-- Conversation history will be populated here -->
            </div>
        </div>
        
        <!-- Main Content -->
        <div id="main-content">
            <div class="header">
                <img src="/lightbear.png" alt="Bear" class="bear-image">
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
        </div>

        <script>
            const chatContainer = document.getElementById('chat-container');
            const userInput = document.getElementById('user-input');
            const sendButton = document.getElementById('send-button');
            const conversationList = document.getElementById('conversation-list');
            
            // Store conversations
            let conversations = [];
            let currentConversationId = null;
            
            // Load conversations from localStorage if available
            function loadConversations() {
                const savedConversations = localStorage.getItem('nicebear-conversations');
                if (savedConversations) {
                    conversations = JSON.parse(savedConversations);
                    renderConversationList();
                }
                
                // Start a new chat if no conversations exist
                if (conversations.length === 0) {
                    startNewChat();
                } else {
                    // Load the most recent conversation
                    loadConversation(conversations[0].id);
                }
            }
            
            // Save conversations to localStorage
            function saveConversations() {
                localStorage.setItem('nicebear-conversations', JSON.stringify(conversations));
            }
            
            // Delete a conversation
            function deleteConversation(id, event) {
                // Prevent the click from propagating to the parent (which would load the conversation)
                event.stopPropagation();
                
                // Ask for confirmation
                if (confirm('Are you sure you want to delete this conversation?')) {
                    // Remove the conversation from the array
                    const index = conversations.findIndex(c => c.id === id);
                    if (index !== -1) {
                        conversations.splice(index, 1);
                    }
                    
                    // If we deleted the current conversation, load another one
                    if (id === currentConversationId) {
                        if (conversations.length > 0) {
                            loadConversation(conversations[0].id);
                        } else {
                            startNewChat();
                        }
                    }
                    
                    // Update UI and save
                    renderConversationList();
                    saveConversations();
                }
            }
            
            // Render the conversation list in the sidebar
            function renderConversationList() {
                conversationList.innerHTML = '';
                
                conversations.forEach(conv => {
                    const item = document.createElement('div');
                    item.className = 'conversation-item';
                    if (conv.id === currentConversationId) {
                        item.classList.add('active');
                    }
                    
                    // Use the first user message as the title, or a default title
                    let title = 'New conversation';
                    for (const message of conv.messages) {
                        if (message.role === 'user') {
                            title = message.content.substring(0, 25);
                            if (message.content.length > 25) title += '...';
                            break;
                        }
                    }
                    
                    // Create title span
                    const titleSpan = document.createElement('span');
                    titleSpan.className = 'conversation-title';
                    titleSpan.textContent = title;
                    item.appendChild(titleSpan);
                    
                    // Create delete button
                    const deleteBtn = document.createElement('span');
                    deleteBtn.className = 'delete-btn';
                    deleteBtn.textContent = 'x';
                    deleteBtn.title = 'Delete conversation';
                    deleteBtn.onclick = (e) => deleteConversation(conv.id, e);
                    item.appendChild(deleteBtn);
                    
                    // Set click handler for the item
                    item.onclick = () => loadConversation(conv.id);
                    
                    conversationList.appendChild(item);
                });
            }
            
            // Start a new chat
            function startNewChat() {
                const newId = Date.now().toString();
                const newConversation = {
                    id: newId,
                    messages: []
                };
                
                // Add to the beginning of the array (most recent first)
                conversations.unshift(newConversation);
                currentConversationId = newId;
                
                // Clear the chat container
                chatContainer.innerHTML = '<div>chat with bear</div><div>type your message</div><br>';
                
                // Update UI
                renderConversationList();
                saveConversations();
            }
            
            // Load a conversation
            function loadConversation(id) {
                const conversation = conversations.find(c => c.id === id);
                if (!conversation) return;
                
                currentConversationId = id;
                
                // Clear the chat container
                chatContainer.innerHTML = '';
                
                // Render all messages
                conversation.messages.forEach(msg => {
                    if (msg.role === 'user') {
                        addMessage(`You: ${msg.content}`, 'user-message');
                    } else if (msg.role === 'assistant') {
                        addMessage(`LLM: ${msg.content}`, 'llm-message');
                    }
                });
                
                // Update UI
                renderConversationList();
            }
            
            function addMessage(text, className) {
                const messageDiv = document.createElement('div');
                messageDiv.className = className;
                messageDiv.textContent = text;
                chatContainer.appendChild(messageDiv);
                chatContainer.scrollTop = chatContainer.scrollHeight;
                return messageDiv;
            }
            
            function getCurrentConversation() {
                return conversations.find(c => c.id === currentConversationId);
            }
            
            async function sendMessage() {
                const message = userInput.value.trim();
                if (!message) return;
                
                // Get current conversation
                const conversation = getCurrentConversation();
                if (!conversation) return;
                
                // Add user message
                addMessage(`You: ${message}`, 'user-message');
                userInput.value = '';
                
                // Store the message
                conversation.messages.push({
                    role: 'user',
                    content: message
                });
                
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
                    
                    // Store the response
                    conversation.messages.push({
                        role: 'assistant',
                        content: data.response
                    });
                    
                    // Update the conversation list (in case this is the first message)
                    renderConversationList();
                    
                    // Save to localStorage
                    saveConversations();
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
            
            // Initialize
            loadConversations();
        </script>
    </body>
    </html>
    '''
    
    # Write the file with explicit UTF-8 encoding
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

if __name__ == '__main__':
    create_template_files()
    
    print("IMPORTANT: Please save your bear image as 'lightbear.png' in the same directory as this script")
    
    # Open browser after a short delay
    threading.Timer(1.5, open_browser).start()
    
    # Run the Flask app
    app.run(debug=True)