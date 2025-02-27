import streamlit as st
import pandas as pd
from fuzzywuzzy import process

# Load the dataset
@st.cache_data
def load_data():
    file_path = "reach higher curriculum all units.csv"
    return pd.read_csv(file_path)

df = load_data()

# Streamlit app setup
st.title("Reach Higher Curriculum Search")
st.write("Find relevant units and parts for your teaching topics or learning objectives.")

# User input for search query
query = st.text_input("Enter your topic or learning objective:")

# Define relevant columns
columns_to_search = df.columns.tolist()
skill_columns = [col for col in columns_to_search if "Skill" in col and "Phonics" not in col]

# Predefined related words dictionary
def generate_related_words(topic):
    related_words = {
        "frogs": ["animal", "amphibian", "egg", "tadpole", "water", "pond", "jump"],
        "weather": ["rain", "storm", "temperature", "climate", "wind", "snow", "forecast"],
        "plants": ["tree", "leaf", "flower", "photosynthesis", "roots", "stem", "sunlight"],
        "animals": ["mammal", "reptile", "bird", "fish", "habitat", "wildlife"],
        "space": ["planet", "moon", "stars", "galaxy", "astronaut", "orbit"],
        "energy": ["electricity", "solar", "wind", "power", "battery", "fuel"],
    }
    return related_words.get(topic.lower(), [])

# Check if the input is a learning objective
def is_learning_objective(query):
    action_verbs = ["write", "describe", "compare", "analyze", "summarize", "explain", "identify"]
    return any(verb in query.lower() for verb in action_verbs)

# Improved fuzzy search with correct match tracking
def fuzzy_search(query):
    results = []
    related_words = generate_related_words(query)
    search_terms = [query] + related_words
    learning_objective = is_learning_objective(query)
    
    for _, row in df.iterrows():
        match_scores = []
        best_match = {"category": None, "content": None, "score": 0}
        
        for col in columns_to_search:
            for term in search_terms:
                text = str(row[col]).lower()
                score = process.extractOne(term, [text], score_cutoff=70)
                
                if score:
                    score_value = score[1]
                    match_scores.append(score_value)
                    
                    # Determine the best match
                    if learning_objective and col in skill_columns:
                        score_value *= 1.5  # Boost skill-related matches
                    elif not learning_objective and col == "Vocabulary Words":
                        score_value *= 1.5  # Boost vocabulary matches
                    
                    if score_value > best_match["score"]:
                        best_match = {"category": col, "content": row[col], "score": score_value}
        
        if match_scores:
            avg_score = sum(match_scores) / len(match_scores)
            results.append((
                avg_sco
