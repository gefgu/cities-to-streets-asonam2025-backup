import polars as pl
import random
import lightgbm as lgb
import numpy as np
import lime
from lime.lime_tabular import LimeTabularExplainer


def get_city_coordinates_data():
    """
    Load CBSA city data from CSV and return as a dictionary of city names to coordinates.

    Returns:
        dict: Dictionary with city names as keys and [latitude, longitude] as values
    """
    # Read the CSV data using polars
    df = pl.read_csv("data/cbsa_data.csv")

    # Convert to dictionary format {city_name: [latitude, longitude]}
    cities_dict = {
        row["name"]: [row["latitude"], row["longitude"]]
        for row in df.iter_rows(named=True)
    }

    return cities_dict


def generate_recommendation(non_selected_cities, top_cities, bottom_cities):
    """
    Generate a city recommendation based on user's preferences.

    Args:
        non_selected_cities (list): List of cities that haven't been selected
        top_cities (list): List of top preferred cities (green)
        bottom_cities (list): List of lower ranked cities (orange)

    Returns:
        tuple: (recommended_city, confidence_percentage, explanation_dict, distances_dict) or (None, None, None, None) if no recommendation possible
    """
    if not (top_cities and bottom_cities and non_selected_cities):
        print(
            f"Missing data: top_cities={top_cities}, bottom_cities={bottom_cities}, non_selected count={len(non_selected_cities)}"
        )
        return None, None, None, None

    features = [
        "scenesDistance",
        "frequencyCosine",
        "geographicDistance",
        "populationDistance",
        "bachelorDistance",
        "raceDistance",
        "incomeDistance",
        "employmentDistance",
        "votingDistance",
    ]

    # Load the saved model
    booster = lgb.Booster(model_file="data/lgbm_cbsa_k3_model.txt")

    pairs_df = pl.read_csv("data/similar_cbsa_pairs.csv")

    city_scores = {}
    city_distances = {}

    for city in non_selected_cities:
        city_pairs = pairs_df.filter(
            (pl.col("cbsa1_name") == city) | (pl.col("cbsa2_name") == city)
        )

        if len(city_pairs) == 0:
            print("skipped city because of no city pairs")
            # Skip cities with no data
            continue

        city_pairs = city_pairs.with_columns(
            pl.when(pl.col("cbsa1_name") == city)
            .then(pl.col("cbsa1_name"))
            .otherwise(pl.col("cbsa2_name"))
            .alias("city_name")
        )

        top_pairs = city_pairs.filter(
            pl.col("cbsa1_name").is_in(top_cities)
            | pl.col("cbsa2_name").is_in(top_cities)
        )

        bottom_pairs = city_pairs.filter(
            pl.col("cbsa1_name").is_in(bottom_cities)
            | pl.col("cbsa2_name").is_in(bottom_cities)
        )

        # Skip if no data for comparison with selected cities
        if len(top_pairs) == 0 or len(bottom_pairs) == 0:
            print("skipped - no data for comparison with selected citiess")
            continue

        top_distances = top_pairs.group_by(["city_name"]).agg(
            [
                pl.col(feat).drop_nans().drop_nulls().mean().alias(f"mean_top_{feat}")
                for feat in features
            ]
        )
        bottom_distances = bottom_pairs.group_by(["city_name"]).agg(
            [
                pl.col(feat)
                .drop_nans()
                .drop_nulls()
                .mean()
                .alias(f"mean_bottom_{feat}")
                for feat in features
            ]
        )

        joined_distances = top_distances.join(
            bottom_distances,
            on=["city_name"],
            how="full",
            suffix="_bottom",
        )

        df = joined_distances.to_pandas()

        # Skip cities with missing data - ADDING DEBUG PRINT
        if df.empty:
            print("skipped city because of empty dataframe")
            continue

        X = df[
            [f"mean_top_{feat}" for feat in features]
            + [f"mean_bottom_{feat}" for feat in features]
        ]

        # Skip cities with missing data
        # if X.isna().any().any():
        #     print(X)
        #     print(f"skipped city because of missing data in X: {city}")
        #     continue

        predictions = booster.predict(X)

        # Create fallback simple explanation if LIME fails
        feature_importance = {}

        try:
            # Add LIME explanation
            feature_names = list(X.columns)
            explanation = explain_prediction_with_lime(booster, X, feature_names)

            # Store the explanation results and sort them by absolute value
            feature_importance_list = explanation.as_list()
            # Sort by absolute magnitude of feature importance
            sorted_importance = sorted(
                feature_importance_list, key=lambda x: abs(x[1]), reverse=True
            )

            # Store as ordered dictionary
            feature_importance = {feat: value for feat, value in sorted_importance}
        except Exception as e:
            print(f"LIME explanation failed for {city}: {e}")
            # Create a fallback simplified explanation using the raw feature values
            for feat in features:
                top_key = f"mean_top_{feat}"
                bottom_key = f"mean_bottom_{feat}"
                if top_key in df.columns and bottom_key in df.columns:
                    feature_importance[top_key] = float(df[top_key].iloc[0])
                    feature_importance[bottom_key] = float(df[bottom_key].iloc[0])

        # Store the raw distance values for this city
        raw_distances = {}
        for feat in features:
            if f"mean_top_{feat}" in df.columns:
                raw_distances[f"top_{feat}"] = float(df[f"mean_top_{feat}"].iloc[0])
            if f"mean_bottom_{feat}" in df.columns:
                raw_distances[f"bottom_{feat}"] = float(
                    df[f"mean_bottom_{feat}"].iloc[0]
                )

        city_distances[city] = raw_distances

        # Store city score and explanation
        city_scores[city] = {
            "score": float(predictions[0]),
            "explanation": feature_importance,
        }

    # If no cities were scored, return random recommendation with simple explanation
    if not city_scores:
        if non_selected_cities:
            recommended = random.choice(non_selected_cities)
            confidence = random.randint(60, 95)

            # Create a simple explanation
            simple_explanation = {
                "random_recommendation": 1.0,
                "insufficient_data": 0.8,
            }

            # Create simple distances
            simple_distances = {"notice": "Insufficient data for detailed analysis"}

            return recommended, confidence, simple_explanation, simple_distances
        else:
            return None, None, None, None

    # Find city with highest score
    recommended = max(city_scores.keys(), key=lambda c: city_scores[c]["score"])

    # Convert score to confidence percentage (assuming scores are between 0-1)
    # Limit to range between 60-95%
    score = city_scores[recommended]["score"]
    confidence = int(max(60, min(95, score * 100)))

    # Return the top recommendation, confidence score, and explanation
    return (
        recommended,
        confidence,
        city_scores[recommended]["explanation"],
        city_distances[recommended],
    )


