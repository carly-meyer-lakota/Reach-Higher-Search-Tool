import streamlit as st 
import pandas as pd
import nltk
from nltk.corpus import wordnet
from fuzzywuzzy import process

# Ensure necessary NLTK resources are available
nltk.download('wordnet')
nltk.download('omw-1.4')

# Set Streamlit page configuration (must be the first Streamlit command)
st.set_page_config(page_title="Reach Higher Search", layout="wide")

# Load the dataset
@st.cache_data
def load_data():
    df = pd.read_csv("reach_higher_curriculum_all_units.csv")
    df.columns = df.columns.str.strip()
    return df.fillna('')

df = load_data()

# Streamlit UI Setup
st.title("🔍 Reach Higher Curriculum Search")
st.write("Find relevant units and parts for your teaching topics or learning objectives.")

# Sidebar for user input
with st.sidebar:
    st.header("Search Settings")
    query = st.text_input("Enter a topic or concept:")
    search_type = st.radio("Select Search Type:", ["Topic Search", "Concept Search"])
    
    st.markdown("""
    **How to Search:**
    - Enter a **topic** (e.g., "climate change") to find relevant **vocabulary-heavy** results.
    - Enter a **concept** (e.g., "cause and effect") to find relevant **skill-based** results.
    """)

# Define relevant columns
columns_to_search = df.columns.tolist()
skill_columns = [col for col in columns_to_search if "Skill" in col and "Phonics" not in col]

# Function to generate synonyms using WordNet
def generate_related_words(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name().replace("_", " "))
    return list(synonyms)

# Search function using fuzzy matching
@st.cache_data
def search_units(query, df, columns_to_search, search_type):
    related_words = generate_related_words(query)
    all_words = [query] + related_words
    results = []

    for word in all_words:
        for col in columns_to_search:
            if search_type == "Concept Search" and col not in skill_columns:
                continue
            if search_type == "Topic Search" and "Vocabulary" not in col:
                continue

            matches = process.extract(word, df[col].dropna(), limit=5)
            for match in matches:
                if match[1] > 70:
                    row = df[df[col] == match[0]].iloc[0]
                    results.append({
                        "Matched Term": match[0],
                        "Skill Type": col,
                        "RH Level": row.get('RH Level', 'N/A'),
                        "Unit Name": f"{row.get('Unit', 'N/A')}: {row.get('Unit Name', 'N/A')}",
                        "Language Skill": row.get('Language Skill', 'N/A'),
                        "Reading Skill": row.get('Reading Skill', 'N/A'),
                        "Vocabulary Words": row.get('Vocabulary Words', 'N/A'),
                        "Relevance Score": match[1] / 100  # Convert to decimal for formatting
                    })

    return sorted(results, key=lambda x: x['Relevance Score'], reverse=True)[:5]

# Display search results
if query:
    with st.spinner("Searching..."):
        results = search_units(query, df, columns_to_search, search_type)
        if results:
            st.subheader("🔎 Search Results")
            results_df = pd.DataFrame(results)
            
            # Apply color formatting to Relevance Score
            def highlight_relevance(val):
                color = "#85C1E9" if val > 0.8 else ("#F9E79F" if val > 0.7 else "#F5B7B1")
                return f'background-color: {color}'
            
            styled_df = results_df.style.format({"Relevance Score": "{:.0%}"}).applymap(
                highlight_relevance, subset=['Relevance Score']
            )
            
            st.dataframe(styled_df)  # Display enhanced table
        else:
            st.warning("⚠️ No relevant units found. Try a different topic or concept.")
