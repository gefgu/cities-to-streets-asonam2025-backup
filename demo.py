import folium
import streamlit as st
import random
from folium.features import Marker
from streamlit_folium import st_folium
from helper import (
    generate_recommendation,
    generate_travel_recommendation,
    generate_travel_recommendation_prompt,
    get_city_coordinates_data,
)
import plotly.graph_objects as go

# Set page to wide mode
st.set_page_config(layout="wide")
st.write("# Select Your Top 6 Favorite US Cities")
st.write("Click on markers to select your favorite cities in order of preference.")

# Initialize session state to store selected cities if it doesn't exist
if "selected_cities" not in st.session_state:
    st.session_state.selected_cities = []

# Initialize recommended city if it doesn't exist
if "recommended_city" not in st.session_state:
    st.session_state.recommended_city = None

# Initialize a state to track if the demo is in "recommendation shown" state
if "recommendation_shown" not in st.session_state:
    st.session_state.recommendation_shown = False

# Maximum number of cities that can be selected
MAX_CITIES = 6

# Add a slider for k value
k = st.slider(
    "Select k value for highlighting top cities",
    1,
    3,
    2,
    disabled=st.session_state.recommendation_shown,
)

# Cities data - major US cities with coordinates
cities = get_city_coordinates_data()


# Function to recommend a city based on selections
def recommend_city():
    # Check if we have enough selected cities to make a recommendation
    if len(st.session_state.selected_cities) >= k + 1:
        # Identify green and orange cities
        green_cities = [
            st.session_state.selected_cities[i]
            for i in range(len(st.session_state.selected_cities))
            if i < k
        ]
        orange_cities = [
            st.session_state.selected_cities[i]
            for i in range(len(st.session_state.selected_cities))
            if i >= k
        ]

        # Get non-selected cities
        non_selected = [
            city
            for city in cities.keys()
            if city not in st.session_state.selected_cities
        ]

        # Use helper function to generate recommendation
        return generate_recommendation(non_selected, green_cities, orange_cities)

    return None, None, None, None


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

    # Show a warning message when in recommendation state
    if st.session_state.recommendation_shown:
        st.warning(
            "A recommendation has been made. Please use the Reset button to start again."
        )

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

        # Add a get recommendation button (disabled if recommendation already shown)
        with col_rec:
            if st.button(
                "Get Recommendation", disabled=st.session_state.recommendation_shown
            ):
                recommended_city, confidence, lime_explanation, distances = (
                    recommend_city()
                )
                if recommended_city:
                    st.session_state.recommended_city = recommended_city
                    st.session_state.confidence = confidence
                    st.session_state.lime_explanation = (
                        lime_explanation  # Store the explanation
                    )
                    st.session_state.distances = distances  # Store the distances
                    st.session_state.recommendation_shown = True
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
                st.session_state.recommendation_shown = False
                st.rerun()

        # Display recommendation if available
        if st.session_state.recommended_city:
            st.markdown("---")
            st.markdown("## Our Recommendation")
            st.markdown(
                f"<span style='color:purple; font-weight:bold; font-size:16px'>Based on your past behavior, we recommend the city {st.session_state.recommended_city} with {st.session_state.confidence}% certainty.</span>",
                unsafe_allow_html=True,
            )
            # Add the personalized travel recommendation
            if (
                hasattr(st.session_state, "lime_explanation")
                and st.session_state.lime_explanation
                and hasattr(st.session_state, "distances")
                and st.session_state.distances
            ):
                travel_recommendation = generate_travel_recommendation_prompt(
                    st.session_state.recommended_city,
                    st.session_state.selected_cities[:k],  # Top cities (green)
                    st.session_state.selected_cities[k:],  # Bottom cities (orange)
                    st.session_state.lime_explanation,
                    st.session_state.distances,
                )

                st.markdown("### Travel Recommendation - Prompt")
                st.markdown(
                    f"<div style='padding:15px; border-radius:5px;'><i>{travel_recommendation}</i></div>",
                    unsafe_allow_html=True,
                )

            # Display LIME explanation
            st.markdown("### Explanation")
            st.write("Factors influencing this recommendation:")

            if (
                hasattr(st.session_state, "lime_explanation")
                and st.session_state.lime_explanation
            ):
                # Create a bar chart for LIME explanation
                explanation_data = st.session_state.lime_explanation
                print(explanation_data)
                features = list(explanation_data.keys())
                values = list(explanation_data.values())

                if features and values:
                    # Sort features by absolute importance
                    sorted_features_values = sorted(
                        zip(features, values), key=lambda x: abs(x[1]), reverse=True
                    )
                    sorted_features = [x[0] for x in sorted_features_values]
                    # Top 5 features
                    sorted_values = [x[1] for x in sorted_features_values]

                    # Create color list based on positive/negative values
                    colors = [
                        "green" if value > 0 else "red" for value in sorted_values
                    ]

                    # Create readable feature names
                    readable_features = [
                        feat.replace("mean_top_", "Top: ")
                        .replace("mean_bottom_", "Bottom: ")
                        .replace("Distance", "")
                        for feat in sorted_features
                    ]

                    fig = go.Figure()
                    fig.add_trace(
                        go.Bar(
                            x=sorted_values,
                            y=readable_features,
                            orientation="h",
                            marker_color=colors,
                        )
                    )

                    fig.update_layout(
                        title="Feature Importance",
                        xaxis_title="Impact on Recommendation",
                        yaxis_title="Features",
                        height=600,
                    )

                    st.plotly_chart(fig)

                    st.write("#### Interpreting the chart:")
                    st.write(
                        "- Green bars (positive values) contribute to recommending this city"
                    )
                    st.write(
                        "- Red bars (negative values) count against this recommendation"
                    )
                    st.write("- The larger the bar, the more influential that factor")
            else:
                st.info("No detailed explanation available for this recommendation.")

            # Print distances as dict
            if hasattr(st.session_state, "distances") and st.session_state.distances:
                st.markdown("### Distance Values")
                st.json(st.session_state.distances)

# Handle marker clicks
if out["last_object_clicked"] and not st.session_state.recommendation_shown:
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
