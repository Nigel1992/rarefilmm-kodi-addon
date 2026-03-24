
# RareFilmm Kodi Addon

A Kodi video plugin for browsing and playing movies from [rarefilmm.com](https://rarefilmm.com).

## Features
- Browse the full RareFilmm index, paginated (50 movies per page)
- Search for movies by title (case-insensitive)
- Displays movie poster and plot (from the site's OpenGraph metadata)
- Direct playback: press Enter to play a movie (no right-click needed)
- Extracts and plays raw HLS manifests (including OK.ru embeds)
- Kodi 19/20+ compatible (Python 3)

## Usage
1. **Install**: Use the provided ZIP or copy the folder to your Kodi addons directory.
2. **Browse**: Open the "RareFilmm" addon in Kodi. Use page navigation to browse movies.
3. **Search**: Use the "Search RareFilmm" entry to find movies by title.
4. **Play**: Select a movie and press Enter to play. The addon resolves the best available stream.

## Functions
- `list_movies(page=1)`: Shows 50 movies per page, with art and plot.
- `search_movies(query)`: Prompts for a search term, lists matching movies, and allows direct playback.
- `play_movie(url)`: Resolves and plays the best available stream for a movie page.
- `fetch_movie_metadata(url)`: Extracts poster and plot from the movie page's OpenGraph tags.
- `find_direct_links(page_html, base)`: Finds playable video URLs, including OK.ru and HLS manifests.

## Installation
### Method 1: Kodi ZIP Install
1. Download the latest `plugin.video.rarefilmm-1.0.0.zip` from the [releases](https://github.com/YOUR_GITHUB_USER/rarefilmm-kodi-addon/releases).
2. In Kodi: **Add-ons > Install from zip file** and select the downloaded ZIP.

### Method 2: Manual
- Copy the `plugin.video.rarefilmm` folder to your Kodi `addons` directory (e.g. `~/.kodi/addons/`).

## Requirements
- Kodi 19 (Matrix) or newer
- Python 3

## License
MIT

---
Maintained by Nigel1992. Not affiliated with rarefilmm.com.
