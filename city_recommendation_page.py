import folium
import streamlit as st
import random
from folium.features import Marker
from streamlit_folium import st_folium
from helper import (
    generate_recommendation,
    generate_travel_recommendation_prompt,
    get_city_coordinates_data,
)
import plotly.graph_objects as go
import urllib.parse


# st.set_page_config(layout="wide", page_title="City Explorer", )


def show():
    # Header with custom styling for dark mode
    # Add this to your CSS styles section
    st.markdown(
        """
        <style>
        .title-container {
            background-color: #263238;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            color: #E0E0E0;
        }
        .subtitle {
            color: #FF9800;
            font-style: italic;
        }
        .recommendation-box {
            background-color: #1A237E;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #7986CB;
            margin-top: 20px;
            color: #E0E0E0;
        }
        .city-list {
            background-color: #37474F;
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
            color: #E0E0E0;
        }
        .button-container {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
        .city-selection-card {
            background-color: #37474F;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            color: #E0E0E0;
        }
        .confidence-box {
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
            color: #E0E0E0;
        }
        .limit-message {
            background-color: #B71C1C;
            color: white;
            padding: 8px;
            border-radius: 4px;
            font-size: 14px;
            margin: 5px 0;
        }
        .debug-box {
            background-color: #303F9F;
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            color: #E0E0E0;
            border-left: 5px solid #FF9800;
        }
        </style>
        <div class="title-container">
            <h1>🏙️ Explore Your Ideal City</h1>
            <p class="subtitle">Discover cities that match your lifestyle preferences</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        ### How It Works
        1. **Click on city markers** on the map to view details
        2. Select if you want **more** of that city's experience (green) or **less** (orange)
        3. Click the **Get Recommendation** button to find your perfect match
        
        **Note:** You can select up to 3 cities in each category. Adding cities to both categories gives the most accurate recommendations, but you can also use just one category.
        """
    )

    # Initialize session state for city preferences
    if "more_of_cities" not in st.session_state:
        st.session_state.more_of_cities = []
    if "less_of_cities" not in st.session_state:
        st.session_state.less_of_cities = []
    if "recommended_city" not in st.session_state:
        st.session_state.recommended_city = None
    if "show_recommendation_details" not in st.session_state:
        st.session_state.show_recommendation_details = False
    if "recommendation_data" not in st.session_state:
        st.session_state.recommendation_data = None
    if "debug_mode" not in st.session_state:
        st.session_state.debug_mode = False

    # Cities data - major US cities with coordinates
    cities = get_city_coordinates_data()

    # Create map centered on US
    m = folium.Map(
        location=[39.8283, -98.5795],
        zoom_start=4,
        tiles="CartoDB Positron",  # Using dark tiles for dark mode
        min_zoom=3,  # Prevent zooming out too far
        max_zoom=10,  # Prevent zooming in too much
    )

    # Add a custom title to the map
    folium.map.Marker(
        [51.5, -0.09],
        icon=folium.DivIcon(
            icon_size=(150, 36),
            icon_anchor=(0, 0),
            html='<div style="font-size: 12pt; color: white; font-weight: bold;">Click on cities to select</div>',
        ),
    ).add_to(m)

    # Define marker colors based on selection
    def get_marker_color(city):
        if city in st.session_state.more_of_cities:
            return "green"  # Cities user wants more of
        elif city in st.session_state.less_of_cities:
            return "orange"  # Cities user wants less of
        elif city == st.session_state.recommended_city:
            return "purple"  # Recommended city
        else:
            return "cadetblue"  # Default color for unselected cities

    # Define icon type based on selection
    def get_icon_type(city):
        if city in st.session_state.more_of_cities:
            return "thumbs-up"
        elif city in st.session_state.less_of_cities:
            return "thumbs-down"
        elif city == st.session_state.recommended_city:
            return "star"
        else:
            return "info-sign"

    # Add markers for each city with custom popups
    for city, coords in cities.items():
        color = get_marker_color(city)
        icon_type = get_icon_type(city)

        # Create a popup with more information about the city
        popup_html = f"""
        <div style="width: 200px; text-align: center;">
            <h4 style="margin-bottom: 5px;">{city}</h4>
            <div style="font-size: 0.9em; margin-bottom: 10px;">Click to select this city</div>
        </div>
        """

        # Add the marker to the map
        Marker(
            location=coords,
            tooltip=city,
            icon=folium.Icon(color=color, icon=icon_type, prefix="fa"),
            popup=folium.Popup(popup_html, max_width=300),
        ).add_to(m)

    # Display the map and sidebar in columns
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown("### 🗺️ Select Cities on the Map")
        out = st_folium(m, height=600, width=None)

    with col2:
        st.markdown("### 📋 Your Selections")

        # Debug mode toggle
        st.session_state.debug_mode = st.checkbox(
            "🛠️ Debug Mode", value=st.session_state.debug_mode
        )

        # More of cities with custom styling
        st.markdown("#### 👍 Cities You Want More Of:")
        if st.session_state.more_of_cities:
            st.markdown('<div class="city-list">', unsafe_allow_html=True)
            for city in st.session_state.more_of_cities:
                st.markdown(f"- **{city}** 🌟")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("None selected yet")

        # Less of cities with custom styling
        st.markdown("#### 👎 Cities You Want Less Of:")
        if st.session_state.less_of_cities:
            st.markdown('<div class="city-list">', unsafe_allow_html=True)
            for city in st.session_state.less_of_cities:
                st.markdown(f"- **{city}** ⛔")
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("None selected yet")

        # Action buttons with custom styling
        st.markdown('<div class="button-container">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state.more_of_cities = []
                st.session_state.less_of_cities = []
                st.session_state.recommended_city = None
                st.session_state.show_recommendation_details = False
                st.session_state.recommendation_data = None
                st.rerun()

        with col2:
            if st.button(
                "🔍 Get Recommendation", type="primary", use_container_width=True
            ):
                # Changed to check if at least one category has cities
                if st.session_state.more_of_cities or st.session_state.less_of_cities:
                    non_selected = [
                        city
                        for city in cities.keys()
                        if city not in st.session_state.more_of_cities
                        and city not in st.session_state.less_of_cities
                    ]
                    with st.spinner("Finding your perfect city match..."):
                        recommendation_result = generate_recommendation(
                            non_selected,
                            st.session_state.more_of_cities,
                            st.session_state.less_of_cities,
                        )

                    if recommendation_result:
                        city, confidence, lime_explanation, distances = (
                            recommendation_result
                        )
                        st.session_state.recommended_city = city
                        st.session_state.recommendation_data = recommendation_result
                        st.session_state.show_recommendation_details = True
                        st.rerun()
                    else:
                        st.error("Unable to generate a recommendation.")
                else:
                    st.warning("Please select at least one city in either category.")
        st.markdown("</div>", unsafe_allow_html=True)

    # Display recommendation if available
    if (
        st.session_state.recommended_city
        and st.session_state.show_recommendation_details
        and st.session_state.recommendation_data
    ):
        confidence = st.session_state.recommendation_data[1]
        lime_explanation = st.session_state.recommendation_data[2]
        distances = st.session_state.recommendation_data[3]

        # Generate travel recommendation prompt
        travel_recommendation = generate_travel_recommendation_prompt(
            st.session_state.recommended_city,
            st.session_state.more_of_cities,
            st.session_state.less_of_cities,
            lime_explanation,
            distances,
        )
        # Button to ask ChatGPT about the recommendation
        encoded_prompt = urllib.parse.quote(travel_recommendation)
        chatgpt_url = f"https://chat.openai.com/?prompt={encoded_prompt}"

        st.markdown(
            f"""
            <div class="recommendation-box">
                <h2>🎉 Your Recommended City</h2>
                <h3 style="color: #7986CB; margin-top: 10px;">{st.session_state.recommended_city}</h3>
                <p>Based on your preferences, we think you'll love {st.session_state.recommended_city}! We have {confidence}% of certainty!</p>
                <a href="{chatgpt_url}" target="_blank">
                        <button style="
                            background-color: #10A37F; 
                            color: white; 
                            padding: 10px 20px; 
                            border: none; 
                            border-radius: 5px; 
                            font-size: 16px;
                            cursor: pointer;">
                            💬 Ask ChatGPT to explain the recommendation
                        </button>
                </a>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Debug mode content
        if st.session_state.debug_mode:
            st.markdown('<div class="debug-box">', unsafe_allow_html=True)
            st.markdown("## 🔍 Debug Information")

            st.markdown("### Travel Recommendation - Prompt")
            st.markdown(
                f"<div style='padding:15px; border-radius:5px; background-color: #263238;'><i>{travel_recommendation}</i></div>",
                unsafe_allow_html=True,
            )

            # Display LIME explanation
            st.markdown("### Explanation")
            st.write("Factors influencing this recommendation:")

            if lime_explanation:
                # Create a bar chart for LIME explanation
                features = list(lime_explanation.keys())
                values = list(lime_explanation.values())

                if features and values:
                    # Sort features by absolute importance
                    sorted_features_values = sorted(
                        zip(features, values), key=lambda x: abs(x[1]), reverse=True
                    )
                    sorted_features = [x[0] for x in sorted_features_values]
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
                        height=400,
                        template="plotly_dark",
                        paper_bgcolor="#263238",
                        plot_bgcolor="#263238",
                        font=dict(color="#E0E0E0"),
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
            if distances:
                st.markdown("### Distance Values")
                st.json(distances)

            st.markdown("</div>", unsafe_allow_html=True)

    # Handle marker clicks
    # Handle marker clicks
    if out and "last_object_clicked" in out and out["last_object_clicked"]:
        clicked_coords = (
            out["last_object_clicked"]["lat"],
            out["last_object_clicked"]["lng"],
        )

        # Find which city was clicked
        for city, coords in cities.items():
            if (
                abs(coords[0] - clicked_coords[0]) < 0.01
                and abs(coords[1] - clicked_coords[1]) < 0.01
            ):
                # Create a card-like UI for city selection
                st.markdown(
                    f"""
                    <div class="city-selection-card">
                        <h3 style="color: #7986CB;">🏙️ {city}</h3>
                        <p>Would you like to see more or less of what {city} has to offer?</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # Check if we've reached the limit for either category
                more_limit_reached = (
                    len(st.session_state.more_of_cities) >= 3
                    and city not in st.session_state.more_of_cities
                )
                less_limit_reached = (
                    len(st.session_state.less_of_cities) >= 3
                    and city not in st.session_state.less_of_cities
                )

                # Show warning if limit reached
                if more_limit_reached:
                    st.warning(
                        "⚠️ You can select up to 3 cities in the 'More of' category. Please remove a city first."
                    )

                if less_limit_reached:
                    st.warning(
                        "⚠️ You can select up to 3 cities in the 'Less of' category. Please remove a city first."
                    )

                # Ask whether this is a "more of" or "less of" city
                col1, col2 = st.columns(2)
                with col1:
                    more_button = st.button(
                        f"👍 More of {city}",
                        key="more",
                        use_container_width=True,
                        disabled=more_limit_reached,
                    )
                    if more_button:
                        if city not in st.session_state.more_of_cities:
                            st.session_state.more_of_cities.append(city)
                        if city in st.session_state.less_of_cities:
                            st.session_state.less_of_cities.remove(city)
                        # Clear recommendation data when a new city is selected
                        st.session_state.recommended_city = None
                        st.session_state.show_recommendation_details = False
                        st.session_state.recommendation_data = None
                        st.rerun()

                with col2:
                    less_button = st.button(
                        f"👎 Less of {city}",
                        key="less",
                        use_container_width=True,
                        disabled=less_limit_reached,
                    )
                    if less_button:
                        if city not in st.session_state.less_of_cities:
                            st.session_state.less_of_cities.append(city)
                        if city in st.session_state.more_of_cities:
                            st.session_state.more_of_cities.remove(city)
                        # Clear recommendation data when a new city is selected
                        st.session_state.recommended_city = None
                        st.session_state.show_recommendation_details = False
                        st.session_state.recommendation_data = None
                        st.rerun()
