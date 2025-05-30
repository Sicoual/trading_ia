import os
import requests

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
BASE_URL = "https://newsapi.org/v2/everything"

def fetch_news(query, from_date=None, to_date=None, page_size=10):
    """
    Récupère les dernières news pour un mot-clé ou symbole.

    Args:
        query (str): mot-clé ou symbole boursier
        from_date (str): date début au format 'YYYY-MM-DD'
        to_date (str): date fin au format 'YYYY-MM-DD'
        page_size (int): nombre max d'articles

    Returns:
        list: articles (dictionnaires avec titre, description, url, publishedAt)
    """
    params = {
        'q': query,
        'apiKey': NEWSAPI_KEY,
        'pageSize': page_size,
        'sortBy': 'publishedAt',
        'language': 'en',
    }
    if from_date:
        params['from'] = from_date
    if to_date:
        params['to'] = to_date

    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()
    return data.get('articles', [])
