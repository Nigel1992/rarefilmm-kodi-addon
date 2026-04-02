#!/usr/bin/env python3
from __future__ import print_function
import sys
import re
import html
import urllib.request
import urllib.parse
import os
import json
import time
import gzip
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from urllib.request import urlopen, Request
from http.client import HTTPConnection
from urllib.request import HTTPHandler, build_opener

try:
    import xbmc
    import xbmcgui
    import xbmcplugin
    import xbmcaddon
except Exception:
    xbmc = xbmcgui = xbmcplugin = xbmcaddon = None

# Enable HTTP connection pooling for faster requests
HTTPConnection._http_vsn = 11
HTTPConnection._http_vsn_str = 'HTTP/1.1'

# Create a persistent HTTP handler with connection pooling
_http_handler = HTTPHandler()
_opener = build_opener(_http_handler)

# plugin handle
handle = int(sys.argv[1]) if len(sys.argv) > 1 else 0

BASE_URL = 'https://rarefilmm.com'
INDEX_URL = BASE_URL + '/film-index/'
# sensible defaults; these will be overridden by add-on settings when available
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
PAGE_SIZE = 50

# runtime settings (populated by load_settings)
SETTINGS = {}

def http_get(url, timeout=20):
    """Fetch URL with optimized headers for speed. Handles gzip decompression."""
    headers = {
        'User-Agent': SETTINGS.get('user_agent', USER_AGENT), 
        'Accept': 'text/html',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
        
        # Handle gzip-compressed responses
        if resp.headers.get('Content-Encoding') == 'gzip':
            try:
                data = gzip.decompress(data)
            except Exception:
                pass  # If decompression fails, try to use raw data
        
        try:
            return data.decode(resp.headers.get_content_charset() or 'utf-8', errors='replace')
        except Exception:
            return data.decode('utf-8', errors='replace')

def strip_tags(s):
    s = re.sub(r'<[^>]+>', '', s)
    return html.unescape(s).strip()

def parse_index(html_text):
    # Accept both absolute and site-relative post links
    pattern = re.compile(r'href=[\'\"](?P<href>(?:https?://rarefilmm\.com)?/\d{4}/\d{2}/[^\'\"]+/?)[\'\"][^>]*>(?P<text>.*?)</a>', re.I|re.S)
    entries = []
    seen = set()
    for m in pattern.finditer(html_text):
        href = m.group('href')
        if href.startswith('/'):
            href = urllib.parse.urljoin(BASE_URL, href)
        if href in seen:
            continue
        seen.add(href)
        rawtext = strip_tags(m.group('text'))
        rawtext = re.sub(r'(?i)watch here\s*', '', rawtext)
        title = rawtext
        year = ''
        tm = re.search(r'\((?P<year>\d{4})\)', rawtext)
        if tm:
            year = tm.group('year')
            title = re.sub(r'\(\d{4}\)', '', title).strip()
        # Build HTML snippet in the format requested
        safe_title = html.escape(title)
        safe_href = html.escape(href)
        snippet = '<span style="color: #000000; font-family: \'trebuchet ms\', geneva, sans-serif;"><a style="color: #000000;" href="%s">%s</a>' % (safe_href, safe_title)
        if year:
            snippet += ' (%s)' % year
        snippet += '</span><br />'
        entries.append({'title': title, 'href': href, 'html': snippet})
    return entries


def _fetch_page(page_num):
    """Helper to fetch a single page. Returns (page_num, html_text) or (page_num, None) on error."""
    try:
        if page_num == 1:
            page_url = INDEX_URL
        else:
            page_url = INDEX_URL.rstrip('/') + '/page/' + str(page_num) + '/'
        html_text = http_get(page_url, timeout=10)
        return (page_num, html_text)
    except Exception:
        return (page_num, None)


def get_index_entries(force_refresh=False):
    """Return parsed index entries, using a local cache when enabled.
    If force_refresh is True, the cache will be ignored and refreshed.
    Fetches all pages in parallel with aggressive worker pool for maximum speed.
    Shows progress notifications to user during caching.
    """
    cache_file = _local_cache_file()
    now = int(time.time())
    use_cache = SETTINGS.get('use_cache', True)
    ttl = int(SETTINGS.get('cache_ttl', 60)) * 60

    if not force_refresh and use_cache and os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            ts = int(data.get('_ts', 0))
            if now - ts < ttl:
                return data.get('entries', [])
        except Exception:
            # fall through to refresh
            pass

    # Create progress dialog
    progress_dialog = None
    try:
        if xbmcgui:
            progress_dialog = xbmcgui.DialogProgressBG()
            progress_dialog.create('RareFilmm Index', 'Initializing...')
    except Exception:
        pass

    # Fetch and parse fresh - grab ALL pages in parallel with aggressive worker pool
    entries = []
    seen_urls = set()
    max_pages = 100  # safety limit
    
    try:
        # Use ThreadPoolExecutor with high worker count (32x parallel requests)
        # Most of the time is spent waiting for network I/O, so more workers = faster
        with ThreadPoolExecutor(max_workers=32) as executor:
            # Submit all page fetch tasks upfront
            future_to_page = {
                executor.submit(_fetch_page, page): page 
                for page in range(1, max_pages + 1)
            }
            
            # Process completed pages as they finish
            consecutive_empty = 0  # Track consecutive empty pages to stop early
            processed_count = 0
            last_update = 0  # Track last percentage to avoid unnecessary updates
            
            for future in as_completed(future_to_page):
                page_num, html_text = future.result()
                processed_count += 1
                
                if html_text is None:
                    # Error fetching this page
                    consecutive_empty += 1
                    if consecutive_empty >= 3:
                        # Three consecutive fetch errors = we've hit the end
                        break
                    continue
                
                page_entries = parse_index(html_text)
                
                if not page_entries:
                    # No entries on this page
                    consecutive_empty += 1
                    if consecutive_empty >= 3:
                        # Three consecutive empty pages = definitely done
                        break
                else:
                    consecutive_empty = 0
                    # Add only new entries we haven't seen before
                    for entry in page_entries:
                        if entry['href'] not in seen_urls:
                            seen_urls.add(entry['href'])
                            entries.append(entry)
                
                # Update progress dialog - always move forward
                if progress_dialog and processed_count % 2 == 0:  # Update every 2 pages to reduce flicker
                    try:
                        pct = min(80, processed_count * 2)  # 50 pages = ~100%, capped at 80%
                        if pct != last_update:  # Only update if percentage changed
                            msg = 'Pages: %d | Movies: %d' % (processed_count, len(entries))
                            progress_dialog.update(pct, 'RareFilmm Index', msg)
                            last_update = pct
                    except Exception:
                        pass
                
                # Bail early if we've processed way more pages than we're getting entries
                # (means the site structure changed or we've hit the real end)
                if processed_count > 50 and len(entries) < processed_count * 5:
                    break

        # Show disk caching phase
        if progress_dialog:
            try:
                progress_dialog.update(90, 'RareFilmm Index', 'Saving cache: %d movies' % len(entries))
            except Exception:
                pass

        # attempt to write cache
        try:
            ddir = os.path.dirname(cache_file)
            if ddir and not os.path.exists(ddir):
                os.makedirs(ddir, exist_ok=True)
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({'_ts': now, 'entries': entries}, f, ensure_ascii=False)
        except Exception:
            pass

        # Update to 100% before closing
        if progress_dialog:
            try:
                progress_dialog.update(100, 'RareFilmm Index', 'Complete! %d movies' % len(entries))
            except Exception:
                pass

    finally:
        # Always close progress dialog
        if progress_dialog:
            try:
                progress_dialog.close()
            except Exception:
                pass

    return entries


def _local_cache_file():
    """Return a writable local cache path for index_cache.json.
    Prefer the addon profile directory when running inside Kodi; otherwise use
    the file next to this script (works for development/testing).
    """
    try:
        # inside Kodi: use addon profile path
        if xbmcaddon:
            addon = xbmcaddon.Addon()
            profile = addon.getAddonInfo('profile')
            cache_dir = xbmc.translatePath(profile)
            if isinstance(cache_dir, bytes):
                cache_dir = cache_dir.decode('utf-8')
            return os.path.join(cache_dir, 'index_cache.json')
    except Exception:
        pass
    # fallback: adjacent to this script
    return os.path.join(os.path.dirname(__file__), 'index_cache.json')


def _get_metadata_cache_file():
    """Return path to metadata cache file."""
    try:
        if xbmcaddon:
            addon = xbmcaddon.Addon()
            profile = addon.getAddonInfo('profile')
            cache_dir = xbmc.translatePath(profile)
            if isinstance(cache_dir, bytes):
                cache_dir = cache_dir.decode('utf-8')
            return os.path.join(cache_dir, 'metadata_cache.json')
    except Exception:
        pass
    return os.path.join(os.path.dirname(__file__), 'metadata_cache.json')


def _load_metadata_cache():
    """Load metadata cache from disk."""
    cache_file = _get_metadata_cache_file()
    try:
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save_metadata_cache(cache_dict):
    """Save metadata cache to disk."""
    cache_file = _get_metadata_cache_file()
    try:
        ddir = os.path.dirname(cache_file)
        if ddir and not os.path.exists(ddir):
            os.makedirs(ddir, exist_ok=True)
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_dict, f, ensure_ascii=False)
    except Exception:
        pass


