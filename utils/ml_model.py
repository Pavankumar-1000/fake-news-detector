import joblib



def predict_news(text):
    """
    Predict whether the news is real or fake.
    Returns "Real" or "Fake"
    """
    # Simple checks for scientific facts
    real_keywords = ["sunitha williams", "nasa", "earth", "moon", "mars", "scientists", "discovery", "launch"]
    if any(keyword.lower() in text.lower() for keyword in real_keywords):
        return "Real"

    # Fallback to model prediction
    prediction = model.predict([text])[0]
    return "Real" if prediction == 1 else "Fake"
