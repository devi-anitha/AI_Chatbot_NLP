# app.py
from flask import Flask, render_template, request, jsonify
from chatbot import get_chatbot_response
import datetime

app = Flask(__name__)

def log_conversation(user_input, bot_response):
    with open("conversation_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now()}] You: {user_input}\n")
        f.write(f"[{datetime.datetime.now()}] Bot: {bot_response}\n\n")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get", methods=["POST"])
def chatbot_reply():
    user_input = request.json.get("message")
    bot_response = get_chatbot_response(user_input)
    log_conversation(user_input, bot_response)
    return jsonify({"response": bot_response})

if __name__ == "__main__":
    app.run(debug=True)
