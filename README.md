# 🤖 Multi-Agent Chatbot (T3 Chat Clone)

A lightweight, full-stack AI chat interface that supports multiple Large Language Models (LLMs) and features agentic tool-calling capabilities. Built with a Vanilla JavaScript frontend and a Python FastAPI backend, this project allows users to seamlessly switch between different AI engines while maintaining conversation memory and executing both server-side and client-side actions.

## ✨ Features

* **Multi-Model Support:** Seamlessly switch between powerful cloud-based AI engines:
    * **Google Gemini** (`gemini-2.5-flash-lite`) - Server-side authentication.
    * **Anthropic Claude** (`claude-3-opus`) - Client-side dynamic API key input.
    * **Groq** (`llama-3.1-8b-instant`) - Client-side dynamic API key input.
* **Conversation Memory:** The frontend maintains a contextual history array, allowing the AI to remember your name and previous messages throughout the session.
* **Agentic Capabilities:**
    * **Backend Tools:** The agent can fetch real-time server data (e.g., current time, simulated stock prices).
    * **Frontend Actions:** The agent can send commands to the browser to perform UI tasks, such as opening new tabs or changing the application's theme color.
* **Zero-Build Frontend:** No Webpack, Vite, or React required. Just plain HTML, CSS, and JS for maximum simplicity and speed.

## 🛠️ Tech Stack

* **Frontend:** HTML5, CSS3, Vanilla JavaScript (Easily deployable to Vercel, Netlify, or Render)
* **Backend:** Python 3.10+, FastAPI, Uvicorn (Deployable as a Web Service)
* **AI SDKs:** `google-genai`, `anthropic`, `openai` (Used for Groq routing)

---

## 🚀 Getting Started (Local Setup)

Follow these steps to run the full-stack application locally on your machine.

### 1. Clone the Repository
```bash
git clone [https://github.com/SakshamKataria2/Agentic-Chatbot.git](https://github.com/SakshamKataria2/Agentic-Chatbot.git)
cd Agentic-Chatbot

# Navigate to the backend directory
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install the required dependencies
pip install -r requirements.txt
uvicorn main:app --reload

cd frontend
python -m http.server 3000