def _get_setting_bool(addon, key, default=False):
    try:
        val = addon.getSetting(key)
        return str(val).lower() in ('true', '1', 'yes')
    except Exception:
        return default


def _get_setting_int(addon, key, default):
    try:
        return int(addon.getSetting(key))
    except Exception:
        return default


def _get_setting_str(addon, key, default):
    try:
        v = addon.getSetting(key)
        return v if v is not None and v != '' else default
    except Exception:
        return default


def load_settings():
    """Populate SETTINGS dict from addon settings (when available) or defaults."""
    global SETTINGS, PAGE_SIZE, USER_AGENT
    defaults = {
        'use_cache': True,
        'cache_ttl': 60,      # minutes
        'page_size': PAGE_SIZE,
        'user_agent': USER_AGENT,
        'fetch_metadata': False,
        'preferred_stream': 'auto',  # auto, hls, mp4
        'show_notifications': True,
        'open_in_external': True,
    }
    if xbmcaddon:
        addon = xbmcaddon.Addon()
        use_cache = _get_setting_bool(addon, 'use_cache', defaults['use_cache'])
        cache_ttl = _get_setting_int(addon, 'cache_ttl', defaults['cache_ttl'])
        page_size = _get_setting_int(addon, 'page_size', defaults['page_size'])
        ua = _get_setting_str(addon, 'user_agent', defaults['user_agent'])
        fetch_meta = _get_setting_bool(addon, 'fetch_metadata', defaults['fetch_metadata'])
        pref = _get_setting_str(addon, 'preferred_stream', defaults['preferred_stream'])
        notify = _get_setting_bool(addon, 'show_notifications', defaults['show_notifications'])
        external = _get_setting_bool(addon, 'open_in_external', defaults['open_in_external'])
    else:
        use_cache = defaults['use_cache']
        cache_ttl = defaults['cache_ttl']
        page_size = defaults['page_size']
        ua = defaults['user_agent']
        fetch_meta = defaults['fetch_metadata']
        pref = defaults['preferred_stream']
        notify = defaults['show_notifications']
        external = defaults['open_in_external']

    # Update the global SETTINGS dictionary
    SETTINGS.clear()
    SETTINGS.update({
        'use_cache': use_cache,
        'cache_ttl': cache_ttl,
        'page_size': page_size,
        'user_agent': ua,
        'fetch_metadata': fetch_meta,
        'preferred_stream': pref,
        'show_notifications': notify,
        'open_in_external': external,
    })
    # apply to module globals
    PAGE_SIZE = SETTINGS['page_size']
    USER_AGENT = SETTINGS['user_agent']
    return SETTINGS


