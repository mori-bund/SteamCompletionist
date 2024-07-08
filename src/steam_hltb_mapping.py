#steam_hltb_mapping.py
"""
This module manages a JSON file (`steam_hltb_map.json`) that maps Steam AppIDs to HLTB IDs
for games. It provides functionality to scan user JSON files containing game data, extract
relevant information, and update the `steam_hltb_map.json` file with new entries.

Functions:
    - add_new_ids_from_users(): Scan user JSON files and add new Steam IDs to the mapping file.
    - load_existing_ids(): Load existing Steam AppIDs from `steam_hltb_map.json`.
    - update_steam_hltb_map(new_entries): Update `steam_hltb_map.json` with new entries.
    - list_user_json_files(): List all user JSON files in the data directory.
    - sort_steam_hltb_map(): Sort the `steam_hltb_map.json` file by AppID.
    - update_rarest_achievement_percentages(): Update the Rarest Achievement % for each game.
    - update_hltb_completionist_times(): Update HLTB completionist times for all entries.

Example Usage:
    # Add new Steam IDs from user JSON files to the mapping file
    add_new_ids_from_users()
"""
import os
import json
from tqdm import tqdm
from steam_utils import get_game_achievement_data, get_rarest_achievement_percentage
from hltb_utils import get_time_by_id

DATA_DIR = 'data'
STEAM_HLTB_MAP_FILE = os.path.join(DATA_DIR, 'steam_hltb_map.json')

def add_new_ids_from_users():
    """
    Scan all user JSON files in the data directory and add any new Steam IDs
    found to the `steam_hltb_map.json` file.
    """
    existing_ids = load_existing_ids()

    new_entries = {}

    user_json_files = list_user_json_files()
    for json_file in user_json_files:
        with open(json_file, 'r', encoding='utf-8') as jsonfile:
            user_data = json.load(jsonfile)
            for entry in user_data:
                app_id = entry.get('AppID')
                title = entry.get('Title')
                rarest_achievement = entry.get('Rarest Achievement %')
                hltb_id = entry.get('HLTB ID')
                hltb_title = entry.get('HLTB Title')
                hltb_completionist_time = entry.get('HLTB Completionist Time')

                if app_id not in existing_ids and app_id not in new_entries:
                    new_entries[app_id] = {
                        'AppID': app_id,
                        'Title': title,
                        'Rarest Achievement %': rarest_achievement,
                        'HLTB ID': hltb_id,
                        'HLTB Title': hltb_title,
                        'HLTB Completionist Time': hltb_completionist_time
                    }

    if new_entries:
        update_steam_hltb_map(list(new_entries.values()))
    else:
        print("No new entries added.")


def load_existing_ids():
    """
    Load existing Steam IDs from `steam_hltb_map.json`.

    Returns:
        dict: A dictionary of existing entries with AppIDs as keys.
    """
    if not os.path.exists(STEAM_HLTB_MAP_FILE):
        with open(STEAM_HLTB_MAP_FILE, 'w', encoding='utf-8') as jsonfile:
            json.dump([], jsonfile)

    with open(STEAM_HLTB_MAP_FILE, 'r', encoding='utf-8') as jsonfile:
        try:
            existing_data = json.load(jsonfile)
        except json.JSONDecodeError:
            existing_data = []

    return {entry['AppID']: entry for entry in existing_data}


def update_steam_hltb_map(new_entries):
    """
    Update `steam_hltb_map.json` with new entries (AppID, HLTB ID, Title,
    Rarest Achievement %, HLTB Title, HLTB Completionist Time).

    Args:
        new_entries (list): List of dictionaries containing new entries to be added to the
                            `steam_hltb_map.json` file. Each dictionary represents an entry
                            with keys 'AppID', 'HLTB ID', 'Title', 'Rarest Achievement %',
                            'HLTB Title', 'HLTB Completionist Time'.
    """
    with open(STEAM_HLTB_MAP_FILE, 'r', encoding='utf-8') as jsonfile:
        try:
            existing_data = json.load(jsonfile)
        except json.JSONDecodeError:
            existing_data = []

    existing_data.extend(new_entries)

    with open(STEAM_HLTB_MAP_FILE, 'w', encoding='utf-8') as jsonfile:
        json.dump(existing_data, jsonfile, indent=4)

    num_entries_added = len(new_entries)
    entry_word = "entry" if num_entries_added == 1 else "entries"
    print(f"Added {num_entries_added} new {entry_word} to steam_hltb_map.json.")


