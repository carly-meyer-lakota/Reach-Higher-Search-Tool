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

# Search function using fuzzy matching with WordNet synonyms and relevance scoring
def search_units(query, df, columns_to_search):
    related_words = generate_related_words(query)
    all_words = [query] + related_words  # Include query and its synonyms
    results = []

    # Check if query starts with "Students will" or "theme is"
    exclude_unit_name = query.lower().startswith("students will")
    is_theme_search = query.lower().startswith("theme is")

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
                    key_words = row.get('Vocabulary Words', 'N/A').split(', ') if row.get('Vocabulary Words', 'N/A') != 'N/A' else []
                    skill_matched = match[0]  # Extract the actual matched skill
                    skill_type = col  # Store the column name as Skill Type

                    # Format key vocabulary words as a bulleted list
                    key_words_formatted = "\n".join([f"- {word}" for word in key_words])

                    # Assign a relevance score based on the column type and match strength
                    score = match[1]
                    if 'Vocabulary' in col:  # Weight vocabulary matches more heavily for topics
                        score *= 1.5
                    elif 'Skill' in col:  # Weight skill matches more heavily for concepts
                        score *= 1.2

                    # If it's a theme search, generate a theme title instead of using the vocabulary words in the "Concept/Topic Matched" column
                    if is_theme_search:
                        theme_title = generate_theme_title(key_words)
                        results.append({
                            "Theme": theme_title,
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
    
    # Sort results by relevance score in descending order
    sorted_results = sorted(results, key=lambda x: x['Relevance Score'], reverse=True)

    return sorted_results[:5]  # Limit to top 5 results

# Display search results
if query:
    is_theme_search = query.lower().startswith("theme is")  # Check for theme search condition here
    results = search_units(query, df, columns_to_search)
    if results:
        st.write("### Search Results:")
        df_results = pd.DataFrame(results)
        if is_theme_search:
            df_results = df_results.drop(columns=["Skill Type"])  # Remove Skill Type column for theme searches
        st.dataframe(df_results.style.set_properties(**{'white-space': 'pre-wrap'}), hide_index=True, use_container_width=True)  # Auto-adjust width, hide index, format list
    else:
        st.write("No relevant units found. Try a different topic or learning objective.")
