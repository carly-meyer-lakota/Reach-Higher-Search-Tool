import streamlit as st
import pandas as pd
from fuzzywuzzy import process

# Load the dataset
@st.cache_data
def load_data():
    file_path = "reach_higher_curriculum_all_units.csv"
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()  # Remove leading/trailing spaces
    return df

df = load_data()

# Streamlit app setup
st.title("Reach Higher Curriculum Search")
st.write("Find relevant units and parts for your teaching topics or learning objectives.")

# User input for search query
query = st.text_input("Enter your topic or learning objective:")

# Define relevant columns
columns_to_search = df.columns.tolist()
skill_columns = [col for col in columns_to_search if "Skill" in col and "Phonics" not in col]

# Predefined related words dictionary
def generate_related_words(topic):
    related_words = {
        "frogs": ["animal", "amphibian", "egg", "tadpole", "water", "pond", "jump"],
        "weather": ["rain", "storm", "temperature", "climate", "wind", "snow", "forecast"],
        "plants": ["tree", "leaf", "flower", "photosynthesis", "roots", "stem", "sunlight"],
        "animals": ["mammal", "reptile", "bird", "fish", "habitat", "wildlife"],
        "space": ["planet", "moon", "stars", "galaxy", "astronaut", "orbit"],
        "energy": ["electricity", "solar", "wind", "power", "battery", "fuel"],
        # Add more topics and related words as needed
    }
    return related_words.get(topic.lower(), [])

# Search function using fuzzy matching
def search_units(query, df, skill_columns):
    related_words = generate_related_words(query)
    all_words = [query] + related_words
    results = []

    for word in all_words:
        for col in skill_columns:
            matches = process.extract(word, df[col], limit=5)
            for match in matches:
                if match[1] > 70:  # Adjust the threshold as needed
                    row = df[df[col] == match[0]]
                    if not row.empty:
                        row = row.iloc[0]
                        rh_level = row.get('RH Level', 'N/A')
                        unit_number = row.get('Unit Number', 'N/A')
                        unit_name = row.get('Unit Name', 'N/A')
                        part_number = row.get('Part Number', 'N/A')
                        if "Skill" in col:
                            results.append(f"Skill Matched: {match[0]} (RH{rh_level}, Unit {unit_number} - {unit_name}, Part {part_number})")
                        else:
                            results.append(f"Topic Matched: {col} in RH{rh_level}, Unit {unit_number} - {unit_name} - Key Words: {', '.join(row[col].split())}")
    return results[:5]

# Display search results
if query:
    results = search_units(query, df, skill_columns)
    if results:
        st.write("### Search Results:")
        st.markdown("\n".join([f"- {result}" for result in results]))
    else:
        st.write("No relevant units found. Please try a different topic or learning objective.")
