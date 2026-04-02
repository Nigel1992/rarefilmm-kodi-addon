# Changelog

## [1.2.2] - 2026-04-02

### Fixed
- **Debug Logging Path**: Fixed debug log file path to correctly write to `~/.kodi/userdata/addon_data/plugin.video.rarefilmm/debug.log` instead of addon directory
- **Directory Creation**: Ensured addon_data directory is automatically created if it doesn't exist
- **Error Logging**: Improved error reporting - debug errors now logged to Kodi's log file for visibility

## [1.2.1] - 2026-04-02

### Added
- **Comprehensive debug logging**: New debug mode that logs all addon operations to a file
  - All HTTP requests and responses with error handling
  - Index fetching with cache operations and entry counts
  - Movie playback with link extraction details and stream selection
  - Search operations with match counts
  - Metadata fetching with cache hit rates
  - User navigation and page visits
- **Debug toggle in settings**: New "Debug" category with "Enable debug logging" option (disabled by default)
- **Structured logging**: Timestamped log entries with severity levels (INFO, DEBUG, WARNING, ERROR)
- **Log file location**: `userdata/addon_data/plugin.video.rarefilmm/debug.log`

### Features
- Zero performance impact when debug mode is disabled
- Detailed operational insights when enabled for troubleshooting
- Automatic log file creation and directory management
- Comprehensive link extraction logging for iframe/stream URL detection

## [1.2.0] - 2026-04-02

### Added
- **Parallel page fetching**: Index downloads now fetch 32 pages simultaneously (4-8x faster than sequential loading)
- **Live progress notifications**: Real-time progress dialog during cache indexing showing downloaded pages and movie count
- Accurate progress percentage that continuously updates without stalling

### Changed
- Index fetching refactored to use `ThreadPoolExecutor` with 32 concurrent workers for massive speed boost
- HTTP timeout reduced from 15s to 10s per page for faster failure detection
- Progress updates display as "Pages: X | Movies: Y" instead of separate messages

### Performance
- Initial index load reduced from 30+ seconds to 2-5 seconds (4-8x faster)
- Parallel page requests eliminate sequential bottleneck
- Non-blocking progress dialog allows UI responsiveness during caching

## [1.1.0] - 2026-04-02

### Added
- **Performance optimization**: 28-worker parallel metadata fetching (8-9 seconds for 100 items vs 80+ seconds before)
- Gzip decompression for HTTP responses
- Batch cache writes (1 write per page load instead of 100+ individual writes)
- HTTP connection pooling for reusable connections
- Full pagination support for index fetching (automatically grabs all 2900+ movies on first load)
- Improved regex patterns for metadata extraction (handles og:image/og:description with both property and name attributes)
- Metadata caching (`metadata_cache.json`) for instant retrieval
- Settings: `use_cache` (index caching), `cache_ttl` (minutes), `page_size` (items per page), `fetch_metadata` (toggle to fetch metadata), and `user_agent` (HTTP User-Agent).
- Local caching for index entries (writes `index_cache.json`).
- `CHANGELOG.md` and `LICENSE` (GPL-2.0-only) added to the project.
- `.gitignore` to exclude build artifacts and temporary files.

### Changed
- Metadata fetching now uses 28 parallel workers for optimal throughput
- Index fetching now supports full pagination to grab all 2900+ movies automatically
- Settings loading now properly initializes at module import time
- Updated README with performance improvements

### Fixed
- Fixed gzip-compressed HTML responses not being decompressed
- Fixed settings not being loaded from addon configuration
- Fixed metadata extraction failing on meta tags with both property and name attributes
- Fixed metadata not being scraped even when enabled in settings

### Changed
- Documentation updates: README improvements (logo size, image URL), and a note about slow loading of movie lists.

### Removed
- Removed `__pycache__` directory from the repository.

### Commits
- `7b9de85` — Add settings for cache, metadata fetching, and user agent; implement local caching for index entries (2026-04-01)
- `f2e11a3` — Update logo size in README.md (2026-03-24)
- `7770087` — Add .gitignore file to exclude unnecessary files and directories (2026-03-24)
- `46cc5db` — Delete __pycache__ directory (2026-03-24)
- `25ed05b` — Add note about slow loading of movie lists in README.md (2026-03-24)
- `d48ac7a` — Add MIT License to the project (2026-03-24)
- `5a3c1c7` — Update image URL in README.md from main to master (2026-03-24)
- `685a7a7` — Update README.md (2026-03-24)
