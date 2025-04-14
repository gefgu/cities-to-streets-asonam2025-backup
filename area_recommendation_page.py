import streamlit as st
import pandas as pd
import plotly.express as px
import random
import folium
from streamlit_folium import st_folium


def show():
    st.title("Area Recommendation")

    st.write(
        """
    ## Find Your Next Destination
    
    Tell us which neighborhoods you love and the ones that are ok, but you wouldn't go again, in New York and LA, 
    and we'll recommend the perfect Miami neighborhood for your preferences
    """
    )

    # Initialize session state for selected areas
    if "ny_favorite_area" not in st.session_state:
        st.session_state.ny_favorite_area = None
    if "ny_ok_area" not in st.session_state:
        st.session_state.ny_ok_area = None
    if "la_favorite_area" not in st.session_state:
        st.session_state.la_favorite_area = None
    if "la_ok_area" not in st.session_state:
        st.session_state.la_ok_area = None
    if "show_miami" not in st.session_state:
        st.session_state.show_miami = False

    # Define New York areas with coordinates and descriptions
    ny_areas = {
        "Manhattan": {
            "coords": [40.7831, -73.9712],
            "description": "Dense urban center with skyscrapers, bustling streets, and cultural attractions.",
        },
        "Brooklyn": {
            "coords": [40.6782, -73.9442],
            "description": "Hip borough with trendy neighborhoods, diverse communities, and waterfront parks.",
        },
        "Queens": {
            "coords": [40.7282, -73.7949],
            "description": "Diverse borough with international food, Flushing Meadows Park, and LaGuardia Airport.",
        },
        "The Bronx": {
            "coords": [40.8448, -73.8648],
            "description": "Home to Yankee Stadium, the Bronx Zoo, and diverse residential neighborhoods.",
        },
        "Staten Island": {
            "coords": [40.5795, -74.1502],
            "description": "More suburban area with green spaces, connected to Manhattan by ferry.",
        },
    }

    # Define Los Angeles areas with coordinates and descriptions
    la_areas = {
        "Downtown LA": {
            "coords": [34.0522, -118.2437],
            "description": "Urban center with business district, arts scene, and entertainment venues.",
        },
        "Hollywood": {
            "coords": [34.0928, -118.3287],
            "description": "Famous entertainment district with Walk of Fame, studios, and nightlife.",
        },
        "Santa Monica": {
            "coords": [34.0195, -118.4912],
            "description": "Beachfront city with pier, shopping, and outdoor activities.",
        },
        "Beverly Hills": {
            "coords": [34.0736, -118.4004],
            "description": "Upscale area with luxury shopping, fine dining, and celebrity homes.",
        },
        "Venice": {
            "coords": [33.9850, -118.4695],
            "description": "Bohemian beachfront neighborhood with canals and famous boardwalk.",
        },
    }

    # Create New York map
    st.markdown("### Step 1: Select areas in New York")
    st.write("Select one favorite area (green) and one 'ok' area (yellow)")

    ny_map = folium.Map(location=[40.7128, -74.0060], zoom_start=11)

    for area, data in ny_areas.items():
        # Determine marker color based on selection state
        color = "blue"  # default
        icon = "info-sign"

        if area == st.session_state.ny_favorite_area:
            color = "green"
            icon = "star"
        elif area == st.session_state.ny_ok_area:
            color = "orange"
            icon = "ok-sign"

        # Add marker to map with area name in tooltip and description in popup
        popup_html = f"<b>{area}</b><br>{data['description']}"
        folium.Marker(
            location=data["coords"],
            tooltip=area,
            icon=folium.Icon(color=color, icon=icon),
            popup=folium.Popup(popup_html, max_width=300),
        ).add_to(ny_map)

    # Display New York map
    ny_col1, ny_col2 = st.columns([3, 1])

    with ny_col1:
        ny_map_data = st_folium(ny_map, width=900, height=600)

    with ny_col2:
        st.write("#### Selected in NY:")
        if st.session_state.ny_favorite_area:
            st.markdown(f"⭐ Favorite: **{st.session_state.ny_favorite_area}**")
        else:
            st.write("Favorite: None selected")

        if st.session_state.ny_ok_area:
            st.markdown(f"👌 Ok area: **{st.session_state.ny_ok_area}**")
        else:
            st.write("Ok area: None selected")

        if st.button("Clear NY Selections"):
            st.session_state.ny_favorite_area = None
            st.session_state.ny_ok_area = None
            st.rerun()

    # Handle New York map clicks
    if (
        ny_map_data
        and "last_object_clicked_tooltip" in ny_map_data
        and ny_map_data["last_object_clicked_tooltip"]
    ):
        area_name = ny_map_data["last_object_clicked_tooltip"]

        # Ask whether this is a favorite or ok area
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"Favorite: {area_name}"):
                st.session_state.ny_favorite_area = area_name
                st.rerun()
        with col2:
            if st.button(f"Ok area: {area_name}"):
                st.session_state.ny_ok_area = area_name
                st.rerun()

    st.markdown("---")

    # Create Los Angeles map
    st.markdown("### Step 2: Select areas in Los Angeles")
    st.write("Select one favorite area (green) and one 'ok' area (yellow)")

    la_map = folium.Map(location=[34.0522, -118.2437], zoom_start=11)

    for area, data in la_areas.items():
        # Determine marker color based on selection state
        color = "blue"  # default
        icon = "info-sign"

        if area == st.session_state.la_favorite_area:
            color = "green"
            icon = "star"
        elif area == st.session_state.la_ok_area:
            color = "orange"
            icon = "ok-sign"

        # Add marker to map with area name in tooltip and description in popup
        popup_html = f"<b>{area}</b><br>{data['description']}"
        folium.Marker(
            location=data["coords"],
            tooltip=area,
            icon=folium.Icon(color=color, icon=icon),
            popup=folium.Popup(popup_html, max_width=300),
        ).add_to(la_map)

    # Display Los Angeles map
    la_col1, la_col2 = st.columns([3, 1])

    with la_col1:
        la_map_data = st_folium(la_map, width=900, height=600)

    with la_col2:
        st.write("#### Selected in LA:")
        if st.session_state.la_favorite_area:
            st.markdown(f"⭐ Favorite: **{st.session_state.la_favorite_area}**")
        else:
            st.write("Favorite: None selected")

        if st.session_state.la_ok_area:
            st.markdown(f"👌 Ok area: **{st.session_state.la_ok_area}**")
        else:
            st.write("Ok area: None selected")

        if st.button("Clear LA Selections"):
            st.session_state.la_favorite_area = None
            st.session_state.la_ok_area = None
            st.rerun()

    # Handle Los Angeles map clicks
    if (
        la_map_data
        and "last_object_clicked_tooltip" in la_map_data
        and la_map_data["last_object_clicked_tooltip"]
    ):
        area_name = la_map_data["last_object_clicked_tooltip"]

        # Ask whether this is a favorite or ok area
        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"Favorite: {area_name}"):
                st.session_state.la_favorite_area = area_name
                st.rerun()
        with col2:
            if st.button(f"Ok area: {area_name}"):
                st.session_state.la_ok_area = area_name
                st.rerun()

    # Show Get Recommendation button when all selections are made
    if (
        st.session_state.ny_favorite_area
        and st.session_state.ny_ok_area
        and st.session_state.la_favorite_area
        and st.session_state.la_ok_area
    ):

        st.markdown("---")

        if not st.session_state.show_miami:
            if st.button("Get Recommendation", type="primary"):
                st.session_state.show_miami = True
                st.rerun()

        # Show Miami recommendation if all conditions are met
        if st.session_state.show_miami:
            st.markdown("### Your Recommended Area: Miami")
            st.write(
                "Based on your preferences, we recommend exploring Miami neighborhoods."
            )

            # Define Miami areas with descriptions
            miami_areas = {
                "Miami Beach": {
                    "coords": [25.7907, -80.1300],
                    "description": "Famous for Art Deco buildings, white sand beaches, and vibrant nightlife.",
                },
                "Downtown Miami": {
                    "coords": [25.7743, -80.1937],
                    "description": "Urban center with business district, museums, and waterfront parks.",
                },
                "Brickell": {
                    "coords": [25.7616, -80.1918],
                    "description": "Financial district with upscale dining, shopping, and luxury high-rises.",
                },
                "Wynwood": {
                    "coords": [25.8050, -80.1994],
                    "description": "Arts district known for colorful murals, galleries, and trendy restaurants.",
                },
                "Coral Gables": {
                    "coords": [25.7215, -80.2684],
                    "description": "Elegant suburb with historic architecture, tree-lined streets, and golf courses.",
                },
            }

            # Create Miami map
            miami_map = folium.Map(location=[25.7617, -80.1918], zoom_start=12)

            # Highlight recommended area (Wynwood) based on user preferences
            recommended_area = (
                "Wynwood"  # You could make this dynamic based on user preferences
            )

            for area, data in miami_areas.items():
                # Make the recommended area purple
                color = "purple" if area == recommended_area else "blue"
                icon = "star" if area == recommended_area else "info-sign"

                # Add marker to map with area name in tooltip and description in popup
                popup_html = f"<b>{area}</b><br>{data['description']}"
                folium.Marker(
                    location=data["coords"],
                    tooltip=area,
                    icon=folium.Icon(color=color, icon=icon),
                    popup=folium.Popup(popup_html, max_width=300),
                ).add_to(miami_map)

            # Display Miami map
            st_folium(miami_map, width=900, height=600)

            # Show recommendation details
            st.markdown(f"### We recommend: **{recommended_area}**")
            st.write(f"**Why?** {miami_areas[recommended_area]['description']}")

            st.write(
                """
            Based on your preferences from New York and Los Angeles, we think you'll enjoy the 
            artistic atmosphere and urban energy of Wynwood, with its unique blend of cultural 
            attractions and vibrant street life.
            """
            )

            # Reset button
            if st.button("Start Over"):
                st.session_state.ny_favorite_area = None
                st.session_state.ny_ok_area = None
                st.session_state.la_favorite_area = None
                st.session_state.la_ok_area = None
                st.session_state.show_miami = False
                st.rerun()
