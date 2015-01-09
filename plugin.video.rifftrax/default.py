from resources.lib.requesthandler import RequestHandler

import json
import xbmc
import xbmcaddon
import xbmcplugin
import xbmcgui
import xbmcvfs

addon_id = int(sys.argv[1])
my_addon = xbmcaddon.Addon('plugin.video.rifftrax')

handler = RequestHandler(sys.argv[0])

xbmcplugin.setContent(addon_id, 'movies')
xbmcplugin.setPluginFanart(addon_id, my_addon.getAddonInfo('fanart'))

def jsonrpc(query):
    return json.loads(xbmc.executeJSONRPC(json.dumps(query)))

@handler.default_page
def index():
    if my_addon.getSetting('include_local') == 'true':
        folder = my_addon.getSetting('local_folder')
        data = jsonrpc({
            'jsonrpc': '2.0',
            'method': 'Files.GetDirectory',
            'params': {'directory': folder, 'media': 'video'},
            'id': 1
        })
        if data.get('error') is not None:
            xbmcgui.Dialog().ok(
                'Error listing directory',
                'We received the following error:',
                str(data['error'])
            )

        for f in data['result'].get('files', []):
            li = xbmcgui.ListItem(f['label'], iconImage='DefaultFolder.png')
            xbmcplugin.addDirectoryItem(handle=addon_id, url=f['file'],
                                        listitem=li, isFolder=False)
    xbmcplugin.endOfDirectory(addon_id)

handler.run(sys.argv[2])
