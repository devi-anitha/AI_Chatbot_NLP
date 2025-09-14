import pandas as pd
import numpy as np
import tensorflow as tf
import os
import re

from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
import pickle

# Load dataset
df = pd.read_csv('data/chatbot_data.csv')

# Lowercase and clean
def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text

df['question'] = df['question'].apply(clean_text)
df['answer'] = df['answer'].apply(lambda x: '<START> ' + clean_text(x) + ' <END>')

# Tokenization
tokenizer = Tokenizer()
tokenizer.fit_on_texts(df['question'].tolist() + df['answer'].tolist())

VOCAB_SIZE = len(tokenizer.word_index) + 1

# Save tokenizer
with open('tokenizer.pkl', 'wb') as f:
    pickle.dump(tokenizer, f)

# Sequence conversion
encoder_input = tokenizer.texts_to_sequences(df['question'])
decoder_output = tokenizer.texts_to_sequences(df['answer'])

# Padding
max_len = 20
encoder_input = pad_sequences(encoder_input, maxlen=max_len, padding='post')
decoder_output = pad_sequences(decoder_output, maxlen=max_len, padding='post')

# Save preprocessed data
np.savez_compressed("data/processed_data.npz",
                    encoder_input=encoder_input,
                    decoder_output=decoder_output,
                    vocab_size=VOCAB_SIZE,
                    max_len=max_len)

print("✅ Data preprocessing complete. Vocab size:", VOCAB_SIZE)
