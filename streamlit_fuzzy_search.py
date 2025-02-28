import streamlit as st
import pandas as pd
import nltk
from nltk.corpus import wordnet
from fuzzywuzzy import process

# Ensure necessary NLTK resources are available
nltk.download('wordnet')
nltk.download('omw-1.4')

# Define a mapping of common vocabulary-related topics to categories
topic_map = {
    "Business": ["advertisement", "buyer", "market", "money", "pay", "seller", "investment", "profit", "trade", "commerce"],
    "Environment": ["plant", "animal", "ecosystem", "climate", "environment", "habitat", "conservation", "sustainability", "biodiversity"],
    "Technology": ["computer", "internet", "technology", "innovation", "digital", "data", "robot", "software", "AI", "cybersecurity"],
    "Society": ["community", "society", "culture", "government", "law", "education", "history", "rights", "social", "policy"],
    "Science": ["experiment", "research", "theory", "hypothesis", "chemistry", "biology", "physics", "astronomy", "geology"],
    "Arts": ["painting", "sculpture", "music", "theater", "design", "creative", "expression", "gallery", "literature", "dance"],
    "Health": ["medicine", "doctor", "patient", "illness", "treatment", "health", "wellness", "prevention", "nutrition", "fitness"],
    "Sports": ["football", "basketball", "tennis", "cricket", "athletics", "competition", "team", "coach", "tournament", "league"],
    "Travel": ["destination", "journey", "adventure", "tourism", "explore", "vacation", "trip", "itinerary", "culture", "landmark"]
}

# Function to generate theme title from vocabulary words
def generate_theme_title(vocabulary_words):
    vocabulary_words_lower = [word.lower() for word in vocabulary_words]
    matched_topics = []

    # Check each category in the topic_map to see if there's a match
    for topic, keywords in topic_map.items():
        if any(keyword in vocabulary_words_lower for keyword in keywords):
            matched_topics.append(topic)

    # If there's a match, return the matching topics as the theme title
    if matched_topics:
        return ", ".join(matched_topics)
    else:
        return None  # Return None if no match is found

# Load the dataset
@st.cache_data
def load_data():
    file_path = "reach_higher_curriculum_all_units.csv"
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()
    df['Theme Title'] = df['Vocabulary Words'].apply(lambda x: generate_theme_title(x.split(', ')))
    return df.fillna('')

df = load_data()

# Streamlit UI Setup
st.title("📚 Reach Higher Curriculum Search")
st.write("Find relevant units and parts for your teaching topics or learning objectives.")

# Sidebar for Search Options
st.sidebar.header("Search Options")
search_type = st.sidebar.radio("Select Search Type:", ["Search by Theme", "Search by Learning Objective"])

# Instructions
if search_type == "Search by Theme":
    st.sidebar.info("For best results, start your search with **'Theme is'** followed by your topic. Example: _'Theme is Space Exploration'_.")
else:
    st.sidebar.info("For best results, start your search with **'Students will'** followed by the learning objective. Example: _'Students will analyze character development.'_")

# User input for search query
query = st.text_input("Enter your search query:")

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

# Search function using fuzzy matching with WordNet synonyms and relevance scoring
def search_units(query, df, columns_to_search):
    related_words = generate_related_words(query)
    all_words = [query] + related_words
    results = []

    exclude_unit_name = query.lower().startswith("students will")
    is_theme_search = query.lower().startswith("theme is")

    for word in all_words:
        for col in columns_to_search:
            if exclude_unit_name and col == "Unit Name":
                continue

            matches = process.extract(word, df[col].dropna(), limit=5)
            for match in matches:
                if match[1] > 70:
                    row = df[df[col] == match[0]].iloc[0]

                    rh_level = row.get('RH Level', 'N/A')
                    unit_number = row.get('Unit Number', 'N/A')
                    unit_name = row.get('Unit Name', 'N/A')
                    key_words = row.get('Vocabulary Words', 'N/A').split(', ') if row.get('Vocabulary Words', 'N/A') != 'N/A' else []
                    skill_matched = match[0]
                    skill_type = col

                    key_words_formatted = "\n".join([f"- {word}" for word in key_words])

                    score = match[1]
                    if 'Vocabulary' in col:
                        score *= 1.5
                    elif 'Skill' in col:
                        score *= 1.2

                    # Generate the theme title based on the vocabulary words
                    theme_title = generate_theme_title(key_words) or unit_name  # Default to unit_name if no match

                    if is_theme_search:
                        results.append({
                            "Theme": theme_title,
                            "Skill Type": skill_type,
                            "RH Level": rh_level,
                            "Unit Number: Unit Name": f"{unit_number}: {unit_name}",
                            "Key Vocabulary Words": key_words_formatted,
                            "Relevance Score": score
                        })
                    else:
                        results.append({
                            "Concept/Topic Matched": skill_matched,
                            "Skill Type": skill_type,
                            "RH Level": rh_level,
                            "Unit Number: Unit Name": f"{unit_number}: {unit_name}",
                            "Key Vocabulary Words": key_words_formatted,
                            "Relevance Score": score
                        })
    
    # Sort results based on relevance score
    sorted_results = sorted(results, key=lambda x: x['Relevance Score'], reverse=True)
    return sorted_results[:5]

# Display search results
if query:
    results = search_units(query, df, columns_to_search)
    if results:
        st.write("### 🔎 Search Results:")
        df_results = pd.DataFrame(results)
        st.dataframe(df_results.style.set_properties(**{'white-space': 'pre-wrap'}), hide_index=True, use_container_width=True)
    else:
        st.write("⚠️ No relevant units found. Try a different topic or learning objective.")
