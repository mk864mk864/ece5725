import pygame.midi
import time
import os
import pygame
from midiutil import MIDIFile




pygame.midi.init()
player = pygame.midi.Output(0)
player.set_instrument(0)


player.note_on(57,127)
print "on event"

time.sleep(2)

player.note_off(57,127)
print "off event"

player.note_on(60,127)
print "on event"

time.sleep(2)

player.note_off(60,127)
print "off event"

player.note_on(55,127)
print "on event"

time.sleep(2)

player.note_off(55,127)
print "off event"

del player
pygame.midi.quit()