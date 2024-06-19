# Steam Completionist

Steam Completionist is a Python script designed to scrape and analyze Steam user libraries to find games with the easiest achievements to complete. It retrieves information about owned games, their rarest achievements, and the completion status of each game.

## Features

- Retrieve a list of games owned by a Steam user.
- Identify the rarest achievement in each game based on global achievement percentages.
- Determine whether the user has completed all achievements for a game.
- Option to rescan games with no achievements and update the list accordingly.

## Prerequisites

Before using the script, ensure you have the following:

- Python 3.x installed on your system.
- Steam API Key obtained from the [Steam Developer website](https://steamcommunity.com/dev/apikey).
- [Steam ID](https://help.steampowered.com/en/faqs/view/2816-BE67-5B69-0FEC) of the user you want to scrape. Note that the Steam community profile must be public for the script to work.

## Installation

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/your_username/steam-completionist.git
   cd steam-completionist
   ```

2. Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up your Steam API Key:

   - Obtain your API Key from the [Steam Developer website](https://steamcommunity.com/dev/apikey) if you haven't already.
   - Rename `con_fig.py` to `config.py`.
   - Add your API Key and Steam ID to `config.py`:

     ```python
     # config.py
     API_KEY = 'your_api_key_here'
     STEAM_ID = 'your_steam_id_here'
     ```

## Usage

Run the script using the following command:

```bash
python main.py [-s STEAMID] [-v VANITY] [-u]
```

- Use `-s STEAMID` to specify a SteamID to scrape (optional). This overrides the Steam ID in your `config.py`.
- Use `-v VANITY` to specify a Steam Vanity URL to scrape (optional). The vanity URL is converted to a SteamID for scraping.
- Use `-u` to check and update the list of games with no achievements (optional). Games without achievements are added to `no_achievements.json`.

## Output

The script generates CSV files containing scraped data in the `data` directory. Each file corresponds to a Steam user's library and is sorted by the rarest achievement column in descending order.

## Notes

- This script is developed for personal use and may require further optimization.
- Scanning large libraries or updating games without achievements may take considerable time.
- Profile privacy settings on Steam can affect data retrieval. The script handles partially private profiles by omitting completion status if necessary.
- Future updates may include integration with HowLongToBeat for game completion time estimates.

---

Feel free to adjust the details based on any specific instructions or additional notes you have for users of your script. This README should provide a comprehensive overview of your project's purpose, usage, and installation steps.