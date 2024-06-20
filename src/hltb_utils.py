# hltb_utils.py
"""
Utility functions to interact with How Long to Beat (HLTB) in the Steam Completionist project.

This module provides functions to retrieve completion times for games from the HLTB site.

Functions:
    - get_hltb_data(game_name): Retrieve HLTB data for a specific game.

Dependencies:
    - re: Module for regular expressions.
    - howlongtobeatpy: Library for interacting with the How Long to Beat site.
"""

import re
from howlongtobeatpy import HowLongToBeat as hltb

def get_hltb_data(game_name):
    """
    Retrieve How Long to Beat data for a specific game.

    Args:
        game_name (str): The name of the game.

    Returns:
        tuple: A tuple containing the HLTB ID (int), HLTB game name (str),
               and completionist time (float) for the game.
               If no data is found, returns (None, None, None).
    """
    results_list = hltb().search(game_name)

    # try searching a lowercase title if not found
    if not results_list:
        results_list = hltb().search(game_name.lower())

    # try searching after removing any details about the game edition
    if not results_list and game_name.split()[-1].lower() == "edition":
        results_list = hltb().search(game_name.rsplit(' ', 2)[0])

    # try searching after removing the year from the title
    if not results_list and bool(re.search(r"\s\(\w+\)$", game_name)):
        results_list = hltb().search(game_name.rsplit(' ', 1)[0])

    if not results_list and ':' in game_name:
        results_list = hltb().search(game_name.split(':')[0])

    if len(results_list) > 0:
        best_element = max(results_list, key=lambda element: element.similarity)

        if best_element:
            hltb_id = best_element.game_id
            hltb_game_name = best_element.game_name
            completionist_time = round(best_element.completionist)
            return int(hltb_id), hltb_game_name, float(completionist_time)

    return None, None, None
