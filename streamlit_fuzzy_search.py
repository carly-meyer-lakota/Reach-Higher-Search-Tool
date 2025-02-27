import streamlit as st
import pandas as pd
import nltk
from nltk.corpus import wordnet
from fuzzywuzzy import process

# Download WordNet if not already present
nltk.download('wordnet')
nltk.download('omw-1.4')  # Improves synonym searches

# Load the dataset
@st.cache_data
def load_data():
    file_path = "reach_higher_curriculum_all_units.csv"
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()  # Remove leading/trailing spaces
    return df

df = load_data()

# Streamlit app setup
st.title("Reach Higher Curriculum Search")
st.write("Find relevant units and parts for your teaching topics or learning objectives.")

# User input for search query
query = st.text_input("Enter your topic or learning objective:")

# Define relevant columns
columns_to_search = df.columns.tolist()
skill_columns = [col for col in columns_to_search if "Skill" in col and "Phonics" not in col]

# Function to generate synonyms using WordNet
def generate_related_words(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().replace("_", " "))  # Replace underscores in multi-word phrases
    return list(synonyms)

# Search function using fuzzy matching with WordNet synonyms
def search_units(query, df, columns_to_search):
    related_words = generate_related_words(query)
    all_words = [query] + related_words  # Include query and its synonyms
    results = []

    for word in all_words:
        for col in columns_to_search:
            matches = process.extract(word, df[col].dropna(), limit=5)
            for match in matches:
 
