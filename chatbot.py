import re
import json
import random
import numpy as np
import pandas as pd
from fuzzywuzzy import fuzz
import wikipedia
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# NLTK downloads
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

# Load and preprocess dataset
df = pd.read_csv("data/chatbot_data.csv")

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def preprocess(text):
    tokens = nltk.word_tokenize(text.lower())
    return ' '.join([lemmatizer.lemmatize(w) for w in tokens if w.isalpha() and w not in stop_words])

# Preprocess patterns
df['processed_patterns'] = df['patterns'].apply(preprocess)

# TF-IDF vectorization
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df['processed_patterns'])

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
        ratio = fuzz.partial_ratio(user_input.lower(), row['patterns'].lower())
        if ratio > best_ratio:
            best_ratio = ratio
            best_response = row['response']

    # Accept fuzzy match only if ratio > 85 (stricter)
    if best_ratio > 85:
        return best_response

    return None

# Wikipedia fallback
def wikipedia_summary(query):
    try:
        return wikipedia.summary(query, sentences=2)
    except:
        return "I'm still learning. Can you rephrase that?"

# Main function to get chatbot response
def get_chatbot_response(user_input):
    result = evaluate_math_expression(user_input)
    if result:
        return result  # from math

    rule = rule_based_response(user_input)
    if rule:
        return rule  # from rule-based

    best = get_best_match(user_input)
    if best:
        return best  # from dataset

    return wikipedia_summary(user_input)  # from Wikipedia
