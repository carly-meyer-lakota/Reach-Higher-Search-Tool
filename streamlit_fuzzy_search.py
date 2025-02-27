import streamlit as st
import pandas as pd
import nltk
from nltk.corpus import wordnet
from fuzzywuzzy import process

# Ensure necessary NLTK resources are available
nltk.download('wordnet')
nltk.download('omw-1.4')

# Load the dataset
@st.cache_data
def load_data():
    file_path = "reach_higher_curriculum_all_units.csv"
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()  # Remove leading/trailing spaces
    return df.fillna('')  # Replace NaN with empty strings for searching

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

    # Check if query starts with "Students will"
    exclude_unit_name = query.lower().startswith("students will")

    for word in all_words:
        for col in columns_to_search:
            # If excluding Unit Name in Skill Type for "Students will" queries, skip Unit Name matches
            if exclude_unit_name and col == "Unit Name":
                continue

            matches = process.extract(word, df[col].dropna(), limit=5)
            for match in matches:
                if match[1] > 70:  # Only consider strong matches
                    row = df[df[col] == match[0]].iloc[0]  # Select the first matching row

                    rh_level = row.get('RH Level', 'N/A')
                    unit_number = row.get('Unit Number', 'N/A')  # Ensure correct column name
                    unit_name = row.get('Unit Name', 'N/A')
                    key_words = row.get('Vocabulary Words', 'N/A')
                    skill_matched = match[0]  # Extract the actual matched skill
                    skill_type = col  # Store the column name as Skill Type

                    # Format key vocabulary words as a bulleted list
                    key_words_list = key_words.split(', ') if key_words != 'N/A' else []
                    key_words_formatted = "\n".join([f"- {word}" for word in key_words_list])

                    results.append({
                        "Concept/Topic Matched": skill_matched,
                        "Skill Type": skill_type,
                        "RH Level": rh_level,
                        "Unit Number: Unit Name": f"{unit_number}: {unit_name}",
                        "Key Vocabulary Words": key_words_formatted
      
