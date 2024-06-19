"""Module providing a way to read and write to files"""
# file_utils.py

import json
import os

from steam_utils import get_game_achievement_data

DATA_DIR = '../data'

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
    no_achievements_filename = "no_achievements.json"
    existing_appids = set()

    if os.path.isfile(json_filename):
        with open(json_filename, 'r', encoding='utf-8') as jsonfile:
            data = json.load(jsonfile)
            for game in data:
                existing_appids.add(game['AppID'])

    if os.path.isfile(no_achievements_filename):
        with open(no_achievements_filename, 'r', newline='', encoding='utf-8') as jsonfile:
            no_achievements_appids = json.load(jsonfile)
            existing_appids.update(no_achievements_appids)

    return existing_appids

def save_to_json(data, steamid):
    """
    Save scraped data to a JSON file for each unique SteamID. Appends to the
    file if it already exists, and creates the file if it doesn't.

    Args:
        data (list): List of data to be saved to the JSON file.
        steamid (str): The SteamID of the user.
    """
    filename = os.path.join(DATA_DIR, f"{steamid}.json")

    if os.path.isfile(filename):
        with open(filename, 'r', encoding='utf-8') as jsonfile:
            existing_data = json.load(jsonfile)
    else:
        existing_data = []

    existing_data.extend(data)

    existing_data.sort(key=lambda x: x['Rarest Achievement %'], reverse=True)

    with open(filename, 'w', encoding='utf-8') as jsonfile:
        json.dump(existing_data, jsonfile, indent=4)

def save_appids_without_achievements(appids):
    """
    Adds a list of appids without achievements to the JSON file.

    Args:
        appids (list): List of appids without achievements.
    """
    no_achievements_filename = "no_achievements.json"

    if os.path.isfile(no_achievements_filename):
        with open(no_achievements_filename, 'r', encoding='utf-8') as jsonfile:
            existing_appids = json.load(jsonfile)
    else:
        existing_appids = []

    existing_appids.extend(appids)
    existing_appids = list(set(existing_appids))  # Remove duplicates

    with open(no_achievements_filename, 'w', encoding='utf-8') as jsonfile:
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

    with open("no_achievements.json", 'w', encoding='utf-8') as jsonfile:
        json.dump(updated_appids, jsonfile, indent=4)

    print(f"Removed {num_games} appid(s) that now have achievements.")
