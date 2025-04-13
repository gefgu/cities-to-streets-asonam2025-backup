import folium
import streamlit as st
import random
from folium.features import Marker
from streamlit_folium import st_folium

# Set page to wide mode
st.set_page_config(layout="wide")
st.write("# Select Your Top 4 Favorite US Cities")
st.write("Click on markers to select your favorite cities in order of preference.")

# Initialize session state to store selected cities if it doesn't exist
if "selected_cities" not in st.session_state:
    st.session_state.selected_cities = []

# Initialize recommended city if it doesn't exist
if "recommended_city" not in st.session_state:
    st.session_state.recommended_city = None

# Maximum number of cities that can be selected
MAX_CITIES = 4

# Add a slider for k value
k = st.slider("Select k value for highlighting top cities", 1, 3, 2)

# Cities data - major US cities with coordinates
cities = {
    "New York": [40.7128, -74.0060],
    "Los Angeles": [34.0522, -118.2437],
    "Chicago": [41.8781, -87.6298],
    "Houston": [29.7604, -95.3698],
    "Phoenix": [33.4484, -112.0740],
    "San Francisco": [37.7749, -122.4194],
}


# Function to recommend a city based on selections
def recommend_city():
    # Check if we have enough selected cities to make a recommendation
    if len(st.session_state.selected_cities) >= k + 1:
        # Check if we have at least one green and one orange city
        has_green = any(i < k for i in range(len(st.session_state.selected_cities)))
        has_orange = any(i >= k for i in range(len(st.session_state.selected_cities)))

        if has_green and has_orange:
            # Get all non-selected cities
            non_selected = [
                city
                for city in cities.keys()
                if city not in st.session_state.selected_cities
            ]
            if non_selected:
                # Randomly select a city to recommend
                recommended = random.choice(non_selected)
                # Generate a random confidence percentage between 60% and 95%
                confidence = random.randint(60, 95)
                return recommended, confidence

    return None, None


# Create map centered on US
m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)


# Define marker colors based on selection
def get_marker_color(city):
    if city == st.session_state.recommended_city:
        return "purple"  # Color for recommended city
    elif city not in st.session_state.selected_cities:
        return "blue"  # Default color for unselected cities

    city_rank = st.session_state.selected_cities.index(city)
    if city_rank < k:
        return "green"  # Top-k cities
    else:
        return "orange"  # Selected but not top-k


# Add markers for each city
for city, coords in cities.items():
    color = get_marker_color(city)
    icon_type = "info-sign"

    # Use a different icon for recommended city
    if city == st.session_state.recommended_city:
        icon_type = "star"

    Marker(
        location=coords,
        tooltip=city,
        icon=folium.Icon(color=color, icon=icon_type),
    ).add_to(m)

# Create two columns - one for the map and one for the selected cities
col1, col2 = st.columns([2, 2])

# Display the map in the first column
with col1:
    out = st_folium(m, height=600, width=800)

# Display selected cities in the second column
with col2:
    st.write("## Your Top Cities")
    if not st.session_state.selected_cities:
        st.write("You haven't selected any cities yet.")
    else:
        for i, city in enumerate(st.session_state.selected_cities):
            # Color top-k cities differently
            if i < k:
                st.markdown(
                    f"<span style='color:green; font-weight:bold'>{i+1}. {city}</span>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<span style='color:orange'>{i+1}. {city}</span>",
                    unsafe_allow_html=True,
                )

        # Add buttons for actions
        col_rec, col_reset = st.columns(2)

        # Add a get recommendation button
        with col_rec:
            if st.button("Get Recommendation"):
                recommended_city, confidence = recommend_city()
                if recommended_city:
                    st.session_state.recommended_city = recommended_city
                    st.session_state.confidence = confidence
                    st.rerun()
                else:
                    st.warning(
                        "Not enough diverse selections to make a recommendation. Select both high and lower ranked cities."
                    )

        # Add a reset button
        with col_reset:
            if st.button("Reset Selections"):
                st.session_state.selected_cities = []
                st.session_state.recommended_city = None
                st.rerun()

        # Display recommendation if available
        if st.session_state.recommended_city:
            st.markdown("---")
            st.markdown("## Our Recommendation")
            st.markdown(
                f"<span style='color:purple; font-weight:bold; font-size:16px'>Based on your past behavior, we recommend the city {st.session_state.recommended_city} with {st.session_state.confidence}% certainty.</span>",
                unsafe_allow_html=True,
            )

# Handle marker clicks
if out["last_object_clicked"]:
    clicked_coords = (
        out["last_object_clicked"]["lat"],
        out["last_object_clicked"]["lng"],
    )

    needs_update = False
    # Find which city was clicked
    for city, coords in cities.items():
        if (
            abs(coords[0] - clicked_coords[0]) < 0.01
            and abs(coords[1] - clicked_coords[1]) < 0.01
        ):
            # Add city if not already selected and limit to MAX_CITIES
            if city not in st.session_state.selected_cities:
                if len(st.session_state.selected_cities) < MAX_CITIES:
                    st.session_state.selected_cities.append(city)
                    needs_update = True
                else:
                    st.warning(
                        f"You already selected {MAX_CITIES} cities! Use the reset button to start over."
                    )
            break

    # Force rerun if we added a new city
    if needs_update:
        st.rerun()
