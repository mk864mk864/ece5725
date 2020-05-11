#do pip install MIDIUtil

import pygame.midi
import time
import os
import pygame
from midiutil import MIDIFile
import subprocess
import threading

#os.putenv('SDL_VIDEODRIVER', 'fbcon')
#os.putenv('SDL_FBDEV', '/dev/fb1')
#os.putenv('SDL_MOUSEDRV', 'TSLIB')
#os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

pygame.midi.init()
player = pygame.midi.Output(0)
player.set_instrument(0)

red = 200,0,0
green = 0,200,0

bright_red = 255,0,0
bright_green = 0,255,0

BLACK = 0,0,0

WHITE = 255,255,255


for i in range( pygame.midi.get_count() ):
    r = pygame.midi.get_device_info(i)
    (interf, name, input, output, opened) = r
    in_out = ""
    if input:
        in_out = "(input)"
    if output:
        in_out = "(output)"

    print ("%2i: interface :%s:, name :%s:, opened :%s:  %s" % (i, interf, name, opened, in_out))

mydevicenumber=raw_input('See list above. Please enter the number for your midi input device: ')

print "you chose " + mydevicenumber + ''

input_id = int(mydevicenumber)
i = pygame.midi.Input( input_id )

print "starting"

pygame.init()

#pygame.mouse.set_visible(False)

size = width, height = 320, 240
screen = pygame.display.set_mode(size)
screen.fill(BLACK)
my_font = pygame.font.Font(None, 20)

pygame.draw.rect(screen, red, (60, 80, 80, 80))
text_surface = my_font.render("RECORD", True, WHITE)
rect = text_surface.get_rect(center = (100,120))
screen.blit(text_surface, rect)

pygame.draw.rect(screen, green, (160, 80, 80, 80))
text_surface = my_font.render("PLAY", True, WHITE)
rect = text_surface.get_rect(center = (200,120))
screen.blit(text_surface, rect)

pygame.display.flip()

syson = True

going = True

playing = False

RECORDING = False

global mf
global starttime

mf = MIDIFile(1)
track = 0

#clock = pygame.time.Clock()

freq = 44100    # audio CD quality
bitsize = -16   # unsigned 16 bit
channels = 2    # 1 is mono, 2 is stereo
buffer = 2048   # number of samples (experiment to get right sound)
pygame.mixer.init(freq, bitsize, channels, buffer)
# optional volume 0 to 1.0
pygame.mixer.music.set_volume(0.8)

while syson:

	while going:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
			if event.type == pygame.MOUSEBUTTONUP:
				pos = pygame.mouse.get_pos()
				x,y = pos

				if 125>x>75 and 145>y>95 :
					mf = MIDIFile(1)
					starttime = time.time()
					mf.addTrackName(track, 0, "Track")
					mf.addTempo(track, 0, 60)
					pygame.draw.rect(screen, bright_red, (60, 80, 80, 80))
					text_surface = my_font.render("RECORDING", True, WHITE)
					rect = text_surface.get_rect(center = (100,120))
					screen.blit(text_surface, rect)
					RECORDING = True
					going = False

				if 225>x>175 and 145>y>95 :
					if playing:
						pygame.mixer.music.stop()
						playing = False
						pygame.draw.rect(screen, green, (160, 80, 80, 80))
						text_surface = my_font.render("PLAY", True, WHITE)
						rect = text_surface.get_rect(center = (200,120))
						screen.blit(text_surface, rect)
					else:
						playing = True
						pygame.draw.rect(screen, bright_green, (160, 80, 80, 80))
						text_surface = my_font.render("PLAYING", True, WHITE)
						rect = text_surface.get_rect(center = (200,120))
						screen.blit(text_surface, rect)
				pygame.display.flip()

		if playing:
			# if not pygame.mixer.music.get_busy():
			# 	pygame.mixer.music.load("output.mid")
			# 	pygame.mixer.music.play()
			# This is jank command line calling, fork works best
			subprocess.call(["python", "MIDIplay.py", "output.mid"])
			playing = False
			pygame.draw.rect(screen, green, (160, 80, 80, 80))
			text_surface = my_font.render("PLAY", True, WHITE)
			rect = text_surface.get_rect(center = (200,120))
			screen.blit(text_surface, rect)
			pygame.display.flip()


		if i.poll():
			midi_events = i.read(10)
			print "full midi_events " + str(midi_events)
			print "my midi note is " + str(midi_events[0][0][1])

			if str(midi_events[0][0][2]) != "0":
				player.note_on(midi_events[0][0][1],127)
				print "on event"

			if str(midi_events[0][0][2]) == "0":
				player.note_off(midi_events[0][0][1],127)
				print "off event"


	notes = {}

	while RECORDING:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
			if event.type == pygame.MOUSEBUTTONUP:
				pos = pygame.mouse.get_pos()
				x,y = pos

				if 125>x>75 and 145>y>95 :
					with open("output.mid", 'wb') as outf:
						mf.writeFile(outf)
					pygame.draw.rect(screen, red, (60, 80, 80, 80))
					text_surface = my_font.render("RECORD", True, WHITE)
					rect = text_surface.get_rect(center = (100,120))
					screen.blit(text_surface, rect)
					pygame.display.flip()
					going = True
					RECORDING = False

		if i.poll():
			midi_events = i.read(10)
			print "full midi_events " + str(midi_events)
			print "my midi note is " + str(midi_events[0][0][1])

			if str(midi_events[0][0][2]) != "0":
				player.note_on(midi_events[0][0][1],127)
				print "on event"
				notes[midi_events[0][0][1]] = time.time()-starttime

			if str(midi_events[0][0][2]) == "0":
				player.note_off(midi_events[0][0][1],127)
				print "off event"
				startnote = notes.pop(midi_events[0][0][1])
				duration = time.time() - startnote -starttime
				print (duration)
				mf.addNote(0,0,midi_events[0][0][1],startnote, duration, 100)


del player
pygame.midi.quit()
pygame.quit()