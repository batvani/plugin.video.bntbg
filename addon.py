# -*- coding: utf-8 -*-
import os
import re
import sys
import urllib
import urllib.parse
import urllib.request
from urllib.request import urlopen

import requests
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs
from bs4 import BeautifulSoup

"""
Vars.
"""
KodiV = xbmc.getInfoLabel('System.BuildVersion')
KodiV = int(KodiV[:2])

requests = requests.Session()

__addon__ = xbmcaddon.Addon()
if KodiV >= 19:
    __cwd__ = xbmcvfs.translatePath(__addon__.getAddonInfo('path'))
    bnt1 = xbmcvfs.translatePath(os.path.join(__cwd__, 'resources', 'bnt1.png'))
    bnt2 = xbmcvfs.translatePath(os.path.join(__cwd__, 'resources', 'bnt2.png'))
    bnt3 = xbmcvfs.translatePath(os.path.join(__cwd__, 'resources', 'bnt3.png'))
    bnt4 = xbmcvfs.translatePath(os.path.join(__cwd__, 'resources', 'bnt4.png'))
    bnt = xbmcvfs.translatePath(os.path.join(__cwd__, 'icon.png'))
else:
    __cwd__ = xbmc.translatePath(__addon__.getAddonInfo('path')).decode('utf-8')
    bnt1 = xbmc.translatePath(os.path.join(__cwd__, 'resources', 'bnt1.png')).decode('utf-8')
    bnt2 = xbmc.translatePath(os.path.join(__cwd__, 'resources', 'bnt2.png')).decode('utf-8')
    bnt3 = xbmc.translatePath(os.path.join(__cwd__, 'resources', 'bnt3.png')).decode('utf-8')
    bnt4 = xbmc.translatePath(os.path.join(__cwd__, 'resources', 'bnt4.png')).decode('utf-8')
    bnt = xbmcvfs.translatePath(os.path.join(__cwd__, 'icon.png')).decode("utf-8")

__url__ = sys.argv[0]
__handle__ = int(sys.argv[1])
items = [
    {"title": "Live", "url": None, "action": "list_live", "thumb": bnt},
    {'title': "БНТ 1", "url": 'https://bnt.bg/bnt1/shows', "action": "list_shows",
     'thumb': bnt1},
    {'title': "БНТ 2", "url": 'https://bnt.bg/bnt2/shows', "action": "list_shows",
     'thumb': bnt2},
    {'title': 'БНТ 3', "url": 'https://bnt.bg/bnt3/shows', "action": "list_shows",
     'thumb': bnt3},
    {'title': 'БНТ 4', "url": 'https://bnt.bg/bnt4/shows', "action": "list_shows",
     'thumb': bnt4}
]
items_live = [
    {'title': "БНТ 1", "url": 'http://tv.bnt.bg/', "action": "live",
     'thumb': bnt1},
    {'title': "БНТ 2", "url": 'http://tv.bnt.bg/bnt2', "action": "live",
     'thumb': bnt2},
    {'title': "БНТ 3", "url": 'http://tv.bnt.bg/bnt3', "action": "live",
     'thumb': bnt3},
    {'title': "БНТ 4", "url": 'http://tv.bnt.bg/bnt4', "action": "live",
     'thumb': bnt4}
]
next_page_title = "Следваща страница"
view_mode = 55

"""
Helper functions.
"""


def make_url(action, url, add_plugin_path=True):
    """
    Build a URL suitable for a Kodi add-on from a dict
    Prepends plugin path
    """
    if add_plugin_path:
        return '{0}?action={1}&url={2}'.format(__url__, action, url)


def add_listitems(listing):
    xbmcplugin.addDirectoryItems(__handle__, listing, len(listing))
    xbmcplugin.endOfDirectory(__handle__)


"""
Functions.
"""

