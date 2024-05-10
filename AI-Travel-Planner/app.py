import streamlit as st
import folium
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium
import google.generativeai as genai
from datetime import date
import spacy

# Load the NLP model for location extraction
nlp = spacy.load("en_core_web_sm")

# Function to get geographical coordinates
def get_location_coordinates(address):
    geolocator = Nominatim(user_agent="streamlit_travel_app")
    location = geolocator.geocode(address)
    if location:
        return (location.latitude, location.longitude)
    return (None, None)

# Function to generate and display map based on location names
def generate_map(locations):
    if not locations:
        return None
    map_obj = folium.Map(location=[40.7128, -74.0060], zoom_start=5)  # Default to New York City coordinates
    for location in locations:
        coords = get_location_coordinates(location)
        if coords:
            folium.Marker([coords[0], coords[1]], popup=location).add_to(map_obj)
    return map_obj

# Function to extract location names from AI-generated text
def extract_locations(text):
    doc = nlp(text)
    return [ent.text for ent in doc.ents if ent.label_ == 'GPE']

# Initialize the application's title and subtitle
st.title('AI Travel Planner')
st.subheader('Plan your next trip with AI')

# Sidebar for user input
st.sidebar.header('Enter details to generate a travel plan:')
api_key = "AIzaSyAYrqY9vA2zrKOrZ11RJRWwZeCRzniArvY"  # Replace with your actual API key
source = st.sidebar.text_input('Source', 'New York')
destination = st.sidebar.text_input('Destination', 'Los Angeles')
date_input = st.sidebar.date_input('Travel Start Date', min_value=date.today())
date = date_input.strftime('%Y-%m-%d')
budget = st.sidebar.number_input('Budget', min_value=100, value=1000, step=100)
duration = st.sidebar.slider('Duration (days)', 1, 90, 7)
currencies = ['USD', 'EUR', 'GBP', 'JPY', 'AUD']
selected_currency = st.sidebar.selectbox('Select Currency', currencies)

# Additional preferences
language_preference = st.sidebar.selectbox('Language Preference', ['English', 'Spanish', 'French', 'German', 'Japanese'], index=0)
interests = st.sidebar.text_input('Interests', 'historical sites, nature')
past_travel = st.sidebar.text_input('Past Travel Destinations', 'Paris, Tokyo')
dietary_restrictions = st.sidebar.text_input('Dietary Restrictions', 'None')
activity_level = st.sidebar.selectbox('Activity Level', ['Low', 'Moderate', 'High'])
specific_interests = st.sidebar.text_input('Specific Interests', 'art museums, hiking trails')
accommodation_preference = st.sidebar.selectbox('Accommodation Preference', ['Hotel', 'Hostel', 'Apartment', 'No Preference'])
travel_style = st.sidebar.selectbox('Travel Style', ['Relaxed', 'Fast-Paced', 'Adventurous', 'Cultural', 'Family-Friendly'])
must_visit_landmarks = st.sidebar.text_input('Must-Visit Landmarks', 'e.g., Eiffel Tower, Grand Canyon')

# Button to generate the travel plan and map
if st.sidebar.button('Generate Travel Plan'):
    if api_key and source and destination and date and budget and duration:
        # Configure API and generate message
        genai.configure(api_key=api_key)
        message = f"Create a detailed travel itinerary from {source} to {destination}, starting on {date}, lasting for {duration} days, with a budget of {selected_currency} {budget}. Include interests like {interests}, past travel experiences like {past_travel}, and any dietary restrictions. Must-visit landmarks include {must_visit_landmarks}."
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(message)
        travel_plan_text = response.text
        locations = extract_locations(travel_plan_text)
        st.session_state.travel_plan_text = travel_plan_text
        st.session_state.map = generate_map(locations)

# Display the travel plan text if it's stored in session state
if 'travel_plan_text' in st.session_state:
    st.markdown("### AI-Generated Travel Plan")
    st.markdown(st.session_state.travel_plan_text)

# Display the map with extracted locations
if 'map' in st.session_state and st.session_state.map is not None:
    st.subheader('Visualize your journey:')
    st_folium(st.session_state.map, width=725)
elif 'map' in st.session_state and st.session_state.map is None:
    st.error("Unable to generate map. Check if the location names are correct and try again.")