from resources.lib.requesthandler import RequestHandler
from resources.lib.riffdb import RiffDB
from resources.lib.rifftrax import RiffTrax
from collections import defaultdict

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
xbmcplugin.setPluginFanart(addon_id, my_addon.getAddonInfo('fanart'))

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

@handler.page
def refreshdb():
    progress = xbmcgui.DialogProgress()
    progress.create('Scanning', 'Getting local file list...')

    try:
        filelist = get_local_files()
        for i, f in enumerate(filelist):
            if progress.iscanceled():
                break
            progress.update(
                100*i / len(filelist), 'Fetching info...', f['label']
            )
            if not riffdb.has(f['file']):
                query = re.sub(r'\.[^.]*$', '', f['label'])
                try:
                    results = rifftrax.video_search(query)
                    info = rifftrax.video_info(results[0]['url'])
                    info['date'] = time.strftime('%d.%m.%Y', info['date'])
                    riffdb.insert(f['file'], **info)
                except:
                    riffdb.insert(f['file'], title=f['label'],
                                  feature_type='unknown')
    except Exception, e:
        xbmcgui.Dialog().ok(
            'Error refreshing database',
            'We received the following error:',
            str(e)
        )

    progress.close()

@handler.page
def cleardb():
    yes = xbmcgui.Dialog().yesno(
        'Delete Riffs Database',
        'Are you sure you want to delete the Riffs database?',
        'This cannot be undone!'
    )
    if yes:
        riffdb.clear()

@handler.default_page
def index():
    refreshdb()

    url = handler.build_url({ 'mode': 'videos', 'feature_type': 'feature' })
    li = xbmcgui.ListItem('Features', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_id, url=url, listitem=li,
                                isFolder=True)

    url = handler.build_url({ 'mode': 'videos', 'feature_type': 'short' })
    li = xbmcgui.ListItem('Shorts', iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_id, url=url, listitem=li,
                                isFolder=True)

    try:
        riffdb.iterate('unknown').next()
        url = handler.build_url({ 'mode': 'videos', 'feature_type': 'unknown' })
        li = xbmcgui.ListItem('Unknown Videos', iconImage='DefaultFolder.png')
        xbmcplugin.addDirectoryItem(handle=addon_id, url=url, listitem=li,
                                    isFolder=True)
    except StopIteration:
        pass

    xbmcplugin.endOfDirectory(addon_id)

@handler.page
def videos(feature_type):
    for info in riffdb.iterate(feature_type):
        li = xbmcgui.ListItem(info['title'], iconImage='DefaultVideo.png')
        li.setArt({'poster': info['poster']})
        li.setInfo('video', infoLabels={
            'title': info['title'],
            'plot': info['summary'],
            'date': info['date'],
            'rating': info['rating'],
            'genre': info['feature_type'],
        })
        xbmcplugin.addDirectoryItem(handle=addon_id, url=info['filename'],
                                    listitem=li, isFolder=False)
    xbmcplugin.endOfDirectory(addon_id)

handler.run(sys.argv[2])
