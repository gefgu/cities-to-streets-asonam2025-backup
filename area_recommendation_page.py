import streamlit as st
import pandas as pd
import plotly.express as px
import random
import folium
from streamlit_folium import st_folium
import json
from helper import process_area_selections


def show():
    # Add custom styling for dark mode
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
        </style>
        <div class="title-container">
            <h1>🏙️ Area Recommendation</h1>
            <p class="subtitle">Find neighborhoods that match your preferences</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write(
        """
    ## Find Your Next Destination
    
    Select neighborhoods you want more or less of in New York and Los Angeles,
    and we'll recommend the perfect Miami neighborhood for your preferences.
    """
    )

    st.markdown(
        """
        ### How It Works
        1. **Click on neighborhood areas** on the maps to view details
        2. Select if you want **more** of that area's experience (green) or **less** (orange)
        3. Click the **Get Recommendation** button to find your perfect Miami match
        
        **Note:** You can select up to 2 areas in each category from each city. For the best results, select areas in both categories.
        """
    )

    # Initialize session state for selected areas (switching to more_of/less_of paradigm)
    if "ny_more_of_areas" not in st.session_state:
        st.session_state.ny_more_of_areas = []
    if "ny_less_of_areas" not in st.session_state:
        st.session_state.ny_less_of_areas = []
    if "la_more_of_areas" not in st.session_state:
        st.session_state.la_more_of_areas = []
    if "la_less_of_areas" not in st.session_state:
        st.session_state.la_less_of_areas = []
    if "show_miami" not in st.session_state:
        st.session_state.show_miami = False

    # Load GeoJSON data
    with open("data/zipcodes_with_geometry.geojson", "r") as f:
        geojson_data = json.load(f)

    # Filter zipcodes by city
    ny_zipcodes = [
        feature
        for feature in geojson_data["features"]
        if feature["properties"]["city_name"] == "New York"
    ]
    la_zipcodes = [
        feature
        for feature in geojson_data["features"]
        if feature["properties"]["city_name"] == "Los Angeles"
    ]
    miami_zipcodes = [
        feature
        for feature in geojson_data["features"]
        if feature["properties"]["city_name"] == "Miami"
    ]

    # Create New York map
    st.markdown("### Step 1: Select areas in New York")
    st.write("Click on neighborhoods to select areas you want more or less of")

    ny_map = folium.Map(
        location=[40.7128, -74.0060], zoom_start=11, tiles="CartoDB positron"
    )

    # Add NY neighborhoods as polygon layers
    for zipcode_feature in ny_zipcodes:
        zipcode_id = zipcode_feature["properties"]["zipcode_id"]
        description = f"Zipcode {zipcode_id}: A vibrant neighborhood in New York with its own unique character."

        # Determine style based on selection state
        if zipcode_id in st.session_state.ny_more_of_areas:
            style = {
                "fillColor": "#4CAF50",  # Green
                "color": "#81C784",
                "weight": 2,
                "fillOpacity": 0.7,
            }
            icon = "thumbs-up"
        elif zipcode_id in st.session_state.ny_less_of_areas:
            style = {
                "fillColor": "#FF9800",  # Orange
                "color": "#FFB74D",
                "weight": 2,
                "fillOpacity": 0.7,
            }
            icon = "thumbs-down"
        else:
            style = {
                "fillColor": "#2196F3",  # Blue
                "color": "#64B5F6",
                "weight": 1,
                "fillOpacity": 0.5,
            }
            icon = "info-sign"

        # Add GeoJSON polygon with popup
        popup_html = f"<b>{zipcode_id}</b><br>{description}"

        folium.GeoJson(
            zipcode_feature,
            name=zipcode_id,
            style_function=lambda x, style=style: style,
            tooltip=zipcode_id,
            popup=folium.Popup(popup_html, max_width=300),
        ).add_to(ny_map)

        # Add a marker at the centroid for better visibility
        lat = zipcode_feature["properties"]["latitude"]
        lng = zipcode_feature["properties"]["longitude"]
        folium.Marker(
            location=[lat, lng],
            tooltip=zipcode_id,
            icon=folium.Icon(
                color=style["fillColor"].replace("#", ""), icon=icon, prefix="fa"
            ),
        ).add_to(ny_map)

    # Display New York map
    ny_col1, ny_col2 = st.columns([3, 1])

    with ny_col1:
        ny_map_data = st_folium(ny_map, width=900, height=600)

    with ny_col2:
        st.markdown('<div class="city-list">', unsafe_allow_html=True)
        st.write("#### Selected in NY:")

        st.markdown("##### 👍 Areas You Want More Of:")
        if st.session_state.ny_more_of_areas:
            for area in st.session_state.ny_more_of_areas:
                st.markdown(f"- **{area}** 🌟")
        else:
            st.write("None selected yet")

        st.markdown("##### 👎 Areas You Want Less Of:")
        if st.session_state.ny_less_of_areas:
            for area in st.session_state.ny_less_of_areas:
                st.markdown(f"- **{area}** ⛔")
        else:
            st.write("None selected yet")

        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Clear NY Selections", use_container_width=True):
            st.session_state.ny_more_of_areas = []
            st.session_state.ny_less_of_areas = []
            st.rerun()

    # Handle New York map clicks
    if (
        ny_map_data
        and "last_object_clicked_tooltip" in ny_map_data
        and ny_map_data["last_object_clicked_tooltip"]
    ):
        area_name = ny_map_data["last_object_clicked_tooltip"]

        # Display selection options in a card
        st.markdown(
            f"""
            <div class="city-selection-card">
                <h3 style="color: #7986CB;">🏙️ {area_name}</h3>
                <p>Would you like to see more or less of what this New York neighborhood has to offer?</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Check if we've reached the limit for either category
        more_limit_reached = (
            len(st.session_state.ny_more_of_areas) >= 2
            and area_name not in st.session_state.ny_more_of_areas
        )
        less_limit_reached = (
            len(st.session_state.ny_less_of_areas) >= 2
            and area_name not in st.session_state.ny_less_of_areas
        )

        # Show warning if limit reached
        if more_limit_reached:
            st.warning(
                "⚠️ You can select up to 2 areas in the 'More of' category. Please remove an area first."
            )

        if less_limit_reached:
            st.warning(
                "⚠️ You can select up to 2 areas in the 'Less of' category. Please remove an area first."
            )

        # Ask whether this is a "more of" or "less of" area
        col1, col2 = st.columns(2)
        with col1:
            if st.button(
                f"👍 More of {area_name}",
                key="ny_more",
                use_container_width=True,
                disabled=more_limit_reached,
            ):
                if area_name not in st.session_state.ny_more_of_areas:
                    st.session_state.ny_more_of_areas.append(area_name)
                if area_name in st.session_state.ny_less_of_areas:
                    st.session_state.ny_less_of_areas.remove(area_name)
                st.session_state.show_miami = False
                st.rerun()
        with col2:
            if st.button(
                f"👎 Less of {area_name}",
                key="ny_less",
                use_container_width=True,
                disabled=less_limit_reached,
            ):
                if area_name not in st.session_state.ny_less_of_areas:
                    st.session_state.ny_less_of_areas.append(area_name)
                if area_name in st.session_state.ny_more_of_areas:
                    st.session_state.ny_more_of_areas.remove(area_name)
                st.session_state.show_miami = False
                st.rerun()

    st.markdown("---")

    # Create Los Angeles map
    st.markdown("### Step 2: Select areas in Los Angeles")
    st.write("Click on neighborhoods to select areas you want more or less of")

    la_map = folium.Map(
        location=[34.0522, -118.2437], zoom_start=10, tiles="CartoDB positron"
    )

    # Add LA neighborhoods as polygon layers
    for zipcode_feature in la_zipcodes:
        zipcode_id = zipcode_feature["properties"]["zipcode_id"]
        description = f"Zipcode {zipcode_id}: A distinctive neighborhood in Los Angeles with its own unique vibe."

        # Determine style based on selection state
        if zipcode_id in st.session_state.la_more_of_areas:
            style = {
                "fillColor": "#4CAF50",  # Green
                "color": "#81C784",
                "weight": 2,
                "fillOpacity": 0.7,
            }
            icon = "thumbs-up"
        elif zipcode_id in st.session_state.la_less_of_areas:
            style = {
                "fillColor": "#FF9800",  # Orange
                "color": "#FFB74D",
                "weight": 2,
                "fillOpacity": 0.7,
            }
            icon = "thumbs-down"
        else:
            style = {
                "fillColor": "#2196F3",  # Blue
                "color": "#64B5F6",
                "weight": 1,
                "fillOpacity": 0.5,
            }
            icon = "info-sign"

        # Add GeoJSON polygon with popup
        popup_html = f"<b>{zipcode_id}</b><br>{description}"

        folium.GeoJson(
            zipcode_feature,
            name=zipcode_id,
            style_function=lambda x, style=style: style,
            tooltip=zipcode_id,
            popup=folium.Popup(popup_html, max_width=300),
        ).add_to(la_map)

        # Add a marker at the centroid for better visibility
        lat = zipcode_feature["properties"]["latitude"]
        lng = zipcode_feature["properties"]["longitude"]
        folium.Marker(
            location=[lat, lng],
            tooltip=zipcode_id,
            icon=folium.Icon(
                color=style["fillColor"].replace("#", ""), icon=icon, prefix="fa"
            ),
        ).add_to(la_map)

    # Display Los Angeles map
    la_col1, la_col2 = st.columns([3, 1])

    with la_col1:
        la_map_data = st_folium(la_map, width=900, height=600)

    with la_col2:
        st.markdown('<div class="city-list">', unsafe_allow_html=True)
        st.write("#### Selected in LA:")

        st.markdown("##### 👍 Areas You Want More Of:")
        if st.session_state.la_more_of_areas:
            for area in st.session_state.la_more_of_areas:
                st.markdown(f"- **{area}** 🌟")
        else:
            st.write("None selected yet")

        st.markdown("##### 👎 Areas You Want Less Of:")
        if st.session_state.la_less_of_areas:
            for area in st.session_state.la_less_of_areas:
                st.markdown(f"- **{area}** ⛔")
        else:
            st.write("None selected yet")

        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("Clear LA Selections", use_container_width=True):
            st.session_state.la_more_of_areas = []
            st.session_state.la_less_of_areas = []
            st.rerun()

    # Handle Los Angeles map clicks
    if (
        la_map_data
        and "last_object_clicked_tooltip" in la_map_data
        and la_map_data["last_object_clicked_tooltip"]
    ):
        area_name = la_map_data["last_object_clicked_tooltip"]

        # Display selection options in a card
        st.markdown(
            f"""
            <div class="city-selection-card">
                <h3 style="color: #7986CB;">🏙️ {area_name}</h3>
                <p>Would you like to see more or less of what this Los Angeles neighborhood has to offer?</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Check if we've reached the limit for either category
        more_limit_reached = (
            len(st.session_state.la_more_of_areas) >= 2
            and area_name not in st.session_state.la_more_of_areas
        )
        less_limit_reached = (
            len(st.session_state.la_less_of_areas) >= 2
            and area_name not in st.session_state.la_less_of_areas
        )

        # Show warning if limit reached
        if more_limit_reached:
            st.warning(
                "⚠️ You can select up to 2 areas in the 'More of' category. Please remove an area first."
            )

        if less_limit_reached:
            st.warning(
                "⚠️ You can select up to 2 areas in the 'Less of' category. Please remove an area first."
            )

        # Ask whether this is a "more of" or "less of" area
        col1, col2 = st.columns(2)
        with col1:
            if st.button(
                f"👍 More of {area_name}",
                key="la_more",
                use_container_width=True,
                disabled=more_limit_reached,
            ):
                if area_name not in st.session_state.la_more_of_areas:
                    st.session_state.la_more_of_areas.append(area_name)
                if area_name in st.session_state.la_less_of_areas:
                    st.session_state.la_less_of_areas.remove(area_name)
                st.session_state.show_miami = False
                st.rerun()
        with col2:
            if st.button(
                f"👎 Less of {area_name}",
                key="la_less",
                use_container_width=True,
                disabled=less_limit_reached,
            ):
                if area_name not in st.session_state.la_less_of_areas:
                    st.session_state.la_less_of_areas.append(area_name)
                if area_name in st.session_state.la_more_of_areas:
                    st.session_state.la_more_of_areas.remove(area_name)
                st.session_state.show_miami = False
                st.rerun()

    # Show Get Recommendation button when at least one selection is made
    has_ny_selections = (
        st.session_state.ny_more_of_areas or st.session_state.ny_less_of_areas
    )
    has_la_selections = (
        st.session_state.la_more_of_areas or st.session_state.la_less_of_areas
    )

    if has_ny_selections and has_la_selections:
        st.markdown("---")

        if not st.session_state.show_miami:
            st.markdown('<div class="button-container">', unsafe_allow_html=True)
            if st.button(
                "🔍 Get Recommendation", type="primary", use_container_width=True
            ):
                st.session_state.show_miami = True

                # Process selections to get recommendation
                more_of_zipcodes = []
                less_of_zipcodes = []

                more_of_zipcodes.extend(st.session_state.ny_more_of_areas)
                more_of_zipcodes.extend(st.session_state.la_more_of_areas)
                less_of_zipcodes.extend(st.session_state.ny_less_of_areas)
                less_of_zipcodes.extend(st.session_state.la_less_of_areas)

                # Call helper function to process selections
                process_area_selections(more_of_zipcodes, less_of_zipcodes)

                st.rerun()

        # Show Miami recommendation if all conditions are met
        if st.session_state.show_miami:
            st.markdown(
                """
                <div class="recommendation-box">
                    <h2>🎉 Your Recommended Miami Area</h2>
                    <p>Based on your preferences, we've found the perfect neighborhood for you in Miami.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Create Miami map
            miami_map = folium.Map(
                location=[25.7617, -80.1918], zoom_start=10, tiles="CartoDB positron"
            )

            # Highlight recommended area based on user preferences
            recommended_area = (
                "33139"  # You can make this dynamic based on user preferences
            )

            # Add Miami neighborhoods as polygon layers
            for zipcode_feature in miami_zipcodes:
                zipcode_id = zipcode_feature["properties"]["zipcode_id"]
                description = f"Zipcode {zipcode_id}: A beautiful neighborhood in Miami with its own unique character."

                # Make the recommended area purple
                if zipcode_id == recommended_area:
                    style = {
                        "fillColor": "#9C27B0",  # Purple
                        "color": "#BA68C8",
                        "weight": 2,
                        "fillOpacity": 0.7,
                    }
                    icon = "star"
                else:
                    style = {
                        "fillColor": "#2196F3",  # Blue
                        "color": "#64B5F6",
                        "weight": 1,
                        "fillOpacity": 0.5,
                    }
                    icon = "info-sign"

                # Add GeoJSON polygon with popup
                popup_html = f"<b>{zipcode_id}</b><br>{description}"

                folium.GeoJson(
                    zipcode_feature,
                    name=zipcode_id,
                    style_function=lambda x, style=style: style,
                    tooltip=zipcode_id,
                    popup=folium.Popup(popup_html, max_width=300),
                ).add_to(miami_map)

                # Add a marker at the centroid for better visibility
                lat = zipcode_feature["properties"]["latitude"]
                lng = zipcode_feature["properties"]["longitude"]
                folium.Marker(
                    location=[lat, lng],
                    tooltip=zipcode_id,
                    icon=folium.Icon(
                        color=style["fillColor"].replace("#", ""),
                        icon=icon,
                        prefix="fa",
                    ),
                ).add_to(miami_map)

            # Display Miami map
            st_folium(miami_map, width=900, height=600)

            # Show recommendation details
            st.markdown(
                f"### We recommend: **Miami Beach (Zipcode {recommended_area})**"
            )
            st.write(
                f"**Why?** This vibrant Miami neighborhood features stunning beaches, art deco architecture, and a lively cultural scene."
            )

            st.write(
                """
            Based on your preferences from New York and Los Angeles, we think you'll enjoy the 
            artistic atmosphere and urban energy of Miami Beach, with its unique blend of cultural 
            attractions and vibrant street life.
            """
            )

            # Reset button
            if st.button("🔄 Start Over", use_container_width=True):
                st.session_state.ny_more_of_areas = []
                st.session_state.ny_less_of_areas = []
                st.session_state.la_more_of_areas = []
                st.session_state.la_less_of_areas = []
                st.session_state.show_miami = False
                st.rerun()
