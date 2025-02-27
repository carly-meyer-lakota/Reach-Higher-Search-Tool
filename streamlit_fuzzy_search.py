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

# User input for search type
search_type = st.radio("Are you searching for a topic or a learning objective?", ("Topic", "Learning Objective"))
query = st.text_input("Enter your topic or learning objective:")

# Define relevant columns
columns_to_search = df.columns.tolist()
skill_columns = [col for col in columns_to_search if "Skill" in col]

# Function to generate related words for a topic-based search
def generate_related_words(topic):
    related_words = {
        "frogs": ["animal", "amphibian", "egg", "tadpole", "water", "pond", "jump"],
        "weather": ["rain", "storm", "temperature", "climate", "wind", "snow", "forecast"],
        "plants": ["tree", "leaf", "flower", "photosynthesis", "roots", "stem", "sunlight"]
    }
    return related_words.get(topic.lower(), [])

# Search function
def fuzzy_search(query, search_type):
    results = []
    related_words = generate_related_words(query) if search_type == "Topic" else []
    search_terms = [query] + related_words
    
    for index, row in df.iterrows():
        match_scores = []
        best_skill_match = (None, 0, "")
        
        for col in columns_to_search:
            for term in search_terms:
                score = process.extractOne(term, str(row[col]).split(','), score_cutoff=70)
                if score:
                    match_scores.append(score[1])
                    
                    if search_type == "Learning Objective" and col in skill_columns and score[1] > best_skill_match[1]:
                        best_skill_match = (col, score[1], score[0])
        
        if match_scores:
            avg_score = sum(match_scores) / len(match_scores)
            if search_type == "Learning Objective" and best_skill_match[2]:
                results.append((avg_score, f"{best_skill_match[0]}: {best_skill_match[2]}", row.get("RH Level", "N/A"), row.get("Unit", "N/A")))
            elif search_type == "Topic":
                results.append((avg_score, "", row.get("RH Level", "N/A"), row.get("Unit", "N/A"), row.get("Vocabulary Words", "N/A")))
    
    return sorted(results, reverse=True, key=lambda x: x[0])

# Display results
if query:
    matches = fuzzy_search(query, search_type)
    if matches:
        st.subheader("Top 5 Relevant Curriculum Matches:")
        match_list = []
        for match in matches[:5]:
            if search_type == "Learning Objective":
                _, skill_text, level, unit = match
                match_list.append(f"- **{skill_text}, found in RH{level}, Unit {unit}.**")
            else:
                _, _, level, unit, vocab = match
                match_list.append(f"- **RH Level:** {level}, **Unit:** {unit}")
                match_list.append("  **Vocabulary Words:**")
                match_list.extend([f"  - {word.strip()}" for word in vocab.split(',')])
        
        st.markdown("\n".join(match_list))
    else:
        st.write("No relevant matches found.")
