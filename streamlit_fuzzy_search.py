import streamlit as st
import pandas as pd
import fuzzywuzzy
from fuzzywuzzy import fuzz
from nltk.corpus import wordnet
import re

# Load data from CSV
@st.cache_data
def load_data():
    return pd.read_csv("reach_higher_curriculum_all_units.csv")

# Function to check if the search is a Theme search
def is_theme_search(query):
    return "theme" in query.lower()

# Function to check if the search is a Concept/Topic search
def is_concept_search(query):
    return "concept" in query.lower() or "learning objective" in query.lower()

# Function to generate a thematic title based on keywords
def generate_theme_title(vocabulary_words):
    topic_map = {
        "action, difference, gift, problem, receive, solution, kindness, need, understand, value, want": "Making an Impact",
        "improve, individual, neighborhood, offer, volunteer, benefit, duty, identify, impact, learn": "Community and Responsibility",
        "amount, behavior, decrease, increase, supply, balance, control, interact, react, scarce": "Resource Management",
        "drought, ecosystem, food chain, level, river, competition, nature, negative, positive, resources": "Environmental Conservation",
        "blossom, cycle, root, seed, soil, sprout, characteristic, conditions, depend, growth, produce": "Plant Growth and Development",
        "city, desert, rainforest, vine, weed, diversity, environment, organism, protect, unique": "Habitats and Ecosystems",
        "advertisement, buyer, market, money, pay, seller, accomplish, cooperation, plenty, purpose, reward": "Business & Trade",
        "agriculture, crop, farmer, field, harvest, plow, alternative, conservation, future, method, sustain": "Sustainable Agriculture",
        "form, freeze, liquid, melt, solid, temperature, thermometer, alter, occur, state, substance, trap": "States of Matter",
        "ground, mixture, sand, water, wetland, area, combine, composition, firm, surface": "Earth's Surface and Composition",
        "heritage, music, region, rhythm, vary, express, feelings, perform, popular, style": "Cultural Heritage",
        "artist, carve, storyteller, tale, tradition, wood, communicate, generation, preservation, process, represent": "Artistic Expression",
        "erupt, flow, island, lava, magma, ocean, rock, volcano, core, create, develop, force, pressure": "Volcanic Activity",
        "earthquake, plate, shore, tsunami, wave, power, rescue, sense, signal, warn": "Natural Disasters",
        "distance, feet, kilometer, measurement, meter, unit, achieve, direction, estimate, goal, strategy": "Measurement and Distance",
        "continent, destination, globe, journey, location, challenge, discover, endurance, explore, prepare": "Global Exploration",
        "craft, musical, perform, pottery, tradition, weave, create, culture, express, medium, style": "Craft and Performance",
        "ancestor, ceremony, marriage, occasion, ritual, belief, custom, influence, relationship, role": "Cultural Practices",
        "adaptation, defend, predator, prey, trait, behavior, characteristic, response, strategy, survival": "Survival and Adaptation",
        "command, imitate, memory, pattern, skill, tool, ability, communication, inherit, language, learn": "Cognitive Skills",
        "continent, country, equator, globe, hemisphere, inhabitant, map, border, imagine, range, suggest, transport": "Geography and Movement",
        "canyon, elevation, landform, ocean, plain, plateau, valley, feature, locate, physical, region, surface": "Landforms and Geography",
        "convert, electricity, generate, power, renewable, scarce, available, conservation, current, flow, resource": "Energy and Power",
        "atmosphere, element, landscape, material, natural, benefit, force, interact, modify, relate": "Earth Systems",
        "decompose, experiment, humid, mold, spore, contain, control, environment, investigate, spread": "Decomposition",
        "habitat, invade, population, species, threatened, balance, competition, introduce, migration, native": "Ecosystems and Conservation",
        "adventure, coastal, compass, navigation, port, treasure, chart, discovery, exploration, interpret, legend": "Exploration",
        "archaeologist, artifact, currency, galleon, merchant, colony, examine, preserve, route, trade": "Archaeology",
        "accelerate, height, measure, motion, speed, average, distance, rate, scale, solve": "Physics of Motion",
        "astronaut, launch, orbit, planet, rotation, capacity, constant limit resistance technology": "Space Exploration",
        "heritage hero president protect volunteer mission motive responsible service value": "History and Leadership",
        "ancient civilization empire object record site courage official principle project risk": "Ancient Civilizations",
        "country, culture, education, employment, immigration, opportunity, refuge, symbol, transition, translate": "Social Studies",
        "citizenship, custom, ethnic, foreign, origin, adapt, challenge, diversity, identity, society": "Cultural Studies",
        "absorb, heat, reflect, thermal, transmit, assume, event, explanation, power, theory": "Energy Transfer",
        "circuit, conduct, current, electrical, insulate, solar, volt, watt, alternate, decrease, energy, obstacle, rely": "Electrical Systems",
        "carnivore, consumer, food chain, herbivore, omnivore, producer, cooperate, essential, partnership, store, transfer": "Food Chains",
        "chlorophyll, magnify, microscope, nutrients, photosynthesis, classify, investigate, observe, propose, specialize": "Plant Science",
        "abolish, emancipation, escape, law, plantation, slavery, distinguish, equality, freedom, risk, route": "History of Freedom",
        "conditions, demands, labor, nonviolence, protest, strike, barriers, conflict, demonstrate, oppose, require": "Labor Rights",
        "atmosphere, condensation, evaporation, fresh water, precipitation, runoff, water cycle, watershed": "Water Cycle",
        "aquifer, canal, channel, climate, course, gourd, region": "Water Systems",
        "construction, gold rush, ranching, reservation, settler": "American History",
        "boomtown, claim, ghost town, investor, limited resources, mining": "Westward Expansion",
        "plastic, pollution, recycle, reduce, renewable, reuse": "Environmental Impact",
        "biodegradable, dispose, generate, landfill, transform": "Waste Management",
        "business, earnings, expenses, goods, income, profit, services": "Economics",
        "borrow, credit, debt, entrepreneur, loan": "Personal Finance",
        "capable, encounter, figure out, reputation, resistance, assumption, diverge, exclude, optional, potential": "Problem Solving",
        "associate, confront, preservation, sensitive, tolerance, awareness, conform, intent, interaction, involve": "Social Interaction",
        "camouflage, deception, duplicate, mimic, parasite, variation, asset, convince, emerge, ensure, resemblance": "Survival Strategies",
        "exhaust, necessity, overcome, reliance, resourceful, concentrate, intense, motivation, resilience, resolve": "Resilience",
        "archaeological, artifact, chronological, civilization, dynasty, pharaoh, tomb, analytical, depict, powerful": "Archaeological Study",
        "chamber, command, hieroglyphics, peer, plunder, procession, consider, contribute, impact, perspective": "Egyptian History",
        "dependent, endangered, extinct, policy, recover, thrive, appeal, effective factor protection sustain": "Environmental Protection",
        "deforestation ecological landscape management regulate advocate intervene obligation participate utilize": "Conservation Efforts",
        "boycott demonstration discrimination integrate prejudice separate, endeavor, implement, inherent, position, react": "Civil Rights",
        "declaration, defensively, humanity, indignation, innocence, authority, commitment, intention, presume, reinforce": "Human Rights",
        "donate, equip, inspiration, nutritious, practical, welfare, devote, envision, eventually, incentive, supplement": "Charity and Welfare",
        "controversy, crucial, eliminate, innovate, modified, gene, global, organic, poverty, production, virus": "Global Issues",
        "ancestor, conquest, empire, infrastructure, revolt, aspect, assemble, domain, foundation, unify": "World History",
        "despair, invasion, legendary, precious, subordinate, expertise, inquiry, integrity, pose, promote": "War and Peace",
        "composition, crater, erode, geologic, survey, terrain, analogy, distinct, simulate, structural, transform": "Geological Processes",
        "cavern, formation, navigation, passage, subterranean, circumstance, constant, estimate, perceive, undertake": "Cave Exploration"
    }
    
    for key, value in topic_map.items():
        if any(vocab in vocabulary_words for vocab in key.split(", ")):
            return value
    return "Unit Name"