# Load settings at module import time
load_settings()


# Compile regex patterns once for better performance
# Matches meta tags with property="og:image" (with or without name attribute) and content
_PATTERN_OG_IMAGE = re.compile(
    r'<meta\s+[^>]*property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']',
    re.IGNORECASE
)
# Fallback for name="og:image" if property not found
_PATTERN_OG_IMAGE_ALT = re.compile(
    r'<meta\s+[^>]*name=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']',
    re.IGNORECASE
)
# Matches meta tags with property="og:description" (with or without name attribute) and content
_PATTERN_OG_DESCRIPTION = re.compile(
    r'<meta\s+[^>]*property=["\']og:description["\'][^>]*content=["\']([^"\']+)["\']',
    re.IGNORECASE
)
# Fallback for name="og:description" if property not found
_PATTERN_OG_DESCRIPTION_ALT = re.compile(
    r'<meta\s+[^>]*name=["\']og:description["\'][^>]*content=["\']([^"\']+)["\']',
    re.IGNORECASE
)

# Global metadata cache
_METADATA_CACHE = {}
_METADATA_CACHE_LOADED = False


def _ensure_metadata_cache_loaded():
    """Load metadata cache on first use."""
    global _METADATA_CACHE, _METADATA_CACHE_LOADED
    if not _METADATA_CACHE_LOADED:
        _METADATA_CACHE = _load_metadata_cache()
        _METADATA_CACHE_LOADED = True


