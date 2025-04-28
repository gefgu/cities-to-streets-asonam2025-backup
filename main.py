import streamlit as st
from streamlit_option_menu import option_menu
import city_recommendation_page
import home_page
import area_recommendation_page

# Set page to wide mode
st.set_page_config(layout="wide", page_title="City Recommendation App", page_icon="🏙️")

# Create a horizontal menu
selected = option_menu(
    menu_title=None,
    options=["Home", "City Recommendation", "Area Recommendation"],
    icons=["house", "map", "building"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
)

# Display the selected page
if selected == "Home":
    home_page.show()
elif selected == "City Recommendation":
    city_recommendation_page.show()
elif selected == "Area Recommendation":
    area_recommendation_page.show()
