# -*- coding: utf-8 -*-
import os
import re
import time
import urllib2
import xbmcgui
import requests
from bs4 import BeautifulSoup
from kodibgcommon.utils import *


def get_parts(url):
  """
  Geting the parts from the page.

  """

  parts = []  
  log ("Get " + url, 2)
  req = urllib2.Request(url)
  text = urllib2.urlopen(req).read()
  soup = BeautifulSoup(text, 'html5lib')
  el = soup.find("div", class_="tab-holder-0")
  
  imgs = el.find_all('img')
  log("imgs: %s" % len(imgs), 0)
  links = el.find_all('a', class_="news-title-hld")
  log("a: %s" % len(links), 0)
  titles = el.find_all('h2', class_='news-title')
  log("h2: %s" % len(titles), 0)
  
  for i in range(0, len(imgs)):
    title = titles[i].get_text().encode('utf-8')
    item = {"title": title, "url": links[i]['href'], "logo": imgs[i]['src']}
    parts.append(item)

  return parts


def get_products(url):
  """
  Geting the broadcasts from the page.

  """
  def SortKey(e):
    return e['title']

  products = []  
  log ("Get " + url, 2)
  req = urllib2.Request(url)
  req.add_header('User-agent', user_agent)
  text = urllib2.urlopen(req).read()
  soup = BeautifulSoup(text, 'html5lib')
  el = soup.find("div", class_="news-descr")
  
  imgs = el.find_all('img')
  log("imgs: %s" % len(imgs), 0)
  links = el.find_all('a', class_="news-title-hld")
  log("a: %s" % len(links), 0)
  
  for i in range(0, len(imgs)):
    title = links[i]['title']
    item = {"title": title, "url": links[i]['href'], "logo": imgs[i]['src']}
    products.sort(key=SortKey)
    products.append(item)

  return products


def get_episodes_by_search(url):
  """
  Geting the episodes from the search page.
  """

  episodes = []  
  log ("Get " + url, 2)
  req = urllib2.Request(url)
  req.add_header('User-agent', user_agent)
  text = urllib2.urlopen(req).read()
  soup = BeautifulSoup(text, 'html5lib')
  el = soup.find("div", class_="col-fixed-big")


  imgs = el.find_all('img')
  log("imgs: %s" % len(imgs), 0)
  links = el.find_all('a', class_="news-title-hld")
  log("a: %s" % len(links), 0)
  
  for i in range(0, len(imgs)):
    title = links[i]['title']
    item = {"title": title, "url": links[i]['href'], "logo": imgs[i]['src']}
    episodes.append(item)

  #pagination
  try:
    next = soup.find('a', {'rel': 'next'})
    if next:
      item = {"title": next_page_title2, "url": next.get('href')}
      log(item)
      episodes.append(item)
  except Exception as er:
    log("Adding pagination failed %s" % er, 4)

  return episodes


def get_episodes(url):
  global baba
  """
  Geting the episodes from the broadcast.
  """

  episodes = []  
  log ("Get " + url, 2)
  req = urllib2.Request(url)
  req.add_header('User-agent', user_agent)
  text = urllib2.urlopen(req).read()
  soup = BeautifulSoup(text, 'html5lib')
  el = soup.find('div', class_='tab-holder-1')

  imgs = el.find_all('img')
  log("imgs: %s" % len(imgs), 0)
  links = el.find_all('a', class_="news-title-hld")
  log("a: %s" % len(links), 0)
  titles = el.find_all('h2', class_='news-title')
  log("h2: %s" % len(titles), 0)
  link = el.find('a', class_="news-title-hld")

  try:
    rep = urllib2.Request(link['href'])
    texp = urllib2.urlopen(rep).read()
    souk = BeautifulSoup(texp, 'html5lib')
    ol = souk.find('div', class_='tab-holder-0')
    if ol:
      baba = False
    else:
      baba = True
  except Exception as er:
    log("Adding pagination failed %s" % er, 4)

  for i in range(0, len(imgs)):
    title = titles[i].get_text().encode('utf-8')
    item = {"title": title, "url": links[i]['href'], "logo": imgs[i]['src']}
    episodes.append(item)

  #pagination
  try:
    next = soup.find('a', {'rel': 'next'})
    if next:
      item = {"title": next_page_title, "url": next.get('href')}
      episodes.append(item)
  except Exception as er:
    log("Adding pagination failed %s" % er, 4)

  return episodes 


def show_parts(parts):
  """
  Showing the broadcast.
  """

  for part in parts:
    url = make_url({"action":"play_stream", "url": part["url"], "title": part["title"]})
    add_listitem_unresolved(part["title"], url, iconImage=part["logo"], thumbnailImage=part["logo"])


