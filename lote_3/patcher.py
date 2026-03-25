# uncompyle6 version 3.9.3
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: client\control\system\patcher.py
"""
Created on Dec 15, 2018

@author: Admin
"""
import builtins, requests
from client.control.events.event import eventManager
from client.data.file import patchFileManager
from client.data.settings import gameSettings
from twisted.internet import threads, defer
import os, subprocess, sys
from twisted.internet import reactor
from twisted.web.iweb import UNKNOWN_LENGTH
from twisted.internet.defer import Deferred
from twisted.internet.protocol import Protocol
from twisted.web.client import Agent, ResponseDone
from twisted.web.http_headers import Headers
import ujson
from client.data.patcher import PatchSettings, BuildInfo
from client.data.utils.utils import bytesToString
import urllib.request, threading
from distutils.version import StrictVersion
client_filename, ext = os.path.splitext(sys.argv[0])
if getattr(sys, "frozen", False):
    is_frozen = True
else:
    is_frozen = False
patchURL = f"https://{gameSettings.getPatchServer()}/manifest.json"

class PatchHandler:
    PATCH_TIMEOUT = 5

    def __init__(self, patchFileHandler):
        self.patches = []
        self.currentVersion = gameSettings.getCurrentPatchNumber()
        self.archive = patchFileHandler
        self.downloadList = []
        self.patchList = []
        self.agent = Agent(reactor)

    def checkDownloadFolder(self):
        """ Makes sure patch folder exists, if not, creates it. """
        if not os.path.exists(PatchSettings.patchStorage):
            os.makedirs(PatchSettings.patchStorage)
        if not os.path.isdir(PatchSettings.patchStorage):
            os.remove(PatchSettings.patchStorage)
            os.makedirs(PatchSettings.patchStorage)

    def saveConfig(self):
        gameSettings["Patch"]["current"] = str(self.currentVersion)
        if not gameSettings.saveConfig():
            eventManager.notify("onNotificationMessage", "Notification", "Could not save to the configuration file. Try running as administrator or check antivirus settings")

    def _getPatchManifest(self):
        response = requests.get(patchURL, timeout=(self.PATCH_TIMEOUT))
        validated = self.validResponse(response)
        if validated:
            return self._patchResult(response.text)
        else:
            return False

    def needsPatching(self):
        eventManager.notify("onDisplayNotification", "Connection", "Checking for latest game data...")
        d = threads.deferToThread(self._getPatchManifest)
        return d

    def _timeout(self, d):
        d.cancel()

    def _patchResult(self, result):
        """ Parses the data we receive """
        if result is False:
            print("Could not get patch data list.")
            return False
        else:
            try:
                data = ujson.loads(result)
            except ValueError:
                print("Got data but it was not JSON")
                return False
            else:
                for build in data["builds"]:
                    if StrictVersion(build["version"]) > self.currentVersion:
                        self.patches.append(BuildInfo(build))

            if not self.patches:
                print("We are all up to date, no patch necessary.")
                return False
            return True

    def connectionFailure(self, response):
        print(response.printTraceback())
        print(response.getErrorMessage())
        print(f"Warning: Failed to get Patch File! {response.getErrorMessage()}")
        return False

    def getURL(self, response, patchInfo):
        print("GETTING", f"https://{gameSettings.getPatchServer()}/patches/{patchInfo.filename}")
        d = self.agent.request(b'GET', f"https://{gameSettings.getPatchServer()}/patches/{patchInfo.filename}".encode(), Headers({"User-Agent": ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"]}), None)
        return d

    def downloadPatches(self):
        self.checkDownloadFolder()
        self.patches.sort(key=(lambda x: StrictVersion(x.version)))
        self.currentVersion = self.patches[-1].version
        patchCount = len(self.patches)
        eventManager.notify("onPatchMessage", f'We found {patchCount} update{"s" if patchCount > 0 else ""}.')
        for patchInfo in self.patches:
            for patchFile in patchInfo.files_to_download:
                pathName = os.path.join(PatchSettings.patchStorage, patchFile.filename)
                if os.path.exists(pathName):
                    zipObj = self.archive.checkCorruption(pathName)
                    if zipObj:
                        patchFile.downloaded = True
                        continue
                    else:
                        try:
                            print(f"Found a patch file, but it was corrupted, removing. {patchFile.filename}")
                            os.remove(pathName)
                        except OSError:
                            print(f"Could not remove a corrupted patch file. {patchFile.filename}")
                            continue

        self.downloadList = [patchFile for patchInfo in self.patches for patchFile in iter((patchInfo.files_to_download)) if patchFile.downloaded is False]
        print("Downloads found:", self.downloadList)
        if self.downloadList:
            import queue
            queue = queue.Queue()
            for patchFile in self.downloadList:
                queue.put(patchFile)

            t = DownloadThread(queue, self)
            t.start()
        else:
            self.allDownloadsComplete(True)

    def allDownloadsComplete(self, response):
        if response is False:
            eventManager.notify("onPatchMessage", "Some updates could not be downloaded from server.")
            return
        for patchInfo in self.patches:
            for patchFile in patchInfo.files_to_download:
                if not patchFile.downloaded:
                    eventManager.notify("onPatchMessage", "Some updates could not be downloaded from server.")
                    return

        eventManager.notify("onPatchMessage", "Updates downloaded successfully.\n\nUpdating files, this may take a few moments... Do not close this window.")
        eventManager.notify("onForceRender")
        d = threads.deferToThread(self.archive.updateBuild, self.patches)
        d.addCallback(self.successfulPatch)
        d.addErrback(self.failedPatch)

    def successfulPatch(self, result):
        """ If we patched the archive and file tree successfully """
        self.saveConfig()
        self.patchList.clear()
        eventManager.notify("onPatchMessage", "All updates installed successfully!\n\nAttempting to restart client in a few seconds...")
        reactor.callLater(2, self.restartClient)

    def failedPatch(self, failure):
        """ If we failed to patch the archive correctly! """
        print(f"Patching Archive File Failed: {failure}")
        eventManager.notify("onPatchMessage", f"Failed to update.\nError: {failure.getErrorMessage()}\nPlease close this application or restart your computer and try again.")

    def restartClient(self):
        absPath = os.path.abspath("./")
        try:
            if is_frozen:
                subprocess.Popen(os.path.join(absPath, sys.argv[0]))
            else:
                subprocess.Popen([sys.executable, os.path.join(absPath, sys.argv[0])])
            eventManager.notify("onQuitGame")
        except Exception:
            eventManager.notify("onPatchMessage", "All updates installed successfully!\n\nAttempting to restart client in a few seconds...\nClient could not be closed, please close this manually and relaunch.")

    def validResponse(self, response):
        """ Determine by using the response data if we can use the data at all or if there is a problem"""
        if response.status_code != 200:
            print(f"Patcher: File not found at destination. Error: {response.status_code}")
            return False
        else:
            return True


class DownloadThread(threading.Thread):

    def __init__(self, queue, patcher):
        super(DownloadThread, self).__init__(daemon=True)
        self.queue = queue
        self.patcher = patcher

    def run(self):
        while not self.queue.empty():
            patchFile = self.queue.get()
            try:
                self.download_url(patchFile)
            except Exception as e:
                print(e)

            self.queue.task_done()

        reactor.callFromThread(self.patcher.allDownloadsComplete, True)

    def download_url(self, patchFile):
        dest = os.path.join(PatchSettings.patchStorage, patchFile.filename)
        response = requests.get(f"https://{gameSettings.getPatchServer()}/patches/{patchFile.filename}", stream=True)
        total_length = response.headers.get("content-length")
        with open(dest, "wb") as outfile:
            if total_length is None:
                eventManager.notify("onPatchMessage", f"File {patchFile.filename}\nDownloading...")
                outfile.write(response.content)
                eventManager.notify("onPatchProgress", 100, 100)
                patchFile.downloaded = True
            else:
                dl = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    outfile.write(data)
                    eventManager.notify("onPatchMessage", f"File {patchFile.filename}\nDownloaded {bytesToString(dl)} / {bytesToString(total_length)}\n{dl / total_length:.0%}")
                    eventManager.notify("onPatchProgress", dl, total_length)

            if dl >= total_length:
                patchFile.downloaded = True


patchHandler = PatchHandler(patchFileManager)
# global patchHandler ## Warning: Unused global
