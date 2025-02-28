import pandas as pd
import streamlit as st
from fuzzywuzzy import fuzz
from nltk.corpus import wordnet
import os

# Load CSV file with the new caching method
@st.cache_data
def load_data():
    file_path = "reach_higher_curriculum_all_units.csv"
    if not os.path.exists(file_path):
        st.error(f"The file {file_path} was not found. Please check the file path.")
        return None
    return pd.read_csv(file_path)

# Load data
data = load_data()

# Topic Map for theme generation
topic_map = {
    "action, difference, gift, problem, receive, solution, kindness, need, understand, value, want": "Making an Impact",
    "improve, individual, neighborhood, offer, volunteer, benefit, duty, identify, impact, learn": "Community Impact",
    "amount, behavior, decrease, increase, supply, balance, control, interact, react, scarce": "Resource Management",
    "drought, ecosystem, food chain, level, river, competition, nature, negative, positive, resources": "Environmental Conservation",
    "blossom, cycle, root, seed, soil, sprout, characteristic, conditions, depend, growth, produce": "Plant Growth",
    "city, desert, rainforest, vine, weed, diversity, environment, organism, protect, unique": "Habitats and Ecosystems",
    "advertisement, buyer, market, money, pay, seller, accomplish, cooperation, plenty, purpose, reward": "Business & Trade",
    "agriculture, crop, farmer, field, harvest, plow, alternative, conservation, future, method, sustain": "Sustainable Agriculture",
    "form, freeze, liquid, melt, solid, temperature, thermometer, alter, occur, state, substance, trap": "States of Matter",
    "ground, mixture, sand, water, wetland, area, combine, composition, firm, surface": "Earth's Surface and Materials",
    "heritage, music, region, rhythm, vary, express, feelings, perform, popular, style": "Cultural Expression",
    "artist, carve, storyteller, tale, tradition, wood, communicate, generation, preservation, process, represent": "Art and Tradition",
    "erupt, flow, island, lava, magma, ocean, rock, volcano, core, create, develop, force, pressure": "Volcanic Activity",
    "earthquake, plate, shore, tsunami, wave, power, rescue, sense, signal, warn": "Natural Disasters",
    "distance, feet, kilometer, measurement, meter, unit, achieve, direction, estimate, goal, strategy": "Measurement and Distance",
    "continent, destination, globe, journey, location, challenge, discover, endurance, explore, prepare": "Global Exploration",
    "craft, musical, perform, pottery, tradition, weave, create, culture, express, medium, style": "Cultural Arts",
    "ancestor, ceremony, marriage, occasion, ritual, belief, custom, influence, relationship, role": "Cultural Traditions",
    "adaptation, defend, predator, prey, trait, behavior, characteristic, response, strategy, survival": "Survival Strategies",
    "command, imitate, memory, pattern, skill, tool, ability, communication, inherit, language, learn": "Language and Communication",
    "continent, country, equator, globe, hemisphere, inhabitant, map, border, imagine, range, suggest, transport": "Geography and Maps",
    "canyon, elevation, landform, ocean, plain, plateau, valley, feature, locate, physical, region, surface": "Landforms and Physical Geography",
    "convert, electricity, generate, power, renewable, scarce, available, conservation, current, flow, resource": "Energy and Resources",
    "atmosphere, element, landscape, material, natural, benefit, force, interact, modify, relate": "Environmental Interaction",
    "decompose, experiment, humid, mold, spore, contain, control, environment, investigate, spread": "Decomposition and Growth",
    "habitat, invade, population, species, threatened, balance, competition, introduce, migration, native": "Biodiversity and Ecosystems",
    "adventure, coastal, compass, navigation, port, treasure, chart, discovery, exploration, interpret, legend": "Exploration and Navigation",
    "archaeologist, artifact, currency, galleon, merchant, colony, examine, preserve, route, trade": "Archaeology and Trade",
    "accelerate, height, measure, motion, speed, average, distance, rate, scale, solve": "Physics and Motion",
    "astronaut, launch, orbit, planet, rotation, capacity, constant limit resistance technology": "Space Exploration",
    "heritage hero president protect volunteer mission motive responsible service value": "Leadership and Responsibility",
    "ancient civilization empire object record site courage official principle project risk": "Ancient Civilizations",
    "country, culture, education, employment, immigration, opportunity, refuge, symbol, transition, translate": "Global Citizenship",
    "citizenship, custom, ethnic, foreign, origin, adapt, challenge, diversity, identity, society": "Cultural Identity",
    "absorb, heat, reflect, thermal, transmit, assume, event, explanation, power, theory": "Heat and Energy",
    "circuit, conduct, current, electrical, insulate, solar, volt, watt, alternate, decrease, energy, obstacle, rely": "Electricity and Circuits",
    "carnivore, consumer, food chain, herbivore, omnivore, producer, cooperate, essential, partnership, store, transfer": "Food Chains and Ecosystems",
    "chlorophyll, magnify, microscope, nutrients, photosynthesis, classify, investigate, observe, propose, specialize": "Photosynthesis",
    "abolish, emancipation, escape, law, plantation, slavery, distinguish, equality, freedom, risk, route": "Civil Rights History",
    "conditions, demands, labor, nonviolence, protest, strike, barriers, conflict, demonstrate, oppose, require": "Social Movements",
    "atmosphere, condensation, evaporation, fresh water, precipitation, runoff, water cycle, watershed": "Water Cycle",
    "aquifer, canal, channel, climate, course, gourd, region": "Water Systems",
    "construction, gold rush, ranching, reservation, settler": "American History",
    "boomtown, claim, ghost town, investor, limited resources, mining": "Mining and Settlements",
    "plastic, pollution, recycle, reduce, renewable, reuse": "Environmental Sustainability",
    "biodegradable, dispose, generate, landfill, transform": "Waste Management",
    "business, earnings, expenses, goods, income, profit, services": "Business and Economics",
    "borrow, credit, debt, entrepreneur, loan": "Financial Literacy",
    "capable, encounter, figure out, reputation, resistance, assumption, diverge, exclude, optional, potential": "Problem-Solving Skills",
    "associate, confront, preservation, sensitive, tolerance, awareness, conform, intent, interaction, involve": "Social Responsibility",
    "camouflage, deception, duplicate, mimic, parasite, variation, asset, convince, emerge, ensure, resemblance": "Adaptation and Survival",
    "exhaust, necessity, overcome, reliance, resourceful, concentrate, intense, motivation, resilience, resolve": "Perseverance",
    "archaeological, artifact, chronological, civilization, dynasty, pharaoh, tomb, analytical, depict, powerful": "Historical Analysis",
    "chamber, command, hieroglyphics, peer, plunder, procession, consider, contribute, impact, perspective": "Ancient Egypt",
    "dependent, endangered, extinct, policy, recover, thrive, appeal, effective factor protection sustain": "Conservation Efforts",
    "deforestation ecological landscape management regulate advocate intervene obligation participate utilize": "Environmental Advocacy",
    "boycott demonstration discrimination integrate prejudice separate, endeavor, implement, inherent, position, react": "Civil Rights Movements",
    "declaration, defensively, humanity, indignation, innocence, authority, commitment, intention, presume, reinforce": "Human Rights",
    "donate, equip, inspiration, nutritious, practical, welfare, devote, envision, eventually, incentive, supplement": "Social Support and Aid",
    "controversy, crucial, eliminate, innovate, modified, gene, global, organic, poverty, production, virus": "Global Challenges",
    "ancestor, conquest, empire, infrastructure, revolt, aspect, assemble, domain, foundation, unify": "Empire Building",
    "despair, invasion, legendary, precious, subordinate, expertise, inquiry, integrity, pose, promote": "History and Conflict",
    "composition, crater, erode, geologic, survey, terrain, analogy, distinct, simulate, structural, transform": "Geology and Terrain",
    "cavern, formation, navigation, passage, subterranean, circumstance, constant, estimate, perceive, undertake": "Cave Systems"
}

