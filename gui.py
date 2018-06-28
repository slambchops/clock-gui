#!/usr/bin/python

import calendar
import datetime
import os
import pygame
import shlex
import signal
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
    f = open(file,"r")
    t = f.read()
    f.close()
    return t

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

        self.TIME_Y = 40
        self.DATE_Y = 120
        self.ARTIST_XY = [60, 170]
        self.SONG_XY  = [60, 190]
        self.MUSIC_ICON_XY  = [20, 175]

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

        self.timeFont = pygame.font.Font(ROBOTO_LIGHT_FILE, 63)
        self.dateFont = pygame.font.Font(ROBOTO_REG_FILE, 22)
        self.songFont = pygame.font.Font(ROBOTO_REG_FILE, 15)

        self.mdThread = threading.Thread(target=self.metadata)
        self.mdThread.daemon = True
        self.mdThread.start()
    
    def run(self):
        while not self.done:
            #refresh the background image
            self.surface.blit(self.bg, [0,0])

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
        text = self.timeFont.render(timeString, True, self.BLACK)
        timeW,timeH = self.timeFont.size(timeString)
        self.surface.blit(text, [(self.WIDTH-timeW)/2, self.TIME_Y])

        #draw the date
        text = self.dateFont.render(dateString, True, self.BLACK)
        dateW, dateH = self.dateFont.size(dateString)
        self.surface.blit(text, [(self.WIDTH-dateW)/2, self.DATE_Y])

        return

    def drawMusicInfo(self):
        artistString = self.artist
        songString =  self.song

        #draw artist
        text = self.songFont.render(artistString, True, self.BLACK)
        w, h = self.songFont.size(artistString)
        self.surface.blit(text, self.ARTIST_XY)

        #draw song
        text = self.songFont.render(songString, True, self.BLACK)
        w, h = self.songFont.size(songString)
        self.surface.blit(text, self.SONG_XY)

        #draw music icon
        self.surface.blit(self.cover, self.MUSIC_ICON_XY)

    def metadata(self):
        proc = subprocess.Popen(shlex.split(PARSER_EXE), stdout=subprocess.PIPE)
        while not self.done:
            output = proc.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                line = output.strip()
                if "Title:" in line:
                    self.song = self.getMetaValue("Title", line)
                    self.song = self.song[1:]
                if "Artist:" in line:
                    self.artist = self.getMetaValue("Artist:", line)
        rc = process.poll()
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        return rc

    def getMetaValue(self, key, line):
        val = line.split(key)[1]
        val = val.replace('"','')
        val = val[1:-1]
        return val

if __name__ == "__main__":
    gui = ClockGui()
    gui.run()
