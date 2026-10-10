import os
import time
from flask import Flask, request, jsonify, send_from_directory
from google import genai
from google.genai import types

app = Flask(__name__)

# Check API key
API_KEY = os.environ.get("GEMINI_API_KEY")

if not API_KEY:
    print("ERROR: GEMINI_API_KEY is not set.")
else:
    print("GEMINI_API_KEY found.")

# Create Gemini client
client = genai.Client(
    api_key=API_KEY
)

# Models to try, in order
MODELS = ["gemini-3.5-flash-lite", "gemini-3.8-flash"]

# Load store information
with open("faq.txt", encoding="utf-8") as f:
    STORE_INFO = f.read()

def ask_gemini(question):

    config = types.GenerateContentConfig(
        system_instruction=(
            "You are a customer support assistant for GlowSkin Co. "
            "Answer ONLY using the store information below. "
            "Keep your answer under 3 sentences. "
            'If the answer is not in the info, say '
            '"Let me get a human to help."'
            "\n\n"
            f"STORE INFO:\n{STORE_INFO}"
        )
    )

    last_error = None

    for model in MODELS:
        for attempt in range(3):
            try:
                print(f"Trying {model} (attempt {attempt + 1})")

                return client.models.generate_content(
                    model=model,
                    contents=question,
                    config=config
                )

            except Exception as e:
                last_error = e
                message = str(e)
                # Retry only when Google is busy
                if "503" in message or "UNAVAILABLE" in message:
                    time.sleep(2)
                else:
                    raise
    raise last_error

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/chat", methods=["POST"])
def chat():

    try:

        data = request.get_json()

        if not data or "message" not in data:
            return jsonify({
                "error": "No message received."
            }), 400

        question = data["message"]
        print("User:", question)
        response = ask_gemini(question)
        reply = response.text or "Let me get a human to help."
        print("AI:", reply)

        return jsonify({
            "reply": reply
        })

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(
        debug=True
    )