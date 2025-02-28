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
    "Action & Problem Solving": ["action", "difference", "gift", "problem", "receive", "solution", "kindness", "need", "understand", "value", "want"],
    "Community & Volunteerism": ["improve", "individual", "neighborhood", "offer", "volunteer", "benefit", "duty", "identify", "impact", "learn"],
    "Resource Management": ["amount", "behavior", "decrease", "increase", "supply", "balance", "control", "interact", "react", "scarce"],
    "Ecosystems & Environment": ["drought", "ecosystem", "food chain", "level", "river", "competition", "nature", "negative", "positive", "resources"],
    "Growth & Development": ["blossom", "cycle", "root", "seed", "soil", "sprout", "characteristic", "conditions", "depend", "growth", "produce"],
    "Natural Environments": ["city", "desert", "rainforest", "vine", "weed", "diversity", "environment", "organism", "protect", "unique"],
    "Business & Trade": ["advertisement", "buyer", "market", "money", "pay", "seller", "accomplish", "cooperation", "plenty", "purpose", "reward"],
    "Agriculture & Sustainability": ["agriculture", "crop", "farmer", "field", "harvest", "plow", "alternative", "conservation", "future", "method", "sustain"],
    "States of Matter & Science": ["form", "freeze", "liquid", "melt", "solid", "temperature", "thermometer", "alter", "occur", "state", "substance", "trap"],
    "Geography & Composition": ["ground", "mixture", "sand", "water", "wetland", "area", "combine", "composition", "firm", "surface"],
    "Cultural Heritage & Expression": ["heritage", "music", "region", "rhythm", "vary", "express", "feelings", "perform", "popular", "style"],
    "Art & Tradition": ["artist", "carve", "storyteller", "tale", "tradition", "wood", "communicate", "generation", "preservation", "process", "represent"],
    "Volcanoes & Earth Sciences": ["erupt", "flow", "island", "lava", "magma", "ocean", "rock", "volcano", "core", "create", "develop", "force", "pressure"],
    "Natural Disasters & Safety": ["earthquake", "plate", "shore", "tsunami", "wave", "power", "rescue", "sense", "signal", "warn"],
    "Measurement & Strategy": ["distance", "feet", "kilometer", "measurement", "meter", "unit", "achieve", "direction", "estimate", "goal", "strategy"],
    "Exploration & Geography": ["continent", "destination", "globe", "journey", "location", "challenge", "discover", "endurance", "explore", "prepare"],
    "Crafts & Culture": ["craft", "musical", "perform", "pottery", "tradition", "weave", "create", "culture", "express", "medium", "style"],
    "Family & Social Roles": ["ancestor", "ceremony", "marriage", "occasion", "ritual", "belief", "custom", "influence", "relationship", "role"],
    "Survival & Adaptation": ["adaptation", "defend", "predator", "prey", "trait", "behavior", "characteristic", "response", "strategy", "survival"],
    "Memory & Communication": ["command", "imitate", "memory", "pattern", "skill", "tool", "ability", "communication", "inherit", "language", "learn"],
    "Geopolitics & Transportation": ["continent", "country", "equator", "globe", "hemisphere", "inhabitant", "map", "border", "imagine", "range", "suggest", "transport"],
    "Physical Geography": ["canyon", "elevation", "landform", "ocean", "plain", "plateau", "valley", "feature", "locate", "physical", "region", "surface"],
    "Energy & Resources": ["convert", "electricity", "generate", "power", "renewable", "scarce", "available", "conservation", "current", "flow", "resource"],
    "Atmosphere & Landscape": ["atmosphere", "element", "landscape", "material", "natural", "benefit", "force", "interact", "modify", "relate"],
    "Decomposition & Environment": ["decompose", "experiment", "humid", "mold", "spore", "contain", "control", "environment", "investigate", "spread"],
    "Species & Ecology": ["habitat", "invade", "population", "species", "threatened", "balance", "competition", "introduce", "migration", "native"],
    "Adventure & Exploration": ["adventure", "coastal", "compass", "navigation", "port", "treasure", "chart", "discovery", "exploration", "interpret", "legend"],
    "Archaeology & History": ["archaeologist", "artifact", "currency", "galleon", "merchant", "colony", "examine", "preserve", "route", "trade"],
    "Motion & Physics": ["accelerate", "height", "measure", "motion", "speed", "average", "distance", "rate", "scale", "solve"],
    "Space & Technology": ["astronaut", "launch", "orbit", "planet", "rotation", "capacity", "constant limit", "resistance", "technology"],
    "Civic Responsibility": ["heritage", "hero", "president", "protect", "volunteer", "mission", "motive", "responsible", "service", "value"],
    "Ancient Civilizations": ["ancient", "civilization", "empire", "object", "record", "site", "courage", "official", "principle", "project", "risk"],
    "Migration & Identity": ["country", "culture", "education", "employment", "immigration", "opportunity", "refuge", "symbol", "transition", "translate"],
    "Citizenship & Society": ["citizenship", "custom", "ethnic", "foreign", "origin", "adapt", "challenge", "diversity", "identity", "society"],
    "Thermal Energy": ["absorb", "heat", "reflect", "thermal", "transmit", "assume", "event", "explanation", "power", "theory"],
    "Electrical Systems": ["circuit", "conduct", "current", "electrical", "insulate", "solar", "volt", "watt", "alternate", "decrease", "energy", "obstacle", "rely"],
    "Food Webs & Ecosystems": ["carnivore", "consumer", "food chain", "herbivore", "omnivore", "producer", "cooperate", "essential", "partnership", "store", "transfer"],
    "Photosynthesis & Biology": ["chlorophyll", "magnify", "microscope", "nutrients", "photosynthesis", "classify", "investigate", "observe", "propose", "specialize"],
    "Civil Rights & Freedom": ["abolish", "emancipation", "escape", "law", "plantation", "slavery", "distinguish", "equality", "freedom", "risk", "route"],
    "Labor & Protest": ["conditions", "demands", "labor", "nonviolence", "protest", "strike", "barriers", "conflict", "demonstrate", "oppose", "require"],
    "Water Cycle & Precipitation": ["atmosphere", "condensation", "evaporation", "fresh water", "precipitation", "runoff", "water cycle", "watershed"],
    "Water Resources & Geography": ["aquifer", "canal", "channel", "climate", "course", "gourd", "region"],
    "Settlement & Expansion": ["construction", "gold rush", "ranching", "reservation", "settler"],
    "Mining & Economy": ["boomtown", "claim", "ghost town", "investor", "limited resources", "mining"],
    "Waste & Sustainability": ["plastic", "pollution", "recycle", "reduce", "renewable", "reuse"],
    "Environmental Impact": ["biodegradable", "dispose", "generate", "landfill", "transform"],
    "Business & Economics": ["business", "earnings", "expenses", "goods", "income", "profit", "services"],
    "Finance & Entrepreneurship": ["borrow", "credit", "debt", "entrepreneur", "loan"],
    "Critical Thinking": ["capable", "encounter", "figure out", "reputation", "resistance", "assumption", "diverge", "exclude", "optional", "potential"],
    "Social Awareness & Interaction": ["associate", "confront", "preservation", "sensitive", "tolerance", "awareness", "conform", "intent", "interaction", "involve"],
    "Biological Adaptations": ["camouflage", "deception", "duplicate", "mimic", "parasite", "variation", "asset", "convince", "emerge", "ensure", "resemblance"],
    "Motivation & Resilience": ["exhaust", "necessity", "overcome", "reliance", "resourceful", "concentrate", "intense", "motivation", "resilience", "resolve"],
    "Archaeological & Historical Analysis": ["archaeological", "artifact", "chronological", "civilization", "dynasty", "pharaoh", "tomb", "analytical", "depict", "powerful"],
    "Command & Influence": ["chamber", "command", "hieroglyphics", "peer", "plunder", "procession", "consider", "contribute", "impact", "perspective"],
    "Endangered Species & Protection": ["dependent", "endangered", "extinct", "policy", "recover", "thrive", "appeal", "effective", "factor", "protection", "sustain"],
    "Environmental Advocacy": ["deforestation", "ecological", "landscape", "management", "regulate", "advocate", "intervene", "obligation", "participate", "utilize"],
    "Social Justice & Civil Rights": ["boycott", "demonstration", "discrimination", "integrate", "prejudice", "separate", "endeavor", "implement", "inherent", "position", "react"],
    "Human Rights & Authority": ["declaration", "defensively", "humanity", "indignation", "innocence", "authority", "commitment", "intention", "presume", "reinforce"],
    "Volunteerism & Welfare": ["donate", "equip", "inspiration", "nutritious", "practical", "welfare", "devote", "envision", "eventually", "incentive", "supplement"],
    "Innovation & Global Challenges": ["controversy", "crucial", "eliminate", "innovate", "modified", "gene", "global", "organic", "poverty", "production", "virus"],
    "Ancient History & Civilization": ["ancestor", "conquest", "empire", "infrastructure", "revolt", "aspect", "assemble", "domain", "foundation", "unify"],
    "Resilience & Conflict": ["despair", "invasion", "legendary", "precious", "subordinate", "expertise", "inquiry", "integrity", "pose", "promote"],
    "Geology & Terrain": ["composition", "crater", "erode", "geologic", "survey", "terrain", "analogy", "distinct", "simulate", "structural", "transform"],
    "Cave Exploration": ["cavern", "formation", "navigation", "passage", "subterranean", "circumstance", "constant", "estimate", "perceive", "undertake"]
}

# Function to generate theme title from vocabulary words
def generate_theme_title(vocabulary_words):
    vocabulary_words_lower = [word.lower() for word in vocabulary_words]
    matched_topics = [topic for topic, keywords in topic_map.items() if any(keyword in vocabulary_words_lower for keyword in keywords)]
    return ", ".join(matched_topics) if matched_topics else None

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

                    if is_theme_search:
                        theme_title = generate_theme_title(key_words) or query.split("theme is")[-1].strip()
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
