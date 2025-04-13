import streamlit as st


def show():
    st.title("Welcome to City Recommendation App")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown(
            """
        ## About This App
        
        This application helps you discover new cities to visit based on your preferences.
        
        ### How it works:
        1. Select your favorite cities
        2. Our algorithm analyzes your preferences
        3. We recommend a new city you might enjoy
        
        Click on "City Recommendation" in the navigation bar to get started!
        """
        )

    with col2:
        st.image(
            "https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?q=80&w=1000",
            caption="Explore new cities based on your preferences",
        )
