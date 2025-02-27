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

    for word in all_words:
        for col in columns_to_search:
            matches = process.extract(word, df[col].dropna(), limit=5)
            for match in matches:
                if match[1] > 70:  # Only consider strong matches
                    row = df[df[col] == match[0]].iloc[0]  # Select the first matching row

                    rh_level = row.get('RH Level', 'N/A')
                    unit_number = row.get('Unit', 'N/A')
                    unit_name = row.get('Unit Name', 'N/A')
                    key_words = row.get('Vocabulary Words', 'N/A')
                    skill_matched = match[0]  # Extract the actual matched skill

                    if col in skill_columns:  
                        result_text = (
                            f"**Concept Matched**: [{skill_matched}] in RH{rh_level}, Unit {unit_number} \"{unit_name}\""
                        )
                    else:
                        result_text = (
                            f"**Topic Matched**: [{skill_matched}] in RH{rh_level}, Unit {unit_number} \"{unit_name}\""
                            f"\n- **Key Words**: {key_words}"
                        )
                    
                    results.append(result_text)

    return results[:5]  # Limit to top 5 results

# Display search results
if query:
    results = search_units(query, df, columns_to_search)
    if results:
        st.write("### Search Results:")
        st.markdown("\n".join([f"- {result}" for result in results]))
    else:
        st.write("No relevant units found. Try a different topic or learning objective.")