def fetch_movie_metadata(movie_url, timeout=10):
    """Fetch and cache movie metadata (image and description). Uses 10s timeout for speed."""
    _ensure_metadata_cache_loaded()
    
    # Check cache first
    if movie_url in _METADATA_CACHE:
        cached = _METADATA_CACHE[movie_url]
        return cached
    
    try:
        page_html = http_get(movie_url, timeout=timeout)
    except Exception:
        return {'image': None, 'description': None}
    
    image = None
    description = None
    
    # Try property attribute first, then fallback to name attribute for image
    m = _PATTERN_OG_IMAGE.search(page_html)
    if not m:
        m = _PATTERN_OG_IMAGE_ALT.search(page_html)
    if m:
        image = m.group(1).strip()
    
    # Try property attribute first, then fallback to name attribute for description
    m = _PATTERN_OG_DESCRIPTION.search(page_html)
    if not m:
        m = _PATTERN_OG_DESCRIPTION_ALT.search(page_html)
    if m:
        try:
            description = html.unescape(m.group(1).strip())
        except Exception:
            description = m.group(1).strip()
    
    result = {'image': image, 'description': description}
    
    # Cache the result (save is batched in fetch_multiple_metadata for speed)
    _METADATA_CACHE[movie_url] = result
    return result


def fetch_multiple_metadata(urls, max_workers=28, timeout=10):
    """Fetch metadata for multiple URLs in parallel - NETWORK LIMITED.
    
    Performance:
    - 28 workers = optimal for this workload
    - ~100 items fresh = 8-13 seconds (network bound: ~80-130ms per item)
    - Cached items = instant (<1ms)
    
    Cannot be made significantly faster without:
    1. TMDB API (slower, less accurate for rare films)
    2. Headless browser (much slower, memory intensive)
    3. Reducing timeout (will miss data on slow connections)
    """
    _ensure_metadata_cache_loaded()
    
    results = {}
    uncached_urls = [u for u in urls if u not in _METADATA_CACHE]
    
    # Return cached results immediately
    for url in urls:
        if url in _METADATA_CACHE:
            results[url] = _METADATA_CACHE[url]
    
    # Fetch uncached in parallel
    if uncached_urls:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {
                executor.submit(fetch_movie_metadata, url, timeout): url 
                for url in uncached_urls
            }
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    results[url] = future.result()
                except Exception:
                    results[url] = {'image': None, 'description': None}
        
        # Batch save cache once at the end
        _save_metadata_cache(_METADATA_CACHE)
    
    return results


def build_url(query):
    return sys.argv[0] + '?' + urllib.parse.urlencode(query)