def explain_prediction_with_lime(model, features_df, feature_names):
    """
    Use LIME to explain a prediction made by a LightGBM model.

    Args:
        model: Trained LightGBM booster
        features_df: Pandas DataFrame with feature values
        feature_names: List of feature names

    Returns:
        lime.explanation.Explanation: LIME explanation object
    """
    class_names = ["Not Top", "Is Top"]

    # Create a wrapper function for the model that returns probabilities in the format LIME expects
    def predict_proba_wrapper(data_instance):
        # LightGBM's predict returns probabilities for binary classification
        predictions = model.predict(data_instance)
        # Convert to the format LIME expects: array of shape (n_samples, n_classes)
        return np.vstack([1 - predictions, predictions]).T

    # Create the LIME explainer
    explainer = LimeTabularExplainer(
        features_df.values,
        feature_names=feature_names,
        class_names=class_names,
        discretize_continuous=False,
        mode="classification",
    )

    # Generate explanation for the first instance
    instance_idx = 0
    explanation = explainer.explain_instance(
        features_df.iloc[instance_idx].values,
        predict_proba_wrapper,
        num_features=len(feature_names),
    )

    return explanation


def generate_travel_recommendation(
    recommended_city, top_cities, bottom_cities, lime_explanation, distances
):
    """
    Generate a personalized travel recommendation based on user preferences and ML explanation.

    Args:
        recommended_city (str): The recommended city name
        top_cities (list): List of user's top preferred cities
        bottom_cities (list): List of user's lower ranked cities
        lime_explanation (dict): LIME explanation with feature importance values
        distances (dict): Raw distance values between cities

    Returns:
        str: A personalized travel recommendation paragraph
    """
    if not lime_explanation or not distances:
        return f"Based on your preferences, {recommended_city} seems like a great match for your next travel destination!"

    # Get the top 2 most influential features (by absolute value)
    top_features = sorted(
        lime_explanation.items(), key=lambda x: abs(x[1]), reverse=True
    )[:2]

    # Feature name translation dictionary
    feature_translations = {
        "scenesDistance": "cultural vibe",
        "frequencyCosine": "venue mix and attractions",
        "geographicDistance": "geographical location",
        "populationDistance": "city size and atmosphere",
        "bachelorDistance": "educational environment",
        "raceDistance": "cultural diversity",
        "incomeDistance": "economic character",
        "employmentDistance": "job market and infrastructure",
        "votingDistance": "local community values",
    }

    # Generate recommendation text
    top_city = top_cities[0] if top_cities else "your favorite cities"
    bottom_city = bottom_cities[0] if bottom_cities else "your less preferred cities"

    # Build recommendation text
    recommendation = f"{recommended_city} is a perfect match for your travel style. "

    # Add insights about top features
    for feature_name, importance in top_features:
        base_feature = feature_name.replace("mean_top_", "").replace("mean_bottom_", "")
        friendly_name = feature_translations.get(base_feature, base_feature)

        # Check if we have raw distance values for this feature
        top_key = f"top_{base_feature}"
        bottom_key = f"bottom_{base_feature}"

        if top_key in distances and bottom_key in distances:
            top_value = distances[top_key]
            bottom_value = distances[bottom_key]

            if "top" in feature_name and importance > 0:
                recommendation += f"Like {top_city}, it offers a similar {friendly_name} (with a similarity score of {top_value:.2f} compared to {bottom_value:.2f} for {bottom_city}). "
            elif "bottom" in feature_name and importance < 0:
                recommendation += f"Unlike {bottom_city}, it provides a different {friendly_name} experience that better aligns with your preferences. "

    # Add a compelling call to action
    recommendation += f"Pack your bags—{recommended_city} has everything you enjoyed in {top_city} and more!"

    return recommendation


