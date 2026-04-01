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

> ⚠️ **Note:** Loading the movie lists is currently slow, as the full index is processed on each load. This will be improved in a future update for faster browsing.

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

- `list_movies(page=1)`: Shows 50 movies per page, with art and plot
- `search_movies(query)`: Prompts for a search term, lists matching movies, and allows direct playback
- `play_movie(url)`: Resolves and plays the best available stream for a movie page
- `fetch_movie_metadata(url)`: Extracts poster and plot from the movie page's OpenGraph tags
- `find_direct_links(page_html, base)`: Finds playable video URLs, including OK.ru and HLS manifests

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
