# -*- coding: utf-8 -*-

#################################################################################################

import logging
import os
import sys

import xbmc
import xbmcaddon

#################################################################################################

__addon__ = xbmcaddon.Addon(id='plugin.video.emby')
__base__ = xbmc.translatePath(os.path.join(__addon__.getAddonInfo('path'), 'resources', 'lib')).decode('utf-8')
__libraries__ = xbmc.translatePath(os.path.join(__addon__.getAddonInfo('path'), 'libraries')).decode('utf-8')
__pcache__ = xbmc.translatePath(os.path.join(__addon__.getAddonInfo('profile'), 'emby')).decode('utf-8')
__cache__ = xbmc.translatePath('special://temp/emby').decode('utf-8')

sys.path.insert(0, __cache__)
sys.path.insert(0, __pcache__)
sys.path.insert(0, __libraries__)
sys.path.append(__base__)

#################################################################################################

from entrypoint import Events

#################################################################################################

LOG = logging.getLogger("EMBY.default")

#################################################################################################


if __name__ == "__main__":

    LOG.debug("--->[ default ]")

    try:
        Events()
    except Exception as error:
        LOG.exception(error)

    LOG.info("---<[ default ]")
