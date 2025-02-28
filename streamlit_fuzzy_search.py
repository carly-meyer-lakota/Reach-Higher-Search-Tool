import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz
from nltk.corpus import wordnet as wn
from collections import defaultdict

# Load CSV file
@st.cache
def load_data():
    return pd.read_csv("reach higher curriculum all units.csv")

data = load_data()

# Predefined topic map for thematic titles
topic_map = {
    "action, difference, gift, problem, receive, solution, kindness, need, understand, value, want": "Making an Impact",
    "improve, individual, neighborhood, offer, volunteer, benefit, duty, identify, impact, learn": "Community Growth",
    "amount, behavior, decrease, increase, supply, balance, control, interact, react, scarce": "Resource Management",
    "drought, ecosystem, food chain, level, river, competition, nature, negative, positive, resources": "Environmental Conservation",
    # Add all other topics similarly...
}

# Generate thematic title from the topic map
def generate_theme_title(vocabulary_words):
    # Join vocabulary words and check against the topic map
    vocabulary_set = set(vocabulary_words.lower().split(", "))
    for key, title in topic_map.items():
        topic_set = set(key.lower().split(", "))
        if vocabulary_set & topic_set:
            return title
    return "General Curriculum"

# Check if the search is for a theme
def is_theme_search(query):
    return any(word in query.lower() for word in ["theme", "topic"])

# Check if the search is for a concept/topic
def is_concept_search(query):
    return any(word in query.lower() for word in ["concept", "student learning objective", "objective"])

# Expand query using synonyms from WordNet
def expand_query_with_synonyms(query):
    synonyms = set()
    for syn in wn.synsets(query):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
    return synonyms

# Calculate relevance score based on fuzzy matching
def calculate_relevance_score(query, text):
    return fuzz.partial_ratio(query.lower(), text.lower())

# Perform the search based on the search type
def perform_search(query, search_type):
    results = []
    
    # Perform search based on theme or concept/topic
    if search_type == "theme":
        for idx, row in data.iterrows():
            vocabulary_words = row['Vocabulary Words']
            theme_title = generate_theme_title(vocabulary_words.split(", "))
            relevance_score = calculate_relevance_score(query, vocabulary_words)
            results.append({
                'RH Level': row['RH Level'],
                'Unit Name': row['Unit'],
                'Theme Match': theme_title,
                'Vocabulary Words': vocabulary_words,
                'Relevance Score': relevance_score
            })
    
    elif search_type == "concept":
        for idx, row in data.iterrows():
            # Check skill columns for relevance
            skills_columns = ['Language Skill', 'Reading Skill', 'Phonics Skill', 'Grammar Skill', 'Thinking Map Skill', 'Project']
            for col in skills_columns:
                if pd.notna(row[col]):
                    relevance_score = calculate_relevance_score(query, row[col])
                    results.append({
                        'Skill Type': col,
                        'Skill': row[col],
                        'RH Level': row['RH Level'],
                        'Unit Name': row['Unit'],
                        'Relevance Score': relevance_score
                    })
    
    # Sort results by relevance score in descending order
    results = sorted(results, key=lambda x: x['Relevance Score'], reverse=True)
    
    return results

# Streamlit UI
st.title("Search the Reach Higher Curriculum")
st.markdown("""
    **Tips for Searching:**
    - **Theme Search**: Enter broad themes like "Space Exploration" or "Environmental Conservation" to find units related to these topics.
    - **Concept/Student Learning Objective Search**: Enter specific learning objectives or skills such as "Write a Persuasive Essay" or "Understand Ecosystems."
    - Use keywords from the curriculum or related terms for more relevant results.
""")

query = st.text_input("Enter your search query")

search_type = "theme" if is_theme_search(query) else "concept" if is_concept_search(query) else "concept"

results = perform_search(query, search_type)

# Display results based on search type
if results:
    if search_type == "theme":
        st.subheader("Theme Search Results")
        st.write("Displaying results sorted by relevance.")
        # Display results as a table for theme search
        results_df = pd.DataFrame(results)
        results_df = results_df[['RH Level', 'Unit Name', 'Theme Match', 'Vocabulary Words']]
        st.dataframe(results_df)
    
    elif search_type == "concept":
        st.subheader("Student Learning Objective Search Results")
        st.write("Displaying results sorted by relevance.")
        # Display results as a table for concept search
        results_df = pd.DataFrame(results)
        results_df = results_df[['Skill Type', 'Skill', 'RH Level', 'Unit Name']]
        st.dataframe(results_df)
else:
    st.write("No results found.")
