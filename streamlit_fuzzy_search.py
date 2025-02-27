import streamlit as st
import pandas as pd
from fuzzywuzzy import process

# Load the dataset
@st.cache_data
def load_data():
    file_path = "reach_higher_curriculum_all_units.csv"
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
        # Add more topics and related words as needed
    }
    return related_words.get(topic.lower(), [])

# Search function using fuzzy matching
def search_units(query, df, skill_columns):
    related_words = generate_related_words(query)
    all_words = [query] + related_words
    results = []

    for word in all_words:
        for col in skill_columns:
            matches = process.extract(word, df[col], limit=5)
            for match in matches:
                if match[1] > 70:  # Adjust the threshold as needed
                    results.append((col, match[0], match[1]))

    return results

# Display search results
if query:
    results = search_units(query, df, skill_columns)
    if results:
        st.write("Search Results:")
        for col, match, score in results:
            st.write(f"Column: {col}, Match: {match}, Score: {score}")
    else:
        st.write("No relevant units found. Please try a different topic or learning objective.")
