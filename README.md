<p align="center">
  <img src="https://raw.githubusercontent.com/Nigel1992/rarefilmm-kodi-addon/master/icon.png" width="300" alt="RareFilmm Logo"/>
</p>

<h1 align="center">RareFilmm Kodi Addon</h1>

<p align="center">
  <b>Browse, search, and play rare movies from <a href="https://rarefilmm.com">rarefilmm.com</a> directly in Kodi!</b><br>
  <a href="https://github.com/Nigel1992/rarefilmm-kodi-addon/releases/latest"><img src="https://img.shields.io/github/v/release/Nigel1992/rarefilmm-kodi-addon?label=Release" alt="Release"></a>
  <a href="CHANGELOG.md"><img src="https://img.shields.io/badge/Changelog-View-orange" alt="Changelog"></a>
  <img src="https://img.shields.io/badge/Kodi-19%2B-blue" alt="Kodi 19+">
  <img src="https://img.shields.io/badge/Python-3.x-blue" alt="Python 3">
</p>

---

## ✨ Features

- 🎬 **Browse** the full RareFilmm index
- ⚙️ **Customizable items per page** in settings
- 🔎 **Search** for movies by title
- 🖼️ **Movie posters & plots** (from site OpenGraph tags)
- ▶️ **Direct playback** (just press Enter)
- 🌐 **OK.ru & HLS** stream extraction
- 🧩 **Kodi 19/20+** compatible (Python 3)

---

> ✅ **Performance v1.1.0:** Index loads from cache in <1ms on repeat visits. Fresh metadata fetching for 100+ items with parallel workers completes in 8-9 seconds. Full index (2900+ movies) fetches automatically on first startup.

---

## 🚀 Quick Start

1. **[Download the latest ZIP](https://github.com/Nigel1992/rarefilmm-kodi-addon/releases/latest)**
2. In Kodi: `Add-ons` → `Install from zip file` → select the ZIP
3. Open the "RareFilmm" addon and enjoy!

---

## 🛠️ Usage

- **Browse:** Use page navigation to explore movies
- **Search:** Use the "Search RareFilmm" entry to find movies by title
- **Play:** Select a movie and press Enter to play

---

## 🧩 Functions

- `load_settings()`: Load addon settings into `SETTINGS` and apply `PAGE_SIZE` and `USER_AGENT`. Settings include `use_cache`, `cache_ttl`, `page_size`, `user_agent`, `fetch_metadata`, `preferred_stream`, `show_notifications`, and `open_in_external`.
- `get_index_entries(force_refresh=False)`: Return parsed index entries; uses a local cache (`index_cache.json`) when `use_cache` is enabled and respects `cache_ttl` (minutes). Pass `force_refresh=True` to bypass the cache and refresh from the site.
- `parse_index(html_text)`: Parse the RareFilmm index HTML and return a list of entry dicts with `title`, `href`, and an `html` snippet used for display.
- `find_direct_links(page_html, base)`: Extract direct playable URLs (m3u8, mp4, etc.) from the page HTML. Scans `<source>` tags, absolute/protocol-relative URLs, inline JSON/scripts (including OK.ru payloads), iframes (fetched and scanned), and returns a cleaned, deduplicated list of URLs.
- `fetch_movie_metadata(movie_url)`: Fetch `og:image` and `og:description` from a movie page and return `{'image', 'description'}`. This is optional and slower; enabled via the `fetch_metadata` setting.
- `list_movies(page=1, force_refresh=False)`: Display a paginated list of movies using `PAGE_SIZE` (from settings). Adds Search/Settings/Refresh entries, provides previous/next navigation, and optionally fetches metadata per item.
- `search_movies(query=None)`: Prompt for a search query (if `query` is None), search cached index titles, and present matching movies for playback.
- `play_movie(url)`: Resolve playable links for a movie page using `find_direct_links`. Reorders links per the `preferred_stream` setting (`auto`, `hls`, `mp4`), allows selection when multiple streams are found, and hands the final URL to Kodi for playback.
- `build_url(query)`: Helper to build plugin URLs for internal navigation.
- `router(paramstring)`: Main entrypoint that dispatches actions (`list`, `play`, `search`, `settings`) based on plugin query parameters.

---

## 📦 Requirements

- Kodi 19 (Matrix) or newer
- Python 3

---

## 📄 License

MIT

---

## 📝 Recent changes (since commit f944800)

- Added settings: `use_cache` (index caching), `cache_ttl` (minutes), `page_size` (items per page), `fetch_metadata` (toggle to fetch metadata), and `user_agent` (HTTP User-Agent).
- Implemented local caching for index entries (`index_cache.json`).
- Added `LICENSE` (MIT) and `.gitignore`.
- Removed `__pycache__` directory.
- Documentation updates: logo size, image URL, and note about slow loading of movie lists.

---

<p align="center">
  <i>Maintained by Nigel1992. Not affiliated with rarefilmm.com.</i>
</p>
