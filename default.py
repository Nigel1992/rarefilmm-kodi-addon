#!/usr/bin/env python3
from __future__ import print_function
import sys
import re
import html
import urllib.request
import urllib.parse

try:
    import xbmc
    import xbmcgui
    import xbmcplugin
except Exception:
    xbmc = xbmcgui = xbmcplugin = None

handle = int(sys.argv[1]) if len(sys.argv) > 1 else 0

BASE_URL = 'https://rarefilmm.com'
INDEX_URL = BASE_URL + '/film-index/'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
PAGE_SIZE = 50

def http_get(url, timeout=20):
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT, 'Accept': 'text/html'})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
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

def build_url(query):
    return sys.argv[0] + '?' + urllib.parse.urlencode(query)

def fetch_movie_metadata(movie_url):
    try:
        page_html = http_get(movie_url)
    except Exception:
        return {'image': None, 'description': None}
    image = None
    description = None
    m = re.search(r'<meta[^>]*property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']', page_html, re.I)
    if not m:
        m = re.search(r'<meta[^>]*name=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']', page_html, re.I)
    if m:
        image = m.group(1).strip()
    m = re.search(r'<meta[^>]*property=["\']og:description["\'][^>]*content=["\']([^"\']+)["\']', page_html, re.I)
    if not m:
        m = re.search(r'<meta[^>]*name=["\']og:description["\'][^>]*content=["\']([^"\']+)["\']', page_html, re.I)
    if m:
        # Only use the og:description meta content as the plot text
        try:
            description = html.unescape(m.group(1).strip())
        except Exception:
            description = m.group(1).strip()
    return {'image': image, 'description': description}


def list_movies(page=1):
    # Use site pagination to load only one page of index entries (PAGE_SIZE per page).
    # The site returns the full index; fetch it and slice into pages locally
    page_url = INDEX_URL
    html_text = http_get(page_url)
    items = parse_index(html_text)
    total = len(items)
    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    page_items = items[start:end]

    if xbmcplugin:
        xbmcplugin.setPluginCategory(handle, 'RareFilmm')
        xbmcplugin.setContent(handle, 'movies')

    # Add a search entry at the top
    try:
        search_url = build_url({'action': 'search'})
        li_search = xbmcgui.ListItem(label='Search RareFilmm') if xbmcgui else None
        if xbmcplugin:
            xbmcplugin.addDirectoryItem(handle=handle, url=search_url, listitem=li_search, isFolder=True)
    except Exception:
        pass

    # page nav previous
    if page > 1:
        prev_url = build_url({'action': 'list', 'page': str(page - 1)})
        li_prev = xbmcgui.ListItem(label='<< Previous page (%d)' % (page - 1)) if xbmcgui else None
        if xbmcplugin:
            xbmcplugin.addDirectoryItem(handle=handle, url=prev_url, listitem=li_prev, isFolder=True)

    for it in page_items:
        metadata = fetch_movie_metadata(it['href'])
        li = xbmcgui.ListItem(label=it['title']) if xbmcgui else None
        if li:
            # Only use the og:description meta content for the plot
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
        if xbmcgui:
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
    if len(direct_links) == 1:
        play_url = direct_links[0]
    else:
        if xbmcgui:
            titles = [u for u in direct_links]
            sel = xbmcgui.Dialog().select('Choose stream', titles)
            if sel == -1:
                return
            play_url = direct_links[sel]
        else:
            play_url = direct_links[0]
    # Properly resolve the playable URL for Kodi
    if xbmcplugin:
        li = xbmcgui.ListItem(path=play_url) if xbmcgui else None
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
    # Fetch full index and search titles
    html_text = http_get(INDEX_URL)
    entries = parse_index(html_text)
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
    for it in matches:
        metadata = fetch_movie_metadata(it['href'])
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
    else:
        page = 1
        if params.get('page') and params.get('page').isdigit():
            page = int(params.get('page'))
        list_movies(page)

if __name__ == '__main__':
    router(sys.argv[2] if len(sys.argv) > 2 else '')