# Function to perform fuzzy matching and synonym expansion using WordNet
def fuzzy_search(query, vocabulary_words, skill_columns, is_theme_search):
    search_results = []
    if is_theme_search:
        for i, row in vocabulary_words.iterrows():
            vocab_list = row['Vocabulary Words'].split(", ")
            for vocab in vocab_list:
                if fuzz.ratio(query, vocab) > 80 or any(fuzz.ratio(query, word) > 80 for word in get_synonyms(query)):
                    theme_title = generate_theme_title(vocab_list)
                    search_results.append({
                        "Theme Match": theme_title,
                        "RH Level": row["RH Level"],
                        "Unit Name": row["Unit Name"],
                        "Vocabulary Words": row["Vocabulary Words"]
                    })
    else:
        for i, row in vocabulary_words.iterrows():
            for skill_column in skill_columns:
                skill_value = row[skill_column]
                if fuzz.ratio(query, skill_value) > 80 or any(fuzz.ratio(query, word) > 80 for word in get_synonyms(query)):
                    search_results.append({
                        "Skill": skill_value,
                        "Skill Type": skill_column,
                        "RH Level": row["RH Level"],
                        "Unit Name": row["Unit Name"],
                        "Relevance Score": fuzz.ratio(query, skill_value)
                    })
    return search_results

# Function to get synonyms of a word using WordNet
def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
    return list(synonyms)

# App layout
st.title("Reach Higher Curriculum Search Tool")

# Search Query Input
query = st.text_input("Enter Search Query:")

# Search Type Selection
search_type = st.radio("Select Search Type", ("Theme", "Learning Objective"))

# Perform the search based on the type selected
if query:
    is_theme = search_type == "Theme"
    is_concept = search_type == "Learning Objective"

    data = load_data()

    # Determine if the query corresponds to theme or concept search
    if is_theme:
        search_results = fuzzy_search(query, data, ["Vocabulary Words"], is_theme_search=query.lower())
        df = pd.DataFrame(search_results)
        if not df.empty:
            df = df[["RH Level", "Unit Name", "Theme Match", "Vocabulary Words"]]
            st.write(df)
        else:
            st.write("No theme matches found.")
    
    if is_concept:
        search_results = fuzzy_search(query, data, ["Thinking Map Skill", "Reading Skill", "Grammar Skill", "Phonics Skill"], is_theme_search=query.lower())
        df = pd.DataFrame(search_results)
        if not df.empty:
            df = df[["Skill", "Skill Type", "RH Level", "Unit Name", "Relevance Score"]]
            st.write(df)
        else:
            st.write("No learning objective matches found.")