def list_user_json_files():
    """
    List all user JSON files in the data directory.

    Returns:
        list: List of file paths to user JSON files in the data directory.
    """
    user_json_files = []
    for root, _dirs, files in os.walk(DATA_DIR):
        for file in files:
            if file.startswith("7"):
                user_json_files.append(os.path.join(root, file))
    return user_json_files


def sort_steam_hltb_map():
    """
    Sort the `steam_hltb_map.json` file by AppID.
    """
    if not os.path.exists(STEAM_HLTB_MAP_FILE):
        print("steam_hltb_map.json does not exist.")
        return

    with open(STEAM_HLTB_MAP_FILE, 'r', encoding='utf-8') as jsonfile:
        try:
            data = json.load(jsonfile)
        except json.JSONDecodeError:
            print("steam_hltb_map.json is empty or corrupted.")
            return

    sorted_data = sorted(data, key=lambda x: x['AppID'])

    with open(STEAM_HLTB_MAP_FILE, 'w', encoding='utf-8') as jsonfile:
        json.dump(sorted_data, jsonfile, indent=4)

    print("steam_hltb_map.json has been sorted.")


def update_rarest_achievement_percentages():
    """
    Update the Rarest Achievement % for each game in `steam_hltb_map.json`
    with a progress bar.
    """
    with open(STEAM_HLTB_MAP_FILE, 'r', encoding='utf-8') as jsonfile:
        try:
            data = json.load(jsonfile)
        except json.JSONDecodeError:
            print("steam_hltb_map.json is empty or corrupted.")
            return

    num_entries = len(data)
    progress_bar = tqdm(total=num_entries, desc="Updating Rarest Achievements",
                        unit="game", ncols=100)

    for entry in data:
        appid = entry.get('AppID')
        if appid:
            achievements = get_game_achievement_data(appid)
            if achievements:
                entry['Rarest Achievement %'] = get_rarest_achievement_percentage(achievements)
        progress_bar.update(1)

    progress_bar.close()

    with open(STEAM_HLTB_MAP_FILE, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=4)

    print("Updated Rarest Achievement % for all games in steam_hltb_map.json.")


def update_hltb_completionist_times():
    """
    Update HLTB completionist times for all entries in the `steam_hltb_map.json` file.

    This function iterates through the entries in the `steam_hltb_map.json` file, retrieves
    the completionist time from HLTB using the HLTB ID, and updates the entry with the new time.
    """
    try:
        with open('data/steam_hltb_map.json', 'r', encoding='utf-8') as file:
            steam_hltb_map = json.load(file)
    except FileNotFoundError:
        print("Error: steam_hltb_map.json file not found.")
        return
    except json.JSONDecodeError:
        print("Error: JSON decoding error in steam_hltb_map.json.")
        return

    progress_bar = tqdm(total=len(steam_hltb_map), unit='games', ncols=100, desc="Updating HLTB Completionist Times")

    for entry in steam_hltb_map:
        hltb_id = entry.get('HLTB ID')
        if hltb_id:
            try:
                completionist_time = get_time_by_id(hltb_id)
                entry['HLTB Completionist Time'] = completionist_time
            except Exception as e:
                print(f"Error processing HLTB ID {hltb_id} for game {entry.get('Game Name')}: {e}")
        progress_bar.update(1)

    progress_bar.close()

    with open('data/steam_hltb_map.json', 'w', encoding='utf-8') as file:
        json.dump(steam_hltb_map, file, indent=4, ensure_ascii=False)
