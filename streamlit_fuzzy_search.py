import streamlit as st
import pandas as pd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# Function to load data with caching
@st.cache_data
def load_data():
    return pd.read_csv("reach_higher_curriculum_all_units.csv")

# Load the data
data = load_data()

# Function to generate theme title from vocabulary words
def generate_theme_title(vocabulary_words):
    # Define a mapping of common vocabulary-related topics to categories
    topic_map = {
        "Economy": ["advertisement", "buyer", "market", "money", "pay", "seller", "reward", "cooperation", "plenty", "purpose", "accomplish"],
        "Nature": ["plant", "animal", "ecosystem", "climate", "environment", "habitat", "growth", "species"],
        "Technology": ["computer", "internet", "technology", "innovation", "digital", "data", "robot", "software"],
        "Society": ["community", "society", "culture", "government", "law", "education", "history", "rights"],
        "Science": ["experiment", "research", "theory", "hypothesis", "chemistry", "biology", "physics", "formula"],
        "Art": ["painting", "sculpture", "music", "theater", "design", "creative", "expression", "gallery"],
        "Health": ["medicine", "doctor", "patient", "illness", "treatment", "health", "wellness", "prevention"]
    }
    
    # Flatten the vocabulary words and map them to a category if possible
    vocabulary_words_lower = [word.lower() for word in vocabulary_words]
    
    # Try to match the vocabulary words with predefined topics
    matched_topics = []
    for topic, keywords in topic_map.items():
        if any(keyword in vocabulary_words_lower for keyword in keywords):
            matched_topics.append(topic)
    
    # If no matches, return a general "Theme" based on key vocabulary terms
    if not matched_topics:
        return ", ".join(vocabulary_words[:3])  # Default theme is the first few words
    
    return ", ".join(matched_topics)  # Return the matched topic(s)

# Fuzzy search function to find the most relevant match
def fuzzy_search(query, column):
    matches = process.extract(query, data[column], scorer=fuzz.token_sort_ratio)
    return matches

# Streamlit app
def app():
    st.title('Reach Higher Curriculum Search Tool')
    
    # User input for topic or concept search
    search_type = st.radio("Select Search Type", ("Topic", "Concept"))
    search_query = st.text_input(f"Enter a {search_type} to Search:")
    
    if search_query:
        # Based on the search type, select the relevant column(s) to search
        if search_type == "Topic":
            search_column = "Vocabulary Words"
            st.write("Searching topics... Please wait.")
        elif search_type == "Concept":
            search_column = "Thinking Map Skill"
            st.write("Searching concepts... Please wait.")
        
        # Perform fuzzy search and show top matches
        matches = fuzzy_search(search_query, search_column)
        
        st.subheader("Top Matches:")
        
        for match in matches[:5]:  # Show top 5 matches
            match_data = match[0]
            match_score = match[1]
            theme_title = generate_theme_title(match_data.split(", "))  # Generate theme title from vocabulary words
            
            st.write(f"**Match:** {match_data}")
            st.write(f"**Score:** {match_score}")
            st.write(f"**Theme Title:** {theme_title}")
            st.write("---")

# Run the app
if __name__ == "__main__":
    app()