def generate_travel_recommendation_prompt(
    recommended_city, top_cities, bottom_cities, lime_explanation, distances
):
    """
    Generate a personalized travel recommendation prompt for an LLM system.

    Args:
        recommended_city (str): The recommended city name
        top_cities (list): List of user's top preferred cities
        bottom_cities (list): List of user's lower ranked cities
        lime_explanation (dict): LIME explanation with feature importance values
        distances (dict): Raw distance values between cities

    Returns:
        str: A formatted LLM prompt for generating travel recommendations
    """
    if not lime_explanation or not distances:
        return f"Based on your preferences, {recommended_city} seems like a great match for your next travel destination!"

    # Feature name translation dictionary
    feature_translations = {
        "scenesDistance": "cultural vibe",
        "frequencyCosine": "venue mix and attractions",
        "geographicDistance": "geographical location",
        "populationDistance": "city size and atmosphere",
        "bachelorDistance": "educational environment",
        "raceDistance": "cultural diversity",
        "incomeDistance": "economic character",
        "employmentDistance": "job market and infrastructure",
        "votingDistance": "local community values",
    }

    # Format lists for the prompt
    top_cities_str = ", ".join(top_cities) if top_cities else "None provided"
    bottom_cities_str = ", ".join(bottom_cities) if bottom_cities else "None provided"

    # Format the LIME explanations and distances for readability
    lime_explanations_formatted = "\n".join(
        [f"    {k}: {v}" for k, v in lime_explanation.items()]
    )

    # Format distances dictionary
    distances_formatted = "\n".join([f"    {k}: {v}" for k, v in distances.items()])

    # Create the prompt template
    prompt = f"""
Task: Write a 3-4 sentence travel recommendation for {recommended_city} based on the user’s preferences, using the provided data to justify why it’s a better fit than alternatives. Focus on relatable comparisons (e.g., "like [TOP_CITY], but with [DIFFERENCE]") and avoid jargon.

Input Data:

    Top Cities (Favorite): {top_cities_str} → The user enjoys these places the most.

    Bottom Cities (Ok): {bottom_cities_str} → The user visited these places but didn't enjoy them as much.

    Key LIME Explanations (Influence Scores):
    {lime_explanations_formatted}

    Raw Distance Values:
    {distances_formatted}

Instructions:

    Prioritize Top LIME Factors: Highlight the 2-3 most influential metrics (e.g., scenesDistance, frequencyCosine) and explain their impact.

    Example: "If mean_top_scenesDistance is high, say: ‘Its artsy vibe feels more like [TOP_CITY] than [BOTTOM_CITY].’"

    Avoid Jargon: Translate metrics into traveler benefits:

        scenesDistance → "cultural vibe"

        frequencyCosine → "similar types of attractions"

        employmentDistance → "tourist-friendly infrastructure"

    Persuasive Hook: End with a call to action (e.g., "If you love [TOP_CITY]'s [trait], you'll feel right at home here!").
    
    Simplify Metrics: Always translate raw data into traveler-friendly terms (e.g., "employmentDistance" → "easy-to-navigate infrastructure").
    
    Stronger Hook: Start with a confident, personalized opener (e.g., "[CITY] is a perfect blend of what you love about [TOP_CITY] and [TOP_CITY]!").
    
    Explicit Comparisons: Directly contrast top/bottom cities (e.g., "Unlike [BOTTOM_CITY], [CITY] has [TRAIT]...").
    
    Raw Value Comparisons: Use these only to support claims (e.g., "Its venue mix is closer to Boston’s (0.93) than Portland’s (0.96)" → rewritten as "You’ll find familiar restaurants and nightlife, like in Boston.").
    
    Use this feature meanings: {str(feature_translations)}

Output Template:
"{recommended_city} is the ideal next stop for you. Like {top_cities[0] if top_cities else 'your favorite destinations'}, it's [trait1] and [trait2], so you'll feel right at home. Unlike {bottom_cities[0] if bottom_cities else 'your less preferred cities'}, it avoids [disliked_trait]—instead offering [alternative]. If you loved {top_cities[0] if top_cities else 'your top city'}'s [aspect], you'll adore {recommended_city}'s twist on it!"
"""

    return prompt
