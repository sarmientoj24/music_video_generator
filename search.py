import json

from youtube_search import YoutubeSearch

QUERY_POSTFIX = " lyrics"


def search_youtube(query, append_to_query=True):
    """Search youtube for a video and return the first result

    Args:
        query (str): Query to search youtube for
    Returns:
        url (str): URL of the first result
    """
    if append_to_query:
        query = query + QUERY_POSTFIX

    results = YoutubeSearch(query, max_results=1).to_json()
    results_dict = json.loads(results)
    return "https://www.youtube.com" + results_dict["videos"][0]["url_suffix"]
