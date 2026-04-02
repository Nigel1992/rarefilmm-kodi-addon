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

- 🎬 **Browse** the full RareFilmm index (2900+ movies)
- ⚙️ **Customizable items per page** in settings
- 🔎 **Search** for movies by title
- 🖼️ **Movie posters & plots** (from site OpenGraph tags)
- ▶️ **Direct playback** (just press Enter)
- 🌐 **OK.ru & HLS** stream extraction
- ⚡ **Lightning-fast loading** with parallel fetching and caching
- 📊 **Live progress notifications** during initial index caching
- 🧩 **Kodi 19/20+** compatible (Python 3)

---

## 🚀 Performance

### v1.2.0 (Current)
- ⚡ **Initial index load: 2-5 seconds** (32x parallel page fetching)
- 📱 **Live progress dialog** showing pages downloaded and movie count
- 🎯 **Accurate progress tracking** that updates continuously
- ✅ **Cached loads: <1ms** on repeat visits

### v1.1.0
- 📥 **Metadata fetching: 8-9 seconds** for 100+ items (28-worker parallel)
- 💾 **Full pagination support** automatically fetches all 2900+ movies
- 🗜️ **Gzip compression support** for faster downloads
- 🔗 **HTTP connection pooling** for persistent connections

---

## � Installation

1. **[Download the latest ZIP](https://github.com/Nigel1992/rarefilmm-kodi-addon/releases/latest)**
2. In Kodi: `Add-ons` → `Install from zip file` → select the ZIP
3. Open the "RareFilmm" addon and enjoy!

---

## 🛠️ Usage

- **Browse:** Use page navigation to explore movies
- **Search:** Use the "Search RareFilmm" entry to find movies by title
- **Play:** Select a movie and press Enter to play
- **Progress:** Watch the live progress dialog during initial index caching (v1.2.0+)

---

## ⚙️ Settings

- `use_cache` - Enable/disable local index caching (recommended: ON)
- `cache_ttl` - Cache time-to-live in minutes (default: 60)
- `page_size` - Movies per page (default: 50)
- `fetch_metadata` - Fetch movie posters and plots (slower but prettier)
- `user_agent` - Custom HTTP User-Agent string
- `preferred_stream` - Preferred stream type: auto/hls/mp4
- `show_notifications` - Show Kodi notifications
- `open_in_external` - Open links in external player

---

## 🧩 Core Functions

- `get_index_entries(force_refresh=False)`: Fetch and parse all index entries with parallel page loading. Uses local cache (`index_cache.json`) respecting `cache_ttl`. Returns list of movie dicts.
- `parse_index(html_text)`: Parse RareFilmm index HTML and extract movie titles, links, and display snippets.
- `fetch_movie_metadata(movie_url)`: Fetch `og:image` and `og:description` from page. Optional, respects `fetch_metadata` setting.
- `fetch_multiple_metadata(urls, max_workers=28)`: Parallel metadata fetching for multiple movies. Returns dict mapping URLs to metadata.
- `find_direct_links(page_html, base)`: Extract playable URLs (m3u8, mp4, etc.) from movie pages. Scans source tags, JSON, scripts, and iframes.
- `list_movies(page=1, force_refresh=False)`: Display paginated movie list with optional metadata and navigation.
- `search_movies(query=None)`: Search cache by movie title.
- `play_movie(url)`: Resolve and play a movie, reordering streams per `preferred_stream` setting.

---

## 📦 Requirements

- Kodi 19 (Matrix) or newer
- Python 3.x
- Internet connection for streaming

---

## 📄 License

GPL-2.0-only

---

## 📝 Version History

### v1.2.0 (Latest) - April 2, 2026
- **32x parallel page fetching** for index (4-8x faster initial load)
- **Live progress notifications** during caching with accurate percentage
- Initial index load reduced from 30+ seconds to 2-5 seconds
- Non-blocking background dialog for better UX
- HTTP timeout reduced to 10s per page

### v1.1.0 - April 2, 2026
- **28-worker parallel metadata fetching** (8-9 seconds for 100+ items)
- Gzip decompression for HTTP responses
- Batch cache writes for efficiency
- HTTP connection pooling
- Full pagination support (2900+ movies auto-fetch)
- Metadata caching with `metadata_cache.json`

---

<p align="center">
  <i>Maintained by Nigel1992. Not affiliated with rarefilmm.com.</i>
</p>