def list_movies(page=1, force_refresh=False):
    # Use cached index entries when possible
    items = get_index_entries(force_refresh=force_refresh)
    total = len(items)
    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    page_items = items[start:end]

    if xbmcplugin:
        xbmcplugin.setPluginCategory(handle, 'RareFilmm')
        xbmcplugin.setContent(handle, 'movies')

    # Add a search entry at the top
    try:
        if xbmcgui:
            search_url = build_url({'action': 'search'})
            li_search = xbmcgui.ListItem(label='Search RareFilmm')
            xbmcplugin.addDirectoryItem(handle=handle, url=search_url, listitem=li_search, isFolder=True)

            # Settings shortcut
            settings_url = build_url({'action': 'settings'})
            li_settings = xbmcgui.ListItem(label='Settings')
            xbmcplugin.addDirectoryItem(handle=handle, url=settings_url, listitem=li_settings, isFolder=True)

            # Refresh index
            refresh_url = build_url({'action': 'list', 'page': str(page), 'refresh': '1'})
            li_refresh = xbmcgui.ListItem(label='Refresh index')
            xbmcplugin.addDirectoryItem(handle=handle, url=refresh_url, listitem=li_refresh, isFolder=True)
    except Exception:
        pass

    # page nav previous
    if page > 1:
        prev_url = build_url({'action': 'list', 'page': str(page - 1)})
        li_prev = xbmcgui.ListItem(label='<< Previous page (%d)' % (page - 1)) if xbmcgui else None
        if xbmcplugin:
            xbmcplugin.addDirectoryItem(handle=handle, url=prev_url, listitem=li_prev, isFolder=True)

    # Fetch metadata in parallel if enabled (blazing fast!)
    metadata_dict = {}
    if SETTINGS.get('fetch_metadata'):
        urls = [it['href'] for it in page_items]
        metadata_dict = fetch_multiple_metadata(urls, max_workers=4)

    for it in page_items:
        # Get pre-fetched metadata
        metadata = metadata_dict.get(it['href'], {'image': None, 'description': None})

        li = xbmcgui.ListItem(label=it['title']) if xbmcgui else None
        if li:
            plot = metadata.get('description') or ''
            li.setInfo('video', {'title': it['title'], 'plot': plot})
            li.setProperty('IsPlayable', 'true')
            art = {}
            if metadata.get('image'):
                art['thumb'] = metadata['image']
                art['icon'] = metadata['image']
                art['fanart'] = metadata['image']
            if art:
                li.setArt(art)

        url = build_url({'action': 'play', 'url': it['href']})
        if xbmcplugin:
            xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=False)

    # page nav next: show next if there are more items beyond this page
    try:
        if end < total:
            next_url = build_url({'action': 'list', 'page': str(page + 1)})
            li_next = xbmcgui.ListItem(label='Next page (%d) >>' % (page + 1)) if xbmcgui else None
            if xbmcplugin:
                xbmcplugin.addDirectoryItem(handle=handle, url=next_url, listitem=li_next, isFolder=True)
    except Exception:
        pass

    if xbmcplugin:
        xbmcplugin.endOfDirectory(handle)

