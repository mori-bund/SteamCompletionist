# hltb_utils.py
"""
Utility functions to interact with How Long to Beat (HLTB) API in Steam Completionist project.

This module provides functions to retrieve completion times for games from HLTB API.

Functions:
    - get_hltb_data(game_name): Retrieve HLTB data for a specific game.

Dependencies:
    - re                    Module for regular expressions.
    - howlongtobeatpy       Library for interacting with How Long to Beat API.
"""

from howlongtobeatpy import HowLongToBeat as hltb

def get_hltb_data(game_name):
    """
    Retrieve How Long to Beat data for a specific game.
    Removed Unicode characters and punctuation from search

    Args:
        game_name (str): The name of the game.

    Returns:
        tuple: A tuple containing the HLTB ID, HLTB game name,
        and completionist time for the game.
    """
    results_list = hltb().search(game_name)

    if not results_list:
        results_list = hltb().search(game_name.lower())

    if len(results_list) > 0:
        best_element = max(results_list, key=lambda element: element.similarity)

        if best_element:
            hltb_id = best_element.game_id
            hltb_game_name = best_element.game_name
            completionist_time = round(best_element.completionist)
            return int(hltb_id), hltb_game_name, float(completionist_time)

    return None, None, None
