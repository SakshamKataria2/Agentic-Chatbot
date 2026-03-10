from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
from google.genai import types
import anthropic
from openai import OpenAI
import os
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# --- BACKEND DATA TOOLS ONLY ---
# We only give the AI tools for fetching data. UI actions are handled by the system prompt.
def get_current_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_stock_price(ticker: str) -> str:
    prices = {"TCS": "₹4,100", "RELIANCE": "₹2,950", "AAPL": "$175", "GOOGL": "$140"}
    return prices.get(ticker.upper(), "Price not found.")

agent_tools = [get_current_time, get_stock_price]

# --- DATA MODELS ---
class Message(BaseModel):
    role: str 
    content: str

class ChatRequest(BaseModel):
    message: str
    model: str
    dynamic_key: str | None = None
    history: list[Message] = []

# --- THE UNIFIED SYSTEM PROMPT ---
UNIVERSAL_SYSTEM_PROMPT = """You are a helpful AI assistant. 
You have the ability to control the user's browser interface. 
- If the user asks you to open a website or search for something, you MUST reply EXACTLY with: ACTION_COMMAND:open_tab|<URL>
- If the user asks to change the background color or theme, you MUST reply EXACTLY with: ACTION_COMMAND:change_color|<CSS_COLOR>
Do not include any conversational text when outputting an ACTION_COMMAND."""

@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        # ----------------------------------------
        # 1. GOOGLE GEMINI
        # ----------------------------------------
        if request.model == "gemini":
            gemini_history = []
            for msg in request.history:
                g_role = "model" if msg.role == "assistant" else "user"
                gemini_history.append(types.Content(role=g_role, parts=[types.Part.from_text(text=msg.content)]))

            chat = gemini_client.chats.create(
                model='gemini-2.5-flash-lite', # FIX: Updated to the active, high-quota model
                config=types.GenerateContentConfig(
                    tools=agent_tools,
                    system_instruction=UNIVERSAL_SYSTEM_PROMPT 
                ),
                history=gemini_history
            )
            response = chat.send_message(request.message)
            reply_text = response.text.strip()
            
        # ----------------------------------------
        # 2. ANTHROPIC CLAUDE
        # ----------------------------------------
        elif request.model == "claude":
            if not request.dynamic_key:
                raise HTTPException(status_code=400, detail="Claude API key is required.")
            
            claude_messages = [{"role": msg.role, "content": msg.content} for msg in request.history]
            claude_messages.append({"role": "user", "content": request.message})

            client = anthropic.Anthropic(api_key=request.dynamic_key)
            message = client.messages.create(
                model="claude-3-opus-20240229", max_tokens=1000,
                system=UNIVERSAL_SYSTEM_PROMPT,
                messages=claude_messages
            )
            reply_text = message.content[0].text.strip()

        # ----------------------------------------
        # 3. GROQ (Cloud) & 4. OLLAMA (Local)
        # ----------------------------------------
        elif request.model in ["groq", "ollama"]:
            open_ai_messages = [{"role": "system", "content": UNIVERSAL_SYSTEM_PROMPT}]
            open_ai_messages.extend([{"role": msg.role, "content": msg.content} for msg in request.history])
            open_ai_messages.append({"role": "user", "content": request.message})

            if request.model == "groq":
                if not request.dynamic_key:
                    raise HTTPException(status_code=400, detail="Groq API key is required.")
                client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=request.dynamic_key)
                target_model = "llama-3.1-8b-instant" 
            else: 
                client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama_local")
                target_model = "llama3" 

            response = client.chat.completions.create(
                model=target_model,
                messages=open_ai_messages,
            )
            reply_text = response.choices[0].message.content.strip()

        else:
            raise HTTPException(status_code=400, detail="Invalid model.")

        # --- GLOBAL FRONTEND ACTION INTERCEPTOR ---
        if reply_text.startswith("ACTION_COMMAND:"):
            clean_command = reply_text.replace("ACTION_COMMAND:", "")
            parts = clean_command.split("|")
            action_type = parts[0]
            payload = parts[1] if len(parts) > 1 else ""
            return {"reply": f"Executing action: {action_type}...", "action": action_type, "payload": payload}
            
        return {"reply": reply_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")