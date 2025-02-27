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

# Streamlit UI Setup
st.set_page_config(page_title="Reach Higher Search", layout="wide")

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
            synonyms.add(lemma.name().replace("_", " "))  # Replace underscores in multi-word phrases
    return list(synonyms)

# Search function using fuzzy matching
def search_units(query, df, columns_to_search, search_type):
    related_words = generate_related_words(query)
    all_words = [query] + related_words  # Include query and its synonyms
    results = []

    for word in all_words:
        for col in columns_to_search:
            if search_type == "Concept Search" and col not in skill_columns:
                continue  # Prioritize skill-based columns for Concept Search
            if search_type == "Topic Search" and "Vocabulary" not in col:
                continue  # Prioritize vocabulary-heavy columns for Topic Search
            
            matches = process.extract(word, df[col].dropna(), limit=5)
            for match in matches:
                if match[1] > 70:  # Only consider strong matches
                    row = df[df[col] == match[0]].iloc[0]  # Select the first matching row

                    results.append({
                        "Concept/Topic Matched": match[0],
                        "Skill Type": col,
                        "RH Level": row.get('RH Level', 'N/A'),
                        "Unit Number & Name": f"{row.get('Unit', 'N/A')}: {row.get('Unit Name', 'N/A')}",
                        "Key Vocabulary Words": row.get('Vocabulary Words', 'N/A'),
                        "Relevance Score": match[1]
                    })

    sorted_results = sorted(results, key=lambda x: x['Relevance Score'], reverse=True)
    return sorted_results[:5]  # Limit to top 5 results

# Display search results
if query:
    results = search_units(query, df, columns_to_search, search_type)
    if results:
        st.subheader("🔎 Search Results")
        
        for result in results:
            with st.expander(f"**{result['Unit Number & Name']}** | {result['RH Level']}"):
                st.write(f"**Matched:** {result['Concept/Topic Matched']}")
                st.write(f"**Skill Type:** {result['Skill Type']}")
                st.write(f"**Vocabulary Words:**\n {result['Key Vocabulary Words']}")
                st.write(f"🔹 **Relevance Score:** {result['Relevance Score']}")
    else:
        st.warning("⚠️ No relevant units found. Try a different topic or concept.")
