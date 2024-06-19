# steam_utils.py
"""
Utility functions to interact with Steam API in Steam Completionist project.

This module provides functions to retrieve owned games, scrape achievement data,
check completion status, resolve vanity URLs, and handle Steam API interactions.

Functions:
    - get_owned_games(steamid): Retrieve list of games owned by a Steam user.
    - get_game_achievement_data(appid): Retrieve achievement data for a specific game.
    - get_rarest_achievement_percentage(data): Get percentage of rarest achievement.
    - player_has_completed(steamid, appid): Check if user has completed all achievements.
    - scrape_steam_data(steamid, new_games, progress_bar): Scrape data for owned games.
    - resolve_vanity_url(vanity): Resolve Steam vanity URL to SteamID.

Dependencies:
    - requests              Library for making HTTP requests.
    - steam.webapi          Library for accessing Steam Web API.
    - steam.steamid         Library for handling Steam IDs.
    - config.py             Configuration file for API keys and IDs.
"""

import sys
import requests
from steam.webapi import WebAPI
from steam import steamid as sid
from hltb_utils import get_hltb_data
from config import API_KEY

api = WebAPI(key=API_KEY)

def get_owned_games(steamid):
    """
    Retrieve the list of games owned by a Steam user.
    Setting skip_unvetted_apps to false will find profile limited games.

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
        list: A list of achievement data dictionaries for the game, or None if there are none.
              Each dictionary contains information about an achievement.
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
    Check if a user has completed all achievements for a game. If the user's
    profile has this data private, then the Completed column will be empty.

    Args:
        steamid (str): The SteamID of the user.
        appid (int): The Steam AppID of the game.

    Returns:
        bool or None:
            - True if the user has completed all achievements.
            - False if the user has not completed all achievements or
              if data is private.
            - None if there's an issue retrieving the data.
    """
    try:
        player_data = api.ISteamUserStats.GetPlayerAchievements(
            steamid=steamid, appid=appid)
    except requests.exceptions.HTTPError as _e:
        return None

    achievements = player_data['playerstats']['achievements']

    return all(achievement.get('achieved', False) for achievement in achievements)


def scrape_steam_data(steamid, new_games, progress_bar):
    """
    Scrape data for each game in a user's library to get the appid, title,
    rarest achievement, and completion status. If a game is determined to
    not have achievements, it will be added to a text file so it doesn't
    get scraped in the future.

    Args:
        steamid (str): The SteamID of the user.
        new_games (list): List of games owned by the user that haven't been scraped yet.
        progress_bar (tqdm.tqdm): Progress bar for tracking progress.

    Returns:
        tuple: A tuple containing scraped data list and a list of appids with no achievements.
    """
    scraped_data, no_achievements = [], []

    for game in new_games:
        appid = game['appid']
        game_name = game['name'].strip()

        if game_name is False:
            progress_bar.update(1)
            continue

        achievements = get_game_achievement_data(appid)
        hltb_id, hltb_completionist_time = get_hltb_data(game_name)

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
            'HLTB Completionist Time': hltb_completionist_time
        })

        progress_bar.update(1)

    return scraped_data, sorted(no_achievements)


def resolve_vanity_url(vanity):
    """
    Resolves a Steam vanity URL to retrieve the associated SteamID.

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
    except requests.exceptions.RequestException as error:
        print(f"Error resolving vanity URL: {error}")
        sys.exit(1)
