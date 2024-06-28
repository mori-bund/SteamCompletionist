# main.py
"""
Main script for the Steam Completionist project.

This script allows scraping of a Steam user's library to find rarest achievements,
update achievement data, and manage the no-achievement game list.

Usage:
    python main.py [-s STEAMID] [-v VANITY] [-u] [-m]

Options:
    -s, --steamid           Specify a SteamID to search.
    -v, --vanity            Specify a vanity URL to convert to a SteamID.
    -u, --update-no-achievements
                            Check and update no_achievements.json.
    -m, --map-update        Pull info from user files to update steam/hltb map.

If no options are provided, it uses STEAM_ID from config.py.

Dependencies:
    - file_utils            Utility functions for file handling.
    - steam_utils           Functions to interact with the Steam API.
    - hltb_utils            Utility functions for How Long to Beat API.
    - tqdm                  Progress bar library for visual feedback.
    - config                Configuration file for API keys and IDs.
"""

import sys
import json
from argparse import ArgumentParser
from tqdm import tqdm
from file_utils import (
    load_existing_appids,
    save_to_json,
    save_appids_without_achievements,
    update_no_achievements
)
from steam_utils import get_owned_games, scrape_steam_data, resolve_vanity_url
from steam_hltb_mapping import add_new_ids_from_users, load_existing_ids, sort_steam_hltb_map
from config import STEAM_ID

def resolve_steamid(args):
    """
    Resolve the SteamID based on provided command-line arguments.

    Args:
        args (argparse.Namespace): The parsed command-line arguments.

    Returns:
        str: The resolved SteamID.

    Raises:
        ValueError: If an invalid SteamID format is provided or if the vanity URL
                    couldn't be resolved to a SteamID.
    """
    steamid = STEAM_ID

    if args.steamid:
        steamid = args.steamid
    elif args.vanity:
        steamid = resolve_vanity_url(args.vanity)
        if steamid is None:
            raise ValueError(
                "The provided vanity URL couldn't be resolved to a SteamID.")
    else:
        if not steamid.isdigit() or len(steamid) != 17:
            raise ValueError(
                "Invalid SteamID. Please check the SteamID and try again.")

    return steamid

def parse_arguments(parser):
    """
    Parse command-line arguments for the Steam Completionist project.

    Args:
        parser (argparse.ArgumentParser): An instance of ArgumentParser initialized
                                          with the project description.

    Returns:
        argparse.Namespace: Parsed arguments as an object with attributes
                            corresponding to argument names.
    """
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-s', '--steamid', type=str,
                       help='Specify a SteamID to search (optional)')
    group.add_argument('-v', '--vanity', type=str,
                       help='Specify a vanity URL which converts to a SteamID (optional)')
    group.add_argument('-u', '--update-no-achievements',
                       action='store_true', help='Check and update no_achievements.txt')
    group.add_argument('-m', '--map-update',
                       action='store_true', help='Update steam_hltb_map.json')
    group.add_argument('--sort', action='store_true', help='Sort the steam_hltb_map.json file')
    return parser.parse_args()

def handle_update_no_achievements():
    """
    Load the list of AppIDs without achievements from 'data/no_achievements.json',
    update the file with the latest data, and display progress using tqdm.
    """
    with open("data/no_achievements.json", 'r', encoding='utf-8') as jsonfile:
        appids = json.load(jsonfile)
    num_games = len(appids)
    progress_bar = tqdm(total=num_games, unit='games', ncols=100)
    update_no_achievements(appids, num_games, progress_bar)

def get_new_games(steamid):
    """
    Retrieve new games owned by a Steam user that are not already listed in their
    existing AppIDs file.

    Args:
        steamid (str): The SteamID of the user.

    Returns:
        list: List of dictionaries representing new games owned by the user.
    """
    existing_appids = load_existing_appids(steamid)
    owned_games = get_owned_games(steamid)
    new_games = [game for game in owned_games if game['appid'] not in existing_appids]
    return new_games


def scrape_and_save_data(steamid, new_games):
    """
    Scrape data for new games from Steam and HowLongToBeat, save the scraped data
    to a JSON file associated with the SteamID, and update 'data/no_achievements.json'
    with AppIDs of games that have no achievements.

    Args:
        steamid (str): The SteamID of the user.
        new_games (list): List of dictionaries representing new games owned by the user.
    """
    steam_hltb_data = load_existing_ids()
    progress_bar = tqdm(total=len(new_games), unit='games', ncols=100)
    for game in new_games:
        try:
            scraped_data, no_achievements = scrape_steam_data(
                steamid, game, progress_bar, steam_hltb_data)
            save_to_json(scraped_data, steamid)
            save_appids_without_achievements(no_achievements)
        except Exception as error:
            game_info = f"AppID: {game.get('appid')}, Title: {game.get('name')}"
            print(f"\nError scraping data for {game_info}: {error}")
            continue
    progress_bar.close()

def main():
    """
    Main entry point for the Steam Completionist project.

    Parses command-line arguments to determine the action to take:
    - If `-u` or `--update-no-achievements` is provided, updates the no_achievements.json file.
    - If `-m` or `--map-update` is provided, updates the steam_hltb_map.json file.
    - If '--sort` is provided, sort the steam_hltb_map.json file
    - Otherwise, scrapes the Steam user's library for new games, retrieves achievement data,
      and manages the no-achievement game list.
    """
    parser = ArgumentParser(description='Steam Library Scraper to find rarest achievements')
    args = parse_arguments(parser)

    num_args_provided = sum(
        1 for arg in [
            args.steamid,
            args.vanity,
            args.update_no_achievements
        ] if arg
    )
    if num_args_provided > 1:
        parser.error('Please provide exactly one of -s, -v, -u, or -m.')

    if args.update_no_achievements:
        handle_update_no_achievements()
        sys.exit()

    if args.map_update:
        add_new_ids_from_users()
        sys.exit()

    if args.sort:
        sort_steam_hltb_map()

    steamid = resolve_steamid(args)
    new_games = get_new_games(steamid)

    if not new_games:
        print("No new games found to update.")
        sys.exit()

    scrape_and_save_data(steamid, new_games)

if __name__ == "__main__":
    main()
