<p align="center">
  <img src="https://raw.githubusercontent.com/Nigel1992/rarefilmm-kodi-addon/main/icon.png" width="120" alt="RareFilmm Logo"/>
</p>

<h1 align="center">RareFilmm Kodi Addon</h1>

<p align="center">
  <b>Browse, search, and play rare movies from <a href="https://rarefilmm.com">rarefilmm.com</a> directly in Kodi!</b><br>
  <a href="https://github.com/Nigel1992/rarefilmm-kodi-addon/releases/latest"><img src="https://img.shields.io/github/v/release/Nigel1992/rarefilmm-kodi-addon?label=Release" alt="Release"></a>
  <img src="https://img.shields.io/badge/Kodi-19%2B-blue" alt="Kodi 19+">
  <img src="https://img.shields.io/badge/Python-3.x-blue" alt="Python 3">
</p>

---

## ✨ Features

- 🎬 **Browse** the full RareFilmm index (50 movies per page)
- 🔎 **Search** for movies by title
- 🖼️ **Movie posters & plots** (from site OpenGraph tags)
- ▶️ **Direct playback** (just press Enter)
- 🌐 **OK.ru & HLS** stream extraction
- 🧩 **Kodi 19/20+** compatible (Python 3)

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

<p align="center">
  <i>Maintained by Nigel1992. Not affiliated with rarefilmm.com.</i>
</p>
