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
import threading
import time

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

class ClockGui:
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit)
        signal.signal(signal.SIGTERM, self.exit)

        pygame.display.init()
        pygame.font.init()
        pygame.mouse.set_visible(False)

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

        self.mdThread = threading.Thread(target=self.metadata)
        self.mdThread.daemon = True
        self.mdThread.start()
    
    def run(self):
        while not self.done:
            #refresh the background image
            self.surface.blit(self.bg, [0,0])

            self.drawNetworkInfo()

            self.drawTime()

            if "on" in cat(STATE_FILE):
                self.drawMusicInfo()

            # Go ahead and update the screen with what we've drawn.
            self.screen.blit(pygame.transform.rotate(self.surface,90), [0,0])
            pygame.display.flip()

            time.sleep(1)

        pygame.quit()

    def exit(self,signum, frame):
        self.done = True

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

    def metadata(self):
        proc = subprocess.Popen(shlex.split(PARSER_EXE), stdout=subprocess.PIPE)
        while not self.done:
            output = proc.stdout.readline()
            if output == '' and proc.poll() is not None:
                print("Metadata app failed...")
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
            print("Could not kill metadata process. Maybe it is already dead?")

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
