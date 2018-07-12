#!/usr/bin/python

import calendar
import datetime
import fcntl
import os
import pygame
import shlex
import signal
import socket
import struct
import subprocess
import sys
import threading
import time

import pygame_text_input

BG_FILE='images/bg2.jpg'
COVER_FILE='images/music.png'
STATE_FILE="/tmp/state"
ROBOTO_LIGHT_FILE='fonts/RobotoMono-Light.ttf'
ROBOTO_REG_FILE='fonts/RobotoMono-Regular.ttf'
PARSER_EXE='scripts/metadata.sh'

def cat(file):
    try:
        f = open(file,"r")
        t = f.read()
        f.close()
        return t
    except:
        return ""

def getIP(ifname):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return  socket.inet_ntoa(fcntl.ioctl(
                    s.fileno(),
                    0x8915,  # SIOCGIFADDR
                    struct.pack('256s', ifname[:15])
                )[20:24])
    except:
        return "No IP Address"

def getSSID():
    ssid = ""
    try:
        f = open("/etc/wpa_supplicant.conf","r")
        t = f.read()
        for item in t.split("\n"):
            if "ssid=" in item:
                ssid = item.strip().split("=")[1]
                ssid = ssid.translate(None, "\"")
        f.close()
        return ssid
    except:
        return ssid

def getSSID_PW():
    ssidpw = ""
    try:
        f = open("/etc/wpa_supplicant.conf","r")
        t = f.read()
        for item in t.split("\n"):
            if "#psk=" in item:
                ssidpw = item.strip().split("=")[1]
                ssidpw = ssidpw.translate(None, "\"")
        f.close()
        return ssidpw
    except:
        return ssidpw

def setHostname(name):
    subprocess.call(["scripts/hostname.sh", name])

def setSSID(name, pw):
    subprocess.call(["scripts/wifi-setup.sh", name, pw])

