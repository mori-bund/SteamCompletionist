# steam_utils.py
"""
Utility functions to interact with the Steam API for the Steam Completionist project.

This module provides functions to retrieve owned games, scrape achievement data,
check completion status, resolve vanity URLs, and handle Steam API interactions.

Functions:
    - get_owned_games(steamid): Retrieve the list of games owned by a Steam user.
    - get_game_achievement_data(appid): Retrieve achievement data for a specific game.
    - get_rarest_achievement_percentage(data): Get the percentage of the rarest achievement.
    - player_has_completed(steamid, appid): Check if a user has completed all achievements.
    - scrape_steam_data(steamid, new_games, progress_bar): Scrape data for owned games.
    - resolve_vanity_url(vanity): Resolve a Steam vanity URL to a SteamID.

Dependencies:
    - requests: Library for making HTTP requests.
    - steam.webapi: Library for accessing the Steam Web API.
    - steam.steamid: Library for handling Steam IDs.
    - config.py: Configuration file for API keys and IDs.
"""

import sys
import re
import requests
from steam.webapi import WebAPI
from steam import steamid as sid
from hltb_utils import get_hltb_data
from config import API_KEY

api = WebAPI(key=API_KEY)

def get_owned_games(steamid):
    """
    Retrieve the list of games owned by a Steam user.

    Args:
        steamid (str): The SteamID of the user.

    Returns:
        list: A list of dictionaries containing game information.
    """
    owned_games = api.IPlayerService.GetOwnedGames(steamid=steamid, include_appinfo=True,
                                                   include_played_free_games=True,
                                                   appids_filter=False,
                                                   include_free_sub=False,
                                                   language='en',
                                                   include_extended_appinfo=False,
                                                   skip_unvetted_apps=False)
    return owned_games['response']['games']


def get_game_achievement_data(appid):
    """
    Retrieve achievement data for a specific game.

    Args:
        appid (int): The Steam AppID of the game.

    Returns:
        list or None: A list of achievement data dictionaries for the game,
        or None if there are none.
    """
    try:
        achievement_data = api.ISteamUserStats.GetGlobalAchievementPercentagesForApp(
            gameid=appid)['achievementpercentages']['achievements']
        if achievement_data == []:
            return None
        return achievement_data
    except requests.exceptions.HTTPError as _e:
        return None


def get_rarest_achievement_percentage(data):
    """
    Get the percentage of the rarest achievement in a game.

    Args:
        data (list): List of achievement data dictionaries for a game.

    Returns:
        str: The percentage completion of the game's rarest achievement.
    """
    rarest_percentage = min(data, key=lambda x: x.get(
        'percent', 100)).get('percent')
    rounded_percentage = round(rarest_percentage, 1)
    return f"{rounded_percentage:.1f}"


def player_has_completed(steamid, appid):
    """
    Check if a user has completed all achievements for a game.

    Args:
        steamid (str): The SteamID of the user.
        appid (int): The Steam AppID of the game.

    Returns:
        bool or None: True if the user has completed all achievements, False if not,
                      or None if there's an issue retrieving the data.
    """
    try:
        player_data = api.ISteamUserStats.GetPlayerAchievements(
            steamid=steamid, appid=appid)
    except requests.exceptions.HTTPError as _e:
        return None

    achievements = player_data['playerstats']['achievements']

    return all(achievement.get('achieved', False) for achievement in achievements)


def scrape_steam_data(steamid, new_games, progress_bar, existing_data):
    """
    Scrape data for each game in a user's library to get the appid, title,
    rarest achievement, and completion status.

    Args:
        steamid (str): The SteamID of the user.
        new_games (list): List of games owned by the user that haven't been scraped yet.
        progress_bar (tqdm.tqdm): Progress bar for tracking progress.

    Returns:
        tuple: A tuple containing a list of scraped data and a list of appids with no achievements.
    """
    scraped_data, no_achievements = [], []

    for game in new_games:
        appid = game['appid']
        game_name = re.sub(r'[^\x00-\x7F]+', '', game['name'].strip())

        if game_name is False:
            progress_bar.update(1)
            continue

        hltb_data = existing_data.get(appid, {})
        if not hltb_data:
            hltb_id, hltb_title, hltb_completionist_time = get_hltb_data(game_name)
        else:
            hltb_id = hltb_data.get('HLTB ID')
            hltb_title = hltb_data.get('HLTB Title')
            hltb_completionist_time = hltb_data.get('HLTB Completionist Time')

        achievements = get_game_achievement_data(appid)

        if achievements is None:
            no_achievements.append(appid)
            progress_bar.update(1)
            continue

        rarest_achievement_percentage = get_rarest_achievement_percentage(achievements)
        has_completed = player_has_completed(steamid, appid)

        scraped_data.append({
            'AppID': appid,
            'Title': game_name,
            'Rarest Achievement %': rarest_achievement_percentage,
            'Completed': has_completed,
            'HLTB ID': hltb_id,
            'HLTB Title': hltb_title,
            'HLTB Completionist Time': hltb_completionist_time
        })

        progress_bar.update(1)

    return scraped_data, sorted(no_achievements)


def resolve_vanity_url(vanity):
    """
    Resolve a Steam vanity URL to retrieve the associated SteamID.

    Args:
        vanity (str): The custom vanity URL identifier from Steam.

    Returns:
        str: The SteamID associated with the provided vanity URL.

    Raises:
        ValueError: If resolution fails.
    """
    try:
        steam_id = str(sid.steam64_from_url(f'https://steamcommunity.com/id/{vanity}'))
        if steam_id:
            return steam_id
        raise ValueError("Resolution of vanity URL failed.")
    except Exception as _e:
        print(f"Error resolving vanity URL: {_e}")
        sys.exit(1)
