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
