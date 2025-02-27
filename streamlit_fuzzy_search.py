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
skill_columns = [col for col in columns_to_search if "Skill" in col]

# Function to generate related words for a topic-based search
def generate_related_words(topic):
    related_words = {
        "frogs": ["animal", "amphibian", "egg", "tadpole", "water", "pond", "jump"],
        "weather": ["rain", "storm", "temperature", "climate", "wind", "snow", "forecast"],
        "plants": ["tree", "leaf", "flower", "photosynthesis", "roots", "stem", "sunlight"]
    }
    return related_words.get(topic.lower(), [])

# Function to determine if the input is a learning objective
def is_learning_objective(query):
    action_verbs = ["write", "describe", "compare", "analyze", "summarize", "explain", "identify"]
    return any(verb in query.lower() for verb in action_verbs)

# Search function
def fuzzy_search(query):
    results = []
    related_words = generate_related_words(query)
    search_terms = [query] + related_words
    learning_objective = is_learning_objective(query)
    
    for index, row in df.iterrows():
        match_scores = []
        best_skill_match = (None, 0, "")
        exact_match_found = False
        vocab_match = []

        for col in columns_to_search:
            for term in search_terms:
                if term.lower() in str(row[col]).lower():
                    score = 100  # Exact match
                else:
                    score = process.extractOne(term, str(row[col]).split(','), score_cutoff=70)
                    score = score[1] if score else 0
                
                if score:
                    match_scores.append(score)
                    
                    if col in skill_columns:
                        if score == 100:
                            best_skill_match = (col, score, row[col])  # Prioritize exact match
                            exact_match_found = True
                        elif score > best_skill_match[1] and not exact_match_found:
                            best_skill_match = (col, score, row[col])
                    elif col == "Vocabulary Words":
                        vocab_match.append(score[0])
        
        if match_scores:
            avg_score = sum(match_scores) / len(match_scores)
            results.append((avg_score, best_skill_match, row.get("RH Level", "N/A"), row.get("Unit", "N/A"), vocab_match))
    
    return sorted(results, reverse=True, key=lambda x: x[0]), learning_objective

# Display results
if query:
    matches, learning_objective = fuzzy_search(query)
    if matches:
        st.subheader("Top 5 Relevant Curriculum Matches:")
        match_list = []
        
        if learning_objective:
            # Learning Objective Search Output
            for match in matches[:5]:
                avg_score, best_skill_match, level, unit, _ = match
                if best_skill_match[2]:
                    match_list.append(f"- **{best_skill_match[0]}: {best_skill_match[2]}, found in RH{level}, Unit {unit}.**")
        else:
            # Topic-Based Search Output
            for match in matches[:5]:
                avg_score, _, level, unit, vocab = match
                match_list.append(f"- **RH Level:** {level}, **Unit:** {unit}")
                match_list.append("  **Vocabulary Words from the RH Unit:**")
                match_list.extend([f"  - {word.strip()}" for word in vocab])
                match_list.append("  **Words Related to Your Search that were used to generate this list:**")
                match_list.extend([f"  - {word}" for word in generate_related_words(query)])
        
        st.markdown("\n".join(match_list))
    else:
        st.write("No relevant matches found.")
