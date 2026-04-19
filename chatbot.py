import re
import json
import random
import numpy as np
import pandas as pd
from fuzzywuzzy import fuzz
from flask import Flask, request, render_template_string
try:
    import wikipedia
except ImportError:
    wikipedia = None
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# NLTK downloads - Load safely
try:
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet', quiet=True)
except Exception as e:
    print(f"Warning: NLTK downloads failed: {e}")

# Load and preprocess dataset safely
ML_READY = False
try:
    df = pd.read_csv("data/chatbot_data.csv", on_bad_lines='skip')

    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))

    def preprocess(text):
        try:
            tokens = nltk.word_tokenize(text.lower())
            return ' '.join([lemmatizer.lemmatize(w) for w in tokens if w.isalpha() and w not in stop_words])
        except Exception:
            return text.lower()  # fallback

    # Preprocess patterns
    df['processed_patterns'] = df['patterns'].astype(str).apply(preprocess)

    # TF-IDF vectorization
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(df['processed_patterns'])
    ML_READY = True
except Exception as e:
    print(f"Warning: Could not initialize ML matching logic: {e}")

# Math evaluator
def evaluate_math_expression(text):
    try:
        if re.match(r'^[\d\s\+\-\*/\(\)]+$', text):
            return f"The answer is {eval(text)}"
    except:
        return None
    return None

# Simple rule-based responses
def rule_based_response(user_input):
    query = user_input.lower()
    if "name" in query and "flower" in query:
        return "Rose, Tulip, Lily, Jasmine, Sunflower."
    if "name" in query and "fruit" in query:
        return "Apple, Mango, Banana, Orange, Grapes."
    return None

# Match from custom dataset using TF-IDF + fuzzy
def get_best_match(user_input):
    if not ML_READY:
        return None
    try:
        user_input_processed = preprocess(user_input)
        user_vec = vectorizer.transform([user_input_processed])
        similarity_scores = cosine_similarity(user_vec, X)
        max_score_index = np.argmax(similarity_scores)
        
        # Accept match only if confidence > 0.6
        if similarity_scores[0][max_score_index] > 0.6:
            return df.iloc[max_score_index]['response']

        # Try fuzzy matching
        best_ratio = 0
        best_response = None
        for i, row in df.iterrows():
            ratio = fuzz.partial_ratio(user_input.lower(), str(row['patterns']).lower())
            if ratio > best_ratio:
                best_ratio = ratio
                best_response = row['response']

        # Accept fuzzy match only if ratio > 85 (stricter)
        if best_ratio > 85:
            return best_response

    except Exception:
        pass
    return None

# Wikipedia fallback
def wikipedia_summary(query):
    if wikipedia is None:
        return None
    try:
        return wikipedia.summary(query, sentences=2)
    except:
        return None

# Main function to get chatbot response
def get_chatbot_response(user_input):
    try:
        result = evaluate_math_expression(user_input)
        if result:
            return result  # from math
    
        rule = rule_based_response(user_input)
        if rule:
            return rule  # from rule-based
    
        best = get_best_match(user_input)
        if best:
            return best  # from dataset
    
        wiki = wikipedia_summary(user_input)
        if wiki:
            return wiki  # from Wikipedia
            
        return "I'm still learning. Could you rephrase your question?"
    except Exception as e:
        return f"Echo: {user_input}"

# --- FLASK WEB APP ---
app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Chatbot</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f0f2f5; margin: 0; padding: 20px; display: flex; justify-content: center; }
        .chat-container { width: 100%; max-width: 600px; background: white; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); padding: 20px; display: flex; flex-direction: column; height: 80vh; }
        .chat-history { flex-grow: 1; overflow-y: auto; padding: 10px; border: 1px solid #ddd; border-radius: 8px; background: #fafafa; margin-bottom: 20px; }
        .message { margin: 10px 0; padding: 12px 16px; border-radius: 20px; max-width: 80%; word-wrap: break-word; }
        .user { background: #0084ff; color: white; align-self: flex-end; margin-left: auto; border-bottom-right-radius: 4px; }
        .bot { background: #e4e6eb; color: black; align-self: flex-start; margin-right: auto; border-bottom-left-radius: 4px; }
        form { display: flex; gap: 10px; }
        input[type="text"] { flex-grow: 1; padding: 12px; border: 1px solid #ccc; border-radius: 20px; font-size: 16px; outline: none; }
        button { padding: 12px 24px; border: none; background: #0084ff; color: white; border-radius: 20px; cursor: pointer; font-size: 16px; transition: background 0.2s; }
        button:hover { background: #0073e6; }
        .message-wrapper { display: flex; flex-direction: column; }
    </style>
</head>
<body>
    <div class="chat-container">
        <h2 style="text-align: center; margin-top: 0;">🤖 AI Chatbot</h2>
        <div class="chat-history" id="chat-history">
            {% for sender, msg in history %}
                <div class="message-wrapper">
                    <div class="message {{ 'user' if sender == 'You' else 'bot' }}">
                        {{ msg }}
                    </div>
                </div>
            {% endfor %}
        </div>
        <form method="POST">
            <input type="text" name="message" placeholder="Type your message..." required autocomplete="off" autofocus>
            <button type="submit">Send</button>
        </form>
    </div>
    <script>
        // Auto-scroll to bottom
        var historyDiv = document.getElementById("chat-history");
        historyDiv.scrollTop = historyDiv.scrollHeight;
    </script>
</body>
</html>
"""

chat_history = []

@app.route("/", methods=["GET", "POST"])
def home():
    try:
        if request.method == "POST":
            user_msg = request.form.get("message")
            if user_msg and user_msg.strip():
                try:
                    bot_response = get_chatbot_response(user_msg.strip())
                except Exception:
                    bot_response = "Oops, something went wrong on my end. Please try again."
                
                chat_history.append(("You", user_msg.strip()))
                chat_history.append(("Bot", bot_response))
        
        return render_template_string(HTML_TEMPLATE, history=chat_history)
    except Exception as e:
        return f"<h3>Application Error</h3><p>{e}</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