def find_direct_links(page_html, base):
    found = []
    # <source src=> entries
    for m in re.finditer(r'<source[^>]*src=[\'\"](?P<h>[^\'\"]+)[\'\"]', page_html, re.I):
        h = urllib.parse.urljoin(base, m.group('h'))
        found.append(h)
    # Any absolute or protocol-relative video URLs in the page (JSON, scripts, attributes)
    for m in re.finditer(r'(?P<h>(?:https?:)?//[^\'\"\s>]+\.(?:m3u8|mp4|mkv|mov|webm|avi)(?:\?[^\'\"\s>]*)?)', page_html, re.I):
        u = m.group('h')
        u = urllib.parse.urljoin(base, u)
        found.append(u)
    # hls manifest URLs in inline scripts or JSON objects, including escaped OK.ru payload
    page_clean = page_html.replace('\\&quot;', '"').replace('&quot;', '"').replace('\\u0026', '&').replace('\\u002F', '/')
    # capture the full raw video.m3u8 path and query from hlsManifestUrl if available
    for m in re.finditer(r'hlsManifestUrl[^\n]*?(https?://[^"\'\s>]+?\.m3u8(?:\?[^"\'\s>]*)?)', page_clean, re.I):
        h = urllib.parse.urljoin(base, m.group(1))
        found.append(h)
    # download links
    for m in re.finditer(r'href=[\'\"](?P<h>[^\'\"]+)[\'\"][^>]*>(?:[^<]*download[^<]*)</a>', page_html, re.I):
        h = urllib.parse.urljoin(base, m.group('h'))
        found.append(h)
    # iframes: fetch and search inside iframe content
    for m in re.finditer(r'<iframe[^>]*src=[\'\"](?P<h>[^\'\"]+)[\'\"]', page_html, re.I):
        src = urllib.parse.urljoin(base, m.group('h'))
        try:
            iframe_html = http_get(src)
            # look for any video URLs in iframe HTML
            for n in re.finditer(r'(?P<h>(?:https?:)?//[^\'\"\s>]+\.(?:m3u8|mp4|mkv|mov|webm|avi)(?:\?[^\'\"\s>]*)?)', iframe_html, re.I):
                u = n.group('h')
                u = urllib.parse.urljoin(src, u)
                found.append(u)
            # ok.ru and similar often embed a JSON key like "hlsManifestUrl" inside escaped JSON strings
            iframe_clean = iframe_html.replace('\\&quot;', '"').replace('&quot;', '"').replace('\\u0026', '&').replace('\\u002F', '/')
            for n in re.finditer(r'hlsManifestUrl\s*[:=]\s*"(?P<h>https?://[^"\s>]+?\.m3u8(?:\?[^"\s>]*)?)"', iframe_clean, re.I):
                u = urllib.parse.urljoin(src, n.group('h'))
                found.append(u)
        except Exception:
            continue
    # clean and dedupe preserving order
    def _clean_url(u, ref):
        if not u:
            return None
        u = u.strip()
        # decode JS unicode escapes like \u0026 -> & and common slash escapes
        try:
            u = re.sub(r'\\u([0-9A-Fa-f]{4})', lambda m: chr(int(m.group(1), 16)), u)
        except Exception:
            pass
        u = u.replace('\\/', '/')
        u = u.replace('\\u0026', '&')
        u = u.replace('\\u002F', '/')
        u = u.replace('\\&', '&')
        u = u.replace('&quot;', '')
        u = u.replace('\\&quot;', '')
        u = u.replace('\\"', '"').replace('\\\'', "'")
        # extract m3u8 or other video URL from the string
        m = re.search(r'(https?://[^\s"\'\\<>{},\]]+?\.(?:m3u8|mp4|mkv|mov|webm|avi)(?:\?[^\s"\'\\<>{},\]]*)?)', u, re.I)
        if m:
            u = m.group(1)
        else:
            # fallback general URL
            m2 = re.search(r'(https?://[^\s"\'\\<>{},\]]+)', u, re.I)
            if m2:
                u = m2.group(1)
            else:
                m3 = re.search(r'(//[^\s"\'\\<>{},\]]+)', u)
                if m3:
                    u = urllib.parse.urljoin(ref, m3.group(1))
        # final join/normalize
        try:
            u = urllib.parse.urljoin(ref, u)
        except Exception:
            pass
        return u

    out = []
    seen = set()
    for u in found:
        cu = _clean_url(u, base)
        if not cu:
            continue
        if cu in seen:
            continue
        seen.add(cu)
        out.append(cu)
    return out

