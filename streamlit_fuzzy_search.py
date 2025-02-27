import streamlit as st
import pandas as pd
from fuzzywuzzy import process

# Load the dataset
@st.cache_data
def load_data():
    file_path = "reach higher curriculum all units.csv"
    return pd.read_csv(file_path)

df = load_data()

# Debugging step: Print column names
st.write("Columns in dataset:", df.columns.tolist())

# Streamlit app setup
st.title("Reach Higher Curriculum Search")
st.write("Find relevant units and parts for your teaching topics or concepts.")

# User input for search type
search_type = st.radio("Are you searching for a topic or a concept?", ("Topic", "Concept"))
query = st.text_input("Enter your topic or concept:")

# Define relevant columns
columns_to_search = df.columns.tolist()

# Search function
def fuzzy_search(query):
    results = []
    for index, row in df.iterrows():
        match_scores = []
        for col in columns_to_search:
            score = process.extractOne(query, str(row[col]).split(','), score_cutoff=70)
            if score:
                match_scores.append(score[1])
        
        if match_scores:
            avg_score = sum(match_scores) / len(match_scores)
            results.append((avg_score, row.get("RH Level", "N/A"), row.get("Unit", "N/A"), row.get("Vocabulary Words", "N/A")))
    
    return sorted(results, reverse=True, key=lambda x: x[0])

# Display results
if query:
    matches = fuzzy_search(query)
    if matches:
        st.subheader("Relevant Curriculum Matches:")
        for score, level, unit, vocab in matches[:5]:
            st.write(f"**RH Level:** {level}")
            st.write(f"**Unit:** {unit}")
            st.write("**Vocabulary Words:**")
            st.write("\n".join([f"- {word.strip()}" for word in vocab.split(',')]))
            st.write("---")
    else:
        st.write("No relevant matches found.")
