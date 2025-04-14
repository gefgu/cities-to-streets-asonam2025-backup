import streamlit as st


def show():
    st.title("Travel Destination Recommender")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown(
            """
        ## Plan Your Next Adventure
        
        This application helps travelers discover ideal destinations based on your preferences.
        
        ### How it works:
        
        **City Recommendations:**
        1. Select cities you've enjoyed visiting in the past
        2. Our algorithm analyzes your travel preferences
        3. Discover a new city destination that matches your taste
        
        **Neighborhood Recommendations:**
        1. Tell us which neighborhoods you loved in New York and LA
        2. Indicate areas you found just okay during past visits
        3. We'll suggest the perfect Miami neighborhood for your next trip
        
        Start exploring new travel destinations now!
        """
        )

        # Add quick navigation buttons with navigation functionality
        st.write("### Ready to explore?")
        st.markdown(
            """
                    Select a page on the navbar above to start your journey
            """
        )

    with col2:
        st.image(
            "https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?q=80&w=1000",
            caption="Find your next perfect travel destination",
        )

        # Tourism-focused call to action
        st.info(
            "💡 **Travel Tip**: Use our recommendations to discover hidden gems and neighborhoods that match your travel style!"
        )