"""
Video playing.
"""
def get_stream(url):
    """
    Geting the broadcast.
    """
    text = urlopen(url).read()
    if KodiV >= 19:
        text_re = text.decode("utf-8")
    else:
        text_re = text
    soup = BeautifulSoup(text, 'html5lib')
    item = {"stream": None, "thumb": None, "title": None}

    title = str(soup.title.get_text())

    m = re.findall("https.*mp4", text_re)
    if len(m) > 0:
        item["stream"] = m[0]

        p = re.findall('https.*png', text_re)
        if len(m) > 0:
            item["thumb"] = p[0]
        item['title'] = title
    return item


def play_video(url):
    """
    Play a video by the provided path.
    :param url: str
    :return: None
    """
    stream = get_stream(url)['stream']
    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=stream)
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(__handle__, True, listitem=play_item)


def play_live(url):
    play_item = xbmcgui.ListItem(path=url)
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(__handle__, True, listitem=play_item)


"""
Getting from web.
"""
def get_live(url):
    text = urlopen(url).read()
    soup = BeautifulSoup(text, 'html5lib')

    frame = soup.find("iframe", {"frameborder": 0})
    link = frame["src"]

    if not "http" in link:
        link = "http:" + link

    headers = {
        'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0',
        'Referer': "http://tv.bnt.bg/"
    }

    r_play = requests.post(link, headers=headers)
    match_play = re.search("sdata.src = '(.+?)';", r_play.text)
    urlPlay = match_play.group(1)
    requests.close()
    return urlPlay


def get_episodes(url):
    check = False

    episodes = []
    text = urlopen(url).read()
    soup = BeautifulSoup(text, 'html5lib')
    el = soup.find('div', {"class": 'tab-holder-1'})

    links = el.find_all('a', {"class": "hov-img"})
    link_check = el.find('a', {"class": "news-title-hld"})

    try:
        url_check = link_check['href']
        text_check = urlopen(url_check).read()
        soup_check = BeautifulSoup(text_check, 'html5lib')
        el_check = soup_check.find('div', {"class": 'tab-holder-0'})
        if el_check:
            check = True
        else:
            check = False
    except:
        pass

    for i in range(0, len(links)):
        title = links[i]['title']
        imgs = links[i].find('img')
        item = {"title": title, "url": links[i]['href'], "thumb": imgs['src'], "parts": check}
        episodes.append(item)

    # check for next page
    try:
        next = soup.find('a', {'rel': 'next'})
        if next:
            item = {"title": next_page_title, "url": next.get('href')}
            episodes.append(item)
    except:
        pass

    return episodes


def get_shows(url):
    """
    Geting the broadcasts from the page.
    """

    shows = []
    text = urlopen(url).read()
    soup = BeautifulSoup(text, 'html5lib')
    el = soup.find("div", {"class": "news-descr"})

    links = el.find_all('a', {"class": "hov-img"})

    for i in range(0, len(links)):
        title = links[i]['title']
        imgs = links[i].find('img')
        item = {"title": title, "url": links[i]['href'], "thumb": imgs['src']}
        shows.append(item)

    return shows


def get_parts(url):
    """
    Geting the parts from the page.
    """

    parts = []
    text = urlopen(url).read()
    soup = BeautifulSoup(text, 'html5lib')
    el = soup.find("div", {"class": "tab-holder-0"})

    links = el.find_all('a', {"class": "hov-img"})
    titles_ful_episode = el.find_all('h2', {"class": 'opened-episode'})
    img_holder = el.find_all('div', {"class": 'news-img-hld'})

    for i in range(0, len(links)):
        if img_holder[i].find_all('div', {"class": 'whole-show'}):
            title = "[COLOR red]" + "Цялото предаване - " + "[/COLOR]" + titles_ful_episode[0].get_text()
        else:
            title = links[i]['titleTrue']
        imgs = links[i].find('img')
        item = {"title": title, "url": links[i]['href'], "thumb": imgs['src']}
        parts.append(item)

    return parts


"""
Listing.
"""
def list_live():
    listitems = []
    for item in items_live:
        is_dir = False
        list_item = xbmcgui.ListItem(label=item['title'])
        list_item.setInfo("Video", {"Title": item["title"]})
        list_item.setProperty('IsPlayable', 'true')
        list_item.setArt({"icon": item['thumb'], "thumb": item['thumb'], "fanart": item["thumb"]})
        url = make_url(item["action"], item["url"])
        listitems.append((url, list_item, is_dir))
    add_listitems(listitems)