def show_products(products):
  """
  Showing the broadcast.
  """

  for product in products:
    url = make_url({"action":"show_episodes", "url": product["url"]})
    add_listitem_folder(product["title"], url, iconImage=product["logo"], thumbnailImage=product["logo"])


def show_episodes(episodes):
  """
  Showing the episodes.
  """

  for episode in episodes:
    if episode['title'] != next_page_title and episode['title'] != next_page_title2 and baba == True:
      url = make_url({"action": "play_stream", "url": episode["url"]})
      add_listitem_unresolved(episode["title"], url, iconImage=episode['logo'], thumbnailImage=episode['logo'])

    elif episode['title'] != next_page_title and episode['title'] != next_page_title2 and baba == False:
      url = make_url({"action": "show_parts", "url": episode["url"]})
      add_listitem_folder(episode["title"], url, iconImage=episode['logo'], thumbnailImage=episode['logo'])

    elif episode['title'] == next_page_title:
      url = make_url({"action": "show_episodes", "url": episode["url"]})
      add_listitem_folder(episode["title"], url)

    elif episode['title'] == next_page_title2:
      url = make_url({"action": "show_episodes_by_search", "url": episode["url"]})
      add_listitem_folder(episode["title"], url)



def get_stream(url):
  """
  Geting the broadcast.
  """

  log ("GET " + url, 0)
  req = urllib2.Request(url)
  text = urllib2.urlopen(req).read()
  soup = BeautifulSoup(text, 'html5lib')
  item = {"stream": None, "logo": None, "title": None}

  title = soup.title.get_text()
  m = re.compile('https.*mp4').findall(text)
  if len(m) > 0:
    item["stream"] = m[0]
    log("resolved stream: %s" % item["stream"], 0)
    
    p = re.compile('https.*png').findall(text)
    if len(m) > 0:
          item["logo"] = p[0]
    item['title'] = title
  else:
    log("No streams found!", 4)
  return item


def update(name, location, crash=None):
  lu = settings.last_update
  day = time.strftime("%d")
  if lu == "" or lu != day:
    settings.last_update = day
    p = {}
    p['an'] = get_addon_name()
    p['av'] = get_addon_version()
    p['ec'] = 'Addon actions'
    p['ea'] = name
    p['ev'] = '1'
    p['ul'] = get_kodi_language()
    p['cd'] = location

params = get_params()
action = params.get("action")
id = params.get("id")
url = params.get("url")
title = params.get("title")
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
view_mode = 55

next_page_title = 'Следваща страница'
next_page_title2 = 'Следваща страница '

if action == None:
  items = [
    {'title': 'Търси', "url": None, "action": "search", 'logo': 'https://cdn4.iconfinder.com/data/icons/eldorado-basic/40/search-512.png'},
    {'title': 'БНТ 1', "url": 'https://bnt.bg/bnt1/shows', "action": "show_products", 'logo': "https://upload.wikimedia.org/wikipedia/commons/b/b8/BNT1.png"},
    {'title': 'БНТ 2', "url": 'https://bnt.bg/bnt2/shows', "action": "show_products", 'logo': "https://upload.wikimedia.org/wikipedia/commons/f/fb/BNT2.png"},
    {'title': 'БНТ 3', "url": 'https://bnt.bg/bnt3/shows', "action": "show_products", 'logo': 'https://upload.wikimedia.org/wikipedia/commons/6/68/BNT3.png'},
    {'title': 'БНТ 4', "url": 'https://bnt.bg/bnt4/shows', "action": "show_products", 'logo': 'https://upload.wikimedia.org/wikipedia/commons/7/79/BNT4.png'}
  ]

  for item in items:
    url = make_url({"url": item['url'], "action": item['action']})
    add_listitem_folder(item['title'], url, iconImage=item['logo'])
  
  update('browse', 'Categories')
  view_mode = 50

elif action == 'show_products':
  show_products(get_products(url))

elif action == 'show_parts':
  show_parts(get_parts(url))


elif action == 'show_episodes':
  show_episodes(get_episodes(url))


elif action == 'show_episodes_by_search':
  show_episodes(get_episodes_by_search(url))


elif action == 'play_stream':
  stream = get_stream(url)['stream']
  log('Extracted stream %s ' % stream, 0)
  add_listitem_resolved_url('Video', stream)


elif action == 'search':
  keyboard = xbmc.Keyboard('', 'Търсене...')
  keyboard.doModal()
  searchText = ''
  if keyboard.isConfirmed():
    searchText = urllib.quote_plus(keyboard.getText())
    if searchText != '':
      show_episodes(get_episodes_by_search('https://bnt.bg/search?q=%s' % searchText))
        
        
xbmcplugin.endOfDirectory(get_addon_handle())
xbmc.executebuiltin("Container.SetViewMode(%s)" % view_mode)