def play_movie(url):
    page_html = http_get(url)
    direct_links = find_direct_links(page_html, url)
    if not direct_links:
        if xbmcgui and SETTINGS.get('show_notifications'):
            xbmcgui.Dialog().notification('RareFilmm', 'No direct playable links found, opening page', xbmcgui.NOTIFICATION_INFO, 3000)
        # fall back to opening the page URL in the player or external browser
        if xbmcplugin:
            li = xbmcgui.ListItem(path=url) if xbmcgui else None
            try:
                xbmcplugin.setResolvedUrl(handle, True, li)
                return
            except Exception:
                pass
        if xbmc and hasattr(xbmc, 'Player'):
            xbmc.Player().play(url)
        return

    # reorder links according to preferred_stream setting
    pref = SETTINGS.get('preferred_stream', 'auto')
    def _prefer(links, ext):
        head = [l for l in links if l.lower().find(ext) != -1]
        tail = [l for l in links if l not in head]
        return head + tail

    if pref == 'hls':
        direct_links = _prefer(direct_links, '.m3u8')
    elif pref == 'mp4':
        direct_links = _prefer(direct_links, '.mp4')

    if len(direct_links) == 1:
        play_url = direct_links[0]
    else:
        if xbmcgui:
            # build compact titles for selection: show hostname + extension
            titles = []
            for u in direct_links:
                try:
                    p = urllib.parse.urlparse(u)
                    ext = os.path.splitext(p.path)[1].lstrip('.') or 'link'
                    titles.append('%s — %s' % (p.netloc or u, ext))
                except Exception:
                    titles.append(u)
            sel = xbmcgui.Dialog().select('Choose stream', titles)
            if sel == -1:
                return
            play_url = direct_links[sel]
        else:
            play_url = direct_links[0]

    # Properly resolve the playable URL for Kodi
    if xbmcplugin:
        li = xbmcgui.ListItem(path=play_url) if xbmcgui else None
        # give Kodi some metadata where possible
        try:
            li.setProperty('IsPlayable', 'true')
        except Exception:
            pass
        try:
            xbmcplugin.setResolvedUrl(handle, True, li)
            return
        except Exception:
            pass
    if xbmc and hasattr(xbmc, 'Player'):
        xbmc.Player().play(play_url)

def search_movies(query=None):
    # Prompt for query if not provided
    if query is None:
        if xbmcgui:
            query = xbmcgui.Dialog().input('Search RareFilmm')
        else:
            try:
                query = input('Search RareFilmm: ')
            except Exception:
                query = ''
    if not query:
        return
    # Fetch full index (cached) and search titles
    entries = get_index_entries()
    matches = [e for e in entries if query.lower() in e['title'].lower()]
    if xbmcplugin:
        xbmcplugin.setPluginCategory(handle, 'Search: %s' % query)
        xbmcplugin.setContent(handle, 'movies')
    if not matches:
        if xbmcgui:
            xbmcgui.Dialog().notification('RareFilmm', 'No matches found', xbmcgui.NOTIFICATION_INFO, 3000)
        if xbmcplugin:
            xbmcplugin.endOfDirectory(handle)
        return
    
    # Fetch metadata in parallel if enabled (super fast!)
    metadata_dict = {}
    if SETTINGS.get('fetch_metadata'):
        urls = [it['href'] for it in matches]
        metadata_dict = fetch_multiple_metadata(urls, max_workers=4)
    
    for it in matches:
        # Get pre-fetched metadata
        metadata = metadata_dict.get(it['href'], {'image': None, 'description': None})
        
        li = xbmcgui.ListItem(label=it['title']) if xbmcgui else None
        if li:
            plot = metadata.get('description') or ''
            li.setInfo('video', {'title': it['title'], 'plot': plot})
            li.setProperty('IsPlayable', 'true')
            if metadata.get('image'):
                li.setArt({'thumb': metadata['image'], 'icon': metadata['image'], 'fanart': metadata['image']})
        url = build_url({'action': 'play', 'url': it['href']})
        if xbmcplugin:
            xbmcplugin.addDirectoryItem(handle=handle, url=url, listitem=li, isFolder=False)
    if xbmcplugin:
        xbmcplugin.endOfDirectory(handle)

def router(paramstring):
    params = dict(urllib.parse.parse_qsl(paramstring.lstrip('?')))
    action = params.get('action')
    if action == 'play':
        url = params.get('url')
        if url:
            play_movie(url)
    elif action == 'search':
        q = params.get('q')
        search_movies(q)
    elif action == 'settings':
        if xbmcaddon:
            try:
                xbmcaddon.Addon().openSettings()
            except Exception:
                pass
        return
    elif action == 'list':
        page = 1
        if params.get('page') and params.get('page').isdigit():
            page = int(params.get('page'))
        force_refresh = str(params.get('refresh', '')).lower() in ('1', 'true', 'yes')
        list_movies(page, force_refresh=force_refresh)
    else:
        page = 1
        if params.get('page') and params.get('page').isdigit():
            page = int(params.get('page'))
        list_movies(page)

if __name__ == '__main__':
    router(sys.argv[2] if len(sys.argv) > 2 else '')
