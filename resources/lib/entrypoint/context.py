# -*- coding: utf-8 -*-

#################################################################################################

import json
import logging
import sys

import xbmc
import xbmcaddon

import database
from dialogs import context
from helper import _, settings, dialog
from downloader import TheVoid

#################################################################################################

LOG = logging.getLogger("EMBY."+__name__)
XML_PATH = (xbmcaddon.Addon('plugin.video.emby').getAddonInfo('path'), "default", "1080i")
OPTIONS = {
    'Refresh': _(30410),
    'Delete': _(30409),
    'Addon': _(30408),
    'AddFav': _(30405),
    'RemoveFav': _(30406),
    'Transcode': _(30412)
}

#################################################################################################


class Context(object):

    _selected_option = None

    def __init__(self, play=False, transcode=False, delete=False):

        self.server = None
        self.kodi_id = None
        self.media = None

        try:
            self.kodi_id = max(sys.listitem.getVideoInfoTag().getDbId(), 0) or max(sys.listitem.getMusicInfoTag().getDbId(), 0) or None
            self.media = self.get_media_type()
            self.server = sys.listitem.getProperty('embyserver') or None
            item_id = sys.listitem.getProperty('embyid')
        except AttributeError:

            if xbmc.getInfoLabel('ListItem.Property(embyid)'):
                item_id = xbmc.getInfoLabel('ListItem.Property(embyid)')
            else:
                self.kodi_id = xbmc.getInfoLabel('ListItem.DBID')
                self.media = xbmc.getInfoLabel('ListItem.DBTYPE')
                item_id = None

        if self.server or item_id:
            self.item = TheVoid('GetItem', {'ServerId': self.server, 'Id': item_id}).get()
        else:
            self.item = self.get_item_id()

        if self.item:

            if play or transcode:
                self.play(transcode)

            elif delete:
                self.delete_item()

            elif self.select_menu():
                self.action_menu()

    def get_media_type(self):

        ''' Get media type based on sys.listitem. If unfilled, base on visible window.
        '''
        media = sys.listitem.getVideoInfoTag().getMediaType() or sys.listitem.getMusicInfoTag().getMediaType()

        if not media:

            if xbmc.getCondVisibility('Container.Content(albums)'):
                media = "album"
            elif xbmc.getCondVisibility('Container.Content(artists)'):
                media = "artist"
            elif xbmc.getCondVisibility('Container.Content(songs)'):
                media = "song"
            elif xbmc.getCondVisibility('Container.Content(pictures)'):
                media = "picture"
            else:
                LOG.info("media is unknown")

        return media.decode('utf-8')

    def get_item_id(self):

        ''' Get synced item from embydb.
        '''
        item = database.get_item(self.kodi_id, self.media)

        if not item:
            return

        return {
            'Id': item[0],
            'UserData': json.loads(item[4]) if item[4] else {},
            'Type': item[3]
        }

    def select_menu(self):

        ''' Display the select dialog.
            Favorites, Refresh, Delete (opt), Settings.
        '''
        options = []

        if self.item['Type'] not in ('Season'):

            if self.item['UserData'].get('IsFavorite'):
                options.append(OPTIONS['RemoveFav'])
            else:
                options.append(OPTIONS['AddFav'])

        options.append(OPTIONS['Refresh'])

        if settings('enableContextDelete.bool'):
            options.append(OPTIONS['Delete'])

        options.append(OPTIONS['Addon'])

        context_menu = context.ContextMenu("script-emby-context.xml", *XML_PATH)
        context_menu.set_options(options)
        context_menu.doModal()

        if context_menu.is_selected():
            self._selected_option = context_menu.get_selected()

        return self._selected_option

    def action_menu(self):

        selected = self._selected_option.decode('utf-8')

        if selected == OPTIONS['Refresh']:
            TheVoid('RefreshItem', {'ServerId': self.server, 'Id': self.item['Id']})

        elif selected == OPTIONS['AddFav']:
            TheVoid('FavoriteItem', {'ServerId': self.server, 'Id': self.item['Id'], 'Favorite': True})

        elif selected == OPTIONS['RemoveFav']:
            TheVoid('FavoriteItem', {'ServerId': self.server, 'Id': self.item['Id'], 'Favorite': False})

        elif selected == OPTIONS['Addon']:
            xbmc.executebuiltin('Addon.OpenSettings(plugin.video.emby)')

        elif selected == OPTIONS['Delete']:
            self.delete_item()

    def delete_item(self):

        delete = True

        if not settings('skipContextMenu.bool'):

            if not dialog("yesno", heading="{emby}", line1=_(33015)):
                delete = False

        if delete:
            TheVoid('DeleteItem', {'ServerId': self.server, 'Id': self.item['Id']})

    def play(self, transcode=False):

        path = "http://127.0.0.1:57578/emby/play/file.strm?mode=play&Id=%s" % self.item['Id']

        if self.kodi_id:
            path += "&KodiId=%s" % self.kodi_id

        if self.media:
            path += "&MediaType=%s" % self.media

        if transcode:
            path += "&transcode=true"

        xbmc.executebuiltin("PlayMedia(%s)" % path)
