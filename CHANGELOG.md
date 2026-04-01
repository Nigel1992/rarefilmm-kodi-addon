# Changelog

## [Unreleased]

### Added
- Settings: `use_cache` (index caching), `cache_ttl` (minutes), `page_size` (items per page), `fetch_metadata` (toggle to fetch metadata), and `user_agent` (HTTP User-Agent).
- Local caching for index entries (writes `index_cache.json`).
- `CHANGELOG.md` and `LICENSE` (MIT) added to the project.
- `.gitignore` to exclude build artifacts and temporary files.

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
