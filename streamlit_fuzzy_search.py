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

# Function to check for exact matches in any column
def has_exact_match(query, df, columns_to_search):
    query_words = set(query.lower().split())  # Get individual words from the query
    exact_matches = {}

    for col in columns_to_search:
        # Ensure the column is treated as strings, even if it contains other types
        col_values = df[col].dropna().apply(str).str.lower()  # Convert to string before applying .str.lower()
        
        for value in col_values:
            value_words = set(value.split())  # Get individual words from the column value
            if query_words & value_words:  # If there's an intersection of words
                exact_matches[col] = exact_matches.get(col, set()) | value_words  # Record the matched words

    return exact_matches

# Search function using fuzzy matching with WordNet synonyms
def search_units(query, df, columns_to_search):
    related_words = generate_related_words(query)
    all_words = [query] + related_words  # Include query and its synonyms
    results = []

    # Check for exact matches in any column
    exact_matches = has_exact_match(query, df, columns_to_search)

    # Check if query starts with "Students will"
    exclude_unit_name = query.lower().startswith("students will")

    for word in all_words:
        for col in columns_to_search:
            # If excluding Unit Name in Skill Type for "Students will" queries, skip Unit Name matches
            if exclude_unit_name and col == "Unit Name":
                continue

            # If the word matches exactly in any column (except Unit Name), match with skill columns
            if col != "Unit Name" and col in exact_matches and word.lower() in exact_matches[col]:
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
                        })
    
    # Check Unit Name only if the word is specifically found in the Unit Name column
    for word in all_words:
        if word.lower() in exact_matches.get("Unit Name", set()):
            matches = process.extract(word, df["Unit Name"].dropna(), limit=5)
            for match in matches:
                if match[1] > 70:  # Only consider strong matches
                    row = df[df["Unit Name"] == match[0]].iloc[0]  # Select the first matching row

                    rh_level = row.get('RH Level', 'N/A')
                    unit_number = row.get('Unit Number', 'N/A')
                    unit_name = row.get('Unit Name', 'N/A')
                    key_words = row.get('Vocabulary Words', 'N/A')
                    skill_matched = match[0]  # Extract the actual matched unit name
                    skill_type = "Unit Name"  # Store as Unit Name for clarity

                    # Format key vocabulary words as a bulleted list
                    key_words_list = key_words.split(', ') if key_words != 'N/A' else []
                    key_words_formatted = "\n".join([f"- {word}" for word in key_words_list])

                    results.append({
                        "Concept/Topic Matched": skill_matched,
                        "Skill Type": skill_type,
                        "RH Level": rh_level,
                        "Unit Number: Unit Name": f"{unit_number}: {unit_name}",
                        "Key Vocabulary Words": key_words_formatted
                    })

    return results[:5]  # Limit to top 5 results

# Display search results
if query:
    results = search_units(query, df, columns_to_search)
    if results:
        st.write("### Search Results:")
        df_results = pd.DataFrame(results)
        st.dataframe(df_results.style.set_properties(**{'white-space': 'pre-wrap'}), hide_index=True, use_container_width=True)  # Auto-adjust width, hide index, format list
    else:
        st.write("No relevant units found. Try a different topic or learning objective.")
