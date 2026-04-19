import re
import json
import random
import numpy as np
import pandas as pd
from fuzzywuzzy import fuzz
from flask import Flask, request, render_template, jsonify
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

@app.route("/", methods=["GET"])
def home():
    try:
        return render_template("index.html")
    except Exception as e:
        return f"<h3>Application Error</h3><p>Could not load frontend. Ensure 'templates/index.html' exists. Error: {e}</p>"

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"response": "Oops, skipped empty message."}), 400
        
        user_msg = data.get("message", "").strip()
        if not user_msg:
            return jsonify({"response": "Please provide a valid message."}), 400
            
        bot_response = get_chatbot_response(user_msg)
        return jsonify({"response": bot_response})
    except Exception as e:
        print(f"Error in /chat endpoint: {e}")
        return jsonify({"response": "An error occurred on the server while processing your message."}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
