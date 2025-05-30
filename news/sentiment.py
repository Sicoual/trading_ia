from textblob import TextBlob

def analyze_sentiment(text):
    """
    Analyse le sentiment d'un texte via TextBlob.

    Args:
        text (str): texte à analyser

    Returns:
        float: score de sentiment entre -1 (négatif) et 1 (positif)
    """
    if not text:
        return 0.0
    blob = TextBlob(text)
    return blob.sentiment.polarity