class ClockGui:
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit)
        signal.signal(signal.SIGTERM, self.exit)

        self.log = open("/tmp/gui.log","w")
        self.stdout = sys.stdout
        sys.stdout = self.log

        self.dbg("Starting init...")

        #pygame init -- used for graphics
        pygame.display.init()
        pygame.font.init()
        pygame.mouse.set_visible(False)

        self.ssid = getSSID()
        self.pw = getSSID_PW()

        self.clock = pygame.time.Clock()

        self.mode = "clock"

        self.menuTextBox = pygame_text_input.TextInput(font_family=ROBOTO_REG_FILE, font_size=15)

        self.WIDTH = 320
        self.HEIGHT = 240

        # Define some colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)

        self.NET_Y = 5
        self.TIME_Y = 40
        self.DATE_Y = 120
        self.ARTIST_XY = [55, 170]
        self.SONG_XY  = [55, 190]
        self.MUSIC_ICON_XY  = [15, 175]

        self.MENU_INFO_XY = [20, 20]
        self.MENU_TEXT_BOX_XY = [20, 60]

        # Set the height and width of the screen
        #NOTE: X and Y are reversed since the screen on its side
        self.screen = pygame.display.set_mode([self.HEIGHT, self.WIDTH])

        #program onto a surface that will be rotated later to match the actual screen
        self.surface = pygame.Surface([self.WIDTH, self.HEIGHT], pygame.SRCALPHA)

        self.bg = pygame.image.load(BG_FILE)
        self.cover = pygame.image.load(COVER_FILE)

        # Loop until the user clicks the close button.
        self.done = False
        self.song = ''
        self.artist = ''

        self.fontLarge = pygame.font.Font(ROBOTO_LIGHT_FILE, 63)
        self.fontMedium = pygame.font.Font(ROBOTO_REG_FILE, 22)
        self.fontSmall = pygame.font.Font(ROBOTO_REG_FILE, 15)

        self.mdThread = threading.Thread(target=self.processMetadata)
        self.mdThread.daemon = True
        self.mdThread.start()

        self.dbg("... finished init")

    def dbg(self, *args):
        print(map(str, args))
        self.log.flush()

    def run(self):
        self.dbg("Main thread starting...")
        cnt = 0;
        while not self.done:
            self.processEvents()

            #refresh the background image
            self.surface.blit(self.bg, [0,0])

            #draw the correct screen elements
            if self.mode == "clock":
                self.drawClockGui()
            else:
                self.drawMenuGui()

            # Go ahead and update the screen with what we've drawn.
            self.screen.blit(pygame.transform.rotate(self.surface,90), [0,0])
            pygame.display.flip()

            #control the fps
            self.clock.tick(5)

        self.dbg("... exiting main thread")
        self.exit()
        pygame.quit()

    def exit(self,signum, frame):
        self.done = True
        sys.stdout = self.stdout
        try:
            self.log.close()
        except():
            self.dbg("Log file must have already closed")

    def blockKeyboard(self):
        pygame.event.set_blocked(pygame.KEYDOWN)
        pygame.event.set_blocked(pygame.KEYUP)

    def unblockKeyboard(self):
        pygame.event.set_allowed(pygame.KEYDOWN)
        pygame.event.set_allowed(pygame.KEYUP)

    def processEvents(self):
        #check to see if any system control keys were pressed
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.mode = ("clock", "menu.1")[self.mode == "clock"]
                self.menuTextBox.clear_text()
                self.dbg("Switched mode to " + self.mode)
                return
            elif event.type == pygame.QUIT:
                self.done = True
                return

        #if we got here, process normal events
        if "menu" in self.mode:
            self.processMenuEvent(events)

    def processMenuEvent(self, events):
        enter = self.menuTextBox.update(events)
        strData = self.menuTextBox.get_text()
        valid = enter and (strData != "")
        if valid:
            if self.mode == "menu.1":
                setHostname(strData)
                self.mode = "menu.2"
            elif self.mode == "menu.2":
                self.ssid = strData
                self.mode = "menu.3"
            elif self.mode == "menu.3":
                self.pw = strData
                self.blockKeyboard()
                setSSID(self.ssid, self.pw)
                self.unblockKeyboard()
                self.mode = "clock"

            self.menuTextBox.clear_text()

    def drawClockGui(self):
        self.drawNetworkInfo()

        self.drawTime()

        if "on" in cat(STATE_FILE):
            self.drawMusicInfo()

    def drawMenuGui(self):
        if self.mode == "menu.1": #update hostname
            infoString = "Hostname = " + cat("/etc/hostname")[:-1]
            text = self.fontSmall.render(infoString, True, self.BLACK)
            self.surface.blit(text, self.MENU_INFO_XY)
        elif self.mode == "menu.2": #update ssid
            infoString = "SSID = " + getSSID()
            text = self.fontSmall.render(infoString, True, self.BLACK)
            self.surface.blit(text, self.MENU_INFO_XY)
        elif self.mode == "menu.3": #update ssid
            infoString = "PW = " + getSSID_PW()
            text = self.fontSmall.render(infoString, True, self.BLACK)
            self.surface.blit(text, self.MENU_INFO_XY)

        surface = self.menuTextBox.get_surface()
        self.surface.blit(surface, self.MENU_TEXT_BOX_XY)

    def drawTime(self):
        #generate the strings that will be displayed
        date = datetime.datetime.now()
        day = datetime.date.today().strftime("%A")
        dateString = day +  ', {:%B %d}'.format(date)
        timeString = '{:%I:%M %p}'.format(date)

        #draw the time
        text = self.fontLarge.render(timeString, True, self.BLACK)
        timeW,timeH = self.fontLarge.size(timeString)
        self.surface.blit(text, [(self.WIDTH-timeW)/2, self.TIME_Y])

        #draw the date
        text = self.fontMedium.render(dateString, True, self.BLACK)
        dateW, dateH = self.fontMedium.size(dateString)
        self.surface.blit(text, [(self.WIDTH-dateW)/2, self.DATE_Y])

        return

    def drawMusicInfo(self):
        artistString = self.artist
        songString =  self.song

        #draw artist
        text = self.fontSmall.render(artistString, True, self.BLACK)
        w, h = self.fontSmall.size(artistString)
        self.surface.blit(text, self.ARTIST_XY)

        #draw song
        text = self.fontSmall.render(songString, True, self.BLACK)
        w, h = self.fontSmall.size(songString)
        self.surface.blit(text, self.SONG_XY)

        #draw music icon
        self.surface.blit(self.cover, self.MUSIC_ICON_XY)

    def drawNetworkInfo(self):
        ip = cat("/etc/hostname")[:-1] + " : " + getIP("wlan0")
        text = self.fontSmall.render(ip, True, self.BLACK)
        w, h = self.fontSmall.size(ip)
        self.surface.blit(text, [(self.WIDTH-w)/2, self.NET_Y])

    def processMetadata(self):
        self.dbg("Metadata thread starting...")
        proc = subprocess.Popen(shlex.split(PARSER_EXE), stdout=subprocess.PIPE)
        while not self.done:
            output = proc.stdout.readline()
            if output == '' and proc.poll() is not None:
                self.dbg("Metadata app failed...")
                break
            if output:
                line = output.strip()
                if "Title:" in line:
                    self.song = self.getMetaValue("Title", line)
                    self.song = self.song[1:]
                if "Artist:" in line:
                    self.artist = self.getMetaValue("Artist:", line)

        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except:
            self.dbg("Could not kill metadata process. Maybe it is already dead?")

        self.dbg("... exiting metadata thread")

        rc = proc.poll()
        return rc

    def getMetaValue(self, key, line):
        val = line.split(key)[1]
        val = val.replace('"','')
        val = val[1:-1]
        return val

if __name__ == "__main__":
    gui = ClockGui()
    gui.run()
