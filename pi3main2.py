#do pip install MIDIUtil

import pygame.midi
import time
import os
import sys
import pygame
from midiutil import MIDIFile

#Pygame midi initialized. This NEEDS to be done before pygame.init
pygame.midi.init()
player = pygame.midi.Output(4)
player.set_instrument(0)

#colors to be used for pygame display
red = 200,0,0
green = 0,200,0
bright_red = 255,0,0
bright_green = 0,255,0
BLACK = 0,0,0
WHITE = 255,255,255

#detect and display all the input devices detected so the user can select which port to use as MIDI input.
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

#Set the port selected by user as the input port for MIDI
input_id = int(mydevicenumber)
i = pygame.midi.Input( input_id )

print "starting"

pygame.init()

#Draw the screen with record and play buttons
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

#The big while loop that should be True always when the program is running
syson = True

#While loop for when it's not recording
going = True

#Conditional for when recorded file should be playing.
playing = False

#While loop for when it's recording
RECORDING = False

global mf
global starttime

mf = MIDIFile(1)
track = 0

#Initializing pygame mixer with appropriate variables
freq = 44100    # audio CD quality
bitsize = -16   # unsigned 16 bit
channels = 2    # 1 is mono, 2 is stereo
buffer = 2048   # number of samples (experiment to get right sound)
pygame.mixer.init(freq, bitsize, channels, buffer)
# optional volume 0 to 1.0
pygame.mixer.music.set_volume(0.8)

#array to store note state (on/off)
notestate = [0]*110

while syson:
	#Not recording
	while going:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
			if event.type == pygame.MOUSEBUTTONUP:
				pos = pygame.mouse.get_pos()
				x,y = pos
				#If record button is pressed, make a new midi file to record the notes in,
				#set the current time as start time to keep track of note timings,
				#change the button to recording, and toggle recording and going variables so
				#the program enters the recording loop
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
				#If play button is pressed
				if 225>x>175 and 145>y>95 :
					#If it was playing, stop playing the recorded file and change the button
					#to play. Set playing to False so the music would not play again.
					if playing:
						pygame.mixer.music.stop()
						playing = False
						pygame.draw.rect(screen, green, (160, 80, 80, 80))
						text_surface = my_font.render("PLAY", True, WHITE)
						rect = text_surface.get_rect(center = (200,120))
						screen.blit(text_surface, rect)
					#If it was not playing, set playing to true so it keeps playing
					# and looping, change the button to playing.
					else:
						playing = True
						pygame.draw.rect(screen, bright_green, (160, 80, 80, 80))
						text_surface = my_font.render("PLAYING", True, WHITE)
						rect = text_surface.get_rect(center = (200,120))
						screen.blit(text_surface, rect)
				#flip so the button changes appear on screen.
				pygame.display.flip()

		#If playing is true, play the recorded music over and over.
		#If mixer is busy, it means it's still playing the music,
		#So don't start playing again. If mixer is not busy, (music
		# is done playing) play it again.
		if playing:
			if not pygame.mixer.music.get_busy():
				pygame.mixer.music.load("output.mid")
				pygame.mixer.music.play()

		#If there is a new midi event, read the event.
		if i.poll():
			midi_events = i.read(10)
			print "full midi_events " + str(midi_events)
			print "my midi note is " + str(midi_events[0][0][1])

			#If the note is not playing, turn on the note.
			if notestate[midi_events[0][0][1]] == 0:
				player.note_on(midi_events[0][0][1],127)
				print "on event"
                notestate[midi_events[0][0][1]] = 1

            #If the note is playing, turn off the note.
			elif notestate[midi_events[0][0][1]] == 1:
				player.note_off(midi_events[0][0][1],127)
				print "off event"
                notestate[midi_events[0][0][1]] = 0


	notes = {}
	#If recording
	while RECORDING:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
			if event.type == pygame.MOUSEBUTTONUP:
				pos = pygame.mouse.get_pos()
				x,y = pos
				#If recording button is pressed, write all the notes
				# to output.mid file and stop recording.
				#Change back the button to record and toggle 
				#going and recording so the program enters
				#non recording while loop.
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
		#If there is new midi input event, play the note and take down
		#information needed to record it into the mid file.
		if i.poll():
			midi_events = i.read(10)
			print "full midi_events " + str(midi_events)
			print "my midi note is " + str(midi_events[0][0][1])
			#If note is not playing, turn it on and store its starting time
			if notestate[midi_events[0][0][1]] == 0:
				player.note_on(midi_events[0][0][1],127)
				print "on event"
				notes[midi_events[0][0][1]] = time.time()-starttime
                notestate[midi_events[0][0][1]] = 1

            #Else if the note was playing, turn it off and calcualte the duration
            #of the note, and add the note to the midi file being generated.
		    elif notestate[midi_events[0][0][1]] == 1:
				player.note_off(midi_events[0][0][1],127)
				print "off event"
				startnote = notes.pop(midi_events[0][0][1])
				duration = time.time() - startnote -starttime
				print (duration)
				mf.addNote(0,0,midi_events[0][0][1],startnote, duration, 100)
                notestate[midi_events[0][0][1]] = 0

#End the program and quit
#You need to delete the midi output for appropriate quitting.
del player
pygame.midi.quit()
pygame.quit()
