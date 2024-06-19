# file_utils.py
"""
Utility functions for file handling in Steam Completionist project.

This module provides functions to load existing data, save data to CSV and JSON,
manage no-achievement game lists, and handle file operations.

Functions:
    - load_existing_appids(steamid): Retrieve existing Steam AppIDs from CSV and text files.
    - save_to_csv(data, steamid): Save scraped data to CSV file sorted by rarest achievement.
    - save_to_json(data, steamid): Save scraped data to JSON file sorted by rarest achievement.
    - save_appids_without_achievements(appids): Append new appids without achievements to text file.
    - update_no_achievements(appids, num_games, progress_bar): Update no-achievements list.

Dependencies:
    - csv                   Module for CSV file operations.
    - os                    Module for operating system functions.
    - pandas                Library for data manipulation and analysis.
    - api_utils.py          Utility functions for interacting with external APIs.
    - tqdm                  Progress bar library for visual feedback.
"""

import json
import os

from steam_utils import get_game_achievement_data

DATA_DIR = 'data'
NO_ACHIEVEMENTS_PATH = os.path.join('src', 'no_achievements.json')

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


def load_existing_appids(steamid):
    """
    Get a list of AppIDs that have already been scanned. Gets them from an
    existing JSON (if there is one) and from a list of games known to have
    no achievements.

    Args:
        steamid (str): The SteamID of the user.

    Returns:
        set: A set of previously scraped Steam AppIDs.
    """
    json_filename = os.path.join(DATA_DIR, f"{steamid}.json")
    existing_appids = set()

    if os.path.isfile(json_filename):
        with open(json_filename, 'r', encoding='utf-8') as jsonfile:
            data = json.load(jsonfile)
            for item in data:
                appid = int(item['AppID'])
                existing_appids.add(appid)

    if os.path.isfile(NO_ACHIEVEMENTS_PATH):
        with open(NO_ACHIEVEMENTS_PATH, 'r', encoding='utf-8') as jsonfile:
            data = json.load(jsonfile)
            for appid in data:
                existing_appids.add(appid)

    return existing_appids


def save_to_json(data, steamid):
    """
    Save scraped data to a JSON file for each unique SteamID. Appends to the
    file if it already exists, and creates the file if it doesn't. Sorts
    the JSON by rarest achievement when finished.

    Args:
        data (list): List of data to be saved to the JSON file.
        steamid (str): The SteamID of the user.
    """
    json_filename = os.path.join(DATA_DIR, f"{steamid}.json")

    existing_data = []

    if os.path.isfile(json_filename):
        with open(json_filename, 'r', encoding='utf-8') as jsonfile:
            existing_data = json.load(jsonfile)

    existing_data.extend(data)

    existing_data.sort(key=lambda x: float(x['Rarest Achievement %']), reverse=True)

    with open(json_filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(existing_data, jsonfile, indent=4)


def save_appids_without_achievements(appids):
    """
    Adds a list of appids without achievements to the JSON file.

    Args:
        appids (list): List of appids without achievements.
    """

    existing_appids = []

    if os.path.isfile(NO_ACHIEVEMENTS_PATH):
        with open(NO_ACHIEVEMENTS_PATH, 'r', encoding='utf-8') as jsonfile:
            existing_appids = json.load(jsonfile)

    existing_appids.extend(appids)
    existing_appids = sorted(set(existing_appids))  # Remove duplicates and sort

    with open(NO_ACHIEVEMENTS_PATH, 'w', encoding='utf-8') as jsonfile:
        json.dump(existing_appids, jsonfile, indent=4)


def update_no_achievements(appids, num_games, progress_bar):
    """
    Update the list of appids without achievements. This is done with an
    optional flag at runtime.

    Args:
        appids (list): List of appids without achievements.
        num_games (int): The total number of appids to be updated.
        progress_bar (tqdm.tqdm): Progress bar for tracking progress.
    """
    updated_appids = []
    for appid in appids:
        if get_game_achievement_data(appid) is None:
            updated_appids.append(appid)
            num_games -= 1
        progress_bar.update(1)

    with open(NO_ACHIEVEMENTS_PATH, 'w', encoding='utf-8') as jsonfile:
        json.dump(updated_appids, jsonfile, indent=4)

    print(f"Removed {num_games} appid(s) that now have achievements.")
