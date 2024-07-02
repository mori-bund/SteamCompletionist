# Steam Completionist

The Steam Completionist project is a command line tool designed to scrape Steam user libraries to find and manage rarest achievements, update achievement data, and maintain a list of games without achievements. It pulls data from How Long to Beat (HLTB) to provide completionist time data for games.

## Features

- **Steam API Integration**: Retrieves owned games, scrapes achievement data, checks completion status, and resolves vanity URLs.
- **HLTB Data Integration**: Retrieves completionist time data for games from How Long to Beat.
- **File Handling**: Saves scraped data to JSON files, manages lists of games without achievements and a master list of Steam-to-HLTB mappings (very much a work in progress).
- **Command-Line Interface**: Supports command-line options for specifying SteamID, vanity URLs, and updating no-achievement game lists.

## Prerequisites

Before using the script, make sure you have the following:

- Python 3.x installed on your system.
- Steam API Key (available from the [Steam Developer website](https://steamcommunity.com/dev/apikey)).
- [Steam ID](https://help.steampowered.com/en/faqs/view/2816-BE67-5B69-0FEC) of the user you want to scrape. There is a command line option to scan any ID (including a vanity ID) as well. **The Steam community profile MUST be public for this to work.**

## Usage

To use the script, follow these steps:

1. Clone the repository.

2. Install the required Python packages:

   ```shell
   pip install -r requirements.txt
   ```

3. Set up your Steam API Key:

   - Obtain your API Key from the [Steam Developer website](https://steamcommunity.com/dev/apikey) if you don't already have one.
   - Rename `con_fig.py` to `config.py` in the project directory (remove the underscore).
   - Add your API Key and [Steam ID](https://help.steampowered.com/en/faqs/view/2816-BE67-5B69-0FEC) to the `config.py` file:

     ```python
     # config.py
     API_KEY = 'your_api_key_here'
     STEAM_ID = 'your_steam_id_here'
     ```

4. Run the script:

   ```shell
   python src/main.py [-s STEAMID] [-v VANITY] [-u] [-m] [-r] [-p]
   ```

   - Use the `-s` option to specify a SteamID to scrape (optional). This will scrape it instead of the one in your `config.py` file.
   - Use the `-v` option to specify a Steam Vanity URL to scrape (optional). This will resolve the vanity url to a SteamID and scrape that library instead of the one in your `config.py` file.
   - Use the `-u` option to check and update the list of games with no achievements (optional). Any scanned game that doesn't have achievements is added to the `no_achievements.txt` file so the scraper knows to not bother checking those. This options rescans this list and removes the appID of any game that now has achievements. 
   - Use the `-m` option to update the `steam_hltb_map.json` file with new Steam IDs from user JSON files.
   - Use the `-r` option to sort the `steam_hltb_map.json` file by AppID.
   - Use the `-p` option to update the rarest achievement percentage for every game in `steam_hltb_map.json`

## Output

The script will generate a JSON file containing the scraped data in a `data` directory. Each JSON file corresponds to a Steam user's library and is sorted in descending order by the rarest achievement.

## Notes

* Please let me know if you find any bugs! I am a complete amateur and just barely know what I'm doing, but I am aware this script is not optimized at all.
* Large libraries will take a longer time to scrape the first time it is run. My 3000+ game library takes over 20 minutes to fully scrape.
* Rescanning games without achievements will also take a long time since there are well over 10,000 games in the list.
* If you scan a library that already has a JSON file saved, it will skip games already saved in the file. The script does NOT update the 100% status of a game when scanning again. I may add this functionality later.
* Steam allows some granularity with making the profile private. I probably didn't catch every nuance of this. The script will close if the profile is totally locked down, and the script will return all data except completion status if achievement data is locked down.
* Finding games by title with HLTB is a bit lackluster. I plan on improving this feature... eventually...