from resources.lib.requesthandler import RequestHandler
from resources.lib.riffdb import RiffDB
from resources.lib.rifftrax import RiffTrax
from urllib import urlencode
from collections import OrderedDict

import json
import os.path
import re
import time
import xbmc
import xbmcaddon
import xbmcplugin
import xbmcgui
import xbmcvfs

addon_id = int(sys.argv[1])
my_addon = xbmcaddon.Addon('plugin.video.rifftrax')

handler = RequestHandler(sys.argv[0])
riffdb = RiffDB(os.path.join(
    xbmc.translatePath(my_addon.getAddonInfo('profile')),
    'riffdb.sqlite'
))
rifftrax = RiffTrax()

xbmcplugin.setContent(addon_id, 'movies')

def jsonrpc(query):
    return json.loads(xbmc.executeJSONRPC(json.dumps(query)))

def get_local_files():
    if my_addon.getSetting('include_local') != 'true':
        return []
    folder = my_addon.getSetting('local_folder')
    data = jsonrpc({
        'jsonrpc': '2.0',
        'method': 'Files.GetDirectory',
        'params': {'directory': folder, 'media': 'video'},
        'id': 1
    })
    if data.get('error') is not None:
        raise Exception(data['error'])

    return data['result'].get('files', [])

def refresh_video(filename, title, prompt_results=False):
    results = rifftrax.video_search(title)
    if prompt_results:
        if len(results) == 0:
            xbmcgui.Dialog().ok(
                'Search Results', 'Sorry, no results for "{}"'.format(title)
            )
            index = None
        else:
            index = xbmcgui.Dialog().select(
                'Search Results', [i['title'] for i in results]
            )
    else:
        if len(results) == 0:
            index = None
        else:
            index = 0

    if index is None:
        riffdb.insert(filename, title=title, feature_type='unknown')
        return False
    else:
        info = rifftrax.video_info(results[index]['url'])
        info['date'] = time.strftime('%d.%m.%Y', info['date'])
        riffdb.insert(filename, **info)
        return True

@handler.default_page
def index():
    if my_addon.getSetting('update_library') != '0':
        refresh_db()

    context = [
        ('Refresh library', 'RunPlugin(' + handler.build_url({
            'mode': 'refresh_db',
            'explicit': 'true',
        }) + ')')
    ]

    titles = OrderedDict([
        ('unknown', 'Unknown Videos'),
        ('feature', 'Features'),
        ('short',   'Shorts'),
        ('live',    'Live'),
    ])
    for kind, title in titles.iteritems():
        if riffdb.count(kind):
            url = handler.build_url({ 'mode': 'videos', 'feature_type': kind })
            li = xbmcgui.ListItem(title, iconImage='DefaultFolder.png')
            li.addContextMenuItems(context)
            xbmcplugin.addDirectoryItem(handle=addon_id, url=url, listitem=li,
                                        isFolder=True)

    xbmcplugin.endOfDirectory(addon_id)

@handler.page
def videos(feature_type):
    if my_addon.getSetting('update_library') == '1':
        refresh_db()

    sort_methods = [
        2,  # SORT_METHOD_LABEL_IGNORE_THE
        3,  # SORT_METHOD_DATE
        8,  # SORT_METHOD_DURATION
        18, # SORT_METHOD_VIDEO_RATING
        19, # SORT_METHOD_DATE_ADDED
    ]
    for i in sort_methods:
        xbmcplugin.addSortMethod(addon_id, i)

    for info in riffdb.iterate(feature_type):
        li = xbmcgui.ListItem(info['title'], iconImage='DefaultVideo.png',
                              thumbnailImage=info['poster'])
        li.setInfo('video', infoLabels={
            'title': info['title'],
            'plot': info['summary'],
            'date': info['date'],
            'rating': info['rating'],
        })
        li.addContextMenuItems([
            ('Refresh', 'RunPlugin(' + handler.build_url({
                'mode': 'refresh',
                'filename': info['filename'],
                'title': info['title'],
            }) + ')')
        ])
        xbmcplugin.addDirectoryItem(handle=addon_id, url=info['filename'],
                                    listitem=li, isFolder=False)
    xbmcplugin.endOfDirectory(addon_id)

@handler.page
def refresh(filename, title):
    while True:
        title = xbmcgui.Dialog().input('Enter Title', title)
        if not title:
            return
        riffdb.remove(filename)
        if refresh_video(filename, title, prompt_results=True):
            break
    xbmc.executebuiltin('Container.Refresh')

@handler.page
def refresh_db(explicit=False):
    explicit = bool(explicit)
    progress = xbmcgui.DialogProgress()

    try:
        if explicit:
            progress.create('Scanning', 'Getting local file list...')
        filelist = get_local_files()
        new_files = filter(lambda f: not riffdb.has(f['file']), filelist)

        if len(new_files) and not explicit:
            progress.create('Scanning')
        for i, f in enumerate(new_files):
            if progress.iscanceled():
                break
            progress.update(
                100*i / len(new_files), 'Fetching info...', f['label']
            )
            title = re.sub(r'\.[^.]*$', '', f['label'])
            refresh_video(f['file'], title)

        progress.close()
    except Exception, e:
        progress.close()
        xbmcgui.Dialog().ok(
            'Error refreshing database',
            'We received the following error:',
            str(e)
        )

@handler.page
def clean_db():
    yes = xbmcgui.Dialog().yesno(
        'Clean Riffs Library',
        'Are you sure you want to clean the Riffs library?',
        'This cannot be undone!'
    )
    if not yes:
        return

    filelist = set((i['file'] for i in get_local_files()))
    for info in riffdb.iterate():
        if info['filename'] not in filelist:
            riffdb.remove(info['filename'])

@handler.page
def delete_db():
    yes = xbmcgui.Dialog().yesno(
        'Delete Riffs Library',
        'Are you sure you want to delete the Riffs library?',
        'This cannot be undone!'
    )
    if yes:
        riffdb.clear()

handler.run(sys.argv[2])