# Function to generate thematic title based on query match
def generate_theme_title(vocabulary_words):
    for key, value in topic_map.items():
        # Match vocabulary words with those in topic map
        if any(fuzz.partial_ratio(vocabulary_word, key_word) > 80 for vocabulary_word in vocabulary_words for key_word in key.split(', ')):
            return value
    return "No Theme Found"

# Function to check if it's a theme search
def is_theme_search(query):
    return query.strip().lower() in ["theme", "thematic"]

# Function to check if it's a concept/topic search
def is_concept_search(query):
    return query.strip().lower() in ["concept", "topic", "learning objective", "student learning objective"]

# Function to perform fuzzy search and return relevant results
def search(query, search_type):
    # Search for themes (matches Vocabulary Words)
    if search_type == "theme":
        theme_matches = []
        for _, row in data.iterrows():
            vocabulary_words = row['Vocabulary Words'].split(', ')
            thematic_title = generate_theme_title(vocabulary_words)
            if fuzz.partial_ratio(query.lower(), thematic_title.lower()) > 80:
                theme_matches.append({
                    "RH Level": row['RH Level'],
                    "Unit Name": row['Unit'],
                    "Theme Match": thematic_title,
                    "Vocabulary Words": ', '.join(vocabulary_words)
                })
        return theme_matches

    # Search for concept/topic (matches Skill columns)
    elif search_type == "concept":
        concept_matches = []
        for _, row in data.iterrows():
            skill_columns = ['Language Skill', 'Reading Skill', 'Thinking Map Skill', 'Grammar Skill', 'Phonics Skill']
            for skill_column in skill_columns:
                skill_value = row[skill_column]
                if fuzz.partial_ratio(query.lower(), str(skill_value).lower()) > 80:
                    concept_matches.append({
                        "Skill Type": skill_column.replace(" Skill", ""),
                        "Skill": skill_value,
                        "RH Level": row['RH Level'],
                        "Unit Name": row['Unit']
                    })
        return concept_matches

# User Interface
st.title("Reach Higher Curriculum Search Tool")
st.write("### Tips for Effective Search:")
st.write("1. Use specific keywords from the curriculum like 'ecosystem', 'photosynthesis', or 'business'.")
st.write("2. You can search for 'themes' or 'concepts/learning objectives' to find the best match.")
st.write("3. Thematic searches will find vocabulary and related words, while concept searches look for specific skills.")

search_query = st.text_input("Enter Search Query:")

if search_query:
    search_type = None
    if is_theme_search(search_query):
        search_type = "theme"
    elif is_concept_search(search_query):
        search_type = "concept"
    
    if search_type == "theme":
        results = search(search_query, search_type)
        if results:
            st.write("### Theme Search Results")
            st.table(results)
        else:
            st.write("No theme matches found.")
    elif search_type == "concept":
        results = search(search_query, search_type)
        if results:
            st.write("### Concept Search Results")
            st.table(results)
        else:
            st.write("No concept matches found.")
    else:
        st.write("Please specify a valid search term like 'theme' or 'concept'.")
