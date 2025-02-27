# Search function using fuzzy matching with WordNet synonyms and relevance scoring
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

                    # Assign a relevance score based on the column type and match strength
                    score = match[1]
                    if 'Vocabulary' in col:  # Weight vocabulary matches more heavily for topics
                        score *= 1.5
                    elif 'Skill' in col:  # Weight skill matches more heavily for concepts
                        score *= 1.2

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
