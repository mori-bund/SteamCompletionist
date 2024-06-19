"""Module providing a way to interact with HLTB"""
import re
from howlongtobeatpy import HowLongToBeat as hltb

def get_hltb_data(game_name):
    """
    Retrieve How Long to Beat data for a specific game.
    Removed Unicode characters and punctuation from search

    Args:
        game_name (str): The name of the game.

    Returns:
        tuple: A tuple containing the HLTB ID and completionist time for the game.
    """
    clean_title = re.sub(r'[^a-z0-9\s]', '', game_name).lower()
    results_list = hltb().search(clean_title)

    if results_list is not None and len(results_list) > 0:
        best_element = max(results_list, key=lambda element: element.similarity)

        if best_element:
            hltb_id = best_element.game_id
            completionist_time = round(best_element.completionist)
            return int(hltb_id), float(completionist_time)

    return None, None
