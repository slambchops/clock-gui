#!/usr/bin/python

import pygame
import datetime
import calendar
from time import sleep
import threading
import subprocess
import shlex

BG_FILE='./bg1.jpg'
COVER_FILE='./music.png'
STATE_FILE="/tmp/state"
ROBOTO_LIGHT_FILE='./RobotoMono-Light.ttf'
ROBOTO_REG_FILE='./RobotoMono-Regular.ttf'
PARSER_EXE='./metadata.sh'

def cat(file):
    f = open(file,"r")
    t = f.read()
    print t
    f.close()
    return t

class ClockGui:
    def __init__(self):
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
        self.ARTIST_YX = [170, 160]
        self.SONG_YX  = [190, 160]
        self.MUSIC_ICON_YX  = [160, 220]

        # Set the height and width of the screen
        size = [self.HEIGHT, self.WIDTH]
        self.screen = pygame.display.set_mode(size)

        self.bg = pygame.image.load(BG_FILE)
        self.bg = pygame.transform.rotate(self.bg,90)
        self.cover = pygame.image.load(COVER_FILE)
        self.cover = pygame.transform.rotate(self.cover,90)

        # Loop until the user clicks the close button.
        self.done = False
        self.song = ''
        self.artist = ''

        self.timeFont = pygame.font.Font(ROBOTO_LIGHT_FILE, 63)
        self.dateFont = pygame.font.Font(ROBOTO_REG_FILE, 22)
        self.songFont = pygame.font.Font(ROBOTO_REG_FILE, 14)

        self.mdThread = threading.Thread(target=self.metadata)
        self.mdThread.daemon = True
        self.mdThread.start()
    
    def run(self):
        while not self.done:
            #refresh the background image
            self.screen.blit(self.bg, [0,0])

            self.drawTime()

            if "on" in cat(STATE_FILE):
                self.drawMusicInfo()

            # Go ahead and update the screen with what we've drawn.
            pygame.display.flip()

            sleep(1)

        pygame.quit()

    def drawTime(self):
        #generate the strings that will be displayed
        date = datetime.datetime.now()
        day = datetime.date.today().strftime("%A")
        dateString = day +  ', {:%B %d}'.format(date)
        timeString = '{:%I:%M %p}'.format(date)

        #draw the time
        text = self.timeFont.render(timeString, True, self.BLACK)
        timeW,timeH = self.timeFont.size(timeString)
        text = pygame.transform.rotate(text, 90)
        self.screen.blit(text, [self.TIME_Y, (self.WIDTH-timeW)/2])

        #draw the date
        text = self.dateFont.render(dateString, True, self.BLACK)
        dateW, dateH = self.dateFont.size(dateString)
        text = pygame.transform.rotate(text,90)
        self.screen.blit(text, [self.DATE_Y, (self.WIDTH-dateW)/2])

        return

    def drawMusicInfo(self):
        artistString = self.artist
        songString =  self.song

        #draw artist
        text = self.songFont.render(artistString, True, self.BLACK)
        w, h = self.songFont.size(artistString)
        text = pygame.transform.rotate(text,90)
        self.screen.blit(text, self.ARTIST_YX)

        #draw song
        text = self.songFont.render(songString, True, self.BLACK)
        w, h = self.songFont.size(songString)
        text = pygame.transform.rotate(text,90)
        self.screen.blit(text, self.SONG_YX)

        #draw music icon
        self.screen.blit(self.cover, self.MUSIC_ICON_YX)

    def metadata(self):
        print('Starting the metadata app')
        proc = subprocess.Popen(shlex.split(PARSER_EXE), stdout=subprocess.PIPE)
        while not self.done:
            output = proc.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                line = output.strip()
                if "Title:" in line:
                    self.song = self.getMetaValue("Title", line)
                if "Artist:" in line:
                    self.artist = self.getMetaValue("Artist:", line)
        rc = process.poll()
        return rc

    def getMetaValue(self, key, line):
        val = line.split(key)[1]
        val = val.replace('"','')
        val = val[1:-1]
        return val

if __name__ == "__main__":
    gui = ClockGui()
    gui.run()
