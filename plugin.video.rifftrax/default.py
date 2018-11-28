from resources.lib.requesthandler import RequestHandler
from resources.lib.riffdb import RiffDB
from resources.lib.rifftrax import RiffTrax
from urllib import urlencode
from collections import OrderedDict

import json
import os.path
import re
import time
import traceback
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
    if title[0] == '/':
        try:
            info = rifftrax.video_info(title)
        except:
            info = None
    else:
        dialog = xbmcgui.Dialog()
        results = rifftrax.video_search(title)

        if len(results) == 0:
            if prompt_results:
                dialog.ok('Search Results',
                          'Sorry, no results for "{}"'.format(title))
            info = None
        else:
            if prompt_results:
                index = dialog.select('Search Results',
                                      [i['title'] for i in results])
                if index == -1:
                    return
            else:
                index = 0
            info = rifftrax.video_info(results[index]['url'])

    if info is None:
        riffdb.insert(filename, title=title, feature_type='unknown')
        return False
    else:
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
        li = xbmcgui.ListItem(info['title'])
        li.setInfo('video', infoLabels={
            'title': info['title'],
            'plot': info['summary'],
            'date': info['date'],
            'rating': info['rating'],
        })

        li.setArt({
            'icon': 'DefaultVideo.png',
            'poster': info['poster'],
            'thumb': info['poster'],
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
    dialog = xbmcgui.Dialog()
    while True:
        title = dialog.input('Enter Title', title)
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
    progress_open = False

    try:
        if explicit:
            progress.create('Scanning', 'Getting local file list...')
            progress_open = True
        filelist = get_local_files()
        new_files = filter(lambda f: not riffdb.has(f['file']), filelist)

        if len(new_files) and not explicit:
            progress.create('Scanning')
            progress_open = True
        for i, f in enumerate(new_files):
            if progress.iscanceled():
                break
            progress.update(
                100*i / len(new_files), 'Fetching info...', f['label']
            )
            title = re.sub(r'\.[^.]*$', '', f['label'])
            refresh_video(f['file'], title)
        if progress_open:
            progress.close()
            progress_open = False
    except Exception as e:
        if progress_open:
            progress.close()
        xbmcgui.Dialog().ok(
            'Error refreshing database',
            'We received the following error:',
            str(e)
        )
        traceback.print_exc()

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
