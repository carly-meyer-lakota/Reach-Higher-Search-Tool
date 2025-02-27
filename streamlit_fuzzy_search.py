import streamlit as st
import pandas as pd
from fuzzywuzzy import process
from nltk.corpus import wordnet

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

# Dynamically generate related words using WordNet
def generate_related_words(topic):
    synonyms = set()
    for syn in wordnet.synsets(topic):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().replace("_", " "))
    return list(synonyms)

# Check if the input is a learning objective
def is_learning_objective(query):
    action_verbs = ["write", "describe", "compare", "analyze", "summarize", "explain", "identify"]
    return any(verb in query.lower() for verb in action_verbs)

# Improved fuzzy search with weighting
def fuzzy_search(query):
    results = []
    related_words = generate_related_words(query)
    search_terms = [query] + related_words
    learning_objective = is_learning_objective(query)
    
    for index, row in df.iterrows():
        match_scores = []
        best_skill_match = (None, 0, "")
        best_vocab_match = (None, 0, "")
        
        for col in columns_to_search:
            for term in search_terms:
                text = str(row[col]).lower()
                score = process.extractOne(term, [text], score_cutoff=70)
                
                if score:
                    score_value = score[1]
                    match_scores.append(score_value)
                    
                    # Adjust weighting based on search type
                    if learning_objective and col in skill_columns:
                        score_value *= 1.5  # Boost skill-related matches
                        if score_value > best_skill_match[1]:
                            best_skill_match = (col, score_value, row[col])
                    
                    elif not learning_objective and col == "Vocabulary Words":
                        score_value *= 1.5  # Boost vocabulary matches for topic searches
                        if score_value > best_vocab_match[1]:
                            best_vocab_match = (col, score_value, row[col])
        
        if match_scores:
            avg_score = sum(match_scores) / len(match_scores)
            results.append((avg_score, best_skill_match, best_vocab_match, row.get("RH Level", "N/A"), row.get("Unit", "N/A")))
    
    return sorted(results, reverse=True, key=lambda x: x[0]), learning_objective, related_words

# Display results
if query:
    matches, learning_objective, related_words = fuzzy_search(query)
    
    if matches:
        st.subheader("Top 5 Relevant Curriculum Matches:")
        
        # Display related words used in search
        if related_words:
            st.write("**Words Related to Your Search:** " + ", ".join(related_words))
        
        # Format results as a table
        results_df = pd.DataFrame([
            {
                "RH Level": match[3],
                "Unit": match[4],
                "Matched Category": match[1][0] if match[1][1] > match[2][1] else match[2][0],
                "Matched Content": match[1][2] if match[1][1] > match[2][1] else match[2][2]
            }
            for match in matches[:5]
        ])
        st.dataframe(results_df)
    
    else:
        st.write("No relevant matches found.")
