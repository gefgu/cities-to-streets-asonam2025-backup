import streamlit as st
import pandas as pd
import plotly.express as px
import random


def show():
    st.title("Area Recommendation")

    st.write(
        """
    ## Find Your Ideal Neighborhood
    
    Based on your preferences, we'll help you discover areas that match your lifestyle needs.
    """
    )
