# hltb_utils.py
"""
Utility functions to interact with How Long to Beat (HLTB) in the Steam Completionist project.

This module provides functions to retrieve completion times for games from the HLTB site.

Functions:
    - get_hltb_data(game_name): Retrieve HLTB data for a specific game.
    - get_time_by_id(hltb_id): Retrieve the completionist time from HLTB for a specific
      game by its HLTB ID.

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

    # try stripping the unicode characters if nothing found
    if not results_list:
        game_name = re.sub(r'[^\x00-\x7F]+', '', game_name)
        results_list = hltb().search(game_name)

    # try searching a lowercase title if nothing found
    if not results_list:
        results_list = hltb().search(game_name.lower())

    # try searching after removing any details about the game edition
    if not results_list and game_name.split()[-1].lower() == "edition":
        results_list = hltb().search(game_name.rsplit(' ', 2)[0])

    # try searching after removing the year from the title
    if not results_list and bool(re.search(r"\s\(\w+\)$", game_name)):
        results_list = hltb().search(game_name.rsplit(' ', 1)[0])

    # try searching without the dash
    if not results_list and '-' in game_name:
        results_list = hltb().search(game_name.split('-')[0])

    # try searching without the colon
    if not results_list and ':' in game_name:
        results_list = hltb().search(game_name.split(':')[0])

    if len(results_list) > 0:
        best_element = max(results_list, key=lambda element: element.similarity)

        if best_element:
            hltb_id = best_element.game_id
            hltb_game_name = best_element.game_name
            times = [
                best_element.main_story,
                best_element.main_extra,
                best_element.completionist,
                best_element.all_styles,
            ]
            time = round(max(times), 2)
            return hltb_id, hltb_game_name, None if time == 0.0 else time

    return None, None, None


def get_time_by_id(hltb_id):
    """
    Retrieve the completionist time from How Long to Beat for a specific game by its HLTB ID.

    Args:
        hltb_id (int): The HLTB ID of the game.

    Returns:
        float or None: The completionist time for the game, rounded to two decimal places.
                       If no valid time is found, returns None.
    """
    result = hltb().search_from_id(hltb_id)

    times = [
        result.main_story,
        result.main_extra,
        result.completionist,
        result.all_styles,
    ]
    time = round(max(times), 2)

    return None if time == 0.0 else time
