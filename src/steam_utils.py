"""Module providing a way to interact with Steam's API"""

# steam_utils.pty
import sys
import requests
from steam.webapi import WebAPI
from steam import steamid as sid
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
        existing_appids (set): Set of existing Steam AppIDs already scraped previously.
        owned_games (list): List of games owned by the user.
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

        if achievements is None:
            no_achievements.append(appid)
            progress_bar.update(1)
            continue

        rarest_achievement_percentage = get_rarest_achievement_percentage(
            achievements)

        has_completed = player_has_completed(steamid, appid)

        scraped_data.append(
            [appid, game_name, rarest_achievement_percentage, has_completed])

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
    except Exception as e:
        print(f"Error resolving vanity URL: {e}")
        sys.exit(1)