def list_shows(shows):
    """
    Create the list of video categories in the Kodi interface.
    :return: None
    """
    # Create a list for our items.
    listing = []
    # Iterate through categories
    for show in shows:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=show["title"])
        # Setting the style of the list item.
        list_item.setArt({"icon": show['thumb'], "thumb": show['thumb'], "fanart": show["thumb"]})
        # Set additional info for the list item.
        # Here we use a category name for both properties for for simplicity's sake.
        # For available properties see the following link:
        # http://mirrors.xbmc.org/docs/python-docs/15.x-isengard/xbmcgui.html#ListItem-setInfo
        list_item.setInfo('Folder', {'title': show["title"]})
        # Create a URL for the plugin recursive callback.
        # Example: plugin://plugin.video.example/?action=listing&category=Animals
        url = make_url("list_episodes", show["url"])
        # is_folder = True means that this item opens a sub-list of lower level items.
        is_folder = True
        # Add our item to the listing as a 3-element tuple.
        listing.append((url, list_item, is_folder))
    # Add our listing to Kodi.
    # Large lists and/or slower systems benefit from adding all items at once via addDirectoryItems
    # instead of adding one by ove via addDirectoryItem.
    add_listitems(listing)


def list_episodes(episodes):
    """
    Create the list of playable videos in the Kodi interface.
    :param episodes: list
    :return: None
    """
    listing = []
    for episode in episodes:
        url = None
        is_folder = False
        list_item = xbmcgui.ListItem(label=episode['title'])

        if episode['title'] != next_page_title and episode.get("parts") is False:
            url = make_url("play", episode["url"])
            list_item.setProperty('IsPlayable', 'true')
            list_item.setInfo('video', {'title': episode['title']})
            is_folder = False
        elif episode['title'] != next_page_title and episode.get("parts") is True:
            url = make_url("list_parts", episode["url"])
            is_folder = True
        elif episode["title"] == next_page_title:
            url = make_url("list_episodes", episode["url"])
            is_folder = True

        list_item.setArt({"icon": episode.get("thumb"), "thumb": episode.get("thumb"), "fanart": episode.get("thumb")})
        listing.append((url, list_item, is_folder))

    add_listitems(listing)


def list_parts(parts):
    listing = []

    for part in parts:
        list_item = xbmcgui.ListItem(label=part['title'])
        list_item.setArt({"icon": part['thumb'], "thumb": part['thumb'], "fanart": part["thumb"]})
        list_item.setInfo('video', {'title': part['title']})
        list_item.setProperty('IsPlayable', 'true')
        is_folder = False
        url = make_url("play", part["url"])
        listing.append((url, list_item, is_folder))

    add_listitems(listing)


def router(param_str):
    global view_mode
    if KodiV >= 19:
        params = dict(urllib.parse.parse_qsl(param_str[1:]))
    else:
        params = dict(urllib.parse_qsl(param_str[1:]))
    if params:
        action = params["action"]
        url = params["url"]
        if action == 'list_shows':
            list_shows(get_shows(url))
        elif action == "list_episodes":
            list_episodes(get_episodes(url))
        elif action == "list_parts":
            list_parts(get_parts(url))
        elif action == 'play':
            play_video(url)
        elif action == "live":
            play_live(get_live(url))
        elif action == "list_live":
            list_live()
    else:
        view_mode = 50
        listitems = []
        for item in items:
            is_dir = True
            list_item = xbmcgui.ListItem(label=item['title'])
            list_item.setArt({"icon": item['thumb'], "thumb": item['thumb'], "fanart": item["thumb"]})
            url = make_url(item["action"], item["url"])
            listitems.append((url, list_item, is_dir))
        add_listitems(listitems)


if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    router(sys.argv[2])
    xbmc.executebuiltin("Container.SetViewMode(%s)" % view_mode)
