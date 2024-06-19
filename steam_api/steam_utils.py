import requests
import re

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