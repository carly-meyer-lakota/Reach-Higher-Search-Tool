import streamlit as st
import pandas as pd
from fuzzywuzzy import process, fuzz

# Load the CSV file from the repository
@st.cache_data
def load_data():
    url = 'https://raw.githubusercontent.com/carly-meyer-lakota/Reach-Higher-Alignment-2/main/reach_higher_curriculum_all_units.csv'
    return pd.read_csv(url)

# Function for fuzzy searching
def fuzzy_search(query, column_data, weight=1):
    results = process.extract(query, column_data, scorer=fuzz.token_sort_ratio, limit=5)
    results = [(match, score * weight) for match, score in results]  # Apply weight
    return sorted(results, key=lambda x: x[1], reverse=True)

# Display matching rows in a table
def display_results(results, data, column):
    if results:
        st.write(f"### Top 5 matches for: {column}")
        result_indices = [i[0] for i in results]
        matches = data.iloc[result_indices]
        st.write(matches[['RH Level', 'Unit', 'Language Skill', 'Vocabulary Words', 
                          'Thinking Map Skill', 'Reading Skill', 'Genres', 'Grammar Skill', 'Project', 'Phonics Skill']])
    else:
        st.write("No matches found")

# Streamlit UI
def main():
    # Load data from the CSV file
    data = load_data()

    # Title of the app
    st.title('Reach Higher Curriculum Search Tool')

    # Let users choose between searching for a Concept or a Skill
    search_type = st.radio("Select Search Type", ['Concept', 'Skill'])

    # Input for the search query
    query = st.text_input(f"Enter a {search_type} or Learning Objective")

    if query:
        if search_type == 'Concept':
            # Focus on Vocabulary Words column for Concept search
            results = fuzzy_search(query, data['Vocabulary Words'], weight=2)
            display_results(results, data, 'Concept')
        elif search_type == 'Skill':
            # Focus on columns with Skills for Skill search (e.g., Thinking Map Skill, Reading Skill, etc.)
            skills_columns = ['Thinking Map Skill', 'Reading Skill', 'Grammar Skill']
            skill_results = []
            for col in skills_columns:
                skill_results.extend(fuzzy_search(query, data[col], weight=1))
            skill_results = sorted(skill_results, key=lambda x: x[1], reverse=True)[:5]
            display_results(skill_results, data, 'Skill')

if __name__ == "__main__":
    main()
